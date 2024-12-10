from django.test import TestCase
from django.contrib.auth.models import User, Group
from .models import BlogPost, Comment
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
from posts.views import BlogPostCreateViewSet
from django.test import TestCase
from posts.views import PostListView
from django.contrib.auth.models import User, Group
from posts.models import BlogPost
from posts.views import BlogPostCreateViewSet
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
        self.view = BlogPostCreateViewSet.as_view({'post': 'create'})

    def test_create_post_authenticated(self):
        # Datos válidos para crear un post
        data = {'title': 'Test Post', 'content': 'This is a test content.'}
        # Crear la solicitud POST simulada
        request = self.factory.post('/posts/create/', data, format='json')
        # Autenticar al usuario en la solicitud
        force_authenticate(request, user=self.user)
        # Llamar a la vista con la solicitud
        response = self.view(request)
        
        # Validar la respuesta
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


class BlogPostCreateViewSetTestWithFactory(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = BlogPostCreateViewSet.as_view({'post': 'create'})
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_post_authenticated(self):
        # Autenticarse con un usuario existente
        self.client.login(username='testuser', password='testpassword')

        # Datos para crear un post
        data = {'title': 'Authenticated Post', 'content': 'Content of authenticated post.'}
        
        # Crear una solicitud autenticada
        request = self.factory.post('/posts/create/', data, format='json')
        request.user = self.user  # Simular que la solicitud proviene de un usuario autenticado
        
        # Llamar a la vista con la solicitud
        response = self.view(request)
        
        # Validar el estado HTTP y datos de respuesta
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogPost.objects.count(), 1)
        self.assertEqual(BlogPost.objects.first().author, self.user)



class PostListViewTestWithFactory(TestCase):
    def setUp(self):
        # Crear un usuario y un grupo
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.group = Group.objects.create(name="Test Group")
        self.user.groups.add(self.group)

        # Crear posts
        self.public_post = BlogPost.objects.create(
            title="Public Post", permissions="public", author=self.user
        )
        self.authenticated_post = BlogPost.objects.create(
            title="Authenticated Post", permissions="authenticated", author=self.user
        )
        self.team_post = BlogPost.objects.create(
            title="Team Post", permissions="team", author=self.user
        )

        # Configurar APIRequestFactory
        self.factory = APIRequestFactory()

    def test_authenticated_user_can_access_posts(self):
        # Crear solicitud GET
        request = self.factory.get('/posts/')
        force_authenticate(request, user=self.user)  # Autenticar al usuario

        # Invocar la vista
        view = PostListView.as_view()
        response = view(request)

        # Verificar la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)  # Debe incluir todos los posts accesibles

    def test_unauthenticated_user_can_access_only_public_posts(self):
        # Crear solicitud GET
        request = self.factory.get('/posts/')

        # Invocar la vista sin autenticar al usuario
        view = PostListView.as_view()
        response = view(request)

        # Verificar la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)  # Solo el post público debe aparecer



class BlogPostDeleteViewTest(TestCase):
    def setUp(self):
        # Crear usuario y grupo
        self.user = User.objects.create_user(username="author", password="testpassword")
        self.group = Group.objects.create(name="Test Group")
        self.user.groups.add(self.group)
        
        # Crear otro usuario y agregarlo al mismo grupo
        self.team_user = User.objects.create_user(username="team_member", password="password123")
        self.team_user.groups.add(self.group)
        
        # Crear un post
        self.post = BlogPost.objects.create(
            title="Team Post", permissions="team", author=self.user
        )
        
        self.factory = APIRequestFactory()

    def test_author_can_delete_post(self):
        request = self.factory.delete(f'/posts/{self.post.id}/')
        force_authenticate(request, user=self.user)
        
        view = BlogPostDeleteView.as_view()
        response = view(request, pk=self.post.id)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BlogPost.objects.filter(id=self.post.id).exists())

    def test_team_member_can_delete_post(self):
        request = self.factory.delete(f'/posts/{self.post.id}/')
        force_authenticate(request, user=self.team_user)
        
        view = BlogPostDeleteView.as_view()
        response = view(request, pk=self.post.id)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BlogPost.objects.filter(id=self.post.id).exists())

    def test_unauthorized_user_cannot_delete_post(self):
        unauth_user = User.objects.create_user(username="unauth_user", password="password")
        request = self.factory.delete(f'/posts/{self.post.id}/')
        force_authenticate(request, user=unauth_user)
        
        view = BlogPostDeleteView.as_view()
        response = view(request, pk=self.post.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(BlogPost.objects.filter(id=self.post.id).exists())



class BlogPostUpdateViewTest(TestCase):
    def setUp(self):
        # Configuración similar a BlogPostDeleteViewTest
        self.user = User.objects.create_user(username="author", password="testpassword")
        self.group = Group.objects.create(name="Test Group")
        self.user.groups.add(self.group)
        
        self.team_user = User.objects.create_user(username="team_member", password="password123")
        self.team_user.groups.add(self.group)
        
        self.post = BlogPost.objects.create(
            title="Team Post", permissions="team", author=self.user
        )
        
        self.factory = APIRequestFactory()

    def test_author_can_update_post(self):
        data = {"title": "Updated Title"}
        request = self.factory.patch(f'/posts/{self.post.id}/', data)
        force_authenticate(request, user=self.user)
        
        view = BlogPostUpdateView.as_view()
        response = view(request, pk=self.post.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")

    def test_team_member_can_update_post(self):
        data = {"title": "Team Updated Title"}
        request = self.factory.patch(f'/posts/{self.post.id}/', data)
        force_authenticate(request, user=self.team_user)
        
        view = BlogPostUpdateView.as_view()
        response = view(request, pk=self.post.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Team Updated Title")

    def test_unauthorized_user_cannot_update_post(self):
        unauth_user = User.objects.create_user(username="unauth_user", password="password")
        data = {"title": "Unauthorized Update"}
        request = self.factory.patch(f'/posts/{self.post.id}/', data)
        force_authenticate(request, user=unauth_user)
        
        view = BlogPostUpdateView.as_view()
        response = view(request, pk=self.post.id)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.title, "Unauthorized Update")



class PostListViewTestWithFactory(TestCase):
    def setUp(self):
        # Crear usuarios y grupos
        self.user = User.objects.create_user(username="author", password="testpassword")
        self.group = Group.objects.create(name="Test Group")
        self.user.groups.add(self.group)

        # Crear un post con permisos 'team'
        self.team_post = BlogPost.objects.create(
            title="Team Post", permissions="team", author=self.user
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

        # Crear un post con permiso "author"
        self.author_post = BlogPost.objects.create(
            title="Post del autor",
            content="pasara", 
            author=self.user,
            permissions="author",  # Solo el autor puede verlo
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
        post = BlogPost.objects.create(
            title="Post de autor",
            content="Contenido de post",
            author=self.author,
            permissions="author"
        )

        # Realizar solicitud GET como el usuario que no es autor
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/posts/')

        # Verificar que el código de respuesta sea 404 
        self.assertEqual(response.status_code, 404)






class PostDetailViewSetTest(APITestCase):
    def setUp(self):
        # Crear usuarios
        self.author = UserFactory(username="author")
        self.authenticated_user = UserFactory(username="authenticated_user")
        self.anonymous_user = None

        # Crear grupos para el equipo
        self.team_group = Group.objects.create(name="team_name")

        # Crear posts con diferentes permisos
        self.public_post = BlogPostFactory(author=self.author, permissions="public")
        self.authenticated_post = BlogPostFactory(author=self.author, permissions="authenticated")
        self.author_post = BlogPostFactory(author=self.author, permissions="author")
        
        # Crear post con permiso de equipo
        self.team_post = BlogPostFactory(author=self.author, permissions="team")

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
        force_authenticate(request, user=self.anonymous_user)
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
        

        # Crear posts con diferentes permisos
        self.public_post = BlogPostFactory(permissions="public")
        self.authenticated_post = BlogPostFactory(permissions="authenticated")
        self.author_post = BlogPostFactory(permissions="author", author=self.author_user)
        self.team_post = BlogPostFactory(permissions="team", author=self.team_member)

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
            permissions="public",
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
            permissions="authenticated",
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
            permissions="team",
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
            permissions="author",
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
            permissions="authenticated",  # Permiso de autenticación
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
            permissions="public"
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
        self.public_post = BlogPost.objects.create(title="Public Post", content="Public content", permissions="public", author=self.user_authenticated)

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
            if post.permissions == 'public':
                allowed_likes.append(like)

        # Asegurándonos de que el like público está en la lista de likes permitidos
        self.assertIn(self.like_public, allowed_likes)
        self.assertEqual(len(allowed_likes), 1)  # Solo un like debe ser retornado

    def test_get_likes_for_no_public_post(self):
        # Crear un post con otro permiso
        private_post = BlogPost.objects.create(title="Private Post", content="Private content", permissions="authenticated", author=self.user_authenticated)
        like_private = Like.objects.create(blog_post=private_post, user=self.user_authenticated)

        # Simulando la vista con un usuario autenticado
        request = MagicMock()
        request.user = self.user_authenticated

        # Filtrar likes basados en la lógica de la vista
        all_likes = Like.objects.all()
        allowed_likes = []
        
        for like in all_likes:
            post = like.blog_post
            if post.permissions == 'public':
                allowed_likes.append(like)

        # Asegurándonos de que el like de un post privado no esté en la lista de likes permitidos
        self.assertNotIn(like_private, allowed_likes)
        self.assertEqual(len(allowed_likes), 1)  # Solo el like del post público debe ser retornado



class LikeListViewTest(TestCase):

    def setUp(self):
        # Crear usuarios
        self.user_authenticated = User.objects.create_user(username="authenticated_user", password="password")
        
        # Crear un post con permisos autenticados
        self.auth_post = BlogPost.objects.create(title="Authenticated Post", content="Authenticated content", permissions="authenticated", author=self.user_authenticated)

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
            if post.permissions == 'authenticated' and request.user.is_authenticated:
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
            if post.permissions == 'authenticated' and request.user.is_authenticated:
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
        self.team_post = BlogPost.objects.create(title="Team Post", content="Team content", permissions="team", author=self.user_authenticated)

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
            if post.permissions == 'team' and request.user.groups.filter(id=post.author.groups.first().id).exists():
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
            if post.permissions == 'team' and request.user.groups.filter(id=post.author.groups.first().id).exists():
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
        self.author_post = BlogPost.objects.create(title="Author Post", content="Author content", permissions="author", author=self.user_authenticated)

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
            if post.permissions == 'author' and request.user == post.author:
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
            if post.permissions == 'author' and request.user == post.author:
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

    def test_post_pagination(self):
        # Hacer una solicitud GET a la vista de posts
        response = self.client.get('/api/posts/')  # Cambia la URL según tu configuración

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_pages', response.data)
        self.assertIn('current_page', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # Verificar que el número de resultados por página sea 10
        self.assertEqual(len(response.data['results']), 10)  # Como en tu paginator, la página debe tener 10 resultados por defecto
        
        # Verificar que 'total_pages' sea al menos 3 (25 posts / 10 por página)
        self.assertGreaterEqual(response.data['total_pages'], 3)

    def test_post_pagination_custom_page_size(self):
        # Hacer una solicitud GET con un tamaño de página personalizado
        response = self.client.get('/api/posts/?page_size=5')  # Cambiar el tamaño de la página a 5

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # La página ahora debe tener 5 resultados



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
        response = self.client.get('/api/likes/')  # Ajusta la URL correcta para tu API
        self.assertEqual(len(response.data['results']), 20)  # Espera 20 resultados por página

    def test_like_pagination_custom_page_size(self):
        response = self.client.get('/api/likes/?page_size=10')  # Página con tamaño 10
        self.assertEqual(len(response.data['results']), 10)  # Espera 10 resultados por página



class CommentPaginationTest(APITestCase):
    def setUp(self):
        # Crear usuarios y posts para asociar con los comentarios
        self.user = User.objects.create_user(username="testuser", password="password")
        self.post = BlogPost.objects.create(title="Post for Comments", content="Content", author=self.user)
        
        # Crear varios comentarios para el post
        for i in range(25):  # Crear 25 comentarios
            Comment.objects.create(blog_post=self.post, user=self.user, content=f"Comment {i}")

    def test_comment_pagination(self):
        # Hacer una solicitud GET a la vista de comentarios
        response = self.client.get('/api/comments/')  # Cambia la URL según tu configuración

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_pages', response.data)
        self.assertIn('current_page', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        # Verificar que el número de resultados por página sea 10
        self.assertEqual(len(response.data['results']), 10)  # Como en tu paginator, la página debe tener 10 resultados por defecto
        
        # Verificar que 'total_pages' sea al menos 3 (25 comentarios / 10 por página)
        self.assertGreaterEqual(response.data['total_pages'], 3)

    def test_comment_pagination_custom_page_size(self):
        # Hacer una solicitud GET con un tamaño de página personalizado
        response = self.client.get('/api/comments/?page_size=5')  # Cambiar el tamaño de la página a 5

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # La página ahora debe tener 5 resultados


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
            'permissions': 'public'
        }

        serializer = BlogPostSerializer(data=data)

        # El serializador debe fallar la validación
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), {'title'})


class LikeSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.blog_post = BlogPost.objects.create(
            title="Test Post",
            content="Test content",
            author=self.user,
            permissions="public"
        )
        self.like = Like.objects.create(blog_post=self.blog_post, user=self.user)

    def test_like_serialization(self):
        # Serializar el objeto Like
        serializer = LikeSerializer(self.like)

        # Verificar que los datos serializados coinciden con los del objeto
        expected_data = {
            'id': self.like.id,
            'user': self.user.username,  # Se debe mostrar el nombre de usuario
            'blog_post': self.blog_post.title,  # Se debe mostrar el título del post
        }

        self.assertEqual(serializer.data, expected_data)


class CommentSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.blog_post = BlogPost.objects.create(
            title="Test Post",
            content="Test content",
            author=self.user,
            permissions="public"
        )
        self.comment = Comment.objects.create(
            blog_post=self.blog_post,
            user=self.user,
            content="This is a comment"
        )

    def test_comment_serialization(self):
        # Serializar el objeto Comment
        serializer = CommentSerializer(self.comment)

        # Verificar que los datos serializados coinciden con los del objeto
        expected_data = {
            'id': self.comment.id,
            'blog_post': self.blog_post.id,  # ID del blog post
            'user': self.user.username,  # Nombre del usuario
            'content': "This is a comment",
            'timestamp': self.comment.timestamp.strftime("%Y-%m-%d %H:%M:%S"),  # Formato de fecha
            'post_title': self.blog_post.title  # Título del post
        }

        self.assertEqual(serializer.data, expected_data)
