from Blog.pagination import CustomPageNumberPagination, get_response


class ArticlePaginator(CustomPageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 15

    def get_paginated_response(self, data):
        return get_response('data', data, self.page.paginator.count)

