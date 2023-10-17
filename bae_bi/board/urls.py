from django.urls import path

from . import views

app_name = 'board'

urlpatterns = [
    path('', views.main, name='main'),
    path('<str:category_name>', views.category, name="category"),
    path('comp_cart', views.comp_cart, name="comp_cart"),
]
