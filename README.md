# Система управления производством "Образ Плюс"
pip install -r requirements.txt
## Требования

-   Python 3.7 или выше
-   PostgreSQL 12 или выше

## Установка

1. Установите PostgreSQL, если еще не установлен:

    - Скачайте и установите PostgreSQL с официального сайта: https://www.postgresql.org/download/
    - При установке запомните пароль для пользователя postgres

2. Создайте базу данных:

    - Откройте pgAdmin или psql
    - Создайте новую базу данных с именем `furniture_db`
    - Выполните SQL-скрипт из файла `sql.txt`

3. Установите зависимости Python:

```bash
pip install -r requirements.txt
```

## Запуск приложения

1. Убедитесь, что PostgreSQL запущен и база данных создана

2. Запустите приложение:

```bash
python app.py
```

## Настройка подключения к базе данных

Если необходимо изменить параметры подключения к базе данных, отредактируйте следующие параметры в файле `app.py`:

```python
self.connection = psycopg2.connect(
    dbname="furniture_db",
    user="postgres",
    password="123Qwe",
    host="localhost"
)
```

## Структура проекта

-   `app.py` - основной файл приложения
-   `sql.txt` - SQL-скрипт для создания базы данных
-   `requirements.txt` - зависимости Python
-   `Образ плюс.ico` - иконка приложения
