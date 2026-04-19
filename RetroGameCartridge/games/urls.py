# games/urls.py
from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    # Главная
    path('', views.home, name='home'),
    
    # Игры
    path('games/', views.game_list, name='game_list'),
    path('games/<int:pk>/', views.game_detail, name='game_detail'),
    path('games/create/', views.game_create, name='game_create'),
    path('games/<int:pk>/update/', views.game_update, name='game_update'),
    path('games/<int:pk>/delete/', views.game_delete, name='game_delete'),
    
    # Отзывы (только один раз каждый!)
    path('games/<int:game_id>/review/create/', views.review_create, name='review_create'),
    path('reviews/<int:pk>/update/', views.review_update, name='review_update'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
    
    # Студии
    path('studios/', views.studio_list, name='studio_list'),
    path('studios/create/', views.studio_create, name='studio_create'),
    
    # Жанры
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    
    # Платформы
    path('platforms/', views.platform_list, name='platform_list'),
    path('platforms/create/', views.platform_create, name='platform_create'),
    path('platforms/<int:pk>/update/', views.platform_update, name='platform_update'),
    
    # Регистрация
    path('register/', views.register, name='register'),
]