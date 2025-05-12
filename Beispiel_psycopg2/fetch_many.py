import psycopg

# Verbindung zur Datenbank herstellen
conn = psycopg.connect("dbname=test user=postgres password=***")
# autocommit ist in psycopg3 standardmäßig aktiviert, daher nicht notwendig

# Cursor-Objekt erstellen
cur = conn.cursor()

# SQL-Abfrage ausführen
cur.execute("SELECT * FROM my_table")

# Eine bestimmte Anzahl von Zeilen abrufen
rows = cur.fetchmany(size=5)
for row in rows:
    print(row)

# Cursor schließen
cur.close()

# Verbindung schließen
conn.close()