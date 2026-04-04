from django import forms
from .models import Game, GameStudio, Platform, Category, Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime

class GameStudioForm(forms.ModelForm):
    class Meta:
        model = GameStudio
        fields = ['name', 'year_foundation', 'country', 'director', 'website', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Название студии'  
                }
            ),
            'year_foundation': forms.NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Год основания'  
                }
            ),
            'country': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Расположение'  
                }
            ),
            'director': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Глава студии'  
                }
            ),
            'website': forms.URLInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'https://site.com'  
                }
            ),
            'logo': forms.FileInput(attrs={
                    'class': 'form-control',
                }
            )
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Категория'  
                }
            ),
            'description': forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Описание категории'  
                }
            )
        }


class PlatformForm(forms.ModelForm):
    class Meta:
        model = Platform
        fields = ['name','manufacturer','release_year','description']
        widgets= {
            'name': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Платформа'  
                }
            ),
            'manufacturer': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Производитель'  
                }
            ),
            'release_year': forms.NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Год основания'  
                }
            ),
            'description': forms.Textarea(attrs={
                    'class':'form-control',
                    'rows':3,
                    'placeholder':'Описание'
            })
        }

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name', 'release_date', 'description', 'game_studio',
            'categories', 'platforms', 'cover_image', 'price',
            'video_review_url', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Название игры'
            }),
            'release_date': forms.DateInput(attrs={
                    'class': 'form-control',
                    'type':'date',
                    'placeholder': 'Дата выхода'
            }),
            'description': forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows':5,
                    'placeholder': 'Описание игры'
            }),
            'game_studio': forms.Select(attrs={
                    'class': 'form-control',
            }),
            'categories': forms.SelectMultiple(attrs={
                    'class': 'form-control',
                    'size':5,
            }),
            'platforms': forms.SelectMultiple(attrs={
                    'class': 'form-control',
                    'size':5,
            }),
            'cover_image': forms.FileInput(attrs={
                    'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Цена в рублях',
                    'step': '0.01'
            }),
            'video_review_url': forms.URLInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'https://rutube.com/video.'
            }),
            'is_available': forms.CheckboxInput(attrs={
                    'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['game_studio'].empty_label = "Выберите студию"

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, (forms.FileInput, forms.ClearableFileInput)):
                continue
            elif 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Оценка от 1 до 10', 
                    'min':1,
                    'max':10,
                }
            ),
            'comment': forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Комментарий'  
                }
            ),
        }

    def rating_valid(self):
        rating = self.cleaned_data.get('rating')
        if rating is not None and (rating < 1 or rating > 10):
            raise forms.ValidationError('Оценка должна быть от 1 до 10')
        return rating

        
class UserRegistrationForm(UserCreationForm):
    """
    Форма для регистрации новых пользователей.
    Расширяет стандартную форму регистрации Django.
    """
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя пользователя'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтверждение пароля'
        })
    
    def save(self, saved=True):
        """
        Сохраняет пользователя с email.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if saved:
            user.save()
        return user