import django_filters
from recipes.models import Favorites, Recipes, ShoppingCart


class RecipeFilterSet(django_filters.FilterSet):
    """Класс для фильтрации рецептов."""

    is_favorited = django_filters.BooleanFilter()
    is_in_shopping_cart = django_filters.BooleanFilter()
    tags = django_filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipes
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    @property
    def qs(self):
        user = self.request.user
        qs = self.queryset
        if self.data:
            tags = self.data.getlist('tags')
            if tags:
                qs = qs.filter(tags__slug__in=tags)
            author = self.data.getlist('author')
            if author:
                qs = qs.filter(author__id__in=map(int, author))

            is_favorited = self.data.get('is_favorited')
            if is_favorited is not None and user.is_authenticated:
                recipes_is_favorited_id = Favorites.objects.filter(
                    user=user, recipe__in=qs).values('recipe_id')
                if is_favorited in ('True', '1'):
                    qs = qs.filter(id__in=recipes_is_favorited_id)
                elif is_favorited in ('False', '0'):
                    qs = qs.exclude(id__in=recipes_is_favorited_id)

            is_in_shopping_cart = self.data.get('is_in_shopping_cart')
            if is_in_shopping_cart is not None and user.is_authenticated:
                recipes_is_in_shopping_cart_id = ShoppingCart.objects.filter(
                    user=user, recipe__in=qs).values('recipe_id')
                if is_in_shopping_cart in ('True', '1'):
                    qs = qs.filter(id__in=recipes_is_in_shopping_cart_id)
                elif is_in_shopping_cart in ('False', '0'):
                    qs = qs.exclude(id__in=recipes_is_in_shopping_cart_id)
        self._qs = qs
        return self._qs
