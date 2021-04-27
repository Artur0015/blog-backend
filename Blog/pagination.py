from django.core.paginator import Paginator, InvalidPage
from django.utils.functional import cached_property
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPaginator(Paginator):
    """Custom paginator which make queries for count without unneeded joins"""

    def __init__(self, raw_queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_queryset = raw_queryset

    @cached_property
    def count(self):
        return self.raw_queryset.count()


class CustomPageNumberPagination(PageNumberPagination):
    """Custom drf paginator which provides to django paginator raw_queryset"""
    django_paginator_class = CustomPaginator

    """+raw_queryset im comparison with PageNumberPagination's paginate_queryset"""

    def paginate_queryset(self, raw_queryset, queryset, request, view=None):
        """Paginate a queryset if required, either returning a
                page object, or `None` if pagination is not configured for this view."""
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(raw_queryset, queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)


def get_response(field_name, data, count):
    return Response({
        field_name: data,
        'count': count
    })


class PaginateWithRawQueryset:
    """Provides raw_queryset to drf paginator"""

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(self.raw_queryset, queryset, self.request, view=self)
