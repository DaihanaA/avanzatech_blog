from rest_framework import permissions
from .models import BlogPost, Comment, Permissions


class BlogPostPermission(permissions.BasePermission):
    """ Controla el acceso a los posts y comentarios según los permisos definidos """

    def has_object_permission(self, request, view, obj):
        """ Determina si el usuario puede ver o modificar el post o comentario """
        user = request.user
        is_authenticated = user.is_authenticated

        # 🔹 Si el objeto es un BlogPost, aplicar reglas de acceso a posts
        if isinstance(obj, BlogPost):
            is_author = obj.author == user
            # Verificar si el usuario es miembro del mismo equipo que el autor del post
            is_team_member = user.groups.filter(id__in=obj.author.groups.values_list('id', flat=True)).exists()

            # Determinar nivel de permisos según el rol del usuario
            if is_author:
                permission_level = Permissions.READ_EDIT  # El autor siempre tiene permisos completos
            elif is_team_member:
                permission_level = obj.team_permission
            elif not is_authenticated:
                permission_level = obj.public_permission  # Solo permisos públicos si no está autenticado
            else:
                permission_level = obj.authenticated_permission

            # Reglas para métodos seguros (GET)
            if request.method in permissions.SAFE_METHODS:
                # Métodos seguros como GET
                return permission_level in [Permissions.READ, Permissions.READ_EDIT]
            else:
                # Métodos no seguros como POST, PUT, DELETE
                return permission_level == Permissions.READ_EDIT  # Permite edición si tiene el permiso adecuado

        # 🔹 Si el objeto es un Comment, aplicar reglas de acceso a comentarios
        elif isinstance(obj, Comment):
            # Solo el autor del comentario o del post pueden editar o eliminarlo
            return obj.user == user or obj.blog_post.author == user

        return False  # Si no es un objeto válido o no cumple las condiciones, denegar acceso
