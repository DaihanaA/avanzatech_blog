from rest_framework import viewsets
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import  read_and_edit
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


class PostListView(APIView):
    """
    Vista para listar los posts, incluyendo el conteo de comentarios en cada post.
    Solo los posts accesibles según los permisos del usuario autenticado o anónimo.
    """
    permission_classes = [read_and_edit]

    def get(self, request):
        user = request.user
        
        posts = BlogPost.objects.all()

        # Filtrar según permisos
        if user.is_authenticated:
            posts = posts.filter(
                Q(permissions='public') |
                Q(permissions='authenticated') |
                (Q(permissions='author') & Q(author=user)) |
                (Q(permissions='team') & Q(author__groups__in=user.groups.all()))
            )
        else:
            posts = posts.filter(permissions='public')

        posts = posts.annotate(comment_count=Count('comments')).order_by('-timestamp')


        # Paginación
        paginator = PostPagination()
        result_page = paginator.paginate_queryset(posts, request)
        
        # Serializar los posts
        serializer = BlogPostSerializer(result_page, many=True)
        
        # Retornar respuesta paginada
        return paginator.get_paginated_response(serializer.data)

class BlogPostCreateViewSet(viewsets.ModelViewSet):
    """
    Vista para crear un nuevo post.
    Solo usuarios autenticados pueden crear posts.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados pueden crear posts

    def perform_create(self, serializer):
        # Establecer el autor como el usuario autenticado
        serializer.save(author=self.request.user)
        

    
class PostDetailViewSet(viewsets.ModelViewSet):
    """
    Vista para obtener detalles de un post y agregar comentarios.
    """
    permission_classes = [read_and_edit]  # Solo usuarios autenticados pueden acceder

    # Configurar el queryset para mostrar los posts
    def get_queryset(self):
        queryset = BlogPost.objects.all()
        return queryset

    # Mostrar los detalles del post, comentarios y likes
    def retrieve(self, request, pk=None):
        post = get_object_or_404(BlogPost, id=pk)

        # Serializar el post
        post_serializer = BlogPostSerializer(post)
        
         # Verificar permisos
        if post.permissions == BlogPost.PUBLIC:
            return Response(BlogPostSerializer(post).data)
        
        # Para posts autenticados, solo usuarios autenticados pueden verlos
        if post.permissions == BlogPost.AUTHENTICATED and not request.user.is_authenticated:
            raise PermissionDenied("You must be authenticated to view this post.")
        
        # Para posts solo del autor, solo el autor puede ver el post
        if post.permissions == BlogPost.AUTHOR and post.author != request.user:
            raise PermissionDenied("You are not the author of this post.")
        
        if post.permissions == BlogPost.TEAM:
            # Verificar si el usuario pertenece al grupo "team_name"
            if not request.user.groups.filter(name='team_name').exists():
                raise PermissionDenied("You must be part of the correct team to view this post.")

            
        # Obtener los comentarios del post
        comments = Comment.objects.filter(blog_post=post)
        comments_serializer = CommentSerializer(comments, many=True)

        # Contar los likes
        likes_count = post.likes.count()
        likes = Like.objects.filter(blog_post=post)
        likes_data = LikeSerializer(likes, many=True).data

        # Preparar la respuesta
        response_data = post_serializer.data
        response_data['likes_count'] = likes_count
        response_data['comments'] = comments_serializer.data
        response_data['likes_data'] = likes_data
        
        return Response(BlogPostSerializer(post).data)


        

class BlogPostDeleteView(DestroyAPIView):
    """
    Vista para borrar un post.
    Solo el autor o el team del post puede borrarlo.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [read_and_edit]
    
class BlogPostUpdateView(RetrieveUpdateAPIView):
    """
    Vista para update un post.
    Solo el autor o el team puede update.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [read_and_edit]
    
    
class CommentListView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [read_and_edit]  
    pagination_class = CommentPagination

    def get_queryset(self):
        """
        Filtra los comentarios basados en los permisos del post asociado.
        """
        # Obtiene todos los comentarios
        all_comments = Comment.objects.all()

        # Filtrar comentarios basados en los permisos del post
        allowed_comments = []
        for comment in all_comments:
            post = comment.blog_post
            if post.permissions == 'public':
                allowed_comments.append(comment)
            elif post.permissions == 'authenticated' and self.request.user.is_authenticated:
                allowed_comments.append(comment)
            elif post.permissions == 'author' and self.request.user == post.author:
                allowed_comments.append(comment)
            elif post.permissions == 'team' and self.request.user.groups.filter(id=post.author.groups.first().id).exists():
                allowed_comments.append(comment)

        # Devuelve el queryset filtrado
        return Comment.objects.filter(id__in=[comment.id for comment in allowed_comments]).order_by('timestamp')

class PostCommentsView(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [read_and_edit]

    def perform_create(self, serializer):
        """
        Verifica los permisos del post antes de permitir la creación del comentario.
        """
        post_id = self.kwargs['post_id']
        try:
            post = BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            raise NotFound("Post not found")

        # Verificar permisos del post antes de crear el comentario
        if post.permissions == 'public':
            serializer.save(blog_post=post, user=self.request.user)
        elif post.permissions == 'authenticated' and self.request.user.is_authenticated:
            serializer.save(blog_post=post, user=self.request.user)
        elif post.permissions == 'author' and self.request.user == post.author:
            serializer.save(blog_post=post, user=self.request.user)
        elif post.permissions == 'team' and self.request.user.groups.filter(id=post.author.groups.first().id).exists():
            serializer.save(blog_post=post, user=self.request.user)
        else:
            raise PermissionDenied("You do not have permission to comment on this post.")



        
class CommentDeleteView(APIView):
    permission_classes = [read_and_edit]  # Asegurarse de que el usuario esté autenticado

    def delete(self, request, comment_id):
        try:
            # Intentamos obtener el comentario por su id
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise NotFound("Comentario no encontrado.")
        
        # Verificamos si el usuario que hace la solicitud es el autor del comentario
        if comment.user != request.user:  # Cambié 'author' por 'user'
            raise PermissionDenied("No tienes permiso para eliminar este comentario.")
        
        # Si pasa la verificación, eliminamos el comentario
        comment.delete()
        return Response({"detail": "Comentario eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)


    
from rest_framework.permissions import BasePermission

class LikeListView(ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [read_and_edit]  # Permisos generales para la vista
    pagination_class = LikePagination

    def get_queryset(self):
        """
        Filtra los likes basados en los permisos del post asociado.
        """
        # Obtiene todos los likes
        all_likes = Like.objects.all()

        # Filtrar likes basados en los permisos del post
        allowed_likes = []
        for like in all_likes:
            post = like.blog_post
            if post.permissions == 'public':
                allowed_likes.append(like)
            elif post.permissions == 'authenticated' and self.request.user.is_authenticated:
                allowed_likes.append(like)
            elif post.permissions == 'author' and self.request.user == post.author:
                allowed_likes.append(like)
            elif post.permissions == 'team' and self.request.user.groups.filter(id=post.author.groups.first().id).exists():
                allowed_likes.append(like)

        # Devuelve el queryset filtrado
        return Like.objects.filter(id__in=[like.id for like in allowed_likes]).order_by('timestamp')



from django.db import IntegrityError

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from posts.models import Like, BlogPost

class PostLikeView(APIView):
    permission_classes = [read_and_edit]  

    def post(self, request, *args, **kwargs):
        """
        Agrega un 'like' a un post si el usuario tiene permisos.
        """
        post_id = self.kwargs['post_id']
        try:
            post = BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            raise NotFound("Post not found")

        # Verificar permisos antes de agregar el like
        if post.permissions == 'public':
            return self._add_like(post)
        elif post.permissions == 'authenticated' and self.request.user.is_authenticated:
            return self._add_like(post)
        elif post.permissions == 'author' and self.request.user == post.author:
            return self._add_like(post)
        elif post.permissions == 'team' and self.request.user.groups.filter(id=post.author.groups.first().id).exists():
            return self._add_like(post)
        else:
            raise PermissionDenied("You do not have permission to like this post.")

    def delete(self, request, *args, **kwargs):
        """
        Elimina un 'like' de un post si el usuario lo había dado previamente.
        """
        post_id = self.kwargs['post_id']
        try:
            post = BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            raise NotFound("Post not found")

        # Verificar si el usuario ya ha dado like al post
        like = Like.objects.filter(user=self.request.user, blog_post=post).first()
        
        if like:
            like.delete()
            return Response({"detail": "Like removed successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "You have not liked this post yet."}, status=status.HTTP_400_BAD_REQUEST)

    def _add_like(self, post):
        """
        Función auxiliar para agregar un like a un post.
        """
        # Verificar si el usuario ya ha dado like al post
        existing_like = Like.objects.filter(user=self.request.user, blog_post=post).first()
        
        if existing_like:
            return Response({"detail": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el like
        Like.objects.create(blog_post=post, user=self.request.user)
        return Response({"detail": "Like added successfully."}, status=status.HTTP_201_CREATED)
