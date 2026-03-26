from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email', 'age', 'gender', 'looking_for', 'bio', 'photo_id', 'is_video', 'telegram_id', 'tg_username']
        