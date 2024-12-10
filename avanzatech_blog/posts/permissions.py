from rest_framework import permissions

class read_and_edit(permissions.BasePermission):
    
    def has_permission(self, request, view):
        # Solo los usuarios autenticados pueden crear posts, likes y comentarios
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):

        # Permitir acceso total a superusuarios
        if request.user.is_superuser:
            return True
        
        #permiso de los post
        if hasattr(obj, 'permissions'):
            # Permisos de lectura (SAFE_METHODS)
            if request.method in permissions.SAFE_METHODS:
                if obj.permissions == 'public':
                    return True
                elif obj.permissions == 'authenticated':
                    return request.user.is_authenticated
                elif obj.permissions == 'author':
                    print(f"obj-author{obj.author}")
                    print(f"request-user{request.user}")
                    print(f"user-comparison{obj.author == request.user}")
                    return obj.author == request.user
                elif obj.permissions == 'team':
                    user_group = request.user.groups.first()
                    if user_group:
                        return obj.author.groups.filter(id__in=request.user.groups.values_list('id', flat=True)).exists() ## obj.author.groups == equest.user.groups
                    return False

            # Permisos de edición o eliminación (PUT, PATCH, DELETE)
            elif request.method in ['PUT', 'PATCH', 'DELETE']:
                # Permitir si es el autor
                if obj.author == request.user :
                    return True
                
                # Permitir si es del mismo equipo (team)
                user_group = request.user.groups.first()
                if user_group:
                    return obj.author.groups.filter(id=user_group.id).exists()

                return False

        #permiso de los likes y los comentarios
        if hasattr(obj, 'post'):
            
            if request.method in permissions.SAFE_METHODS:
                if obj.post.permissions == 'public':
                    return True
                elif obj.post.permissions == 'authenticated':
                    return request.user.is_authenticated
                elif obj.post.permissions == 'author':
                    return obj.author == request.user
                elif obj.post.permissions == 'team':
                    user_group = request.user.groups.first()
                    if user_group:
                        return obj.author.groups.filter(id=user_group.id).exists()
                    return False

            # Permitir si el usuario es el autor del comentario o es superusuario
            #return obj.user == request.user or request.user.is_superuser
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                if obj.user == request.user:
                    return True
            
                user_group = request.user.groups.first()
                if user_group:
                    return obj.author.groups.filter(id=user_group.id).exists()

                return False
        # Por defecto, denegar acceso si no es BlogPost ni Comment
        return False