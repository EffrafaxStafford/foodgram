from rest_framework.pagination import PageNumberPagination


class UsersPagination(PageNumberPagination):
    """Класс для пагинации пользователей."""

    page_size = 10
    page_size_query_param = 'limit'


class SubscriptionsPagination(PageNumberPagination):
    """Класс для пагинации подписок."""

    page_size = 10
    page_size_query_param = 'limit'


class RecipesPagination(PageNumberPagination):
    """Класс для пагинации рецептов."""

    page_size = 10
    page_size_query_param = 'limit'