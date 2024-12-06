from rest_framework import serializers
from .models import BlogPost, Like, Comment
from django.contrib.auth.models import Group


class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    comment_count = serializers.IntegerField(read_only=True)
    excerpt = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = ['id','title','content','excerpt','timestamp','permissions','team','author','comment_count',]
        read_only_fields = ['author']
        
        
    def get_likes(self, obj):
        """Obtiene la lista de usuarios que dieron like al post."""
        return obj.likes.values_list('user__username', flat=True)  # Devuelve solo los nombres de usuario
    
    def get_excerpt(self, obj):
        # Calcula los primeros 200 caracteres del contenido
        return obj.content[:200]
    
    def get_team(self, obj):
        # Obtener el primer grupo del autor
        groups = obj.author.groups.all()
        if groups.exists():
            return groups.first().name  # Retorna el nombre del primer grupo
        return "No Group"


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Para mostrar el nombre del usuario
    blog_post = serializers.StringRelatedField()  # Para mostrar el título del post
    
    class Meta:
        model = Like
        fields  = ['id', 'user', 'blog_post']
        

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Devuelve el nombre de usuario (puedes usar otro campo)
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")  # Formato de la fecha
    post_title = serializers.CharField(source='blog_post.title', read_only=True)  # Título del post

    class Meta:
        model = Comment
        fields = ['id', 'blog_post', 'user', 'content', 'timestamp', 'post_title']
        read_only_fields = ['user', 'blog_post', 'timestamp']  # 'user' es solo lectura
        
    def create(self, validated_data):
        # Se asegura de que el campo 'user' se asigna si no se pasa
        user = self.context['request'].user  # Obtiene el usuario autenticado
        return Comment.objects.create(user=user, **validated_data)
