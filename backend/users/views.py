from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import random

from .serializers import UserSerializer
# ИСПРАВЛЕНО: Like и Dislike теперь явно импортированы (раньше Like не был импортирован — падало при лайке)
from .models import Like, Dislike

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        telegram_id = self.request.query_params.get('telegram_id')

        if telegram_id:
            queryset = queryset.filter(telegram_id=telegram_id)

        return queryset

    @action(detail=False, methods=['get'])
    def next_profile(self, request):
        telegram_id = request.query_params.get('telegram_id')

        print(f"--- РАДАР --- next_profile запрос от telegram_id={telegram_id}")

        if not telegram_id:
            return Response({"error": "telegram_id parameter is required."}, status=400)

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        # НОВОЕ: subquery-исключение лайков и дизлайков — один JOIN в SQL вместо Python set
        liked_subq = Like.objects.filter(from_user=user).values('to_user_id')
        disliked_subq = Dislike.objects.filter(from_user=user).values('to_user_id')

        candidates = User.objects.filter(
            gender=user.looking_for,
            looking_for=user.gender,
        ).exclude(
            telegram_id=user.telegram_id
        ).exclude(
            id__in=liked_subq      # НОВОЕ: исключаем уже лайкнутых
        ).exclude(
            id__in=disliked_subq   # НОВОЕ: исключаем уже дизлайкнутых
        )

        print(f"--- РАДАР --- кандидатов найдено: {candidates.count()}")

        if not candidates.exists():
            return Response({"message": "No more profiles available."}, status=200)

        # ИСПРАВЛЕНО: order_by('?') вместо list() — не грузим всю таблицу в память
        random_profile = candidates.order_by('?').first()

        serializer = self.get_serializer(random_profile)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def like(self, request):
        from_telegram_id = request.data.get('from_telegram_id')
        to_telegram_id = request.data.get('to_telegram_id')

        print(f"--- РАДАР --- like: from={from_telegram_id} to={to_telegram_id}")

        if not from_telegram_id or not to_telegram_id:
            return Response({"error": "from_telegram_id and to_telegram_id are required."}, status=400)

        try:
            from_user = User.objects.get(telegram_id=from_telegram_id)
            to_user = User.objects.get(telegram_id=to_telegram_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        Like.objects.get_or_create(from_user=from_user, to_user=to_user)

        is_mutual = Like.objects.filter(from_user=to_user, to_user=from_user).exists()

        if is_mutual:
            print(f"--- РАДАР --- МАТЧ! {from_user.username} и {to_user.username}")
            return Response({
                "match": True,
                "first_name": to_user.first_name,
                "to_telegram_id": to_user.telegram_id,
                "tg_username": to_user.tg_username,  # реальный @handle для отображения
            })

        return Response({"match": False})

    # НОВОЕ: эндпоинт для дизлайков POST /api/users/dislike/
    @action(detail=False, methods=['post'])
    def dislike(self, request):
        from_telegram_id = request.data.get('from_telegram_id')
        to_telegram_id = request.data.get('to_telegram_id')

        print(f"--- РАДАР --- dislike: from={from_telegram_id} to={to_telegram_id}")

        if not from_telegram_id or not to_telegram_id:
            return Response({"error": "from_telegram_id and to_telegram_id are required."}, status=400)

        try:
            from_user = User.objects.get(telegram_id=from_telegram_id)
            to_user = User.objects.get(telegram_id=to_telegram_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        Dislike.objects.get_or_create(from_user=from_user, to_user=to_user)

        return Response({"disliked": True})
