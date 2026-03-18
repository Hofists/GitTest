import sqlite3
import csv
import os

def export_table_to_csv(conn, table_name, output_dir='.'):
    """
    Экспортирует содержимое таблицы table_name в CSV-файл.
    """
    cursor = conn.cursor()
    # Получаем данные таблицы
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    if not rows:
        print(f"Таблица {table_name} пуста.")
        return

    # Получаем названия столбцов
    column_names = [description[0] for description in cursor.description]

    # Формируем имя файла
    csv_file = os.path.join(output_dir, f"{table_name}.csv")

    # Запись в CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)  # числа без кавычек, остальное в кавычках
        writer.writerow(column_names)  # заголовок
        writer.writerows(rows)

    print(f"Таблица {table_name} экспортирована в {csv_file} (записей: {len(rows)})")

def main():
    # Подключение к базе данных (укажите свой путь к файлу)
    db_path = 'jokes.db'  # измените при необходимости
    if not os.path.exists(db_path):
        print(f"Ошибка: файл базы данных {db_path} не найден.")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # для удобного доступа к именам столбцов

    # Получаем список всех таблиц (кроме системных)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]

    if not tables:
        print("В базе данных нет таблиц.")
        return

    print(f"Найдены таблицы: {', '.join(tables)}")

    # Создаём папку для CSV, если её нет
    output_dir = 'csv_exports'
    os.makedirs(output_dir, exist_ok=True)

    # Экспортируем каждую таблицу
    for table in tables:
        export_table_to_csv(conn, table, output_dir)

    conn.close()
    print("Готово!")

if __name__ == "__main__":
    main()
