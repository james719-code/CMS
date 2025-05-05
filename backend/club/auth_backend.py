# auth_backend.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Account

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        if user_id is None:
            raise AuthenticationFailed("Token contained no recognizable user identification")

        try:
            return Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            raise AuthenticationFailed("Account not found")
