from django.db import models
from django.contrib.auth.models import User,Group
#from users.models import Profile


class BlogPost(models.Model):
    
    PUBLIC = 'public'
    AUTHENTICATED = 'authenticated'
    AUTHOR = 'author'
    TEAM = 'team'

    PERMISSIONS = [
        (PUBLIC, 'Public'),
        (AUTHENTICATED, 'Authenticated'),
        (AUTHOR, 'Author'),
        (TEAM, 'Team'),
       
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    
        # Permisos de lectura y edición
    permissions = models.CharField(
        max_length=15,
        choices=PERMISSIONS,
        default=PUBLIC,
    )

    likes = models.ManyToManyField(
        User,  # Relación con el usuario
        through='Like',  # Usa el modelo intermedio `Like`
        related_name='liked_posts'  # Relación inversa
    )
    comments = models.ManyToManyField(User,through='Comment',related_name='comments')


    @property
    def likes_count(self):
        # Contar cuántos likes tiene el post
        return self.like_entries.count()
    
    def __str__(self):
        return self.title
    
   
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_set')
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments_set')  # Relación inversa
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"Comment by {self.user} on {self.blog_post}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes_given")
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="like_entries")  # Nombre único
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'blog_post')  # Evitar likes duplicados por usuario      

    def __str__(self):
        return f"Liked by {self.user.username} on {self.blog_post.title}"  # Cambiar la coma por un return directo
