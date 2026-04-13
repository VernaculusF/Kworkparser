from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import threading
import queue

from .models import Project, Category
from apps.parser.kwork_parser import KworkParser

# Глобальная очередь для передачи данных о парсинге
parse_queue = queue.Queue()
parse_status = {'running': False, 'total': 0}


def project_list(request):
    """Список заказов с фильтрами"""
    projects = Project.objects.select_related('category').all()
    
    # Фильтры
    status = request.GET.get('status')
    category_id = request.GET.get('category')
    search = request.GET.get('search')
    
    if status:
        projects = projects.filter(status=status)
    
    if category_id:
        projects = projects.filter(category_id=category_id)
    
    if search:
        projects = projects.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(projects, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Категории для фильтра
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_status': status,
        'current_category': category_id,
        'search_query': search,
    }
    
    return render(request, 'projects/project_list.html', context)


def responded_list(request):
    """Список заказов с откликами"""
    projects = Project.objects.select_related('category').filter(status='responded')
    
    # Фильтры
    category_id = request.GET.get('category')
    search = request.GET.get('search')
    
    if category_id:
        projects = projects.filter(category_id=category_id)
    
    if search:
        projects = projects.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(projects, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Категории для фильтра
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'search_query': search,
    }
    
    return render(request, 'projects/responded_list.html', context)


def project_detail(request, pk):
    """Детальная страница заказа"""
    project = get_object_or_404(Project, pk=pk)
    
    # Отметить как просмотренный
    if not project.is_viewed:
        project.is_viewed = True
        if project.status == 'new':
            project.status = 'viewed'
        project.save()
    
    return render(request, 'projects/project_detail.html', {'project': project})


def mark_responded(request, pk):
    """Отметить отклик отправлен"""
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        project.status = 'responded'
        project.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def mark_archived(request, pk):
    """Архивировать заказ"""
    project = get_object_or_404(Project, pk=pk)
    project.status = 'archived'
    project.save()
    
    return redirect('projects:project_list')


def parse_projects_start(request):
    """Запуск парсинга в фоновом потоке"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
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
    
    # Запускаем парсинг в отдельном потоке
    thread = threading.Thread(target=run_parser, args=(category_id,))
    thread.daemon = True
    thread.start()
    
    return JsonResponse({'status': 'started'})


def parse_projects_status(request):
    """Получение статуса парсинга"""
    events = []
    
    # Получаем все события из очереди
    while not parse_queue.empty():
        try:
            event = parse_queue.get_nowait()
            events.append(event)
        except queue.Empty:
            break
    
    return JsonResponse({
        'events': events,
        'running': parse_status['running'],
        'total': parse_status['total']
    })


def run_parser(category_id):
    """Функция парсинга в фоновом потоке"""
    try:
        if category_id == 'all':
            categories = Category.objects.filter(is_active=True)
            parser = KworkParser(
                delay=settings.PARSER_DELAY,
                timeout=settings.PARSER_TIMEOUT,
                max_pages=999
            )
            
            for category in categories:
                parse_queue.put({'type': 'category_start', 'category': category.name})
                new_count = parse_single_category(parser, category)
                parse_status['total'] += new_count
                parse_queue.put({'type': 'category_done', 'category': category.name, 'count': new_count})
        
        elif category_id:
            try:
                category = Category.objects.get(kwork_id=int(category_id))
                parser = KworkParser(
                    delay=settings.PARSER_DELAY,
                    timeout=settings.PARSER_TIMEOUT,
                    max_pages=999
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


def parse_single_category(parser, category):
    """Парсинг одной категории"""
    new_projects_count = 0
    page = 1
    empty_pages = 0  # Счетчик пустых страниц подряд
    
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
                except:
                    # Если нет карточек - значит страниц больше нет
                    parse_queue.put({'type': 'page_done', 'page': page, 'count': 0, 'no_more': True})
                    break
                
                time.sleep(3)
                
                html = parser.driver.page_source
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'lxml')
                
                projects = parser.extract_projects(soup, category)
                
                if not projects:
                    parse_queue.put({'type': 'page_done', 'page': page, 'count': 0, 'no_more': True})
                    break
                
                # Сохранение проектов
                page_new = 0
                for project_data in projects:
                    created = parser.save_project(project_data)
                    if created:
                        page_new += 1
                        new_projects_count += 1
                        
                        # Отправляем данные о новом проекте
                        parse_queue.put({
                            'type': 'new_project',
                            'project': {
                                'id': project_data['kwork_id'],
                                'title': project_data['title'],
                                'price': str(project_data.get('price', '')),
                                'url': project_data['url']
                            }
                        })
                
                # Если на странице 0 новых проектов - увеличиваем счетчик
                if page_new == 0:
                    empty_pages += 1
                else:
                    empty_pages = 0  # Сбрасываем если нашли новые
                
                parse_queue.put({'type': 'page_done', 'page': page, 'count': page_new})
                
                # Если 3 страницы подряд без новых проектов - останавливаемся
                if empty_pages >= 3:
                    parse_queue.put({'type': 'info', 'message': f'Остановка: 3 страницы подряд без новых проектов'})
                    break
                
                page += 1
                time.sleep(parser.delay)
                
            except Exception as e:
                parse_queue.put({'type': 'error', 'message': f'Ошибка на странице {page}: {str(e)}'})
                break
    
    finally:
        parser._close_driver()
    
    return new_projects_count
