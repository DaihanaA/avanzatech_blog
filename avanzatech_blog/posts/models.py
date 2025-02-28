from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Permissions(models.TextChoices):
    READ = 'READ', 'Read'
    READ_EDIT = 'READ_EDIT', 'Read and Edit'
    NONE = 'NONE', 'None'


class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    public_permission = models.CharField(
        max_length=10,
        choices=[(Permissions.NONE, 'None'), (Permissions.READ, 'Read')],  # Nunca READ_EDIT
        default=Permissions.READ
    )
    authenticated_permission = models.CharField(
        max_length=15,
        choices=Permissions.choices,
        default=Permissions.READ
    )
    # 🔥 author_permission NO debe ser un campo editable, siempre es READ_EDIT
    team_permission = models.CharField(
        max_length=15,
        choices=Permissions.choices,
        default=Permissions.READ_EDIT
    )
    
     # El autor siempre tiene READ_EDIT (sin opción de cambio)
    author_permission = models.CharField(
        max_length=15, choices=[(Permissions.READ_EDIT, 'Read and Edit')], default=Permissions.READ_EDIT, editable=False
    )

    likes = models.ManyToManyField(
        User,
        through='Like',
        related_name='liked_posts'
    )
    comments = models.ManyToManyField(
        User,
        through='Comment',
        related_name='comments'
    )

    def clean(self):
        """🔥 Validar la jerarquía de permisos"""
        super().clean()  # Llamar validaciones estándar de Django

        if self.team_permission == Permissions.NONE:
            if self.authenticated_permission != Permissions.NONE or self.public_permission != Permissions.NONE:
                raise ValidationError(
                    "Si 'team_permission' es 'NONE', 'authenticated_permission' y 'public_permission' también deben ser 'NONE'."
                )

        if self.authenticated_permission == Permissions.READ_EDIT and self.team_permission != Permissions.READ_EDIT:
            raise ValidationError(
                "'authenticated_permission' no puede ser 'READ_EDIT' si 'team_permission' no lo es."
            )

        if self.public_permission == Permissions.READ and self.authenticated_permission == Permissions.NONE:
            raise ValidationError(
                "'public_permission' no puede ser 'READ' si 'authenticated_permission' es 'NONE'."
            )

    def save(self, *args, **kwargs):
        """🔥 Establecer permisos del autor antes de guardar"""
        self.clean()
        super().save(*args, **kwargs)

    def author_permission(self):
        """🔥 El autor siempre tiene 'READ_EDIT'"""
        return Permissions.READ_EDIT

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_set')
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments_set')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.blog_post}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes_given")
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="like_entries")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog_post')  # Evitar likes duplicados por usuario

    def __str__(self):
        return f"Liked by {self.user.username} on {self.blog_post.title}"
