import csv
import os

from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingridient


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def create_ingredients(self, row):
        return Ingridient(name=row[0], measurement_unit=row[1])

    def import_data(self, reader, object_creator):
        for row in reader:

            try:
                obj = object_creator(row)
                obj.save()
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR('Невозможно импортировать. ' + repr(e))
                )

                continue

    def handle(self, *args, **options):
        filename_to_creator_function = {
            'ingredients.csv': self.create_ingredients,
        }

        csv_file = options['csv_file']

        try:

            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)

                try:
                    filename = os.path.basename(csv_file)
                    object_creator = filename_to_creator_function[filename]
                except KeyError:
                    raise CommandError(f'Не найден файл "{filename}"')

                self.import_data(reader, object_creator)

        except Exception as e:

            raise CommandError(f'Невозможно открыть файл: {str(e)}')

        self.stdout.write(self.style.SUCCESS('Дата успешно импортирована'))
