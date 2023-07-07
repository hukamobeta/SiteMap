import sqlite3
import csv

conn = sqlite3.connect('site_map.db')
cursor = conn.cursor()

sites = [
    ('http://crawler-test.com/', 'crawler_test', 'crawler-test.com'),
    ('http://google.com/', 'google', 'google.com'),
    ('https://vk.com', 'vk', 'vk.com'),
    ('https://dzen.ru', 'dzen', 'dzen.ru'),
    ('https://stackoverflow.com', 'stackoverflow', 'stackoverflow.com')
]

for site_url, site_name, temp_name in sites:
    table_name = site_name
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            processing_time REAL,
            num_links INTEGER,
            filename TEXT
        )
    ''')

    csv_filename = f"{temp_name}_sitemap.csv"


    with open(csv_filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:
            url = row[0]
            processing_time = float(row[1])
            num_links = int(row[2])
            filename = row[3]

            cursor.execute(f"INSERT INTO '{table_name}' (url, processing_time, num_links, filename) VALUES (?, ?, ?, ?)",
                           (url, processing_time, num_links, filename))


conn.commit()
conn.close()
