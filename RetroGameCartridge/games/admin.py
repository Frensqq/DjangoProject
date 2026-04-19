from django.contrib import admin
from .models import GameStudio, Category, Platform, Game, Review


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

    list_display = ['name', 'game_studio', 'release_date', 'price', 'is_available', 'average_rating', 'reviews_count']
    list_filter = [
        'is_available',      #
        'game_studio',      
        'categories',       
        'platforms',         
        'release_date',     
    ]
    search_fields = [
        'name',            
        'description',      
        'game_studio__name',
    ]
    list_editable = ['price', 'is_available']
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
        ('Коммерческая информация', {
            'fields': ('price', 'is_available')
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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['game', 'user', 'rating', 'comment_short', 'created_at']
    list_filter = ['rating', 'created_at', 'game', 'user']
    search_fields = ['game__name', 'user__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    def comment_short(self, obj):
        return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
    comment_short.short_description = 'Комментарий'