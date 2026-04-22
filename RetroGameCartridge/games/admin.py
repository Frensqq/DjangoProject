# games/admin.py
from django.contrib import admin
from .models import GameStudio, Category, Platform, Game, Rating, Comment

@admin.register(GameStudio)
class GameStudioAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'year_foundation', 'director']
    search_fields = ['name', 'country', 'director']
    list_filter = ['country', 'year_foundation']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'games_count']
    search_fields = ['name', 'description']
    list_editable = ['slug']
    prepopulated_fields = {'slug': ('name',)}
    
    def games_count(self, obj):
        return obj.games.count()
    games_count.short_description = 'Количество игр'
    games_count.admin_order_field = 'games__count'


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'release_year', 'games_count']
    search_fields = ['name', 'manufacturer', 'description']
    list_filter = ['manufacturer', 'release_year']
    
    def games_count(self, obj):
        return obj.games.count()
    games_count.short_description = 'Количество игр'
    games_count.admin_order_field = 'games__count'


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'game_studio', 'release_date', 'is_available', 'average_rating', 'reviews_count']
    list_filter = ['is_available', 'game_studio', 'categories', 'platforms', 'release_date']
    search_fields = ['name', 'description', 'game_studio__name']
    list_editable = ['is_available']
    filter_horizontal = ['categories', 'platforms']
    readonly_fields = ['average_rating', 'reviews_count', 'created_at', 'updated_at']
    date_hierarchy = 'release_date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'release_date', 'description', 'game_studio', 'cover_image')
        }),
        ('Категории и платформы', {
            'fields': ('categories', 'platforms')
        }),
        ('Статус и файл', {  # Исправлено: убрали лишнюю запятую
            'fields': ('is_available', 'game_file')
        }),
        ('Медиа', {
            'fields': ('video_review_url',)
        }),
        ('Рейтинг', {
            'fields': ('average_rating', 'reviews_count'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['game', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'game', 'user']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['game', 'user', 'text_short', 'created_at']
    list_filter = ['game', 'user', 'created_at']
    
    def text_short(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_short.short_description = 'Комментарий'