import psycopg2

try:
    conn = psycopg2.connect(
        dbname="mydb",
        user="postgres",
        password="123",
        host="localhost"
    )
    cursor = conn.cursor()
    
    # Проверяем таблицу materials
    cursor.execute("SELECT COUNT(*) FROM public.materials")
    count = cursor.fetchone()[0]
    print(f"Количество записей в таблице materials: {count}")
    
    # Проверяем соединение с другими таблицами
    cursor.execute("""
        SELECT m.material_name, mt.material_type
        FROM public.materials m
        JOIN public.material_type mt ON m.material_type = mt.material_type
        LIMIT 1
    """)
    result = cursor.fetchone()
    print(f"Первая запись: {result}")
    
    conn.close()
    print("Тест подключения успешен!")
except Exception as e:
    print(f"Ошибка: {str(e)}") 