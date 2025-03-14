from django.db.models import F

from recipes.models import Recipes


def create_M2M_recipe_field(
        recipe: Recipes, ingredient_id_amount: list) -> None:
    for ingredient in ingredient_id_amount:
        recipe.ingredients.add(
            ingredient.get('id'),
            through_defaults={'amount': ingredient.get('amount')})


def get_shopping_list(recipes: list[Recipes]) -> str:
    shopping_list = 'Список покупок:\n'
    data = dict()
    for recipe in recipes:
        ingredients = recipe.ingredientinrecipe.annotate(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit')).all()
        for ingredient in ingredients:
            key = f'{ingredient.name} ({ingredient.unit}) - '
            data[key] = data.get(key, 0) + ingredient.amount
    shopping_list += '\n'.join('\t' + k + str(v) for k, v in data.items())
    return shopping_list
