from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class RegistroViewTest(APITestCase):
    def test_registro_exitoso(self):
        data = {
            "username": "newuser",
            "password": "password123",
            "confirm_password": "password123"
        }
        response = self.client.post("/api/register/", data)  # Asegúrate de que esta ruta es correcta
        print(response.data)  # Agregar para depuración
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registro_falla_con_datos_invalidos(self):
        """Verifica que el registro falla si los datos son inválidos"""
        data = {
            "username": "",  # Nombre de usuario vacío
            "password": "testpassword"
        }
        response = self.client.post("/api/register/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)  # Debe fallar por falta de username

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group
from rest_framework import status


class GetCurrentUserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.group = Group.objects.create(name="Test Group")
        self.user.groups.add(self.group)  # Agrega el usuario a un grupo
        self.user.save()
        
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_get_current_user(self):
        response = self.client.get("/api/current-user/")
        print(response.data)  # 🔹 Imprime la respuesta para depuración
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["team"], "Test Group")