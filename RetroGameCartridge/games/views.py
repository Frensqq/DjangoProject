from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Game, GameStudio, Category, Platform, Review
from .forms import (GameForm, GameStudioForm, CategoryForm, 
                   PlatformForm, ReviewForm, UserRegistrationForm)

def is_moderator(user):
    """Проверка, является ли пользователь модератором"""
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Moderator').exists())


def home(request):

    total_games = Game.objects.count()  
    total_studios = GameStudio.objects.count()  
    total_categories = Category.objects.count()  
    total_platforms = Platform.objects.count()  
    recent_games = Game.objects.all()[:5]  
    
    context = {
        'total_games': total_games,
        'total_studios': total_studios,
        'total_categories': total_categories,
        'total_platforms': total_platforms,
        'recent_games': recent_games,
    }
    return render(request, 'games/home.html', context)


def game_list(request):
    games = Game.objects.select_related('game_studio').prefetch_related('categories', 'platforms').all()
    
    query = request.GET.get('q')
    studio_id = request.GET.get('studio')
    category_id = request.GET.get('category')
    platform_id = request.GET.get('platform')
    available_only = request.GET.get('available')
    sort_by = request.GET.get('sort', '-created_at')
    
    if query:
        games = games.filter(
            Q(name__icontains=query) |  
            Q(description__icontains=query) | 
            Q(game_studio__name__icontains=query)  
        )
    
    
    if studio_id:
        games = games.filter(game_studio_id=studio_id)
    
   
    if category_id:
        games = games.filter(categories__id=category_id)
    
    
    if platform_id:
        games = games.filter(platforms__id=platform_id)
    
    if available_only:
        games = games.filter(is_available=True)
    
 
    games = games.order_by(sort_by)
    
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
    game = get_object_or_404(
        Game.objects.select_related('game_studio')
        .prefetch_related('categories', 'platforms', 'reviews__user'),
        pk=pk
    )
    
    reviews = game.reviews.select_related('user').all()
    

    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    
    context = {
        'game': game,
        'reviews': reviews,
        'user_review': user_review,
    }
    return render(request, 'games/game_detail.html', context)



@login_required
def game_create(request):
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
def game_update(request, pk):
    game = get_object_or_404(Game, pk=pk)
    
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            game = form.save()
            messages.success(request, f'Игра "{game.name}" успешно обновлена!')
            return redirect('games:game_detail', pk=game.pk)
    else:
        form = GameForm(instance=game)
    
    return render(request, 'games/game_form.html', {'form': form, 'title': 'Редактировать игру'})



@login_required
def game_delete(request, pk):

    if not (request.user.is_superuser or request.user.groups.filter(name='Moderator').exists()):
        messages.error(request, 'У вас нет прав на удаление!')
        return redirect('games:game_detail', pk=pk)

    game = get_object_or_404(Game, pk=pk)


    
    if request.method == 'POST':
        game.delete()
        messages.success(request, f'Игра "{game.name}" удалена!')
        return redirect('games:game_list')

    return render(request, 'games/game_confirm_delete.html', {'game': game})


@login_required
def review_create(request, game_id):
    """Создание отзыва - могут все авторизованные"""
    game = get_object_or_404(Game, pk=game_id)
    
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
def review_update(request, pk):
    """Редактирование отзыва - только модераторы и админы"""
    review = get_object_or_404(Review, pk=pk)
    
    if not (request.user.is_superuser or request.user.groups.filter(name='Moderator').exists()):
        messages.error(request, 'Вы не можете редактировать чужие отзывы!')
        return redirect('games:game_detail', pk=review.game.pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв обновлен!')
            return redirect('games:game_detail', pk=review.game.pk)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'games/review_form.html', {'form': form, 'game': review.game})


@login_required
def review_delete(request, pk):
    """Удаление отзыва - только модераторы и админы"""
    review = get_object_or_404(Review, pk=pk)
    
    if not (request.user.is_superuser or request.user.groups.filter(name='Moderator').exists()):
        messages.error(request, 'Вы не можете удалять чужие отзывы!')
        return redirect('games:game_detail', pk=review.game.pk)
    
    if request.method == 'POST':
        game_pk = review.game.pk
        review.delete()
        messages.success(request, 'Отзыв удален!')
        return redirect('games:game_detail', pk=game_pk)
    
    return render(request, 'games/review_confirm_delete.html', {'review': review})



# Список студий
def studio_list(request):
    """
    Отображает список всех студий-разработчиков.
    """
    studios = GameStudio.objects.prefetch_related('games').all()

    # Получаем параметры фильтрации из GET запроса
    query = request.GET.get('q')
    
    # Поиск по тексту (название, страна, глава компании)
    if query:
        studios = studios.filter(
            Q(name__icontains=query) |  # Название содержит query (без учета регистра)
            Q(country__icontains=query) |  # Описание содержит query
            Q(director__icontains=query)  # Название студии содержит query
        )
    

    # Контекст для шаблона
    context = {
        'studios': studios,
    }

    return render(request, 'games/studio_list.html', context)


# Добавление студии
@login_required
def studio_create(request):
    """Обрабатывает создание новой студии."""
    if not is_moderator(request.user):
        messages.error(request, 'У вас нет прав на добавление студий!')
        return redirect('games:studio_list')
    
    if request.method == 'POST':
        form = GameStudioForm(request.POST, request.FILES)
        if form.is_valid():
            studio = form.save()
            messages.success(request, f'Студия "{studio.name}" успешно добавлена!')
            return redirect('games:studio_list')
    else:
        form = GameStudioForm()
    
    return render(request, 'games/studio_form.html', {'form': form, 'title': 'Добавить студию'})


# Список жанров с поиском
def category_list(request):
    """
    Отображает список всех жанров с возможностью поиска.
    """
    categories = Category.objects.prefetch_related('games').all()
    
    # Получаем параметры поиска
    query = request.GET.get('q')
    
    # Поиск по названию или описанию
    if query:
        categories = categories.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    context = {
        'categories': categories,
    }
    return render(request, 'games/category_list.html', context)


# Добавление жанра (уже есть, но обновим)
@login_required
def category_create(request):
    """Обрабатывает создание нового жанра."""
    if not is_moderator(request.user):
        messages.error(request, 'У вас нет прав на добавление жанров!')
        return redirect('games:category_list')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Жанр "{category.name}" успешно добавлен!')
            return redirect('games:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'games/category_form.html', {
        'form': form, 
        'title': 'Добавить жанр'
    })


# Редактирование жанра
@login_required
def category_update(request, pk):
    """Обрабатывает редактирование существующего жанра."""
    if not is_moderator(request.user):
        messages.error(request, 'У вас нет прав на редактирование жанров!')
        return redirect('games:category_list')
    
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Жанр "{category.name}" успешно обновлен!')
            return redirect('games:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'games/category_form.html', {
        'form': form,
        'title': 'Редактировать жанр'
    })
# Список платформ
def platform_list(request):
    """
    Отображает список всех платформ.
    """
    platforms = Platform.objects.prefetch_related('games').all()

    query = request.GET.get('q')
    
    # Поиск по названию или производителю
    if query:
        platforms = platforms.filter(
            Q(name__icontains=query) |
            Q(manufacturer__icontains=query)
        )


    return render(request, 'games/platform_list.html', {'platforms': platforms})


# Добавление платформы
@login_required
def platform_create(request):
    """Обрабатывает создание новой платформы."""
    if not is_moderator(request.user):
        messages.error(request, 'У вас нет прав на добавление платформ!')
        return redirect('games:platform_list')
    
    if request.method == 'POST':
        form = PlatformForm(request.POST)
        if form.is_valid():
            platform = form.save()
            messages.success(request, f'Платформа "{platform.name}" успешно добавлена!')
            return redirect('games:platform_list')
    else:
        form = PlatformForm()
    
    return render(request, 'games/platform_form.html', {'form': form, 'title': 'Добавить платформу'})

@login_required
def platform_update(request, pk):
    """Обрабатывает редактирование существующей платформы."""
    if not is_moderator(request.user):
        messages.error(request, 'У вас нет прав на редактирование платформ!')
        return redirect('games:platform_list')
    
    platform = get_object_or_404(Platform, pk=pk)
    
    if request.method == 'POST':
        form = PlatformForm(request.POST, instance=platform)
        if form.is_valid():
            platform = form.save()
            messages.success(request, f'Платформа "{platform.name}" успешно обновлена!')
            return redirect('games:platform_list')
    else:
        form = PlatformForm(instance=platform)
    
    return render(request, 'games/platform_form.html', {
        'form': form,
        'title': 'Редактировать платформу'
    })


# Регистрация пользователя
def register(request):
    """
    Обрабатывает регистрацию нового пользователя.
    GET: отображает пустую форму
    POST: создает пользователя и выполняет автоматический вход
    """
    if request.method == 'POST':
        # Создаем форму с данными POST
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя
            user = form.save()
            # Автоматический вход после регистрации
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! Вы успешно зарегистрированы.')
            return redirect('games:home')
    else:
        # GET запрос - создаем пустую форму
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})