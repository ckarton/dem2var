import psycopg2

try:
    # Подключаемся к базе данных
    conn = psycopg2.connect(
        dbname="mydb",
        user="postgres",
        password="123",
        host="localhost"
    )
    print("Подключение успешно!")

    # Создаем курсор
    cur = conn.cursor()

    # Проверяем список таблиц
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    print("\nСписок таблиц:")
    for table in tables:
        print(table[0])

    # Проверяем содержимое таблицы materials
    print("\nПроверяем таблицу materials:")
    cur.execute("SELECT COUNT(*) FROM materials")
    count = cur.fetchone()
    print(f"Количество записей: {count[0]}")

    # Проверяем первую запись
    cur.execute("SELECT * FROM materials LIMIT 1")
    first_row = cur.fetchone()
    print(f"Первая запись: {first_row}")

    # Закрываем соединение
    cur.close()
    conn.close()
    print("\nСоединение закрыто")

except Exception as e:
    print(f"Ошибка: {str(e)}") 