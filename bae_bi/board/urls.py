from django.urls import path

from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('<str:category_name>', views.category, name="category"),
]
