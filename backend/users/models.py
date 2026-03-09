from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):


    telegram_id = models.BigIntegerField(
        unique=True, 
        null=True, 
        blank=True,
        verbose_name='Telegram ID'
        )


    def __str__(self):
        return self.username