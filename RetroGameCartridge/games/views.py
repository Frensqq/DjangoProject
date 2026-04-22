from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import FileResponse, Http404
from .models import Game, GameStudio, Category, Platform, Rating, Comment
from .forms import ( GameForm, GameStudioForm, CategoryForm, PlatformForm, RatingForm, CommentForm, UserRegistrationForm)

def is_moderator(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Moderator').exists())


def home(request):

    total_games = Game.objects.count()  
    total_studios = GameStudio.objects.count()  
    total_categories = Category.objects.count()  
    total_platforms = Platform.objects.count()  
    recent_games = Game.objects.all().order_by('-created_at')[:6]  
    
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
        .prefetch_related('categories', 'platforms', 'comments__user', 'ratings'),
        pk=pk
    )
    
    comments = game.comments.select_related('user').all()
    
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(game=game, user=request.user).first()
    
    context = {
        'game': game,
        'comments': comments,
        'ratings_count': game.ratings.count(), 
        'user_rating': user_rating,
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

def download_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    if not game.game_file:
        raise Http404("Файл не найден")
    
    response = FileResponse(open(game.game_file.path, 'rb'), as_attachment=True)
    return response


@login_required
def rating_create_or_update(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    
    rating = Rating.objects.filter(game=game, user=request.user).first()
    
    if request.method == 'POST':
        if rating:
            form = RatingForm(request.POST, instance=rating)
        else:
            form = RatingForm(request.POST)
        
        if form.is_valid():
            rating = form.save(commit=False)
            rating.game = game
            rating.user = request.user
            rating.save()
            messages.success(request, 'Ваша оценка сохранена!')
            return redirect('games:game_detail', pk=game.pk)
    else:
        form = RatingForm(instance=rating)
    
    return render(request, 'games/rating_form.html', {'form': form, 'game': game, 'rating': rating})


@login_required
def comment_create(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.game = game
            comment.user = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('games:game_detail', pk=game.pk)
    else:
        form = CommentForm()
    
    return render(request, 'games/comment_form.html', {'form': form, 'game': game})


@login_required
def comment_update(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    if comment.user != request.user and not is_moderator(request.user):
        messages.error(request, 'Вы не можете редактировать этот комментарий!')
        return redirect('games:game_detail', pk=comment.game.pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий обновлен!')
            return redirect('games:game_detail', pk=comment.game.pk)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'games/comment_form.html', {'form': form, 'game': comment.game})


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    if comment.user != request.user and not is_moderator(request.user):
        messages.error(request, 'Вы не можете удалить этот комментарий!')
        return redirect('games:game_detail', pk=comment.game.pk)
    
    if request.method == 'POST':
        game_pk = comment.game.pk
        comment.delete()
        messages.success(request, 'Комментарий удален!')
        return redirect('games:game_detail', pk=game_pk)
    
    return render(request, 'games/comment_confirm_delete.html', {'comment': comment})


# Список студий
def studio_list(request):
    studios = GameStudio.objects.prefetch_related('games').all()

    query = request.GET.get('q')
    
    if query:
        studios = studios.filter(
            Q(name__icontains=query) |
            Q(country__icontains=query) | 
            Q(director__icontains=query)  
        )
    
    context = {
        'studios': studios,
    }

    return render(request, 'games/studio_list.html', context)


# Добавление студии
@login_required
def studio_create(request):
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


# Добавление жанра
@login_required
def category_create(request):
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
    if not is_moderator(request.user):
        messages.error(request, 'У вас нет прав на добавление платформ!')
        return redirect('games:platform_list')
    
    if request.method == 'POST':
        form = PlatformForm(request.POST, request.FILES)
        if form.is_valid():
            platform = form.save()
            messages.success(request, f'Платформа "{platform.name}" успешно добавлена!')
            return redirect('games:platform_list')
    else:
        form = PlatformForm()
    
    return render(request, 'games/platform_form.html', {'form': form, 'title': 'Добавить платформу'})

@login_required
def platform_update(request, pk):
    if not is_moderator(request.user):
        messages.error(request, 'У вас нет прав на редактирование платформ!')
        return redirect('games:platform_list')
    
    platform = get_object_or_404(Platform, pk=pk)
    
    if request.method == 'POST':
        form = PlatformForm(request.POST,request.FILES, instance=platform)
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


#Мини игры
def play_tetris(request):
    return render(request, 'mini_games/Tetris.html')

def play_snake(request):
    return render(request, 'mini_games/Snake.html')

def play_minesweeper(request):
    return render(request, 'mini_games/Minesweeper.html')