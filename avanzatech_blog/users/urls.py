from django.urls import path
from .views import RegistroView
from .views import get_current_user


urlpatterns = [
    path('register/', RegistroView.as_view(), name='register'),
    path('current-user/', get_current_user, name='current-user'),
]
