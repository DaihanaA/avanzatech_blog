from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from rest_framework.pagination import LimitOffsetPagination


class PostPagination(LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        # Obtener el parámetro 'limit' y 'offset' desde la consulta de la URL
        limit = int(request.query_params.get('limit', 10))  # Default limit 10
        offset = int(request.query_params.get('offset', 0))  # Default offset 0
        
        # Aplicar el límite y el desplazamiento al queryset
        self.request = request
        paginated_queryset = queryset[offset: offset + limit]
        
        # Paginación manual para los metadatos
        self.count = queryset.count()
        self.limit = limit
        self.offset = offset
        self.total_pages = (self.count // limit) + (1 if self.count % limit else 0)

        return paginated_queryset

    def get_paginated_response(self, data):
    # Check if there is a next page
        next_link = self.get_next_link()
        if not next_link:  # If there is no next link, it should be None
            next_link = None
        
        return Response({
            'count': self.count,
            'total_pages': self.total_pages,
            'current_page': self.offset // self.limit + 1,
            'page_size': self.limit,
            'next': next_link,  # Ensure it's None if no next link
            'previous': self.get_previous_link(),
            'results': data
        })



class LikePagination(LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        # Obtener el parámetro 'limit' y 'offset' desde la consulta de la URL
        limit = int(request.query_params.get('limit', 2))  # Default limit 20
        offset = int(request.query_params.get('offset', 0))  # Default offset 0
        
        # Aplicar el límite y el desplazamiento al queryset
        self.request = request
        paginated_queryset = queryset[offset: offset + limit]
        
        # Paginación manual para los metadatos
        self.count = queryset.count()
        self.limit = limit
        self.offset = offset
        self.total_pages = (self.count // limit) + (1 if self.count % limit else 0)

        return paginated_queryset

    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
            'total_pages': self.total_pages,
            'current_page': self.offset // self.limit + 1,  # Calcular la página actual basada en el offset
            'page_size': self.limit,  # Usar el limit como el tamaño de la página
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

        
class CommentPagination(LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        # Obtener los parámetros 'limit' y 'offset' desde la URL
        limit = int(request.query_params.get('limit', 5))  # Default limit 10
        offset = int(request.query_params.get('offset', 0))  # Default offset 0
        
        # Aplicar el límite y el desplazamiento al queryset
        self.request = request
        paginated_queryset = queryset[offset: offset + limit]
        
        # Paginación manual para los metadatos
        self.count = queryset.count()
        self.limit = limit
        self.offset = offset
        self.total_pages = (self.count // limit) + (1 if self.count % limit else 0)

        return paginated_queryset

    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
            'total_pages': self.total_pages,
            'current_page': self.offset // self.limit + 1,  # Calcular la página actual basada en el offset
            'page_size': self.limit,  # Usar el limit como el tamaño de la página
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })