from recipes.models import Recipes


def create_M2M_recipe_field(
        recipe: Recipes, ingredient_id_amount: list) -> None:
    for ingredient in ingredient_id_amount:
        recipe.ingredients.add(
            ingredient.get('id'),
            through_defaults={'amount': ingredient.get('amount')})
