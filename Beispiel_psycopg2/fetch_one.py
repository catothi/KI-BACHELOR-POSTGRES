import psycopg2
conn = psycopg2.connect("dbname=test user=postgres password=secret")
conn.autocommit = True
#Cursor-Objekt erstellen
cur = conn.cursor()

cur.execute("SELECT * FROM my_table")

row = cur.fetchone()
print(row)

# Verbindung schließen
conn.close()

# Cursor schließen
cur.close()

