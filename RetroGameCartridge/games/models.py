from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class GameStudio(models.Model):
    # Модель для хранения информации о студиях-разработчиках игр.
    name = models.CharField(
        max_length=200,
        verbose_name="Название студии/компании"
    )

    year_foundation = models.IntegerField(
        verbose_name="Год основания",
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.now().year)
        ],
        null=True, 
        blank=True
    )

    country = models.CharField(
        verbose_name="Страна расположения",
        max_length=100,
        null=True,
        blank=True
    )

    director = models.CharField(
        verbose_name="Глава компании",
        max_length=150,
        null=True, 
        blank=True
    )

    website = models.URLField(
        verbose_name="Сайт компании",
        max_length=300,
        blank=True,
        null=True
    )

    logo = models.ImageField(
        upload_to='studios_logos/',
        verbose_name="Логотип компании",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Студия-разработчик"
        verbose_name_plural = "Студии-разработчики"
        ordering = ['name']


class Category(models.Model):
    #Модель для категорий/жанров игр.
    name = models.CharField(
        max_length=100,
        verbose_name="Название жанра",
        unique=True
    )
    
    description = models.TextField(
        verbose_name="Описание жанра",
        blank=True
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True
    )
    #создание  slug для ссылок /game/tetris вместо /game/23 внутри проекта
    def save(self, *args, **kwargs):
        if not self.slug:  
            self.slug = slugify(self.name) 
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']


class Platform(models.Model):
    #Модель для игровых платформ.
    name = models.CharField(
        max_length=100,
        verbose_name="Название платформы",
        unique=True
    )
    
    manufacturer = models.CharField(
        max_length=150,
        verbose_name="Производитель",
        blank=True
    )
    
    release_year = models.IntegerField(
        verbose_name="Год выпуска платформы",
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1970),
            MaxValueValidator(datetime.now().year)
        ]
    )
    
    description = models.TextField(
        verbose_name="Описание платформы",
        blank=True
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Платформа"
        verbose_name_plural = "Платформы"
        ordering = ['name']


class Game(models.Model):
    #Модель для хранения информации об играх.
    name = models.CharField(
        max_length=200,
        verbose_name="Название игры"
    )

    release_date = models.DateField(
        verbose_name="Дата выхода",
        null=True, 
        blank=True,
        help_text="Дата первого релиза игры"
    )

    description = models.TextField(
        verbose_name="Описание игры",
        max_length=5000,
        blank=True
    )

    game_studio = models.ForeignKey(
        GameStudio, 
        on_delete=models.CASCADE,
        related_name='games',
        verbose_name="Студия-разработчик"
    )
    
    categories = models.ManyToManyField(
        Category,
        related_name='games',
        verbose_name="Жанры",
        blank=True
    )
    
    platforms = models.ManyToManyField(
        Platform,
        related_name='games',
        verbose_name="Платформы",
        blank=True
    )

    cover_image = models.ImageField(
        upload_to='game_covers/',
        verbose_name="Обложка игры", 
        blank=True, 
        null=True  
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        null=True,
        blank=True,
    )
    
    video_review_url = models.URLField(
        verbose_name="Ссылка на видео-обзор",
        max_length=500,
        blank=True,
        null=True,
        help_text="Ссылка на видео с обзором"
    )
    
    is_available = models.BooleanField(
        default=True,
        verbose_name="Доступна для покупки"
    )
    
    average_rating = models.FloatField(
        default=0,
        verbose_name="Средний рейтинг"
    )
    
    reviews_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество отзывов"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('games:game_detail', args=[str(self.id)])
    
    def update_rating(self):
        """Обновляет средний рейтинг и количество отзывов"""
        reviews = self.reviews.filter(rating__isnull=False)
        self.reviews_count = reviews.count()
        
        if self.reviews_count > 0:
            total = sum(review.rating for review in reviews)
            self.average_rating = total / self.reviews_count
        else:
            self.average_rating = 0
        
        # Сохраняем с указанием полей
        self.save(update_fields=['average_rating', 'reviews_count'])
    
    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"
        ordering = ['-release_date', 'name']


class Review(models.Model):
    
    #Модель для отзывов.
    
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Игра"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='game_reviews',
        verbose_name="Пользователь"
    )
    
    rating = models.IntegerField(
        verbose_name="Оценка",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        null=True,
        blank=True,
        help_text="Оценка от 1 до 10 (можно оставить отзыв без оценки)"
    )
    
    comment = models.TextField(
        verbose_name="Комментарий",
        max_length=5000
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    def __str__(self):
        rating_str = f" ({self.rating}/10)" if self.rating else ""
        return f"Отзыв от {self.user.username} к {self.game.name}{rating_str}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            self.game.update_rating()
        except Exception as e:
            print(f"Error updating rating: {e}")
    
    def delete(self, *args, **kwargs):
        #При удалении отзыва обновляем рейтинг игры
        game = self.game
        super().delete(*args, **kwargs)
        game.update_rating()
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
        unique_together = ['user', 'game']