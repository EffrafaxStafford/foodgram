from rest_framework.pagination import PageNumberPagination


class UsersRecipePagination(PageNumberPagination):
    """Класс для пагинации пользователей, подписок и рецептов."""

    page_size = 6
    page_size_query_param = 'limit'
