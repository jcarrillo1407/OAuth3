from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AppUser, MFAChallenge
from .serializers import RegisterSerializer, LoginSerializer, VerifyMFASerializer
from .services.mfa_service import create_mfa_challenge, verify_mfa_code
from .services.email_service import send_mfa_email


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "Usuario creado correctamente",
            "user": {
                "id": user.id,
                "email": user.email,
                "nombres": user.nombres,
                "apellidos": user.apellidos,
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.last_login_at = timezone.now()
        user.save(update_fields=["last_login_at"])

        if user.mfa_enabled:
            _, code = create_mfa_challenge(user, purpose="LOGIN")
            send_mfa_email(user, code)

            return Response({
                "message": "Código MFA enviado al correo",
                "mfa_required": True,
                "email": user.email,
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Login exitoso",
            "mfa_required": False,
            "user": {
                "id": user.id,
                "email": user.email,
                "nombres": user.nombres,
                "apellidos": user.apellidos,
            }
        }, status=status.HTTP_200_OK)


class VerifyMFAView(APIView):
    def post(self, request):
        serializer = VerifyMFASerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        try:
            user = AppUser.objects.get(email=email)
        except AppUser.DoesNotExist:
            return Response({"detail": "Solicitud inválida"}, status=status.HTTP_400_BAD_REQUEST)

        challenge = MFAChallenge.objects.filter(
            user=user,
            purpose="LOGIN",
            consumed_at__isnull=True,
        ).order_by("-created_at").first()

        if not challenge:
            return Response({"detail": "No existe desafío MFA activo"}, status=status.HTTP_400_BAD_REQUEST)

        valid = verify_mfa_code(challenge, code)

        if not valid:
            return Response({"detail": "Código inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)

        # 🔥 marcar como usado
        challenge.consumed_at = timezone.now()
        challenge.save()

        return Response({
            "message": "MFA validado correctamente",
            "user": {
                "id": user.id,
                "email": user.email,
                "nombres": user.nombres,
                "apellidos": user.apellidos,
            }
        }, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    def post(self, request):
        return Response(
            {"message": "Ingrese nueva contraseña directamente"},
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")

        if not email or not new_password:
            return Response(
                {"detail": "Email y nueva contraseña son requeridos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) < 8:
            return Response(
                {"detail": "La contraseña debe tener al menos 8 caracteres"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = AppUser.objects.get(email=email)
        except AppUser.DoesNotExist:
            return Response(
                {"detail": "Usuario no encontrado"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔥 Actualiza la contraseña
        user.set_password(new_password)
        user.save(update_fields=["password"])

        # 🔥 AQUÍ VA LO NUEVO
        return Response({
            "message": "Contraseña actualizada correctamente",
            "user": {
                "id": user.id,
                "email": user.email,
                "nombres": user.nombres,
                "apellidos": user.apellidos,
            }
        }, status=status.HTTP_200_OK)