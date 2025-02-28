from rest_framework import serializers
from .models import BlogPost, Like, Comment
from django.contrib.auth.models import Group


class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    comment_count = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    # 🔥 Campos de permisos correctamente configurados
    public_permission = serializers.ChoiceField(choices=BlogPost._meta.get_field('public_permission').choices)
    authenticated_permission = serializers.ChoiceField(choices=BlogPost._meta.get_field('authenticated_permission').choices)
    team_permission = serializers.ChoiceField(choices=BlogPost._meta.get_field('team_permission').choices)
    
    # ❌ Corregido: `author_permission` debería ser un `CharField`, no un `SerializerMethodField`
    author_permission = serializers.CharField(default="READ_EDIT",read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'content', 'author', 'comment_count', 'excerpt',
            'team', 'likes_count', 'liked_by_user', 'public_permission',
            'authenticated_permission', 'team_permission', 'author_permission', 'timestamp'
        ]
        read_only_fields = ['author']

    def __init__(self, *args, **kwargs):
        """ Evita importaciones circulares """
        super().__init__(*args, **kwargs)
        from .serializers import CommentSerializer  
        self.fields['comments'] = CommentSerializer(source='comments_set', many=True, read_only=True)    

    def get_likes(self, obj):
        return list(obj.likes.values_list('user__username', flat=True))  

    def get_excerpt(self, obj):
        """Muestra los primeros 200 caracteres"""
        return obj.content[:200]
    
    def get_team(self, obj):
        """Obtiene el grupo del autor"""
        groups = obj.author.groups.all()
        return groups.first().name if groups.exists() else "No Group"
    
    def get_likes_count(self, obj):
        return obj.likes.count()  
    
    def get_liked_by_user(self, obj):
        user = self.context['request'].user
        return obj.likes.filter(id=user.id).exists() if user.is_authenticated else False

    def get_comment_count(self, obj):
        """Cuenta los comentarios correctamente"""
        return obj.comments_set.count()  

  

class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    blog_post = serializers.StringRelatedField()
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    
    class Meta:
        model = Like
        fields  = ['id', 'user', 'blog_post', 'timestamp']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    post_title = serializers.CharField(source='blog_post.title', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'blog_post', 'user', 'content', 'timestamp', 'post_title']
        read_only_fields = ['user', 'blog_post', 'timestamp', 'post_title']
        
    def create(self, validated_data): 
        return Comment.objects.create(**validated_data)
    
