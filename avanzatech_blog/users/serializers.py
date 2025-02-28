from django.contrib.auth.models import User, Group
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password']
        
    def validate_username(self, value):
        """Verifica si el username ya está registrado"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # No guardamos confirm_password en la base de datos
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
     # 🔹 Asignar un equipo por defecto
        team, _ = Group.objects.get_or_create(name="Equipo Default")
        user.groups.add(team)  # Si team se maneja con Django Groups

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)