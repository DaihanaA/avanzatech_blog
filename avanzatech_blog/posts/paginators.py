from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PostPagination(PageNumberPagination):
    page_size = 10  # 10 elementos por página
    page_size_query_param = 'page_size'  # Permite que los usuarios cambien el tamaño de la página
    max_page_size = 100  # Tamaño máximo de la página
    
    def get_paginated_response(self, data):
        # Calcula el número total de páginas
        total_pages = self.page.paginator.num_pages
        current_page = self.page.number
        
        return Response({
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'current_page': current_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class LikePagination(PageNumberPagination):
    page_size = 20  # 20 elementos por página
    page_size_query_param = 'page_size'  # Permite que los usuarios cambien el tamaño de la página
    max_page_size = 100  # Tamaño máximo de la página
    
    def get_paginated_response(self, data):
        # Calcula el número total de páginas
        total_pages = self.page.paginator.num_pages
        current_page = self.page.number
        
        return Response({
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'current_page': current_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
        
class CommentPagination(PageNumberPagination):
    page_size = 10  # Puedes cambiar este número según tus necesidades
    page_size_query_param = 'page_size'
    max_page_size = 100  # El número máximo de comentarios que pueden mostrarse por página

    def get_paginated_response(self, data):
        # Calcula el número total de páginas
        total_pages = self.page.paginator.num_pages
        current_page = self.page.number
        
        return Response({
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'current_page': current_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })