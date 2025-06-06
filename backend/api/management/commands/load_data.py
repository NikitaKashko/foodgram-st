import json
from django.core.management.base import BaseCommand
from api.models import Ingredient


class Command(BaseCommand):
    """
    Management command to load ingredients data from a JSON file.
    Usage: python manage.py load_data
    """
    help = 'Load ingredients data from data/ingredients.json'

    def handle(self, *args, **kwargs):

        file_path = 'data/ingredients.json'
        self.stdout.write(self.style.NOTICE(
            f'Starting to load ingredients from {file_path}...'))

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            ingredients_to_create = []

            existing_ingredients = set(
                Ingredient.objects.values_list('name', 'measurement_unit')
            )

            for item in data:
                name = item.get('name')
                measurement_unit = item.get('measurement_unit')

                if not name or not measurement_unit:
                    self.stdout.write(self.style.WARNING(
                        f"Skipping invalid item: {item}"))
                    continue

                if (name, measurement_unit) in existing_ingredients:
                    continue

                ingredients_to_create.append(
                    Ingredient(name=name, measurement_unit=measurement_unit)
                )

                existing_ingredients.add((name, measurement_unit))

            if ingredients_to_create:
                Ingredient.objects.bulk_create(ingredients_to_create)
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully loaded {len(ingredients_to_create)} new'
                    'ingredients.'
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    'All ingredients are already up to date.'
                ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'File not found: {file_path}. '
                'Make sure the data folder with ingredients.json is in the'
                'backend root directory.'
            ))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(
                f'Error decoding JSON from {file_path}. Please check if the'
                'file is a valid JSON.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'An unexpected error occurred: {e}'))
