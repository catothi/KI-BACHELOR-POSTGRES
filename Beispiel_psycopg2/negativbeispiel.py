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



# Beispiel einer unsicheren Methode zum Löschen einer Zeile (SQL-Injection)
def abfrage(user_input):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM test_table WHERE name = '" + user_input + "'"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    print("Result Abfrage:", result)



def main():
    #user_input = "Bob"
    #user_input = "Bob'; select * from test_table; --"
    #user_input = "Bob'; select * from pg_stats; --"
    user_input = "Bob'; drop table ABC; --"
    print("\nAttempting SQL Injection (insecure method)...")
    abfrage(user_input)

  

if __name__ == "__main__":
    main()
