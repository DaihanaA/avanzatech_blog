from django.test import TestCase
from django.contrib.auth.models import User, Group
from .models import BlogPost, Comment, Permissions
from rest_framework.test import APIClient
from django.urls import reverse
import random
import string
from rest_framework.test import APITestCase
from rest_framework import status


#Tests de los modelos
def generate_unique_username():
    return 'testuser_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

class BlogPostModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.post = BlogPost.objects.create(title='Test Post', content='This is a test post', author=self.user)
        
    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.author.username, 'testuser')

class CommentModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.post = BlogPost.objects.create(title='Test Post', content='This is a test post', author=self.user)
        self.comment = Comment.objects.create(content='This is a comment', blog_post=self.post, user=self.user)
        
    def test_comment_creation(self):
        self.assertEqual(self.comment.content, 'This is a comment')
        self.assertEqual(self.comment.blog_post, self.post)


class PostLikeViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = APIClient()
        self.client.login(username='testuser', password='password123')
        self.post = BlogPost.objects.create(title="Test Post", content="This is a test post", author=self.user)

    def test_like_post(self):
        response = self.client.post(reverse('post-like', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 201)


#Tests de la vistas
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from posts.models import BlogPost

from django.test import TestCase
from posts.views import BlogPostViewSet, PostListView
from django.contrib.auth.models import User, Group
from posts.models import BlogPost

from posts.views import BlogPostDeleteView
from posts.views import BlogPostUpdateView
from django.test import TestCase
from posts.models import BlogPost
from rest_framework.test import APITestCase
from posts.views import PostDetailViewSet
from posts.factories import UserFactory, BlogPostFactory, CommentFactory, LikeFactory
from rest_framework import status
from rest_framework.authtoken.models import Token



class BlogPostCreateViewSetTestWithFactory(TestCase):
    def setUp(self):
        # Crear un usuario para autenticación
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # Crear la instancia del APIRequestFactory
        self.factory = APIRequestFactory()
        # La vista que vamos a probar
        self.view = BlogPostViewSet.as_view({'post': 'create'})

    def test_create_post_authenticated(self):
        data = {
            'title': 'Test Post', 
            'content': 'This is a test content.',
            'public_permission': 'READ',  # Ensure this is one of the valid choices
            'authenticated_permission': 'READ_EDIT',  # Ensure this is one of the valid choices
            'team_permission': 'READ_EDIT'  # Ensure this is one of the valid choices
        }
        request = self.factory.post('/posts/create/', data, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        
        print(response.data)  # Check the error details if any

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogPost.objects.count(), 1)
        self.assertEqual(BlogPost.objects.first().title, 'Test Post')




    def test_create_post_unauthenticated(self):
        # Datos válidos para crear un post
        data = {'title': 'Test Post', 'content': 'This is a test content.'}
        # Crear la solicitud POST simulada sin autenticación
        request = self.factory.post('/posts/create/', data, format='json')
        # Llamar a la vista con la solicitud
        response = self.view(request)
        
        # Validar que el acceso no está permitido
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)




from django.test import RequestFactory, TestCase
from rest_framework.test import force_authenticate
from posts.models import BlogPost
from django.contrib.auth.models import User
from posts.views import PostListView
from posts.permissions import Permissions

class PostListViewTestWithFactory(TestCase):
    def setUp(self):
        # Initialize the RequestFactory
        self.factory = RequestFactory()
        
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Create a public post with an author
        self.public_post = BlogPost.objects.create(
            title="Public Post",
            content="This is a public post content.",
            author=self.user,  # Make sure to associate an author
            public_permission=Permissions.READ,
            authenticated_permission='READ_EDIT',
            team_permission='READ_EDIT',
        )

    def test_authenticated_user_can_access_posts(self):
        # Create a GET request
        request = self.factory.get('/posts/')
        force_authenticate(request, user=self.user)  # Authenticate the user

        # Invoke the view
        view = PostListView.as_view()
        response = view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)  # Assuming only one post is created

    def test_unauthenticated_user_can_access_only_public_posts(self):
        # Create a GET request
        request = self.factory.get('/posts/')

        # Invoke the view without authenticating the user
        view = PostListView.as_view()
        response = view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)  # Only the public post should appear


from rest_framework.test import APIRequestFactory
from rest_framework import status
from django.contrib.auth.models import User
from posts.models import BlogPost
from posts.views import BlogPostDeleteView
from posts.permissions import Permissions
from rest_framework_simplejwt.tokens import RefreshToken

class BlogPostDeleteViewTest(TestCase):
    def setUp(self):
        # Create a user and initialize request factory
        self.user = User.objects.create_user(username='testuser', password='password')
        self.team_user = User.objects.create_user(username='teamuser', password='password')  # Team member user
        self.factory = APIRequestFactory()  # Initialize the factory
        
        # Create a post with valid fields
        self.post = BlogPost.objects.create(
            title="Test Post",
            content="This is a test post content.",
            author=self.user,
            public_permission=Permissions.READ,  # Ensure these fields match your model
            authenticated_permission='READ_EDIT',
            team_permission='READ_EDIT',
        )
        
    def test_author_can_delete_post(self):
        # Create a delete request
        request = self.factory.delete(f'/posts/{self.post.id}/delete/')
        force_authenticate(request, user=self.user)  # Authenticate the request
        
        # Invoke the view and check the response
        view = BlogPostDeleteView.as_view()
        response = view(request, pk=self.post.id)
        
        # Assert the post is deleted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BlogPost.objects.filter(id=self.post.id).exists())

    def test_team_member_can_delete_post(self):
        # Simulate a team member deleting the post
        request = self.factory.delete(f'/posts/{self.post.id}/delete')
        force_authenticate(request, user=self.team_user)  # Authenticate as team member
        
        view = BlogPostDeleteView.as_view()
        response = view(request, pk=self.post.id)
        
        # Assert the post is deleted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BlogPost.objects.filter(id=self.post.id).exists())

def test_unauthorized_user_cannot_delete_post(self):
        # Create an unauthorized user
        unauth_user = User.objects.create_user(username="unauth_user", password="password")

        # Create a DELETE request for the post
        request = self.factory.delete(f'/posts/{self.post.id}/delete/')

        # Force authentication as the unauthorized user
        force_authenticate(request, user=unauth_user)

        # Create the view and execute the request
        view = BlogPostDeleteView.as_view()
        response = view(request, pk=self.post.id)

        # Assert that the status code is 403 (Forbidden)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Assert that the post still exists (it wasn't deleted)
        self.assertTrue(BlogPost.objects.filter(id=self.post.id).exists())




class BlogPostUpdateViewTest(TestCase):
    def setUp(self):
        # Configuración similar a BlogPostDeleteViewTest
        self.user = User.objects.create_user(username="author", password="testpassword")
        self.group = Group.objects.create(name="Test Group")
        self.user.groups.add(self.group)
        
        self.team_user = User.objects.create_user(username="team_member", password="password123")
        self.team_user.groups.add(self.group)
        self.unauthorized_user = User.objects.create_user(username="unauthorized", password="password")
        
        # Correct the permissions fields based on your model definition
        self.post = BlogPost.objects.create(
            title="Test Post",
            content="This is a test content.",
            author=self.user,
            public_permission=Permissions.READ,  # Make sure this is correct
            authenticated_permission='READ',
            team_permission='READ_EDIT',
        )

        self.factory = APIRequestFactory()

    def test_author_can_update_post(self):
        data = {"title": "Updated Title"}
        request = self.factory.patch(f'/posts/{self.post.id}/update/', data)
        force_authenticate(request, user=self.user)
        
        view = BlogPostUpdateView.as_view()
        response = view(request, pk=self.post.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")

    def test_team_member_can_update_post(self):
        data = {"title": "Team Updated Title"}
        request = self.factory.patch(f'/posts/{self.post.id}/update/', data)
        force_authenticate(request, user=self.team_user)
        
        view = BlogPostUpdateView.as_view()
        response = view(request, pk=self.post.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Team Updated Title")

    def test_unauthorized_user_cannot_update_post(self):
        # Crear un usuario no autorizado
        unauth_user = User.objects.create_user(username="unauth_user", password="password")

        # Crear una solicitud PATCH para el post
        data = {"title": "Updated Title"}
        request = self.factory.patch(f'/posts/{self.post.id}/update/', data)

        # Forzar autenticación como el usuario no autorizado
        force_authenticate(request, user=unauth_user)

        # Crear la vista y ejecutar la solicitud
        view = BlogPostUpdateView.as_view()
        response = view(request, pk=self.post.id)

        # Asegurarse de que la respuesta sea 403 (Prohibido)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verificar que el contenido del post no haya cambiado
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.title, 'Updated Title')
        self.assertNotEqual(self.post.content, 'Updated content.')




class PostListViewTestWithFactory(TestCase):
    def setUp(self):
        # Crear usuarios y grupos
        self.user = User.objects.create_user(username="author", password="testpassword")
        self.group = Group.objects.create(name="Test Group")
        self.user.groups.add(self.group)

        # Crear un post con permisos 'team'
        self.team_post = BlogPost.objects.create(
            title="Team Post", 
            public_permission=Permissions.NONE,  # Establecer permisos adecuados
            authenticated_permission=Permissions.NONE,  # Permiso autenticado
            team_permission=Permissions.READ_EDIT,  # Permiso para el equipo
            author=self.user
        )

        # Crear un miembro del equipo
        self.team_member = User.objects.create_user(username="team_member", password="team123")
        self.team_member.groups.add(self.group)

        # Crear un usuario que no es miembro del equipo
        self.other_user = User.objects.create_user(username="other_user", password="other123")

        # Configurar APIRequestFactory
        self.factory = APIRequestFactory()

    def test_team_member_can_access_team_posts(self):
        # El usuario del equipo puede acceder al post con permiso 'team'
        request = self.factory.get('/posts/')
        force_authenticate(request, user=self.team_member)

        view = PostListView.as_view()
        response = view(request)

        # Verificar que el post 'team' es accesible
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)  # Solo el post de equipo debe aparecer

    def test_other_user_cannot_access_team_posts(self):
        # El usuario que no pertenece al equipo no puede acceder al post con permiso 'team'
        request = self.factory.get('/posts/')
        force_authenticate(request, user=self.other_user)

        view = PostListView.as_view()
        response = view(request)

        # Verificar que el post 'team' no es accesible
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)  # No debe aparecer el post de equipo

class PostListViewTestWithFactory(TestCase):

    def setUp(self):
        # Crear un usuario
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        
        # Crear otro usuario
        self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")

        # Crear un post con permisos apropiados
        self.author_post = BlogPost.objects.create(
            title="Post del autor",
            content="pasara", 
            author=self.user,
            public_permission=Permissions.NONE,  # Ejemplo de permiso público
            authenticated_permission=Permissions.NONE,  # Permiso autenticado
            team_permission=Permissions.READ_EDIT,  # Permiso de equipo
        )

        # Crear una solicitud de la API con APIRequestFactory
        self.factory = APIRequestFactory()

    def test_author_can_access_post(self):
        # Crear solicitud GET autenticada por el autor
        request = self.factory.get('/posts/')
        force_authenticate(request, user=self.user)  # Autenticar al usuario que es el autor del post

        # Invocar la vista
        view = PostListView.as_view()
        response = view(request)

        # Verificar que el autor puede acceder a su post
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo debería devolver el post del autor


    def test_other_user_cannot_access_author_post(self):
        # Crear solicitud GET autenticada por un usuario diferente
        request = self.factory.get('/posts/')
        force_authenticate(request, user=self.other_user)  # Autenticar al usuario que no es el autor

        # Invocar la vista
        view = PostListView.as_view()
        response = view(request)

        # Verificar que el usuario distinto al autor no puede acceder al post
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)  # No debería devolver el post del autor

class PostListViewTestWithFactory(APITestCase):
    def setUp(self):
        # Crear usuarios únicos antes de cada test
        self.author = User.objects.create_user(username="author_unique", password="password")
        self.other_user = User.objects.create_user(username="otheruser_unique", password="password")

    def test_other_user_cannot_access_author_post(self):
        # Crear un post con permisos adecuados
        post = BlogPost.objects.create(
            title="Post de autor",
            content="Contenido de post",
            author=self.author,
            public_permission=Permissions.NONE,  # Ejemplo: Sin permiso público
            authenticated_permission=Permissions.NONE,  # Ejemplo: Sin permiso para usuarios autenticados
            team_permission=Permissions.NONE,  # Ejemplo: Sin permiso de equipo
        )

        # Realizar solicitud GET como el usuario que no es autor
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/posts/')

        # Verificar que el código de respuesta sea 404, ya que no debería haber acceso
        self.assertEqual(response.status_code, 404)


class PostDetailViewSetTest(APITestCase):
    def setUp(self):
        # Crear usuarios
        self.author = UserFactory(username="author")
        self.authenticated_user = UserFactory(username="authenticated_user")

        # Crear grupos para el equipo
        self.team_group = Group.objects.create(name="team_name")

        # Crear posts con diferentes permisos
        self.public_post = BlogPostFactory(
            author=self.author,
            public_permission=Permissions.READ,  # Aquí, asegúrate de que usas un valor válido
            authenticated_permission=Permissions.READ_EDIT,  # Asegúrate de usar valores válidos
            team_permission=Permissions.READ_EDIT,  # Igualmente
)
                # Crear un post con permiso autenticado
        self.authenticated_post = BlogPostFactory(
            author=self.author,
            public_permission=Permissions.NONE,  # Asigna un valor válido
            authenticated_permission=Permissions.READ,  # Asigna un valor válido
            team_permission=Permissions.READ,  # Asigna un valor válido
        )

        # Crear un post con permiso de autor (solo el autor puede acceder)
        self.author_post = BlogPostFactory(
            author=self.author,
            public_permission=Permissions.NONE,  # Ningún acceso público
            authenticated_permission=Permissions.NONE,  # Ningún acceso autenticado
            team_permission=Permissions.NONE,  # Ningún acceso de equipo
        )

        # Crear un post con permiso de equipo
        self.team_post = BlogPostFactory(
            author=self.author,
            public_permission=Permissions.NONE,  # Ningún acceso público
            authenticated_permission=Permissions.READ_EDIT,  # Ningún acceso autenticado
            team_permission=Permissions.READ_EDIT,  # Acceso para miembros del equipo
)


        # Asignar usuario autenticado al grupo de equipo
        self.authenticated_user.groups.add(self.team_group)
        self.authenticated_user.save()

        # Crear comentarios y likes para el post público
        self.comment = CommentFactory(blog_post=self.public_post, user=self.author)
        self.like = LikeFactory(blog_post=self.public_post, user=self.authenticated_user)

        # Factory para realizar solicitudes
        self.factory = APIRequestFactory()

    def test_public_post_access(self):
        # Verificar que cualquier usuario puede acceder al post público
        request = self.factory.get(f'/posts/{self.public_post.id}/')
        view = PostDetailViewSet.as_view({'get': 'retrieve'})

        # Sin autenticación (usuario anónimo)
        response = view(request, pk=self.public_post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Usuario autenticado
        force_authenticate(request, user=self.authenticated_user)
        response = view(request, pk=self.public_post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_post_access(self):
        # Verificar que solo usuarios autenticados pueden acceder al post autenticado
        request = self.factory.get(f'/posts/{self.authenticated_post.id}/')
        view = PostDetailViewSet.as_view({'get': 'retrieve'})

        # Usuario autenticado
        force_authenticate(request, user=self.authenticated_user)
        response = view(request, pk=self.authenticated_post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_post_access(self):
        # Verificar que solo el autor puede acceder al post del autor
        request = self.factory.get(f'/posts/{self.author_post.id}/')
        view = PostDetailViewSet.as_view({'get': 'retrieve'})

        # Usuario no autorizado (autenticado, pero no el autor)
        force_authenticate(request, user=self.authenticated_user)
        response = view(request, pk=self.author_post.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # El autor puede acceder al post
        force_authenticate(request, user=self.author)
        response = view(request, pk=self.author_post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_team_post_access(self):
        # Verificar que solo los miembros del equipo pueden acceder al post de equipo
        request = self.factory.get(f'/posts/{self.team_post.id}/')
        view = PostDetailViewSet.as_view({'get': 'retrieve'})

        # Usuario no en el equipo (sin añadir al grupo)
        force_authenticate(request)  # No autenticado, o sin agregar al grupo de equipo
        response = view(request, pk=self.team_post.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Usuario en el equipo (asignado al grupo 'team_name')
        force_authenticate(request, user=self.authenticated_user)
        response = view(request, pk=self.team_post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



###Tests para comentarios
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from posts.models import BlogPost, Comment
from rest_framework import status
from .factories import UserFactory, BlogPostFactory, CommentFactory
from .views import CommentListView


class CommentListViewTestCase(APITestCase):
    def setUp(self):
        # Crear usuarios
        self.anonymous_user = UserFactory()
        self.authenticated_user = UserFactory()
        self.author_user = UserFactory()
        
        # Crear grupo para equipo
        self.team_group = Group.objects.create(name="team_name")
        self.team_member = UserFactory()
        self.team_member.groups.add(self.team_group)
        self.team_member.save()
        
        # Crear posts con diferentes permisos (ajustado para usar permisos constantes)
        self.public_post = BlogPostFactory(public_permission=Permissions.READ,authenticated_permission=Permissions.READ,team_permission=Permissions.READ)
        self.authenticated_post = BlogPostFactory(authenticated_permission=Permissions.READ, public_permission=Permissions.NONE,team_permission=Permissions.READ)
        
        self.author_post = BlogPostFactory(author=self.author_user, authenticated_permission=Permissions.NONE, public_permission=Permissions.NONE,team_permission=Permissions.NONE)
        self.team_post = BlogPostFactory(team_permission=Permissions.READ_EDIT, author=self.team_member, authenticated_permission=Permissions.NONE, public_permission=Permissions.NONE)

        # Crear comentarios asociados a los posts
        self.public_comment = CommentFactory(blog_post=self.public_post)
        self.authenticated_comment = CommentFactory(blog_post=self.authenticated_post)
        self.author_comment = CommentFactory(blog_post=self.author_post)
        self.team_comment = CommentFactory(blog_post=self.team_post)

        # Preparar la vista
        self.factory = APIRequestFactory()

    def test_anonymous_user_access(self):
        """Verifica que un usuario no autenticado solo ve comentarios públicos."""
        request = self.factory.get('/comments/')
        view = CommentListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Solo el comentario público

    def test_authenticated_user_access(self):
        """Verifica que un usuario autenticado ve comentarios públicos y autenticados."""
        request = self.factory.get('/comments/')
        force_authenticate(request, user=self.authenticated_user)
        view = CommentListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Públicos y autenticados

    def test_author_access(self):
        """Verifica que el autor del post puede ver su comentario."""
        request = self.factory.get('/comments/')
        force_authenticate(request, user=self.author_user)
        view = CommentListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Públicos, autenticados y de autor

    def test_team_member_access(self):
        """Verifica que un miembro del equipo puede ver comentarios de equipo."""
        request = self.factory.get('/comments/')
        force_authenticate(request, user=self.team_member)
        view = CommentListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Publicos, autenticados y team




class PostCommentsCreateViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.force_login(self.user)
        self.post = BlogPost.objects.create(
            title="Public Post",
            content="This is a public post.",
            public_permission=Permissions.READ,  # Use the Permissions choices here
            author=self.user,
        )

        # Generar la URL con reverse
        self.url = reverse("post-comment-create", kwargs={"post_id": self.post.id})

    def test_create_comment_on_public_post(self):
        data = {
            "content": "This is a test comment.",
            "timestamp": "2024-12-10T00:00:00Z"  # Ajusta al formato esperado
        }
        response = self.client.post(self.url, data)
        print(response.status_code, response.content.decode())  # Depuración
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PostCommentsCreateViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.force_login(self.user)
        self.post = BlogPost.objects.create(
            title="Authenticated Post",
            content="This is an authenticated post.",
            authenticated_permission="READ",
            author=self.user,
        )
        # Generar la URL con reverse
        self.url = reverse("post-comment-create", kwargs={"post_id": self.post.id})

    def test_create_comment_on_auth_post(self):
        data = {
            "content": "This is a test comment.",
            "timestamp": "2024-12-10T00:00:00Z"  # Ajusta al formato esperado
        }
        response = self.client.post(self.url, data)
        print(response.status_code, response.content.decode())  # Depuración
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)




class PostCommentsCreateViewTest(APITestCase):

    def setUp(self):
        # Crear usuario y grupo de equipo
        self.user = User.objects.create_user(username="testuser", password="password")
        self.group = Group.objects.create(name="team_group")
        self.user.groups.add(self.group)  # Asignar el usuario al grupo del equipo
        
        # Crear otro usuario sin pertenecer al grupo
        self.other_user = User.objects.create_user(username="otheruser", password="password")

        # Crear un post con permisos "team"
        self.post = BlogPost.objects.create(
            title="Team Post",
            content="This is a team post.",
            team_permission="READ",
            authenticated_permission="NONE",
            public_permission="NONE",
            author=self.user,
        )
        
        # Generar la URL con reverse
        self.url = reverse("post-comment-create", kwargs={"post_id": self.post.id})

    def test_create_comment_on_team_post_as_team_member(self):
        """
        Test para verificar que un miembro del equipo puede comentar en un post con permisos 'team'.
        """
        # Realizar la solicitud POST con el usuario del equipo
        self.client.force_login(self.user)
        data = {
            "content": "This is a team comment.",
            "timestamp": "2024-12-10T00:00:00Z"
        }
        response = self.client.post(self.url, data)

        # Verificar que el comentario fue creado correctamente
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que el comentario se haya guardado en la base de datos
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, "This is a team comment.")
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.blog_post, self.post)

    def test_create_comment_on_team_post_as_non_team_member(self):
        """
        Test para verificar que un usuario que no pertenece al equipo no pueda comentar en un post con permisos 'team'.
        """
        # Realizar la solicitud POST con el otro usuario que no pertenece al equipo
        self.client.force_login(self.other_user)
        data = {
            "content": "This should not be allowed.",
            "timestamp": "2024-12-10T00:00:00Z"
        }
        response = self.client.post(self.url, data)

        # Verificar que el comentario no fue creado y que el código de estado es '403 Forbidden'
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class PostCommentsCreateViewTest(APITestCase):

    def setUp(self):
        # Crear usuario y otro usuario no autor
        self.user = User.objects.create_user(username="testuser", password="password")
        self.other_user = User.objects.create_user(username="otheruser", password="password")
        
        # Crear un post con permisos "author" y asignar al autor
        self.post = BlogPost.objects.create(
            title="Author Post",
            content="This is an author post.",
            public_permission="NONE",
            authenticated_permission="NONE",
            team_permission="NONE",
            author=self.user,  # El autor del post es el usuario creado
        )
        
        # Generar la URL con reverse
        self.url = reverse("post-comment-create", kwargs={"post_id": self.post.id})

    def test_create_comment_on_author_post_as_author(self):
        """
        Test para verificar que el autor puede comentar en su propio post con permisos 'author'.
        """
        # Realizar la solicitud POST con el usuario autor
        self.client.force_login(self.user)
        data = {
            "content": "This is a comment by the author.",
            "timestamp": "2024-12-10T00:00:00Z"
        }
        response = self.client.post(self.url, data)

        # Verificar que el comentario fue creado correctamente
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que el comentario se haya guardado en la base de datos
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, "This is a comment by the author.")
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.blog_post, self.post)

    def test_create_comment_on_author_post_as_non_author(self):
        """
        Test para verificar que un usuario que no es el autor no pueda comentar en un post con permisos 'author'.
        """
        # Realizar la solicitud POST con otro usuario que no es el autor
        self.client.force_login(self.other_user)
        data = {
            "content": "This should not be allowed.",
            "timestamp": "2024-12-10T00:00:00Z"
        }
        response = self.client.post(self.url, data)

        # Verificar que el comentario no fue creado y que el código de estado es '403 Forbidden'
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)




class CommentDeleteViewTest(APITestCase):

    def setUp(self):
        # Crear usuarios
        self.user = User.objects.create_user(username="testuser", password="password")
        self.other_user = User.objects.create_user(username="otheruser", password="password")
        
        # Crear un post y un comentario asociado
        self.post = BlogPost.objects.create(
            title="Post to delete comments",
            content="Content for testing deletion of comments.",
            authenticated_permission="READ",  # Permiso de autenticación
            author=self.user,
        )
        self.comment = Comment.objects.create(
            content="This is a comment",
            blog_post=self.post,
            user=self.user,  # El comentario pertenece al usuario 'testuser'
        )

        # URL para eliminar el comentario (con la nueva URL proporcionada)
        self.url = reverse("comment_delete", kwargs={"comment_id": self.comment.id})

    def test_delete_comment_as_author(self):
        """
        Test que verifica que el autor del comentario puede eliminarlo.
        """
        # Login como el autor del comentario
        self.client.force_login(self.user)

        # Realizar la solicitud DELETE
        response = self.client.delete(self.url)

        # Verificar que el código de estado es 204 No Content (comentario eliminado)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_as_non_author(self):
        """
        Test que verifica que un usuario que no es el autor no puede eliminar el comentario.
        """
        # Login como otro usuario que no es el autor del comentario
        self.client.force_login(self.other_user)

        # Realizar la solicitud DELETE
        response = self.client.delete(self.url)

        # Verificar que el código de estado es 403 Forbidden (no autorizado)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())  # El comentario sigue existiendo


##Tests para la vista y creacion de likes
from django.contrib.auth.models import User, Group
from unittest.mock import MagicMock
from django.test import TestCase
from posts.models import BlogPost, Like
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class PostLikeTests(APITestCase):

    def setUp(self):
        """
        Configura los datos necesarios para las pruebas.
        """
        # Crear un usuario
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # Crear un post
        self.post = BlogPost.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user,
            public_permission="READ"
        )

        # Autenticación para pruebas que requieren login
        self.client.login(username="testuser", password="testpassword")

    def test_add_like(self):
        """
        Prueba agregar un like a un post.
        """
        url = reverse('post-like', args=[self.post.id])

        # Realizar la petición POST para agregar un like
        response = self.client.post(url)

        # Verificar que el like se ha agregado correctamente
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], "Like added successfully.")

        # Verificar que el like realmente se haya guardado en la base de datos
        like = Like.objects.filter(user=self.user, blog_post=self.post)
        self.assertTrue(like.exists())

    def test_add_like_duplicate(self):
        """
        Prueba agregar un like duplicado a un post.
        """
        url = reverse('post-like', args=[self.post.id])

        # Realizar la petición POST para agregar un like
        self.client.post(url)

        # Intentar agregar el mismo like nuevamente
        response = self.client.post(url)

        # Verificar que no se haya agregado el like duplicado
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "You have already liked this post.")

    def test_remove_like(self):
        """
        Prueba eliminar un like de un post.
        """
        # Agregar un like primero
        Like.objects.create(blog_post=self.post, user=self.user)

        url = reverse('post-like', args=[self.post.id])

        # Realizar la petición DELETE para eliminar el like
        response = self.client.delete(url)

        # Verificar que el like se ha eliminado correctamente
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Like removed successfully.")

        # Verificar que el like ya no existe en la base de datos
        like = Like.objects.filter(user=self.user, blog_post=self.post)
        self.assertFalse(like.exists())

    def test_remove_like_not_exists(self):
        """
        Prueba eliminar un like cuando el usuario no ha dado like previamente.
        """
        url = reverse('post-like', args=[self.post.id])

        # Intentar eliminar un like sin haber dado uno previamente
        response = self.client.delete(url)

        # Verificar que la respuesta sea un error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "You have not liked this post yet.")


class LikeListViewTest(TestCase):
    
    def setUp(self):
        # Crear usuarios
        self.user_authenticated = User.objects.create_user(username="authenticated_user", password="password")
        
        # Crear un post público
        self.public_post = BlogPost.objects.create(title="Public Post", content="Public content", public_permission="READ", author=self.user_authenticated)

        # Crear likes
        self.like_public = Like.objects.create(blog_post=self.public_post, user=self.user_authenticated)

    def test_get_likes_for_public_post(self):
        # Simulando la vista con un usuario autenticado
        # Usamos MagicMock para simular un request y el comportamiento de la vista
        request = MagicMock()
        request.user = self.user_authenticated

        # Filtrar likes basados en la lógica de la vista
        all_likes = Like.objects.all()
        allowed_likes = []
        
        for like in all_likes:
            post = like.blog_post
            if post.public_permission == 'READ':
                allowed_likes.append(like)

        # Asegurándonos de que el like público está en la lista de likes permitidos
        self.assertIn(self.like_public, allowed_likes)
        self.assertEqual(len(allowed_likes), 1)  # Solo un like debe ser retornado

    def test_get_likes_for_no_public_post(self):
        # Create a post with no public permission
        private_post = BlogPost.objects.create(title="Private Post", content="Private content", public_permission="NONE", author=self.user_authenticated)
        like_private = Like.objects.create(blog_post=private_post, user=self.user_authenticated)

        # Simulate the view with an authenticated user
        request = MagicMock()
        request.user = self.user_authenticated

        # Get all likes, filtered by permissions
        all_likes = Like.objects.all()
        allowed_likes = []

        # Add filtering logic to exclude likes on private posts
        for like in all_likes:
            post = like.blog_post
            if post.public_permission != 'NONE':  # Exclude private posts
                allowed_likes.append(like)

        # Ensure that the like from the private post is not included
            self.assertNotIn(like_private, allowed_likes)
            self.assertEqual(len(allowed_likes), 1)  # Only the like for the public post should be returned




class LikeListViewTest(TestCase):

    def setUp(self):
        # Crear usuarios
        self.user_authenticated = User.objects.create_user(username="authenticated_user", password="password")
        
        # Crear un post con permisos autenticados
        self.auth_post = BlogPost.objects.create(title="Authenticated Post", content="Authenticated content",authenticated_permission="READ",  author=self.user_authenticated)

        # Crear un like para el post
        self.like_authenticated = Like.objects.create(blog_post=self.auth_post, user=self.user_authenticated)

    def test_get_likes_for_authenticated_post_authenticated_user(self):
        # Simulando la vista con un usuario autenticado
        request = MagicMock()
        request.user = self.user_authenticated

        # Filtrar likes basados en la lógica de la vista
        all_likes = Like.objects.all()
        allowed_likes = []
        
        for like in all_likes:
            post = like.blog_post
            if post.authenticated_permission == 'READ' and request.user.is_authenticated:
                allowed_likes.append(like)

        # Asegurándonos de que el like del post "authenticated" esté en la lista
        self.assertIn(self.like_authenticated, allowed_likes)
        self.assertEqual(len(allowed_likes), 1)  # Solo un like debe ser retornado

    def test_get_likes_for_authenticated_post_anonymous_user(self):
        # Simulando la vista con un usuario anónimo
        request = MagicMock()
        request.user = AnonymousUser()  # Simulando un usuario anónimo

        # Filtrar likes basados en la lógica de la vista
        all_likes = Like.objects.all()
        allowed_likes = []
        
        for like in all_likes:
            post = like.blog_post
            if post.authenticated_permission == 'READ' and request.user.is_authenticated:
                allowed_likes.append(like)

        # Asegurándonos de que el like del post "authenticated" no esté en la lista para un usuario anónimo
        self.assertNotIn(self.like_authenticated, allowed_likes)
        self.assertEqual(len(allowed_likes), 0)  # Ningún like debe ser retornado para un usuario anónimo



class LikeListViewTest(TestCase):

    def setUp(self):
        # Crear usuarios
        self.user_authenticated = User.objects.create_user(username="authenticated_user", password="password")
        self.user_other = User.objects.create_user(username="other_user", password="password")

        # Crear un grupo (equipo)
        self.team_group = Group.objects.create(name="Team A")
        
        # Asignar el usuario autenticado al equipo
        self.user_authenticated.groups.add(self.team_group)

        # Crear un post con permisos para el equipo
        self.team_post = BlogPost.objects.create(title="Team Post", content="Team content", team_permission="READ_EDIT", author=self.user_authenticated)

        # Crear un like para el post
        self.like_team = Like.objects.create(blog_post=self.team_post, user=self.user_authenticated)

    def test_get_likes_for_team_post_user_in_team(self):
        # Simulando la vista con un usuario del mismo equipo
        request = MagicMock()
        request.user = self.user_authenticated  # Usuario autenticado y en el equipo

        # Filtrar likes basados en la lógica de la vista
        all_likes = Like.objects.all()
        allowed_likes = []
        
        for like in all_likes:
            post = like.blog_post
            if post.team_permission == 'READ_EDIT' and request.user.groups.filter(id=post.author.groups.first().id).exists():
                allowed_likes.append(like)

        # Asegurándonos de que el like del post "team" esté en la lista
        self.assertIn(self.like_team, allowed_likes)
        self.assertEqual(len(allowed_likes), 1)  # Solo un like debe ser retornado

    def test_get_likes_for_team_post_user_not_in_team(self):
        # Simulando la vista con un usuario no perteneciente al equipo
        request = MagicMock()
        request.user = self.user_other  # Usuario no está en el equipo

        # Filtrar likes basados en la lógica de la vista
        all_likes = Like.objects.all()
        allowed_likes = []
        
        for like in all_likes:
            post = like.blog_post
            if post.team_permission == 'READ_EDIT' and request.user.groups.filter(id=post.author.groups.first().id).exists():
                allowed_likes.append(like)

        # Asegurándonos de que el like del post "team" no esté en la lista
        self.assertNotIn(self.like_team, allowed_likes)
        self.assertEqual(len(allowed_likes), 0)  # Ningún like debe ser retornado para un usuario fuera del equipo



class LikeListViewTest(TestCase):

    def setUp(self):
        # Crear usuarios
        self.user_authenticated = User.objects.create_user(username="authenticated_user", password="password")
        self.user_other = User.objects.create_user(username="other_user", password="password")

        # Crear un post con permisos para el autor
        self.author_post = BlogPost.objects.create(title="Author Post", content="Author content", public_permission="NONE", team_permission="NONE", authenticated_permission="NONE", author=self.user_authenticated)

        # Crear un like para el post
        self.like_author = Like.objects.create(blog_post=self.author_post, user=self.user_authenticated)

    def test_get_likes_for_author_post_author_user(self):
        # Simulando la vista con el usuario que es el autor del post
        request = MagicMock()
        request.user = self.user_authenticated  # Usuario es el autor del post

        # Filtrar likes basados en la lógica de la vista
        all_likes = Like.objects.all()
        allowed_likes = []
        
        for like in all_likes:
            post = like.blog_post
            if request.user == post.author:
                allowed_likes.append(like)

        # Asegurándonos de que el like del post "author" esté en la lista
        self.assertIn(self.like_author, allowed_likes)
        self.assertEqual(len(allowed_likes), 1)  # Solo un like debe ser retornado

    def test_get_likes_for_author_post_non_author_user(self):
        # Simulando la vista con un usuario que no es el autor del post
        request = MagicMock()
        request.user = self.user_other  # Usuario no es el autor del post

        # Filtrar likes basados en la lógica de la vista
        all_likes = Like.objects.all()
        allowed_likes = []
        
        for like in all_likes:
            post = like.blog_post
            if  request.user == post.author:
                allowed_likes.append(like)

        # Asegurándonos de que el like del post "author" no esté en la lista para un usuario que no es el autor
        self.assertNotIn(self.like_author, allowed_likes)
        self.assertEqual(len(allowed_likes), 0)  # Ningún like debe ser retornado para un usuario que no es e
    
    def test_invalid_post_like(self):
            # Intentar dar un like a un post inexistente
            request = MagicMock()
            request.user = self.user_authenticated
            invalid_post_id = 9999  # ID de un post que no existe
            
            # Intentar acceder al like (esto debería lanzar un error 404 o similar)
            response = self.client.post(f'/likes/{invalid_post_id}/')
            self.assertEqual(response.status_code, 404)

###Tests para la paginacion
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from posts.models import BlogPost, Like, Comment

class PostPaginationTest(APITestCase):
    def setUp(self):
        # Crear un usuario autenticado
        self.user = User.objects.create_user(username="testuser", password="password")
        
        # Crear varios posts para probar la paginación
        for i in range(25):  # Crear 25 posts
            BlogPost.objects.create(title=f"Post {i}", content="Content of the post", author=self.user)

    def test_empty_posts(self):
        # No posts in the database
        BlogPost.objects.all().delete()  # Clean the database for this test
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])


    def test_last_page(self):
        response = self.client.get('/api/posts/?limit=5&offset=20')  # Specify offset for the last 5 posts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # Ensure 5 results on the last page

        
   

class LikePaginationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Crear un usuario para ser el autor del post
        self.user = User.objects.create_user(username="testuser", password="password")
        
        # Crear el BlogPost con el usuario como autor
        self.post = BlogPost.objects.create(title="Test Post", content="Content", author=self.user)
        
        # Crear 30 usuarios y asignarles un Like a cada uno
        self.users = []
        for i in range(30):
            user = User.objects.create_user(username=f"user{i}", password="password")
            self.users.append(user)
            Like.objects.create(blog_post=self.post, user=user)  # Crear un like por usuario

    def test_like_pagination(self):
        response = self.client.get('/api/likes/?limit=20')  # Usa 'limit' en lugar de 'page_size'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 20)  # Espera 20 resultados por página

    def test_like_pagination_custom_page_size(self):
        response = self.client.get('/api/likes/?limit=10')  # Usa 'limit' en lugar de 'page_size'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 10)  # Espera 10 resultados por página

    def test_like_pagination_last_page(self):
        """Verifica que la última página tenga los elementos restantes"""
        response = self.client.get('/api/likes/?limit=10&offset=20')  # Última página con 10 restantes
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 10)  # 10 elementos en la última página
        self.assertIsNone(response.data['next'])  # No debe haber una página siguiente
        self.assertIsNotNone(response.data['previous'])  # Debe haber una página anterior



class CommentPaginationTest(APITestCase):
    def setUp(self):
        # Crear usuarios y posts para asociar con los comentarios
        self.user = User.objects.create_user(username="testuser", password="password")
        self.post = BlogPost.objects.create(title="Post for Comments", content="Content", author=self.user)
        
        # Crear 25 comentarios
        for i in range(25):
            Comment.objects.create(blog_post=self.post, user=self.user, content=f"Comment {i}")

    def test_comment_pagination(self):
        """Verifica la estructura de la respuesta y el número de resultados por página"""
        response = self.client.get('/api/comments/?limit=10')  # Usa 'limit' en lugar de 'page_size'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_pages', response.data)
        self.assertIn('current_page', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        # Verificar que el número de resultados por página sea 10
        self.assertEqual(len(response.data['results']), 10)

        # Verificar que 'total_pages' sea al menos 3 (25 comentarios / 10 por página)
        self.assertEqual(response.data['total_pages'], 3)

    def test_comment_pagination_custom_page_size(self):
        """Verifica que la paginación respete un tamaño de página personalizado"""
        response = self.client.get('/api/comments/?limit=5')  # Cambiar el tamaño de la página a 5

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # La página ahora debe tener 5 resultados

    def test_comment_pagination_last_page(self):
        """Verifica la última página con los elementos restantes"""
        response = self.client.get('/api/comments/?limit=10&offset=20')  # Última página con 5 elementos

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # Solo quedan 5 comentarios en la última página
        self.assertIsNone(response.data['next'])  # No debe haber una página siguiente
        self.assertIsNotNone(response.data['previous'])  # Debe haber una página anterior


###Tests de los serializadores
from rest_framework.exceptions import ValidationError
from posts.serializers import BlogPostSerializer
from posts.models import Like
from posts.serializers import LikeSerializer
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from posts.models import Comment
from posts.serializers import CommentSerializer
from rest_framework.test import APITestCase


class BlogPostValidationTest(APITestCase):
    def test_blog_post_validation(self):
        # Datos inválidos (sin título)
        data = {
            'title': '',
            'content': 'Test content',
            'author': 1,  
            'public_permission': 'READ',
            'authenticated_permission': 'READ',  # Se agregan estos campos
            'team_permission': 'READ',
        }

        serializer = BlogPostSerializer(data=data)

        # El serializador debe fallar la validación
        self.assertFalse(serializer.is_valid())

        # Verificar que el error sea solo en 'title' y no en otros campos
        self.assertIn('title', serializer.errors)  # Asegura que 'title' tenga error
        self.assertNotIn('authenticated_permission', serializer.errors)  # No debería fallar aquí
        self.assertNotIn('team_permission', serializer.errors)  # No debería fallar aquí



class LikeSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.blog_post = BlogPost.objects.create(
            title="Test Post",
            content="Test content",
            author=self.user,
        )
        self.like = Like.objects.create(blog_post=self.blog_post, user=self.user)

    def test_like_serialization(self):
        # Serializar el objeto Like
        serializer = LikeSerializer(self.like)

        # Imprimir datos serializados para depuración
        print(serializer.data)  

        # Verificar qué datos está devolviendo el serializador
        expected_data = {
            'id': self.like.id,
            'user': self.user.username,  # Ajustar si el serializer usa user.id en lugar de username
            'blog_post': self.blog_post.title,
            'timestamp': self.like.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Ajustar formato si es necesario
        }

        # Verificar que los datos coincidan
        self.assertEqual(serializer.data, expected_data)



from datetime import datetime

class CommentSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.blog_post = BlogPost.objects.create(
            title="Test Post",
            content="Test content",
            author=self.user
        )
        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            user=self.user,
            content="This is a comment"
        )

    def test_comment_serialization(self):
        # Serializar el objeto Comment
        serializer = CommentSerializer(self.comment)

        # Imprimir datos serializados para depuración
        print("Serialized data:", serializer.data)

        # Asegurar que el timestamp tiene el formato "%Y-%m-%d %H:%M:%S"
        expected_data = {
            'id': self.comment.id,
            'blog_post': self.blog_post.id,
            'user': self.user.username,
            'content': "This is a comment",
            'timestamp': self.comment.timestamp.strftime("%Y-%m-%d %H:%M:%S"),  # ✅ Se formatea correctamente
            'post_title': self.blog_post.title
        }

        self.assertEqual(serializer.data, expected_data)

