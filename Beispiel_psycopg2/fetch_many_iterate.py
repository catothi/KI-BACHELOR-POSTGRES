import psycopg

# Verbindung zur PostgreSQL-Datenbank herstellen
conn = psycopg.connect("dbname=test user=postgres password=***")

# Cursor-Objekt erstellen
cur = conn.cursor()

# SQL-Abfrage definieren und ausführen
cur.execute("SELECT * FROM my_table")

# itersize (z. B. 500 – typischer Wert für große Datenmengen)
size = 10

# Schleife zum sukzessiven Abrufen der Daten
while True:
    rows = cur.fetchmany(size)
    if not rows:
        break

    # Anzahl der abgerufenen Zeilen ausgeben
    print(f"{len(rows)} Zeilen abgerufen")

    # Verarbeite die abgerufenen Zeilen (z. B. ausgeben)
    for row in rows:
        print(row)

# Verbindung schließen
cur.close()
conn.close()