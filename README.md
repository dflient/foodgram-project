# praktikum_new_diplom
Домен - https://isfoodgram.hopto.org/
Логин - Superuser
Пароль - 51nersineR

Foodgram - это, интернет-сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Автор проекта - Даниил Пастунов.

Стек технологий:

Python
Django
Django REST Framework
PostgreSQL
Docker
Docker-compose

Для локального запуска:

1. Перейти в папку с проектом infra "cd infra"
2. Создать в папке infra файл .env и указать свои данные для полей, напримере .env_example
3. Запустить команду "docker-compose up --build"
4. Выполнить миграции "docker-compose exec backend python manage.py migrate"
5. Собрать статику "docker-compose exec backend python manage.py collectstatic"
6. Наплнить список ингредиентов "docker-compose exec backend python manage.py importcsv data/ingredients.csv"
7. Создать администратора "docker-compose exec backend python manage.py createsuperuser" и заполнить теги