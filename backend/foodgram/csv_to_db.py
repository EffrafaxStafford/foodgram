import csv
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')

application = get_wsgi_application()

from recipes.models import Ingredients


def del_model_data(model):
    """Удаляет данные в модели."""
    model.objects.all().delete()


def read_csv(filename):
    """Считывает данные из csv и возвращает список строк таблицы."""
    path = os.path.join('../data', filename)
    with open(path, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        return list(reader)


def load_ingredients_data():
    """Загрузка данных в модель Ingredients."""
    filename = 'ingredients.csv'
    for row in read_csv(filename):
        Ingredients.objects.get_or_create(name=row[0], measurement_unit=row[1])


if __name__ == '__main__':
    del_model_data(Ingredients)
    load_ingredients_data()
