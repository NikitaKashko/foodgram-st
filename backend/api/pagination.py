from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class to use 'limit' as the page size query parameter.
    """
    page_size_query_param = 'limit'
