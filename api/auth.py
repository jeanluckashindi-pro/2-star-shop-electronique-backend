import bcrypt
from datetime import datetime, timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AdminUser


def get_tokens(user_id: int) -> dict:
    """Génère access + refresh token pour un AdminUser."""
    refresh = RefreshToken()
    refresh["user_id"] = user_id
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"detail": "Email et mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
            return Response({"detail": "Identifiants invalides."}, status=status.HTTP_401_UNAUTHORIZED)

        if not bcrypt.checkpw(password.encode(), admin.password_hash.encode()):
            return Response({"detail": "Identifiants invalides."}, status=status.HTTP_401_UNAUTHORIZED)

        # Mettre à jour last_login
        admin.last_login = datetime.now(timezone.utc)
        admin.save(update_fields=["last_login"])

        return Response(get_tokens(admin.id), status=status.HTTP_200_OK)


class AdminRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            return Response({"detail": "Refresh token requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(token)
            return Response({"access": str(refresh.access_token)})
        except Exception:
            return Response({"detail": "Token invalide ou expiré."}, status=status.HTTP_401_UNAUTHORIZED)


class AdminMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.auth.get("user_id")
        try:
            admin = AdminUser.objects.get(id=user_id)
            return Response({"id": admin.id, "email": admin.email, "last_login": admin.last_login})
        except AdminUser.DoesNotExist:
            return Response({"detail": "Non trouvé."}, status=status.HTTP_404_NOT_FOUND)
