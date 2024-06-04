import psycopg2
from psycopg2 import sql, IntegrityError, extensions

# Datenbankverbindungsinformationen
DATABASE = {
    'dbname': 'reservierung_db',
    'user': 'postgres',
    'password': '***',
    'host': '127.0.0.1',
    'port': '5432'
}
#In Production get connection parameters from CI/CD Pipeline

def truncate_tables():
    conn = None
    cursor = None
    try:
        # Verbindung zur Datenbank herstellen
        conn = psycopg2.connect(
            dbname=DATABASE['dbname'],
            user=DATABASE['user'],
            password=DATABASE['password'],
            host=DATABASE['host'],
            port=DATABASE['port']
        )
        cursor = conn.cursor()

        # SQL-Befehl zum Bereinigen der Tabellen
        truncate_query = sql.SQL("""
        TRUNCATE TABLE tische, kunden, reservierungen RESTART IDENTITY CASCADE;
        """)

        # SQL-Befehl ausführen
        cursor.execute(truncate_query)
        conn.commit()
        print("Tabellen erfolgreich bereinigt.")

    except Exception as e:
        print(f"Fehler beim Bereinigen der Tabellen: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    truncate_tables()
