from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def paginated_response_type(self, data):
    return Response({
        'count': self.page.paginator.count,
        'articles': data
    })


class ArticlePaginator(PageNumberPagination):
    page_size = 5

    def get_paginated_response(self, data):
        return paginated_response_type(self, data)


class ArticlePaginatorForProfile(PageNumberPagination):
    page_size = 3

    def get_paginated_response(self, data):
        return paginated_response_type(self, data)
