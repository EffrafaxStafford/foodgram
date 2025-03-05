from rest_framework.pagination import PageNumberPagination


class UsersPagination(PageNumberPagination):
    """Класс для пагинации страниц."""

    page_size = 10
    page_size_query_param = 'limit'
