from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    team = serializers.CharField(write_only=True,required=False,default='DEFAULT')
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'team']
        

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid email or password')
        return user