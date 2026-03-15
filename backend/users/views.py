from rest_framework import viewsets  
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import random
from .serializers import UserSerializer
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
        

        if not telegram_id:
            return Response({"error": "telegram_id and looking_for parameters are required."}, status=400)

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        candidates = User.objects.filter(
            gender = user.looking_for,
            looking_for = user.gender
        ).exclude(telegram_id=user.telegram_id)

        if not candidates.exists():
            return Response({"message": "No more profiles available."}, status=200)
    
        random_profile = random.choice(list(candidates))

        serializer = self.get_serializer(random_profile)
        return Response(serializer.data)
