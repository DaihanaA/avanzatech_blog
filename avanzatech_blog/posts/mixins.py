from django.db.models import Q
from rest_framework import mixins
from .models import BlogPost


class QuerysetMixin(mixins.ListModelMixin):


    def get_queryset_for_authenticated_users(self):
        """
        Retorna el queryset para usuarios autenticados basándose en permisos desde modelos relacionados.
        """
        user = self.request.user
        teams = user.groups.first()  # Obtén todos los grupos asociados al usuario
        
        # Depurar: Imprimir los equipos del usuario
        print(f"Equipos del usuario: {teams.name}")
        
        # Construir filtros basados en permisos
        query_author = Q(author=user, post_inverse__category__categoryName='AUTHOR', 
                         post_inverse__permission__permissionName__in=['EDIT', 'READ_ONLY'])
        
        query_team = Q(team__name__in=teams.name, 
                       post_inverse__category__categoryName='TEAM', 
                       post_inverse__permission__permissionName__in=['EDIT', 'READ_ONLY']) & ~Q(author=user)
        
        query_authenticated = ~Q(team__name__in=teams.name) & Q(
            post_inverse__category__categoryName='AUTHENTICATED',
            post_inverse__permission__permissionName__in=['EDIT', 'READ_ONLY']
        )
        # Agregar filtro para posts públicos
        query_public = Q(post_inverse__category__categoryName='PUBLIC', 
                        post_inverse__permission__permissionName__in=['EDIT', 'READ_ONLY'])
        
        # Combina las consultas
        query = query_author | query_team | query_authenticated | query_public
        queryset = BlogPost.objects.filter(query).prefetch_related(
                    'post_inverse__category', 'post_inverse__permission', 'author', 'team'
                ).order_by('-timestamp')

        # Depurar: Imprimir la consulta y los resultados
        #print(f"Consulta para usuarios autenticados: {queryset.query}")
        print(f"Posts encontrados: {queryset.count()}")

        return queryset

    def get_queryset_for_public(self):
        query = Q(post_inverse__category__categoryName='PUBLIC', 
                  post_inverse__permission__permissionName__in=['EDIT', 'READ_ONLY'])
        
        # Depurar: Verificar la consulta
        queryset = BlogPost.objects.filter(query).prefetch_related('post_inverse__category', 'post_inverse__permission')
        
        # Depurar: Imprimir la consulta y los resultados
        #print(f"Consulta para posts públicos: {queryset.query}")
        #print(f"Posts públicos encontrados: {queryset.count()}")
        
        return queryset.order_by('-timestamp')
    
    def get_queryset(self):
        """
        Sobrescribe `get_queryset` para decidir dinámicamente según el usuario.
        """
        user = self.request.user

        # Primero comprobamos si el usuario es un superusuario
        if user.is_superuser:
            return BlogPost.objects.all()  # Para superusuarios, muestra todos los posts

        # Si no es superusuario pero está autenticado
        if user.is_authenticated:
            return self.get_queryset_for_authenticated_users()  # Para usuarios autenticados

        # Para usuarios no autenticados, mostramos solo posts públicos
        return self.get_queryset_for_public()
