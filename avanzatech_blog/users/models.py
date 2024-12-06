from django.contrib.auth.models import Group, User
from django.db import models
from django.contrib.auth.models import AbstractBaseUser



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('blogger', 'Blogger'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='blogger')
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    @property
    def team(self):
        """Devuelve el grupo al que pertenece el usuario"""
        return self.user.groups.first()  # Puedes usar `first()` si un usuario pertenece a un solo grupo
    
    