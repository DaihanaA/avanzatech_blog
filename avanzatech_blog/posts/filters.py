import django_filters
from .models import Comment, Like



class CommentFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name="user__username", label="User Name")
    post_title = django_filters.CharFilter(field_name='blog_post__title', lookup_expr='icontains', label='Post Title')
    blog_post_id = django_filters.NumberFilter(field_name='blog_post', lookup_expr='id')
    
    class Meta:
        model = Comment
        fields = ['user', 'post_title']
        
class LikeFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name="user__username", label="User Name")

    class Meta:
        model = Like
        fields = ['user']
        