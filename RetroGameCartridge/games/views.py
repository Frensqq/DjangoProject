from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Avg
from .models import Game, GameStudio, Category, Platform, Review
from .forms import (GameForm, GameStudioForm, CategoryForm, 
                   PlatformForm, ReviewForm, UserRegistrationForm)


def game_list(request):
    """
    Отображает список всех игр с фильтрацией и поиском.
    """
    games = Game.objects.all()
    
    # Поиск по названию
    query = request.GET.get('q')
    if query:
        games = games.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(game_studio__name__icontains=query)
        )
    
    # Фильтр по студии
    studio_id = request.GET.get('studio')
    if studio_id:
        games = games.filter(game_studio_id=studio_id)
    
    # Фильтр по жанру
    category_id = request.GET.get('category')
    if category_id:
        games = games.filter(categories__id=category_id)
    
    # Фильтр по платформе
    platform_id = request.GET.get('platform')
    if platform_id:
        games = games.filter(platforms__id=platform_id)
    
    # Фильтр по доступности
    if request.GET.get('available'):
        games = games.filter(is_available=True)
    
    # Сортировка
    sort_by = request.GET.get('sort', '-created_at')
    games = games.order_by(sort_by)
    
    # Получаем данные для фильтров
    studios = GameStudio.objects.all()
    categories = Category.objects.all()
    platforms = Platform.objects.all()
    
    context = {
        'games': games,
        'studios': studios,
        'categories': categories,
        'platforms': platforms,
        'current_sort': sort_by,
    }
    return render(request, 'games/game_list.html', context)


def game_detail(request, pk):
    """
    Отображает детальную информацию об игре и отзывы к ней.
    """
    game = get_object_or_404(Game, pk=pk)
    reviews = game.reviews.all()
    
    # Проверяем, может ли пользователь оставить отзыв
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    
    context = {
        'game': game,
        'reviews': reviews,
        'user_review': user_review,
        'review_form': ReviewForm() if not user_review else None,
    }
    return render(request, 'games/game_detail.html', context)


@login_required
def game_create(request):
    """
    Создание новой игры (только для авторизованных пользователей).
    """
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            game = form.save()
            messages.success(request, f'Игра "{game.name}" успешно добавлена!')
            return redirect('games:game_detail', pk=game.pk)
    else:
        form = GameForm()
    
    return render(request, 'games/game_form.html', {'form': form, 'title': 'Добавить игру'})


@login_required
def game_edit(request, pk):
    """
    Редактирование игры (только для авторизованных пользователей).
    """
    game = get_object_or_404(Game, pk=pk)
    
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            form.save()
            messages.success(request, f'Игра "{game.name}" успешно обновлена!')
            return redirect('games:game_detail', pk=game.pk)
    else:
        form = GameForm(instance=game)
    
    return render(request, 'games/game_form.html', {'form': form, 'title': 'Редактировать игру'})


@login_required
def game_delete(request, pk):
    """
    Удаление игры.
    """
    game = get_object_or_404(Game, pk=pk)
    
    if request.method == 'POST':
        game_name = game.name
        game.delete()
        messages.success(request, f'Игра "{game_name}" успешно удалена!')
        return redirect('games:game_list')
    
    return render(request, 'games/game_confirm_delete.html', {'game': game})


@login_required
def review_create(request, game_id):
    """
    Добавление отзыва к игре.
    """
    game = get_object_or_404(Game, pk=game_id)
    
    # Проверяем, не оставлял ли пользователь уже отзыв
    if Review.objects.filter(game=game, user=request.user).exists():
        messages.error(request, 'Вы уже оставили отзыв к этой игре!')
        return redirect('games:game_detail', pk=game.pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.game = game
            review.user = request.user
            review.save()
            messages.success(request, 'Ваш отзыв успешно добавлен!')
            return redirect('games:game_detail', pk=game.pk)
    else:
        form = ReviewForm()
    
    return render(request, 'games/review_form.html', {'form': form, 'game': game})


@login_required
def review_edit(request, pk):
    """
    Редактирование отзыва.
    """
    review = get_object_or_404(Review, pk=pk)
    
    # Проверяем, что пользователь - автор отзыва
    if review.user != request.user:
        messages.error(request, 'Вы не можете редактировать чужой отзыв!')
        return redirect('games:game_detail', pk=review.game.pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш отзыв обновлен!')
            return redirect('games:game_detail', pk=review.game.pk)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'games/review_form.html', {'form': form, 'game': review.game})


@login_required
def review_delete(request, pk):
    """
    Удаление отзыва.
    """
    review = get_object_or_404(Review, pk=pk)
    
    if review.user != request.user:
        messages.error(request, 'Вы не можете удалить чужой отзыв!')
        return redirect('games:game_detail', pk=review.game.pk)
    
    if request.method == 'POST':
        game_pk = review.game.pk
        review.delete()
        messages.success(request, 'Ваш отзыв удален!')
        return redirect('games:game_detail', pk=game_pk)
    
    return render(request, 'games/review_confirm_delete.html', {'review': review})


def studio_list(request):
    """Список студий."""
    studios = GameStudio.objects.all()
    return render(request, 'games/studio_list.html', {'studios': studios})


@login_required
def studio_create(request):
    """Создание студии."""
    if request.method == 'POST':
        form = GameStudioForm(request.POST, request.FILES)
        if form.is_valid():
            studio = form.save()
            messages.success(request, f'Студия "{studio.name}" добавлена!')
            return redirect('games:studio_list')
    else:
        form = GameStudioForm()
    
    return render(request, 'games/studio_form.html', {'form': form})


def category_list(request):
    """Список жанров."""
    categories = Category.objects.all()
    return render(request, 'games/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    """Создание жанра."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Жанр "{category.name}" добавлен!')
            return redirect('games:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'games/category_form.html', {'form': form})


def platform_list(request):
    """Список платформ."""
    platforms = Platform.objects.all()
    return render(request, 'games/platform_list.html', {'platforms': platforms})


@login_required
def platform_create(request):
    """Создание платформы."""
    if request.method == 'POST':
        form = PlatformForm(request.POST)
        if form.is_valid():
            platform = form.save()
            messages.success(request, f'Платформа "{platform.name}" добавлена!')
            return redirect('games:platform_list')
    else:
        form = PlatformForm()
    
    return render(request, 'games/platform_form.html', {'form': form})


def register(request):
    """
    Регистрация нового пользователя.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            messages.success(request, 'Вы успешно зарегистрированы!')
            return redirect('games:game_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})