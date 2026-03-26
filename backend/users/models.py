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

    is_video = models.BooleanField(default=False, verbose_name='Есть видео')

    # Реальный @handle из Telegram (может быть пустым — не у всех пользователей есть username)
    tg_username = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name='Telegram @username'
    )

    def __str__(self):
        return self.username


class Like(models.Model):

    from_user = models.ForeignKey(User, related_name='likes_sent', on_delete=models.CASCADE)

    to_user = models.ForeignKey(User, related_name='likes_received', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} лайкнул(а) {self.to_user.username}"


# НОВОЕ: модель дизлайков — аналог Like, используется чтобы исключать
# просмотренные анкеты из ленты (next_profile)
class Dislike(models.Model):

    from_user = models.ForeignKey(User, related_name='dislikes_sent', on_delete=models.CASCADE)

    to_user = models.ForeignKey(User, related_name='dislikes_received', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} дизлайкнул(а) {self.to_user.username}"
