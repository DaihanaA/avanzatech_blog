from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import  read_and_edit
from .paginators import PageNumberPagination,LikePagination,CommentPagination,PostPagination
from .serializers import BlogPostSerializer, CommentSerializer, LikeSerializer
from .models import BlogPost, Like,Comment
from .mixins import QuerysetMixin
from rest_framework.response import Response
from rest_framework import status
from .filters import LikeFilter, CommentFilter
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import models
from django.http import Http404
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import redirect

# class PostViewSet(ModelViewSet):
#     queryset = BlogPost.objects.all()
#     serializer_class = BlogPostSerializer
#     permission_classes = [read_and_edit]
#     pagination_class = PostPagination
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['author', 'id']
    

#     def get_queryset(self):
#         user = self.request.user

#         # Usuarios no autenticados solo pueden ver posts públicos
#         queryset = BlogPost.objects.filter(permissions='public')

#         if user.is_authenticated:
#             # Filtrar por permisos 'authenticated', 'author', y 'team'
#             queryset |= BlogPost.objects.filter(
#                 Q(permissions='authenticated') | 
#                 Q(author=user)
#             )

#             if user.groups.exists():
#                 queryset |= BlogPost.objects.filter(permissions='team', author__groups__in=user.groups.all())

#         return queryset.distinct()

#     def get_object(self):
#         queryset = self.get_queryset()
#         obj = queryset.filter(pk=self.kwargs["pk"]).first()
#         if obj is None:
#             raise Http404("El post no se encuentra o no tienes permiso para verlo.")
#         return obj

    
#     # def perform_create(self, serializer):
#     #     if not self.request.user.is_authenticated:
#     #         raise NotAuthenticated("Debes estar autenticado para crear un post.")
#     #     serializer.save(author=self.request.user)
        

    
#     # def perform_create_and_redirect(self, serializer):
#     #     post = serializer.save(author=self.request.user)  # Guardamos el post
#     #     return redirect(f"/new-post/{post.id}/")  # Redirigimos a otro endpoint

#     @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='create')
#     def create_post(self, request):
#         """Crear un nuevo post a través de este endpoint"""
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             # Establecer el autor como el usuario autenticado
#             serializer.save(author=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated],serializer_class=LikeSerializer)
#     def toggle_like(self, request, pk=None):
#         """
#         Acción personalizada para alternar entre like y dislike en un post.
#         """
#         user = request.user
#         post = self.get_object()

#         # Verificar si el usuario ya dio like al post
#         existing_like = Like.objects.filter(user=user, blog_post=post).first()

#         if existing_like:
#             # Si existe un like, eliminarlo (dislike)
#             existing_like.delete()
#             return Response({"message": "Dislike realizado"}, status=status.HTTP_200_OK)
#         else:
#             # Si no existe, crear un nuevo like
#             Like.objects.create(user=user, blog_post=post)
#             return Response({"message": "Like realizado"}, status=status.HTTP_201_CREATED)


#     @action(detail=False, methods=['get'],permission_classes=[read_and_edit], serializer_class=LikeSerializer)
#     def likes(self, request):
#         """Obtenemos los likes de un post específico con filtros y paginación."""
#         post = self.get_object()  # Obtener el post correspondiente
#         likes = post.like_entries.all()  # Obtener todos los likes asociados con el post

#         # # Aplicar el filtro LikeFilter
#         # user_id = request.query_params.get('id', None)
#         # if user_id:
#         #     likes = LikeFilter.filter(user__id=user_id)

#         # Paginación
#         paginator = LikePagination()
#         paginated_likes = paginator.paginate_queryset(likes, request)

#         # Serialización
#         serializer = LikeSerializer(paginated_likes, many=True)

#         # Respuesta paginada
#         return paginator.get_paginated_response(serializer.data)
    
#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], serializer_class=CommentSerializer)
#     def add_comment(self, request, pk=None):
#         """Agregar un comentario a un post"""
#         post = self.get_object()  # Obtener el post correspondiente
        

#         # Validar y serializar el comentario
#         serializer = CommentSerializer(data=request.data,context={'post': post})
#         if serializer.is_valid():
#             # Establecer el autor del comentario como el usuario autenticado
#             serializer.save(user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], serializer_class=CommentSerializer)
#     def comments(self, request):
#         """
#         Retorna todos los comentarios de los posts a los que el usuario tiene acceso.
#         """
#         user = request.user

#         # Obtener los posts accesibles para el usuario
#         accessible_posts = BlogPost.objects.filter(
#             Q(permissions='public') |
#             Q(permissions='authenticated') |
#             Q(author=user)
#         )

#         if user.groups.exists():
#             accessible_posts |= BlogPost.objects.filter(
#                 permissions='team',
#                 author__groups__in=user.groups.all()
#             )

#         # Obtener los parámetros de filtrado (author, id) de la consulta
#         author_id = request.query_params.get('author', None)
#         post_id = request.query_params.get('id', None)

#         # Filtrar comentarios por 'author' o 'id' si están presentes en los parámetros
#         comments = Comment.objects.filter(blog_post__in=accessible_posts)

#         if author_id:
#             comments = comments.filter(user__id=author_id)

#         if post_id:
#             comments = comments.filter(blog_post__id=post_id)

#         # Paginación
#         paginator = CommentPagination()
#         paginated_comments = paginator.paginate_queryset(comments, request)

#         # Serialización
#         serializer = CommentSerializer(paginated_comments, many=True)

#         # Respuesta paginada
#         return paginator.get_paginated_response(serializer.data)
        

#     @action(detail=True, methods=['get'], url_path='comments/(?P<comment_id>\d+)', serializer_class=CommentSerializer)
#     def retrieve_comment(self, request, pk=None, comment_id=None):
#         """Obtener un comentario específico de un post"""
#         post = self.get_object()
#         comment = get_object_or_404(post.comments, id=comment_id)
#         serializer = CommentSerializer(comment)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
#     @action(detail=True, methods=['delete'], url_path='comments/(?P<comment_id>\d+)/delete',serializer_class=CommentSerializer)
#     def delete_comment(self, request, pk=None, comment_id=None):
#         """Eliminar un comentario de un post específico"""
#         post = self.get_object()
#         comment = post.comments.filter(id=comment_id).first()

#         if not comment:
#             return Response({"detail": "Comentario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

#         if comment.user != request.user:
#             raise PermissionDenied("No tienes permiso para eliminar este comentario.")

#         comment.delete()
#         return Response({"detail": "Comentario eliminado exitosamente."}, status=status.HTTP_204_NO_CONTENT)


# class LikeViewSet(ModelViewSet):
#     """
#     ViewSet para manejar los likes con soporte de filtros y paginación.
#     """
#     serializer_class = LikeSerializer
#     pagination_class = LikePagination
#     permission_classes = [read_and_edit]
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['user', 'blog_post']

#     def get_queryset(self):
#         user = self.request.user

#         # Obtener todos los posts accesibles al usuario
#         accessible_posts = BlogPost.objects.filter(
#             Q(permissions='public') |
#             Q(permissions='authenticated', author=user) |
#             Q(author=user)
#         )

#         if user.groups.exists():
#             accessible_posts |= BlogPost.objects.filter(
#                 permissions='team',
#                 author__groups__in=user.groups.all()
#             )

#         # Filtrar likes solo de los posts accesibles
#         return Like.objects.filter(blog_post__in=accessible_posts).distinct()
        
# class CommentViewSet(ModelViewSet):
#     """
#     ViewSet para manejar los comentarios con soporte de filtros y paginación.
#     """
#     serializer_class = CommentSerializer
#     pagination_class = CommentPagination
#     permission_classes = [read_and_edit]
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['user', 'blog_post', 'created_at', 'content']

#     def get_queryset(self):
#         user = self.request.user
        
#         # Obtener todos los posts accesibles al usuario
#         accessible_posts = BlogPost.objects.filter(
#             Q(permissions='public') |
#             Q(permissions='authenticated', author=user) |
#             Q(author=user)
#         )

#         if user.groups.exists():
#             accessible_posts |= BlogPost.objects.filter(
#                 permissions='team',
#                 author__groups__in=user.groups.all()
#             )

#         # Filtrar comentarios solo de los posts accesibles
#         return Comment.objects.filter(blog_post__in=accessible_posts).distinct()


# class AllCommentsView(ModelViewSet):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['user', 'blog_post', 'created_at', 'content']
#     permission_classes = [read_and_edit]

# class AllLikesView(ModelViewSet):
#     queryset = Like.objects.all()
#     serializer_class = LikeSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['user', 'blog_post']
#     permission_classes = [read_and_edit]

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import BlogPost
from .serializers import BlogPostSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.exceptions import ValidationError 

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import BlogPost
from .serializers import BlogPostSerializer
from rest_framework import generics
from rest_framework.generics import DestroyAPIView, RetrieveUpdateAPIView,ListCreateAPIView,ListAPIView
from django.db.models import Count
from rest_framework.exceptions import NotFound
from .paginators import PostPagination,LikePagination,CommentPagination

class PostListView(APIView):
    """
    Vista para listar los posts, incluyendo el conteo de comentarios en cada post.
    Solo los posts accesibles según los permisos del usuario autenticado o anónimo.
    """
    permission_classes = [read_and_edit]

    def get(self, request):
        user = request.user
        
        # Verificar si el usuario está autenticado
        if user.is_authenticated:
            # Filtrar los posts según los permisos para usuarios autenticados
            posts = BlogPost.objects.filter(
                Q(permissions='public') |  # Posts públicos
                Q(permissions='authenticated') |  # Posts para usuarios autenticados
                Q(author=user) |  # Posts del autor
                Q(permissions='team') & Q(author__groups__in=user.groups.all())  # Posts de su equipo
            ).annotate(comment_count=Count('comments'))  # Contar los comentarios relacionados
        else:
            # Si el usuario no está autenticado, solo mostrar los posts públicos
            posts = BlogPost.objects.filter(
                Q(permissions='public')
            ).annotate(comment_count=Count('comments'))  # Contar los comentarios

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
        
# class BlogPostLikeView(APIView):
#     """
#     Vista para dar like a un post.
#     """
#     permission_classes = [read_and_edit]

#     def post(self, request, post_id):
#         # Obtener el post o devolver un 404 si no existe
#         post = get_object_or_404(BlogPost, id=post_id)
        
#         # Verificar si el usuario ya le ha dado like
#         if request.user in post.likes.all():
#             # Si ya le dio like, eliminar el like
#             post.likes.remove(request.user)
#             message = "Like removed"
#         else:
#             # Si no le dio like, agregar el like
#             post.likes.add(request.user)
#             message = "Like added"
        
#         post.save()
        # return Response({'message': message, 'likes_count': post.likes.count()}, status=status.HTTP_200_OK)
    
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

        return Response(response_data)

    # Crear un comentario en el post
    def create(self, request, pk=None):
        post = get_object_or_404(BlogPost, id=pk)

        # Crear el comentario con los datos proporcionados en la solicitud
        comment_data = request.data
        comment_data['blog_post'] = post.id
        comment_data['user'] = request.user.id  # Asociar el comentario con el usuario autenticado

        # Serializar el comentario
        comment_serializer = CommentSerializer(data=comment_data)

        if comment_serializer.is_valid():
            comment_serializer.save()
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
        return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
# class CommentViewSet(viewsets.ModelViewSet):
#     serializer_class = CommentSerializer

#     def get_queryset(self):
#         post = self.kwargs['post_id']
#         return Comment.objects.filter(blog_post=post)

#     def perform_create(self, serializer):
#         post = BlogPost.objects.get(id=self.kwargs['post_id'])
#         serializer.save(blog_post=post)
        

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
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [read_and_edit]  # Ajusta según sea necesario
    paginator_class = CommentPagination

    # Solo los comentarios
    def get_queryset(self):
        return Comment.objects.all()
    
class PostCommentsView(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [read_and_edit]

    def get_queryset(self):
        post = self.kwargs['post_id']
        return Comment.objects.filter(blog_post=post)

    def perform_create(self, serializer):
        post = BlogPost.objects.get(id=self.kwargs['post_id'])
        serializer.save(blog_post=post)
        
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

class LikeListView(ListAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [read_and_edit]  # Ajusta según sea necesario
    pagination_class =  LikePagination

    # Solo los comentarios
    def get_queryset(self):
        return Like.objects.all()
    
class PostLikeView(ListCreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]  # Ajusta según tus necesidades de permisos

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Like.objects.filter(blog_post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = BlogPost.objects.get(id=post_id)  # Obtener el post específico
        # Verificar si el usuario ya dio "like" al post
        existing_like = Like.objects.filter(user=self.request.user, blog_post=post).first()
        if existing_like:
            # Si el like ya existe, eliminarlo (dislike)
            existing_like.delete()
            return Response({"detail": "Dislike realizado correctamente."}, status=status.HTTP_204_NO_CONTENT)
        # Si no ha dado "like" antes, proceder con la creación
        serializer.save(user=self.request.user, blog_post=post)  # Cambié "author" por "user"
        return Response(serializer.data, status=status.HTTP_201_CREATED)