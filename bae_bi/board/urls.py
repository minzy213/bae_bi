from django.urls import path

from . import views

urlpatterns = [
    path('', views.category, name='main'),
    path('<str:category_name>', views.category, name="category"),
]
