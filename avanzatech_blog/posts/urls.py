from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (PostListView,
                    BlogPostCreateViewSet, 
                    PostDetailViewSet,
                    BlogPostDeleteView, 
                    BlogPostUpdateView,
                    CommentListView, PostCommentsView,
                    LikeListView, PostLikeView,
                    CommentDeleteView)

# Configuración del DefaultRouter para los detalles de los posts
router = DefaultRouter()
#router.register('posts/(?P<post_id>\d+)/', PostDetailViewSet, basename='post-detail')
#router.register(r'comments/(?P<post_id>\d+)/', CommentViewSet, basename='post-comments')

urlpatterns = [
    # Endpoint para listar los posts
    path('posts/', PostListView.as_view(), name='post-list'),   
    # Endpoint para crear un nuevo post
    path('posts/create/', BlogPostCreateViewSet.as_view({'post': 'create'}), name='post-create'),  
    # Endpoint para los detalles del post
    path('posts/<int:pk>/', PostDetailViewSet.as_view({'get': 'retrieve'}), name='post-detail'), # Esto se usa para obtener detalles del post
    #Endpoint para borrar un post
    path('posts/<int:pk>/delete/', BlogPostDeleteView.as_view(), name='post-delete'),
    path('posts/<int:pk>/update/', BlogPostUpdateView.as_view(), name='post-update'),
    path('comments/', CommentListView.as_view(), name='comment-list'),
    path('comments/<int:post_id>/', PostCommentsView.as_view(), name='post-comment-create'),
    path('likes/', LikeListView.as_view(), name='like-list'),
    path('likes/<int:post_id>/', PostLikeView.as_view(), name='post-like'),
    path('comments/<int:comment_id>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
]+router.urls
