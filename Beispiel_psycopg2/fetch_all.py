import psycopg

# Verbindung zur Datenbank herstellen
conn = psycopg.connect("dbname=test user=postgres password=secret")
conn.autocommit = True

# Cursor-Objekt erstellen
cur = conn.cursor()

# SQL-Abfrage ausführen
cur.execute("SELECT * FROM my_table")

# Alle verbleibenden Zeilen abrufen
rows = cur.fetchall()
for row in rows:
    print(row)

# Cursor schließen
cur.close()

# Verbindung schließen
conn.close()