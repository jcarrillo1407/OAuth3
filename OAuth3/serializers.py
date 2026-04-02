from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import AppUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = AppUser
        fields = ["nombres", "apellidos", "email", "password"]

    def create(self, validated_data):
        return AppUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = AppUser.objects.get(email=email)
        except AppUser.DoesNotExist:
            raise serializers.ValidationError("Credenciales inválidas")

        if not user.check_password(password):
            raise serializers.ValidationError("Credenciales inválidas")

        if not user.is_active:
            raise serializers.ValidationError("Usuario inactivo")

        attrs["user"] = user
        return attrs


class VerifyMFASerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)
    

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(min_length=8)

    def validate_new_password(self, value):
        import re
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Debe tener una mayúscula")
        if not re.search(r"\d", value):
            raise serializers.ValidationError("Debe tener un número")
        if not re.search(r"[\W_]", value):
            raise serializers.ValidationError("Debe tener un símbolo")
        return value