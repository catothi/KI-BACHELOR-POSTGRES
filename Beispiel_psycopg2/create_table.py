import psycopg2

# Funktion zur Herstellung der Datenbankverbindung
def get_db_connection():
    conn = psycopg2.connect(
        dbname='injectiondemo',
        user='postgres',
        password='***',
        host='localhost',
        port='5432'
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
    return conn

# Funktion zum Erstellen einer Testtabelle und Einfügen von Beispieldaten
def create_test_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        )
    """)
    conn.commit()
    cursor.execute("INSERT INTO test_table (name) VALUES ('Alice')")
    cursor.execute("INSERT INTO test_table (name) VALUES ('Bob')")
    conn.commit()
    cursor.close()
    conn.close()





def main():
    create_test_table()
    print("Test Table and Sample Data Created.")

   

  

if __name__ == "__main__":
    main()
