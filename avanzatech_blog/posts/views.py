from rest_framework import viewsets
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from .models import Permissions  # Add this line to import Permissions
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .paginators import LikePagination,CommentPagination,PostPagination
from .serializers import BlogPostSerializer, CommentSerializer, LikeSerializer
from .models import BlogPost, Like,Comment
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import models
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import DestroyAPIView, RetrieveUpdateAPIView,ListAPIView, CreateAPIView
from django.db.models import Count
from rest_framework.exceptions import NotFound


from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import BlogPost
from .serializers import BlogPostSerializer

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all().order_by('-timestamp')
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticated]  # Solo usuarios autenticados pueden crear posts

    def perform_create(self, serializer):
        """ 🔥 Asigna automáticamente el usuario autenticado como autor """
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        """ 📌 Personaliza la respuesta al crear un post """
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Blog post creado con éxito!",
            "post": response.data
        }, status=response.status_code)


from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import BlogPost
from .serializers import BlogPostSerializer
from .paginators import PostPagination
from .permissions import BlogPostPermission  # Importamos la clase de permisos

class PostListView(APIView):
    """
    Vista para listar los posts basados en los permisos definidos en `BlogPostPermission`.
    """
    permission_classes = [BlogPostPermission]
    pagination_class = PostPagination

    def get(self, request):
        user = request.user
        is_authenticated = user.is_authenticated

        # 🔹 Filtros basados en permisos
        filters = Q(public_permission='READ')  # Usuarios anónimos solo ven posts públicos

        if is_authenticated:
            filters |= Q(authenticated_permission__in=['READ', 'READ_EDIT'])  # 🔥 Agregado 'READ_EDIT'
            filters |= Q(author=user)  # El autor siempre puede ver su post
            filters |= Q(team_permission__in=['READ', 'READ_EDIT'], author__groups__in=user.groups.all())


        # 🔹 Filtrar posts en la base de datos
        posts = BlogPost.objects.filter(filters).annotate(
            comment_count=Count('comments'),
            likes_count=Count('like_entries')
        ).distinct().order_by('-timestamp')

        # 🔹 Paginación
        paginator = PostPagination()
        result_page = paginator.paginate_queryset(posts, request)

        # 🔹 Serializar los posts
        serializer = BlogPostSerializer(result_page, many=True, context={'request': request})

        return paginator.get_paginated_response(serializer.data)


class PostDetailViewSet(viewsets.ModelViewSet):
    """
    Vista para obtener detalles de un post y manejar comentarios.
    """
    permission_classes = [BlogPostPermission]  # Aplicar permisos correctamente

    def get_queryset(self):
        """
        Retorna solo los posts a los que el usuario tiene acceso.
        """
        user = self.request.user
        posts = BlogPost.objects.all()

        # Aplicar permisos de acceso
        return [post for post in posts if BlogPostPermission().has_object_permission(self.request, self, post)]

    def retrieve(self, request, pk=None):
        """
        Obtener detalles de un post con sus comentarios y likes.
        """
        post = get_object_or_404(BlogPost, id=pk)
        
        # Verificar permisos con DRF
        self.check_object_permissions(request, post)

        # Serializar el post
        post_serializer = BlogPostSerializer(post, context={'request': request})

        # Obtener comentarios y likes
        comments = Comment.objects.filter(blog_post=post)
        comments_serializer = CommentSerializer(comments, many=True)

        likes_count = post.likes.count()
        likes_data = LikeSerializer(Like.objects.filter(blog_post=post), many=True).data

        # Construir respuesta
        response_data = post_serializer.data
        response_data.update({
            'likes_count': likes_count,
            'comments': comments_serializer.data,
            'likes_data': likes_data
        })

        return Response(response_data)
    
    def destroy(self, request, pk=None):
        """
        Eliminar un post si el usuario tiene permisos.
        """
        post = get_object_or_404(BlogPost, id=pk)
        
        # Verificar permisos de eliminación
        self.check_object_permissions(request, post)

        post.delete()
        return Response({'message': 'Post eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)
        



class BlogPostDeleteView(DestroyAPIView):
    """
    Vista para borrar un post.
    Solo el autor o el equipo pueden borrarlo.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [BlogPostPermission]  # Usamos permisos correctos

    def perform_destroy(self, instance):
        # ✅ Verificar permisos con DRF antes de borrar
        self.check_object_permissions(self.request, instance)
        instance.delete()


                
from rest_framework.generics import RetrieveUpdateAPIView
from django.shortcuts import get_object_or_404
from .models import BlogPost
from .serializers import BlogPostSerializer
from .permissions import BlogPostPermission

class BlogPostUpdateView(RetrieveUpdateAPIView):
    """
    Vista para actualizar un post.
    Solo el autor o el equipo pueden editarlo.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [BlogPostPermission]  # Usamos permisos correctos

    def perform_update(self, serializer):
        post = self.get_object()

         # ✅ Verificar permisos con DRF
        self.check_object_permissions(self.request, post)

        serializer.save(author=post.author)  # 🔹 Mantiene el autor original

    
from rest_framework.permissions import AllowAny
from django.db.models import Q
from rest_framework.generics import ListAPIView

class CommentListView(ListAPIView):
    """
    Vista para listar comentarios de posts que el usuario puede ver.
    """
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    permission_classes = [BlogPostPermission]  # 🔥 Permite acceso sin autenticación

    def get_queryset(self):
        """ Retorna solo los comentarios de posts accesibles según permisos. """
        user = self.request.user
        is_authenticated = user.is_authenticated
        post_id = self.request.query_params.get('post_id')

        # 🔹 Filtro base: Posts públicos
        filters = Q(public_permission__in=[Permissions.READ, Permissions.READ_EDIT])

        if is_authenticated:
            filters |= Q(authenticated_permission__in=[Permissions.READ, Permissions.READ_EDIT])  # ✅ Usuarios autenticados
            filters |= Q(author=user)  # ✅ Si el usuario es el autor del post
            filters |= Q(team_permission__in=[Permissions.READ, Permissions.READ_EDIT], 
                         author__groups__id__in=user.groups.values_list("id", flat=True))  # ✅ Si pertenece al equipo

        # 🔹 Obtener posts accesibles
        allowed_posts = BlogPost.objects.filter(filters).distinct()

        # 🔹 Filtrar comentarios de esos posts
        queryset = Comment.objects.filter(blog_post__in=allowed_posts).order_by('timestamp')

        # 🔹 Si se proporciona `post_id`, filtrar aún más
        if post_id:
            queryset = queryset.filter(blog_post__id=post_id)

        return queryset


class PostCommentsView(CreateAPIView):
    """
    Vista para crear un comentario en un post, validando los permisos del usuario.
    """
    serializer_class = CommentSerializer
    permission_classes = [BlogPostPermission]

    def perform_create(self, serializer):
        """
        Verifica los permisos del post antes de permitir la creación del comentario.
        """
        post_id = self.kwargs['post_id']

        # Obtener el post y verificar si existe
        post = BlogPost.objects.select_related('author').filter(id=post_id).first()
        if not post:
            raise NotFound("Post not found")

        user = self.request.user
        is_authenticated = user.is_authenticated

        # Verificar permisos según los campos del modelo
        has_permission = (
            post.public_permission in [Permissions.READ, Permissions.READ_EDIT] or
            (post.authenticated_permission in [Permissions.READ, Permissions.READ_EDIT] and is_authenticated) or
            (post.author == user)  or
            (post.team_permission in [Permissions.READ, Permissions.READ_EDIT] and user.groups.filter(id__in=post.author.groups.values_list('id', flat=True)).exists())
        )

        if not has_permission:
            raise PermissionDenied("You do not have permission to comment on this post.")

        # Guardar comentario si el usuario tiene permisos
        serializer.save(blog_post=post, user=user)

        
class CommentDeleteView(APIView):
    """
    Vista para eliminar un comentario. Solo el autor o un miembro del equipo con permiso 'read_edit' pueden eliminarlo.
    """
    permission_classes = [BlogPostPermission]  

    def delete(self, request, comment_id):
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied("Debes estar autenticado para eliminar un comentario.")

        # 🔹 Buscar el comentario y manejar si no existe
        comment = get_object_or_404(Comment, id=comment_id)

        # 🔹 Permitir eliminación si el usuario es el autor
        if comment.user == user:
            comment.delete()
            return Response({"detail": "Comentario eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)

        # 🔹 Verificar permisos del equipo si existe
        blog_post = comment.blog_post
        if blog_post.team_permission == "read_edit":
            if blog_post.team and user.groups.filter(id=blog_post.team.id).exists():
                comment.delete()
                return Response({"detail": "Comentario eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)

        # ❌ Si no es el autor ni tiene permisos en el equipo, denegar la acción
        raise PermissionDenied("No tienes permiso para eliminar este comentario.")

    


class LikeListView(ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [BlogPostPermission]
    pagination_class = LikePagination

    def get_queryset(self):
        post_id = self.request.query_params.get('post')

        queryset = Like.objects.all().order_by("timestamp")

        if post_id:
            queryset = queryset.filter(blog_post__id=post_id)

        return queryset  # No llamamos paginate_queryset aquí, DRF lo hace automáticamente



from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from posts.models import Like, BlogPost

class PostLikeView(APIView):
    permission_classes = [BlogPostPermission]  

    def post(self, request, *args, **kwargs):
        """
        Agrega un 'like' a un post si el usuario tiene permisos.
        """
        post_id = self.kwargs['post_id']
        user = self.request.user

        if isinstance(user, AnonymousUser):  # 🔹 Verificamos si el usuario no está autenticado
            raise PermissionDenied("You must be logged in to like a post.")

        try:
            post = BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            raise NotFound("Post not found")

        # Verificar permisos antes de agregar el like
        if post.public_permission == Permissions.READ:
            return self._add_like(post)

        if user.is_authenticated:
            if post.authenticated_permission in [Permissions.READ, Permissions.READ_EDIT]:
                return self._add_like(post)

            if user == post.author:
                return self._add_like(post)

            if post.team_permission in [Permissions.READ, Permissions.READ_EDIT] and user.groups.filter(id__in=post.author.groups.values_list("id", flat=True)).exists():
                return self._add_like(post)


        raise PermissionDenied("You do not have permission to like this post.")

    def delete(self, request, *args, **kwargs):
        """
        Elimina un 'like' de un post si el usuario lo había dado previamente.
        """
        post_id = self.kwargs['post_id']
        user = self.request.user

        if isinstance(user, AnonymousUser):  # 🔹 Verificamos si el usuario no está autenticado
            raise PermissionDenied("You must be logged in to remove a like.")

        try:
            post = BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            raise NotFound("Post not found")

        # Verificar si el usuario ya ha dado like al post
        like = Like.objects.filter(user=user, blog_post=post).first()
        
        if like:
            like.delete()
            return Response({"detail": "Like removed successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "You have not liked this post yet."}, status=status.HTTP_400_BAD_REQUEST)

    def _add_like(self, post):
        """
        Función auxiliar para agregar un like a un post.
        """
        user = self.request.user

        # Verificar si el usuario ya ha dado like al post
        existing_like = Like.objects.filter(user=user, blog_post=post).first()
        
        if existing_like:
            return Response({"detail": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el like
        Like.objects.create(blog_post=post, user=user)
        return Response({"detail": "Like added successfully."}, status=status.HTTP_201_CREATED)