import bcrypt
import random
import string
from datetime import datetime, timezone, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, parsers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import AdminUser


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def send_otp_email(email: str, otp: str):
    subject = "Réinitialisation de mot de passe - 2Star Shop"
    html_content = render_to_string("emails/reset_password.html", {"otp_code": otp})
    text_content = f"Votre code OTP est : {otp}\nIl expire dans 5 minutes."
    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def get_tokens(user_id: int) -> dict:
    refresh = RefreshToken()
    refresh["user_id"] = user_id
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class AdminLoginView(APIView):
    """
    POST /api/auth/login/
    { "email": "...", "password": "..." }
    → { "access": "...", "refresh": "..." }
    """
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


class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            return Response({"detail": "Refresh token requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(token).blacklist()
        except Exception:
            pass
        return Response({"detail": "Déconnecté avec succès."}, status=status.HTTP_200_OK)

class AdminMeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get(self, request):
        admin = request.user
        avatar_url = request.build_absolute_uri(admin.avatar.url) if admin.avatar else None
        return Response({
            "id": admin.id,
            "email": admin.email,
            "first_name": admin.first_name,
            "last_name": admin.last_name,
            "phone": admin.phone,
            "avatar": avatar_url,
            "last_login": admin.last_login,
            "created_at": admin.created_at,
        })

    def patch(self, request):
        admin = request.user

        # Avatar
        avatar = request.FILES.get("avatar")
        if avatar:
            if admin.avatar:
                admin.avatar.delete(save=False)
            admin.avatar = avatar

        # Infos de base
        for field in ["first_name", "last_name", "phone"]:
            value = request.data.get(field)
            if value is not None:
                setattr(admin, field, value)

        # Email
        email = request.data.get("email")
        if email:
            if AdminUser.objects.exclude(id=admin.id).filter(email=email).exists():
                return Response({"detail": "Cet email est déjà utilisé."}, status=status.HTTP_400_BAD_REQUEST)
            admin.email = email

        # Mot de passe
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if old_password or new_password:
            if not old_password or not new_password:
                return Response({"detail": "old_password et new_password sont requis."}, status=status.HTTP_400_BAD_REQUEST)
            if not bcrypt.checkpw(old_password.encode(), admin.password_hash.encode()):
                return Response({"detail": "Ancien mot de passe incorrect."}, status=status.HTTP_400_BAD_REQUEST)
            admin.password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

        admin.save()

        return Response({
            "detail": "Profil mis à jour.",
            "id": admin.id,
            "email": admin.email,
            "first_name": admin.first_name,
            "last_name": admin.last_name,
            "phone": admin.phone,
            "avatar": request.build_absolute_uri(admin.avatar.url) if admin.avatar else None,
        })


class ForgotPasswordView(APIView):
    """
    Étape 1 : envoie un OTP par email
    POST /api/auth/forgot-password/
    { "email": "admin@2starshop.com" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
            # On ne révèle pas si l'email existe ou non
            return Response({"detail": "Si cet email existe, un code vous a été envoyé."}, status=status.HTTP_200_OK)

        otp = generate_otp()
        admin.otp_code = otp
        admin.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        admin.save(update_fields=["otp_code", "otp_expires_at"])

        send_otp_email(email, otp)

        return Response({"detail": "Code OTP envoyé par email."}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """
    Étape 2 : vérifier le code OTP
    POST /api/auth/verify-otp/
    { "email": "admin@2starshop.com", "otp_code": "123456" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp_code = request.data.get("otp_code")

        if not email or not otp_code:
            return Response({"detail": "Email et code OTP requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
            return Response({"detail": "Code invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if admin.otp_code != otp_code:
            return Response({"detail": "Code OTP invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if not admin.otp_expires_at or datetime.now(timezone.utc) > admin.otp_expires_at:
            return Response({"detail": "Code OTP expiré. Veuillez en demander un nouveau."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Code valide. Vous pouvez réinitialiser votre mot de passe."}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    Étape 3 : réinitialiser le mot de passe
    POST /api/auth/reset-password/
    { "email": "admin@2starshop.com", "otp_code": "123456", "new_password": "NouveauMotDePasse123" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp_code = request.data.get("otp_code")
        new_password = request.data.get("new_password")

        if not email or not otp_code or not new_password:
            return Response({"detail": "Email, code OTP et nouveau mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
            return Response({"detail": "Code invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if admin.otp_code != otp_code:
            return Response({"detail": "Code OTP invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if not admin.otp_expires_at or datetime.now(timezone.utc) > admin.otp_expires_at:
            return Response({"detail": "Code OTP expiré. Veuillez en demander un nouveau."}, status=status.HTTP_400_BAD_REQUEST)

        # Hasher et sauvegarder le nouveau mot de passe
        admin.password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        admin.otp_code = None
        admin.otp_expires_at = None
        admin.save(update_fields=["password_hash", "otp_code", "otp_expires_at"])

        return Response({"detail": "Mot de passe réinitialisé avec succès."}, status=status.HTTP_200_OK)
