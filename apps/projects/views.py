from typing import Optional

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, Page
from django.db.models import Q, QuerySet
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST
import threading
import queue

from .models import Project, Category
from apps.parser.kwork_parser import KworkParser

# Константы
PAGINATE_BY = 50
MAX_PARSE_PAGES = 999
EMPTY_PAGES_THRESHOLD = 3
PAGE_LOAD_DELAY = 3  # секунды

# Глобальная очередь для передачи данных о парсинге
parse_queue: queue.Queue = queue.Queue()
parse_status: dict = {'running': False, 'total': 0}


def _get_filtered_projects(
    status_filter: Optional[str] = None,
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    force_status: Optional[str] = None,
) -> QuerySet[Project]:
    """Общая функция фильтрации проектов для устранения дублирования кода."""
    queryset = Project.objects.select_related('category').all()

    if force_status:
        queryset = queryset.filter(status=force_status)
    elif status_filter:
        queryset = queryset.filter(status=status_filter)

    if category_id:
        queryset = queryset.filter(category_id=category_id)

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    return queryset


def _get_paginated_projects(request: HttpRequest, queryset: QuerySet[Project]) -> Page:
    """Пагинация списка проектов."""
    paginator = Paginator(queryset, PAGINATE_BY)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def _get_active_categories() -> QuerySet[Category]:
    """Получение активных категорий для фильтров."""
    return Category.objects.filter(is_active=True)


def _build_filter_context(
    page_obj: Page,
    status: Optional[str] = None,
    category_id: Optional[str] = None,
    search: Optional[str] = None,
) -> dict:
    """Общий контекст для views с фильтрами."""
    return {
        'page_obj': page_obj,
        'categories': _get_active_categories(),
        'current_status': status,
        'current_category': category_id,
        'search_query': search,
    }


def project_list(request: HttpRequest) -> render:
    """Список заказов с фильтрами."""
    status = request.GET.get('status')
    category_id = request.GET.get('category')
    search = request.GET.get('search')

    projects = _get_filtered_projects(
        status_filter=status,
        category_id=category_id,
        search=search,
    )
    page_obj = _get_paginated_projects(request, projects)

    return render(request, 'projects/project_list.html', _build_filter_context(
        page_obj, status=status, category_id=category_id, search=search,
    ))


def responded_list(request: HttpRequest) -> render:
    """Список заказов с откликами."""
    category_id = request.GET.get('category')
    search = request.GET.get('search')

    projects = _get_filtered_projects(
        category_id=category_id,
        search=search,
        force_status='responded',
    )
    page_obj = _get_paginated_projects(request, projects)

    return render(request, 'projects/responded_list.html', _build_filter_context(
        page_obj, category_id=category_id, search=search,
    ))


def project_detail(request: HttpRequest, pk: int) -> render:
    """Детальная страница заказа."""
    project = get_object_or_404(Project, pk=pk)

    if not project.is_viewed:
        project.is_viewed = True
        if project.status == 'new':
            project.status = 'viewed'
        project.save()

    return render(request, 'projects/project_detail.html', {'project': project})


@require_POST
def mark_responded(request: HttpRequest, pk: int) -> JsonResponse:
    """Отметить отклик отправлен."""
    project = get_object_or_404(Project, pk=pk)
    project.status = 'responded'
    project.save()

    return JsonResponse({'success': True})


@require_POST
def mark_archived(request: HttpRequest, pk: int) -> redirect:
    """Архивировать заказ."""
    project = get_object_or_404(Project, pk=pk)
    project.status = 'archived'
    project.save()

    return redirect('projects:project_list')


@require_POST
def parse_projects_start(request: HttpRequest) -> JsonResponse:
    """Запуск парсинга в фоновом потоке."""
    if parse_status['running']:
        return JsonResponse({'error': 'Парсинг уже запущен'}, status=400)

    category_id = request.POST.get('category_id')

    if not category_id:
        return JsonResponse({'error': 'Выберите категорию'}, status=400)

    # Очищаем очередь
    while not parse_queue.empty():
        parse_queue.get()

    parse_status['running'] = True
    parse_status['total'] = 0

    thread = threading.Thread(target=run_parser, args=(category_id,))
    thread.daemon = True
    thread.start()

    return JsonResponse({'status': 'started'})


def parse_projects_status(request: HttpRequest) -> JsonResponse:
    """Получение статуса парсинга."""
    events = []

    while not parse_queue.empty():
        try:
            event = parse_queue.get_nowait()
            events.append(event)
        except queue.Empty:
            break

    return JsonResponse({
        'events': events,
        'running': parse_status['running'],
        'total': parse_status['total'],
    })


def run_parser(category_id: str) -> None:
    """Функция парсинга в фоновом потоке."""
    try:
        if category_id == 'all':
            categories = Category.objects.filter(is_active=True)
            parser = KworkParser(
                delay=settings.PARSER_DELAY,
                timeout=settings.PARSER_TIMEOUT,
                max_pages=MAX_PARSE_PAGES,
            )

            for category in categories:
                parse_queue.put({'type': 'category_start', 'category': category.name})
                new_count = parse_single_category(parser, category)
                parse_status['total'] += new_count
                parse_queue.put({
                    'type': 'category_done',
                    'category': category.name,
                    'count': new_count,
                })

        elif category_id:
            try:
                category = Category.objects.get(kwork_id=int(category_id))
                parser = KworkParser(
                    delay=settings.PARSER_DELAY,
                    timeout=settings.PARSER_TIMEOUT,
                    max_pages=MAX_PARSE_PAGES,
                )

                parse_queue.put({'type': 'category_start', 'category': category.name})
                new_count = parse_single_category(parser, category)
                parse_status['total'] = new_count

            except Category.DoesNotExist:
                parse_queue.put({'type': 'error', 'message': 'Категория не найдена'})

        parse_queue.put({'type': 'complete', 'total': parse_status['total']})

    except Exception as e:
        parse_queue.put({'type': 'error', 'message': str(e)})

    finally:
        parse_status['running'] = False


def parse_single_category(parser: KworkParser, category: Category) -> int:
    """Парсинг одной категории."""
    new_projects_count = 0
    page = 1
    empty_pages = 0

    parser._init_driver()

    try:
        while True:
            url = f'{parser.BASE_URL}/projects?c={category.kwork_id}'
            if page > 1:
                url += f'&page={page}'

            parse_queue.put({'type': 'page_start', 'page': page})

            try:
                parser.driver.get(url)

                try:
                    from selenium.webdriver.common.by import By
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    import time

                    WebDriverWait(parser.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "want-card"))
                    )
                except Exception:
                    parse_queue.put({'type': 'page_done', 'page': page, 'count': 0, 'no_more': True})
                    break

                time.sleep(PAGE_LOAD_DELAY)

                html = parser.driver.page_source
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'lxml')

                projects = parser.extract_projects(soup, category)

                if not projects:
                    parse_queue.put({'type': 'page_done', 'page': page, 'count': 0, 'no_more': True})
                    break

                page_new = 0
                for project_data in projects:
                    created = parser.save_project(project_data)
                    if created:
                        page_new += 1
                        new_projects_count += 1

                        parse_queue.put({
                            'type': 'new_project',
                            'project': {
                                'id': project_data['kwork_id'],
                                'title': project_data['title'],
                                'price': str(project_data.get('price', '')),
                                'url': project_data['url'],
                            },
                        })

                if page_new == 0:
                    empty_pages += 1
                else:
                    empty_pages = 0

                parse_queue.put({'type': 'page_done', 'page': page, 'count': page_new})

                if empty_pages >= EMPTY_PAGES_THRESHOLD:
                    parse_queue.put({
                        'type': 'info',
                        'message': f'Остановка: {EMPTY_PAGES_THRESHOLD} страницы подряд без новых проектов',
                    })
                    break

                page += 1
                time.sleep(parser.delay)

            except Exception as e:
                parse_queue.put({'type': 'error', 'message': f'Ошибка на странице {page}: {str(e)}'})
                break

    finally:
        parser._close_driver()

    return new_projects_count
