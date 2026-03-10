from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    GENDER_CHOICES = (
        ('M', 'Мужской'),
        ('F', 'Женский'),
    )



    telegram_id = models.BigIntegerField(
        unique=True, 
        null=True, 
        blank=True,
        ) 

    age = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name='Возраст'
        )

    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES,
        null=True, 
        blank=True, 
        verbose_name='Пол'
    )

    looking_for = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES,
        null=True, 
        blank=True, 
        verbose_name='Ищет'
    )    

    bio = models.TextField(
        max_length=500,
        null=True, 
        blank=True, 
        verbose_name='О себе'
    )    

    photo_id = models.CharField(
        max_length=255,
        null=True, 
        blank=True, 
        verbose_name='ID фото из Telegram'
    )

    def __str__(self):
        return self.username