from django.urls import path

from . import views

app_name = "responses"

urlpatterns = [
    path("", views.response_list, name="response_list"),
    path("<int:pk>/", views.response_detail, name="response_detail"),
]
