from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        telegram_id = self.request.query_params.get('telegram_id')


        if telegram_id:
            queryset = queryset.filter(telegram_id=telegram_id)

        return queryset