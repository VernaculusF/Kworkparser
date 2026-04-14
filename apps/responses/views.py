from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest
from django.core.paginator import Paginator, Page

from .models import Response


def response_list(request: HttpRequest) -> render:
    """Список откликов."""
    responses = Response.objects.select_related("project").all()

    status = request.GET.get("status")
    if status:
        responses = responses.filter(status=status)

    paginator = Paginator(responses, 50)
    page_obj: Page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "responses/response_list.html",
        {
            "page_obj": page_obj,
        },
    )


def response_detail(request: HttpRequest, pk: int) -> render:
    """Детальная страница отклика."""
    response = get_object_or_404(Response, pk=pk)
    return render(request, "responses/response_detail.html", {"response": response})
