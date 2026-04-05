# Create your views here.
# Импорт необходимых модулей и классов
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Game, GameStudio, Category, Platform, Review
from .forms import (GameForm, GameStudioForm, CategoryForm, 
                   PlatformForm, ReviewForm, UserRegistrationForm)


# Главная страница - вывод статистики и информации
def home(request):
    """
    Главная страница приложения.
    Отображает общую статистику по каталогу:
    - общее количество игр
    - общее количество студий
    - общее количество жанров
    - общее количество платформ
    - последние 5 добавленных игр
    """
    # Подсчет количества записей в базе данных
    total_games = Game.objects.count()  # Все игры
    total_studios = GameStudio.objects.count()  # Все студии
    total_categories = Category.objects.count()  # Все жанры
    total_platforms = Platform.objects.count()  # Все платформы
    recent_games = Game.objects.all()[:5]  # Последние 5 игр (сортировка по умолчанию - по дате создания)
    
    # Контекст для передачи в шаблон
    context = {
        'total_games': total_games,
        'total_studios': total_studios,
        'total_categories': total_categories,
        'total_platforms': total_platforms,
        'recent_games': recent_games,
    }
    return render(request, 'games/home.html', context)


# Список игр с фильтрацией и поиском
def game_list(request):
    """
    Отображает список всех игр с возможностью фильтрации.
    Использует GET параметры для фильтрации.
    """
    # Получаем все игры с предварительной загрузкой связанных данных
    # select_related для ForeignKey, prefetch_related для ManyToMany
    games = Game.objects.select_related('game_studio').prefetch_related('categories', 'platforms').all()
    
    # Получаем параметры фильтрации из GET запроса
    query = request.GET.get('q')
    studio_id = request.GET.get('studio')
    category_id = request.GET.get('category')
    platform_id = request.GET.get('platform')
    available_only = request.GET.get('available')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Поиск по тексту (название, описание, студия)
    if query:
        games = games.filter(
            Q(name__icontains=query) |  # Название содержит query (без учета регистра)
            Q(description__icontains=query) |  # Описание содержит query
            Q(game_studio__name__icontains=query)  # Название студии содержит query
        )
    
    # Фильтр по конкретной студии
    if studio_id:
        games = games.filter(game_studio_id=studio_id)
    
    # Фильтр по жанру
    if category_id:
        games = games.filter(categories__id=category_id)
    
    # Фильтр по платформе
    if platform_id:
        games = games.filter(platforms__id=platform_id)
    
    # Фильтр только доступных игр
    if available_only:
        games = games.filter(is_available=True)
    
    # Сортировка
    games = games.order_by(sort_by)
    
    # Получаем данные для фильтров
    studios = GameStudio.objects.all()
    categories = Category.objects.all()
    platforms = Platform.objects.all()
    
    # Контекст для шаблона
    context = {
        'games': games,
        'studios': studios,
        'categories': categories,
        'platforms': platforms,
        'current_sort': sort_by,
    }
    return render(request, 'games/game_list.html', context)


# Детальная информация об игре
def game_detail(request, pk):
    """
    Отображает подробную информацию о конкретной игре.
    pk - первичный ключ (ID) игры.
    """
    # Получаем игру по ID или возвращаем 404
    game = get_object_or_404(
        Game.objects.select_related('game_studio')
        .prefetch_related('categories', 'platforms', 'reviews__user'),
        pk=pk
    )
    
    # Получаем все отзывы к игре
    reviews = game.reviews.select_related('user').all()
    
    # Проверяем, оставлял ли пользователь отзыв
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    
    context = {
        'game': game,
        'reviews': reviews,
        'user_review': user_review,
    }
    return render(request, 'games/game_detail.html', context)


# Добавление новой игры
@login_required
def game_create(request):
    """
    Обрабатывает создание новой игры.
    GET: отображает пустую форму
    POST: сохраняет данные и перенаправляет на страницу игры
    """
    if request.method == 'POST':
        # Создаем форму с переданными данными и файлами
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохраняем игру в БД
            game = form.save()
            # Добавляем сообщение об успехе
            messages.success(request, f'Игра "{game.name}" успешно добавлена!')
            # Перенаправляем на страницу созданной игры
            return redirect('games:game_detail', pk=game.pk)
    else:
        # GET запрос - создаем пустую форму
        form = GameForm()
    
    # Рендерим шаблон с формой
    return render(request, 'games/game_form.html', {'form': form, 'title': 'Добавить игру'})


# Редактирование игры
@login_required
def game_update(request, pk):
    """
    Обрабатывает редактирование существующей игры.
    GET: отображает форму с текущими данными
    POST: обновляет данные и перенаправляет на страницу игры
    """
    # Получаем игру для редактирования
    game = get_object_or_404(Game, pk=pk)
    
    if request.method == 'POST':
        # Создаем форму с данными POST и привязываем к существующей игре
        form = GameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            # Сохраняем изменения
            game = form.save()
            messages.success(request, f'Игра "{game.name}" успешно обновлена!')
            return redirect('games:game_detail', pk=game.pk)
    else:
        # GET запрос - заполняем форму данными из игры
        form = GameForm(instance=game)
    
    return render(request, 'games/game_form.html', {'form': form, 'title': 'Редактировать игру'})


# Удаление игры
@login_required
def game_delete(request, pk):
    """
    Обрабатывает удаление игры.
    GET: отображает страницу подтверждения удаления
    POST: удаляет игру и перенаправляет на список игр
    """
    # Получаем игру для удаления
    game = get_object_or_404(Game, pk=pk)
    
    if request.method == 'POST':
        # Удаляем игру
        game.delete()
        messages.success(request, f'Игра "{game.name}" удалена!')
        return redirect('games:game_list')
    
    # GET запрос - показываем страницу подтверждения
    return render(request, 'games/game_confirm_delete.html', {'game': game})


# Создание отзыва
@login_required
def review_create(request, game_id):
    """
    Обрабатывает создание отзыва к игре.
    GET: отображает пустую форму
    POST: сохраняет отзыв и перенаправляет на страницу игры
    """
    # Получаем игру
    game = get_object_or_404(Game, pk=game_id)
    
    # Проверяем, не оставлял ли пользователь уже отзыв
    if Review.objects.filter(game=game, user=request.user).exists():
        messages.error(request, 'Вы уже оставили отзыв к этой игре!')
        return redirect('games:game_detail', pk=game.pk)
    
    if request.method == 'POST':
        # Создаем форму с данными POST
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Сохраняем отзыв, но пока не коммитим
            review = form.save(commit=False)
            review.game = game
            review.user = request.user
            review.save()
            messages.success(request, 'Ваш отзыв успешно добавлен!')
            return redirect('games:game_detail', pk=game.pk)
    else:
        # GET запрос - создаем пустую форму
        form = ReviewForm()
    
    return render(request, 'games/review_form.html', {'form': form, 'game': game})


# Редактирование отзыва
@login_required
def review_update(request, pk):
    """
    Обрабатывает редактирование отзыва.
    GET: отображает форму с текущими данными
    POST: обновляет отзыв и перенаправляет на страницу игры
    """
    # Получаем отзыв
    review = get_object_or_404(Review, pk=pk)
    
    # Проверяем права доступа
    if review.user != request.user:
        messages.error(request, 'Вы не можете редактировать чужой отзыв!')
        return redirect('games:game_detail', pk=review.game.pk)
    
    if request.method == 'POST':
        # Создаем форму с данными POST и привязываем к существующему отзыву
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш отзыв обновлен!')
            return redirect('games:game_detail', pk=review.game.pk)
    else:
        # GET запрос - заполняем форму данными отзыва
        form = ReviewForm(instance=review)
    
    return render(request, 'games/review_form.html', {'form': form, 'game': review.game})


# Удаление отзыва
@login_required
def review_delete(request, pk):
    """
    Обрабатывает удаление отзыва.
    GET: отображает страницу подтверждения удаления
    POST: удаляет отзыв и перенаправляет на страницу игры
    """
    # Получаем отзыв
    review = get_object_or_404(Review, pk=pk)
    
    # Проверяем права доступа
    if review.user != request.user:
        messages.error(request, 'Вы не можете удалить чужой отзыв!')
        return redirect('games:game_detail', pk=review.game.pk)
    
    if request.method == 'POST':
        # Удаляем отзыв
        game_pk = review.game.pk
        review.delete()
        messages.success(request, 'Ваш отзыв удален!')
        return redirect('games:game_detail', pk=game_pk)
    
    # GET запрос - показываем страницу подтверждения
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
    """
    Обрабатывает создание новой студии.
    GET: отображает пустую форму
    POST: сохраняет студию и перенаправляет на список студий
    """
    if request.method == 'POST':
        # Создаем форму с данными POST и файлами
        form = GameStudioForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохраняем студию
            studio = form.save()
            messages.success(request, f'Студия "{studio.name}" успешно добавлена!')
            return redirect('games:studio_list')
    else:
        # GET запрос - создаем пустую форму
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
    """
    Обрабатывает создание нового жанра.
    """
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
    """
    Обрабатывает редактирование существующего жанра.
    """
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
    """
    Обрабатывает создание новой платформы.
    GET: отображает пустую форму
    POST: сохраняет платформу и перенаправляет на список платформ
    """
    if request.method == 'POST':
        # Создаем форму с данными POST
        form = PlatformForm(request.POST)
        if form.is_valid():
            # Сохраняем платформу
            platform = form.save()
            messages.success(request, f'Платформа "{platform.name}" успешно добавлена!')
            return redirect('games:platform_list')
    else:
        # GET запрос - создаем пустую форму
        form = PlatformForm()
    
    return render(request, 'games/platform_form.html', {'form': form, 'title': 'Добавить платформу'})

# Редактирование платформы (добавим)
@login_required
def platform_update(request, pk):
    """
    Обрабатывает редактирование существующей платформы.
    """
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