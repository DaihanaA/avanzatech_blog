import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from posts.models import BlogPost, Comment, Like


class UserFactory(DjangoModelFactory):
    """Factory para crear usuarios."""
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpassword')


class BlogPostFactory(DjangoModelFactory):
    """Factory para crear posts."""
    class Meta:
        model = BlogPost

    title = factory.Sequence(lambda n: f"Post {n}")
    content = "Contenido de prueba."
    author = factory.SubFactory(UserFactory)
    permissions = "public"  # Puede ser "public", "authenticated" o "author"


class CommentFactory(DjangoModelFactory):
    """Factory para crear comentarios."""
    class Meta:
        model = Comment

    content = "Comentario de prueba."
    blog_post = factory.SubFactory(BlogPostFactory)
    user = factory.SubFactory(UserFactory)


class LikeFactory(DjangoModelFactory):
    """Factory para crear likes."""
    class Meta:
        model = Like

    blog_post = factory.SubFactory(BlogPostFactory)
    user = factory.SubFactory(UserFactory)
