"""
URL configuration for RetroGameCartridge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

# Пространство имен для URL-шаблонов приложения
# Позволяет использовать 'games:game_list' в шаблонах и представлениях
app_name = 'games'

# Список всех URL-маршрутов приложения
urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    # Пример использования в шаблоне: {% url 'games:home' %}
    
    # Список игр
    path('games/', views.game_list, name='game_list'),
    # Пример: /games/
    
    # Детальная страница игры (динамический параметр pk - первичный ключ)
    path('games/<int:pk>/', views.game_detail, name='game_detail'),
    # Пример: /games/1/ (просмотр игры с ID=1)
    # <int:pk> - конвертер, ожидает целое число и передает его в представление
    
    # Создание новой игры
    path('games/create/', views.game_create, name='game_create'),
    # Пример: /games/create/ (форма создания игры)
    
    # Редактирование существующей игры
    path('games/<int:pk>/update/', views.game_update, name='game_update'),
    # Пример: /games/1/update/ (редактирование игры с ID=1)
    
    # Удаление игры
    path('games/<int:pk>/delete/', views.game_delete, name='game_delete'),
    # Пример: /games/1/delete/ (удаление игры с ID=1)
    
    # Создание отзыва
    path('games/<int:game_id>/review/create/', views.review_create, name='review_create'),
    # Пример: /games/1/review/create/ (создание отзыва к игре)
    
    # Редактирование отзыва
    path('reviews/<int:pk>/update/', views.review_update, name='review_update'),
    # Пример: /reviews/1/update/ (редактирование отзыва с ID=1)
    
    # Удаление отзыва
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
    # Пример: /reviews/1/delete/ (удаление отзыва с ID=1)
    
    # Список студий
    path('studios/', views.studio_list, name='studio_list'),
    # Пример: /studios/
    
    # Создание новой студии
    path('studios/create/', views.studio_create, name='studio_create'),
    # Пример: /studios/create/
    
    # Список жанров
    path('categories/', views.category_list, name='category_list'),
    # Пример: /categories/
    
    # Создание нового жанра
    path('categories/create/', views.category_create, name='category_create'),
    # Пример: /categories/create/
    
    # Список платформ
    path('platforms/', views.platform_list, name='platform_list'),
    # Пример: /platforms/
    
    # Создание новой платформы
    path('platforms/create/', views.platform_create, name='platform_create'),
    # Пример: /platforms/create/

    # Редактирование платформы
    path('platforms/<int:pk>/update/', views.platform_update, name='platform_update')

]