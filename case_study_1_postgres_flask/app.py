from flask import Flask, request, jsonify, make_response
import psycopg2
from psycopg2 import sql, IntegrityError, extensions
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Database connection

# Hinweis: Das Passwort in Produktion per CI/CD Pipeline setzen
# In Windows set DB_PASSWORD=dein_passwort in cmd , in Linux Shell export DB_PASSWORD=dein_passwort
def get_db_connection():
    db_password = os.getenv('DB_PASSWORD')
    if db_password is None:
        raise ValueError("Das Datenbankpasswort wurde nicht als Umgebungsvariable gesetzt.")
    conn = psycopg2.connect(
        dbname='reservierung_db',
        user='postgres',
        password=db_password,
        host='localhost',
        port='5432'
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
    return conn

# Error handler for 400 Bad Request
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({"message": "Bad Request", "details": str(error)}), 400)

# Error handler for 409 Conflict
@app.errorhandler(409)
def conflict(error):
    return make_response(jsonify({"message": "Conflict", "details": str(error)}), 409)

# User Story 1: Create tables
@app.route('/api/v1/tische', methods=['POST'])
def create_table():
    data = request.json

    # Überprüfung der Eingabedaten
    if not data or 'kapazitaet' not in data or 'tischnummer' not in data:
        return bad_request("kapazitaet and tischnummer are required fields")

    kapazitaet = data['kapazitaet']
    tischnummer = data['tischnummer']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tische (kapazitaet, tischnummer) VALUES (%s, %s) RETURNING TID",            (kapazitaet, tischnummer))
        pk = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
    except IntegrityError:
        conn.rollback()
        cursor.close()
        conn.close()
        return conflict("Dieser Tisch existiert bereits")
    except Exception as e:
        return bad_request(str(e))

    return jsonify({'Primary Key in DB': pk}), 201

# User Story 2: Add new reservation
#Hinweis Prüfung ob Tisch zu dieser Zeit noch frei ist und Kapa hat nicht implementiert
@app.route('/api/v1/reservierungen', methods=['POST'])
def add_reservation():
    data = request.json

    required_fields = ['tid', 'personenzahl', 'reservierungsdatum', 'reservierungsuhrzeit', 'nachname', 'vorname', 'telefon']

    if not all(field in data for field in required_fields):
        return bad_request("tid, personenzahl, reservierungsdatum, and reservierungsuhrzeit are required fields")

    tid = data['tid']
    personenzahl = data['personenzahl']
    reservierungsdatum = data['reservierungsdatum']
    reservierungsuhrzeit = data['reservierungsuhrzeit']
    nachname = data['nachname']
    vorname = data['vorname']
    telefon = data['telefon']
    kommentar = data.get('kommentar', '')

    try:
        conn = get_db_connection()
        conn.set_isolation_level(extensions.ISOLATION_LEVEL_SERIALIZABLE)
        cursor = conn.cursor()

        # Ensure TID exists
        cursor.execute("SELECT TID FROM tische WHERE TID = %s", (tid,))
        if cursor.fetchone() is None:
            return bad_request("The provided TID does not exist")

        # Ensure customer exists or create it
        cursor.execute("SELECT KID FROM kunden WHERE nachname = %s AND telefon = %s", (nachname, telefon))
        existing_customer = cursor.fetchone()

        if existing_customer:
            kid = existing_customer[0]
        else:
            cursor.execute(
                "INSERT INTO kunden (nachname, vorname, telefon) VALUES (%s, %s, %s) RETURNING KID",
                (nachname, vorname, telefon)
            )
            kid = cursor.fetchone()[0]

        # Insert the reservation
        cursor.execute(
            """
            INSERT INTO reservierungen (TID, KID, status, kommentar, personenzahl, reservierungsdatum, reservierungsuhrzeit) 
            VALUES (%s, %s, 'active', %s, %s, %s, %s) RETURNING RID
            """,
            (tid, kid, kommentar, personenzahl, reservierungsdatum, reservierungsuhrzeit)
        )
        rid = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()
    except IntegrityError as e:
        conn.rollback()
        return bad_request("Integrity error: " + str(e))
    except Exception as e:
        conn.rollback()
        return bad_request(str(e))

    response_data = {
        'KID': kid,
        'RID': rid,
        'reservierungsuhrzeit': reservierungsuhrzeit
    }

    return jsonify(response_data), 201

# User Story 3: Cancel reservation
@app.route('/api/v1/reservierungen/<int:rid>', methods=['DELETE'])
def cancel_reservation(rid):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Reservierungen WHERE RID = %s",
            (rid,)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return bad_request(str(e))

    return jsonify({'message': 'Reservation cancelled'}), 200

# User Story 4: Modify reservation
@app.route('/api/v1/reservierungen/<int:rid>', methods=['PUT'])
def modify_reservation(rid):
    data = request.json
    if not data or 'tid' not in data or 'kid' not in data or 'status' not in data or 'kommentar' not in data:
        return bad_request("tid, kid, status, and kommentar are required fields")

    tid = data['tid']
    kid = data['kid']
    status = data['status']
    kommentar = data['kommentar']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Reservierungen SET TID = %s, KID = %s, status = %s, kommentar = %s WHERE RID = %s",
            (tid, kid, status, kommentar, rid)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return bad_request(str(e))

    return jsonify({'message': 'Reservation modified'}), 200

# User Story 5: Display occupancy for the next 7 days
@app.route('/api/v1/auslastung_7_tage', methods=['GET'])
def auslastung_7_tage():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Calculate the number of reserved persons for the next 7 days using a window function
        query = """
            SELECT
                SUM(personenzahl) AS total_people
            FROM
                reservierungen
            WHERE
                status = 'active'
                AND reservierungsdatum BETWEEN CURRENT_DATE AND CURRENT_DATE + interval '7 days';
        """

        cursor.execute(query)
        result = cursor.fetchone()

        personenzahl = {'total_people': result[0]}

        cursor.close()
        conn.close()
    except Exception as e:
        return bad_request(str(e))

    return jsonify(personenzahl), 200

if __name__ == '__main__':
    app.run(debug=False)
