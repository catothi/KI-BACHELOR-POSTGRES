import psycopg

def main():
    # Verbindung herstellen (host ggf. anpassen)
    conn = psycopg.connect("dbname=test user=postgres password=secret host=localhost")
    conn.autocommit = True

    with conn.cursor() as cur:
        # Tabelle droppen und neu anlegen
        cur.execute("DROP TABLE IF EXISTS my_table")
        cur.execute("""
            CREATE TABLE my_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                alter INTEGER,
                stadt VARCHAR(100)
            )
        """)

        # 50 Beispiel-Daten
        daten = [
            ("Anna Schmidt", 28, "Berlin"),
            ("Max Mueller", 35, "Hamburg"),
            ("Lisa Weber", 42, "Muenchen"),
            ("Tom Fischer", 31, "Koeln"),
            ("Sarah Meyer", 29, "Frankfurt"),
            ("Jonas Braun", 30, "Stuttgart"),
            ("Laura Becker", 27, "Duesseldorf"),
            ("David Wolf", 39, "Hannover"),
            ("Nina Vogel", 26, "Bremen"),
            ("Lucas Brandt", 45, "Leipzig"),
            ("Mia Hartmann", 33, "Dortmund"),
            ("Felix Klein", 37, "Essen"),
            ("Eva Lehmann", 24, "Nuremberg"),
            ("Paul Richter", 50, "Dresden"),
            ("Marie Neumann", 32, "Bochum"),
            ("Simon Schmitt", 40, "Wuppertal"),
            ("Julia Hoffmann", 29, "Bielefeld"),
            ("Leon Krueger", 41, "Bonn"),
            ("Sophie Zimmer", 22, "Mannheim"),
            ("Tim Schafer", 38, "Karlsruhe"),
            ("Clara Scholz", 34, "Freiburg"),
            ("Jan Seidel", 36, "Augsburg"),
            ("Lina Walter", 30, "Wiesbaden"),
            ("Tobias Kuhn", 43, "Gelsenkirchen"),
            ("Emily Maier", 25, "Moenchengladbach"),
            ("Julian Werner", 27, "Braunschweig"),
            ("Melanie Lorenz", 31, "Kiel"),
            ("Moritz Busch", 48, "Aachen"),
            ("Frida Lang", 37, "Chemnitz"),
            ("Patrick Fuchs", 28, "Halle"),
            ("Kathrin Graf", 39, "Magdeburg"),
            ("Sandra Frank", 35, "Freiburg"),
            ("Martin Peters", 46, "Erfurt"),
            ("Elisa Berger", 23, "Mainz"),
            ("Dennis Albrecht", 40, "Rostock"),
            ("Helene Jansen", 36, "Saarbruecken"),
            ("Kevin Kraus", 33, "Potsdam"),
            ("Sina Engel", 24, "Oldenburg"),
            ("Nico Lorenz", 28, "Heidelberg"),
            ("Claudia Busch", 29, "Luebeck"),
            ("Alexander Klein", 31, "Reutlingen"),
            ("Daniela Schröder", 34, "Osnabrueck"),
            ("Moritz Wagner", 38, "Ingolstadt"),
            ("Carla Neumann", 29, "Jena"),
            ("Florian Zimmer", 40, "Cottbus"),
            ("Heike Scholz", 26, "Wuerzburg"),
            ("Marcel Günther", 33, "Siegen"),
            ("Petra Wolf", 27, "Erlangen"),
            ("Timo Hartmann", 35, "Paderborn"),
        ]

        cur.executemany(
            "INSERT INTO my_table (name, alter, stadt) VALUES (%s, %s, %s)",
            daten
        )

    print("Tabelle my_table erstellt und 50 Datensätze eingefügt.")
    conn.close()

if __name__ == "__main__":
    main()