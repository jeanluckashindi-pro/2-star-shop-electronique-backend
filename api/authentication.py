from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import exceptions
from .models import AdminUser


class AdminJWTAuthentication(JWTAuthentication):
    """
    Authentication JWT custom qui utilise AdminUser
    au lieu du User Django standard.
    """

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        if not user_id:
            raise InvalidToken("Token ne contient pas user_id.")
        try:
            return AdminUser.objects.get(id=user_id)
        except AdminUser.DoesNotExist:
            raise exceptions.AuthenticationFailed("Admin introuvable.", code="user_not_found")
