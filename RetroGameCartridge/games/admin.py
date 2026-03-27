from django.contrib import admin
from .models import GameStudio, Category, Platform, Game, Review


@admin.register(GameStudio)
class GameStudioAdmin(admin.ModelAdmin):
    """
    Настройки административного интерфейса для модели GameStudio.
    Определяет, как студии будут отображаться и управляться в админке.
    """
    
    # Поля, отображаемые в списке всех студий
    list_display = ['name', 'country', 'year_foundation', 'director']
    # Колонки: Название | Страна | Год основания | Глава компании
    
    # Поля, по которым можно выполнять поиск
    search_fields = ['name', 'country', 'director']
    # Поиск работает по названию, стране и главе компании
    
    # Поля для фильтрации в правой боковой панели
    list_filter = ['country', 'year_foundation']
    # Можно фильтровать студии по стране и году основания


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Настройки административного интерфейса для модели Category.
    Определяет, как жанры будут отображаться и управляться в админке.
    """
    
    # Поля, отображаемые в списке всех жанров
    list_display = ['name', 'slug', 'games_count']
    # Колонки: Название | Slug | Количество игр
    
    # Поля, по которым можно выполнять поиск
    search_fields = ['name', 'description']
    # Поиск работает по названию и описанию
    
    # Поля для редактирования прямо в списке
    list_editable = ['slug']
    
    # Автоматическое заполнение slug
    prepopulated_fields = {'slug': ('name',)}
    
    def games_count(self, obj):
        """Возвращает количество игр в этом жанре"""
        return obj.games.count()
    games_count.short_description = 'Количество игр'
    games_count.admin_order_field = 'games__count'


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    """
    Настройки административного интерфейса для модели Platform.
    Определяет, как платформы будут отображаться и управляться в админке.
    """
    
    # Поля, отображаемые в списке всех платформ
    list_display = ['name', 'manufacturer', 'release_year', 'games_count']
    # Колонки: Название | Производитель | Год выпуска | Количество игр
    
    # Поля, по которым можно выполнять поиск
    search_fields = ['name', 'manufacturer', 'description']
    # Поиск работает по названию, производителю и описанию
    
    # Поля для фильтрации в правой боковой панели
    list_filter = ['manufacturer', 'release_year']
    # Можно фильтровать по производителю и году выпуска
    
    def games_count(self, obj):
        """Возвращает количество игр на этой платформе"""
        return obj.games.count()
    games_count.short_description = 'Количество игр'
    games_count.admin_order_field = 'games__count'


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """
    Настройки административного интерфейса для модели Game.
    Определяет, как игры будут отображаться и управляться в админке.
    """
    
    # Поля, отображаемые в списке всех игр
    list_display = ['name', 'game_studio', 'release_date', 'price', 'is_available', 'average_rating', 'reviews_count']
    # Колонки: Название | Студия | Дата выхода | Цена | Доступность | Рейтинг | Отзывы
    
    # Поля для фильтрации в правой боковой панели
    list_filter = [
        'is_available',      # Фильтр по доступности (Да/Нет)
        'game_studio',       # Фильтр по студии
        'categories',        # Фильтр по жанрам
        'platforms',         # Фильтр по платформам
        'release_date',      # Фильтр по дате выхода
    ]
    
    # Поля, по которым можно выполнять поиск
    search_fields = [
        'name',              # Поиск по названию игры
        'description',       # Поиск по описанию
        'game_studio__name', # Поиск по названию студии
    ]
    
    # Поля для редактирования прямо в списке
    list_editable = ['price', 'is_available']
    
    # Горизонтальное отображение ManyToMany полей
    filter_horizontal = ['categories', 'platforms']
    
    # Поля только для чтения
    readonly_fields = ['average_rating', 'reviews_count', 'created_at', 'updated_at']
    
    # Иерархическая навигация по датам
    date_hierarchy = 'release_date'
    # Добавляет навигацию по годам/месяцам/дням над списком игр
    
    # Группировка полей в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'release_date', 'description', 'game_studio', 'cover_image')
        }),
        ('Категории и платформы', {
            'fields': ('categories', 'platforms')
        }),
        ('Коммерческая информация', {
            'fields': ('price', 'is_available')
        }),
        ('Медиа', {
            'fields': ('video_review_url',)
        }),
        ('Рейтинг', {
            'fields': ('average_rating', 'reviews_count'),
            'classes': ('collapse',)  # Сворачиваемая секция
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Настройки административного интерфейса для модели Review.
    Определяет, как отзывы будут отображаться и управляться в админке.
    """
    
    # Поля, отображаемые в списке всех отзывов
    list_display = ['game', 'user', 'rating', 'comment_short', 'created_at']
    # Колонки: Игра | Пользователь | Оценка | Комментарий | Дата создания
    
    # Поля для фильтрации в правой боковой панели
    list_filter = ['rating', 'created_at', 'game', 'user']
    # Можно фильтровать по оценке, дате, игре и пользователю
    
    # Поля, по которым можно выполнять поиск
    search_fields = ['game__name', 'user__username', 'comment']
    # Поиск работает по названию игры, имени пользователя и тексту комментария
    
    # Поля только для чтения
    readonly_fields = ['created_at', 'updated_at']
    
    def comment_short(self, obj):
        """Возвращает сокращенную версию комментария"""
        return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
    comment_short.short_description = 'Комментарий'