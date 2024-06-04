from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import os
from bson.son import SON

app = Flask(__name__)

# Database connection
def get_db_connection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['reservierung_db']
    return db

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

    if not data or 'kapazitaet' not in data or 'tischnummer' not in data:
        return bad_request("kapazitaet and tischnummer are required fields")

    kapazitaet = data['kapazitaet']
    tischnummer = data['tischnummer']

    db = get_db_connection()
    tische = db.tische

    if tische.find_one({"tischnummer": tischnummer}):
        return conflict("Dieser Tisch existiert bereits")

    table_id = tische.insert_one({
        "kapazitaet": kapazitaet,
        "tischnummer": tischnummer
    }).inserted_id

    return jsonify({'Primary Key in DB': str(table_id)}), 201

# User Story 2: Add new reservation
@app.route('/api/v1/reservierungen', methods=['POST'])
def add_reservation():
    data = request.json

    required_fields = ['tische', 'personenzahl', 'reservierungsdatum', 'reservierungsuhrzeit', 'nachname', 'vorname', 'telefon']

    if not all(field in data for field in required_fields):
        return bad_request("Required fields are missing")

    tische_input = data['tische']
    kommentar = data.get('kommentar', '')
    personenzahl = data['personenzahl']
    reservierungsdatum = data['reservierungsdatum']
    reservierungsuhrzeit = data['reservierungsuhrzeit']

    kunde = {
        "nachname": data['nachname'],
        "vorname": data['vorname'],
        "telefon": data['telefon']
    }

    db = get_db_connection()
    tische_col = db.tische

    tische = []
    for tisch in tische_input:
        tischnummer = tisch['tischnummer']
        tisch_doc = tische_col.find_one({"tischnummer": tischnummer})
        if not tisch_doc:
            return bad_request(f"Tisch mit Nummer {tisch['tischnummer']} existiert nicht")
        tische.append({
            "tischnummer": tischnummer
        })

    reservation = {
        "status": "active",
        "kommentar": kommentar,
        "personenzahl": personenzahl,
        "reservierungsdatum": reservierungsdatum,
        "reservierungsuhrzeit": reservierungsuhrzeit,
        "kunde": kunde,
        "tische": tische
    }

    reservierungen = db.reservierungen
    reservation_id = reservierungen.insert_one(reservation).inserted_id

    response_data = {
        'RID': str(reservation_id),
        'reservierungsuhrzeit': reservierungsuhrzeit
    }

    return jsonify(response_data), 201

# User Story 5: Display occupancy for the next 7 days
@app.route('/api/v1/auslastung_7_tage', methods=['GET'])
def auslastung_7_tage():
    db = get_db_connection()
    reservierungen = db.reservierungen

    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=7) 

    pipeline = [
        {
            '$match': {
                'status': 'active',
                '$expr': {
                    '$and': [
                        {
                            '$gte': [
                                {'$dateFromString': {'dateString': '$reservierungsdatum', 'format': '%Y-%m-%d'}},
                                start_date  # Direkte Verwendung von start_date
                            ]
                        },
                        {
                            '$lte': [
                                {'$dateFromString': {'dateString': '$reservierungsdatum', 'format': '%Y-%m-%d'}},
                                end_date  # Direkte Verwendung von end_date
                            ]
                        }
                    ]
                }
            }
        },
        {
            '$group': {
                '_id': None,
                'total_people': {'$sum': '$personenzahl'}
            }
        }
    ]

    result = list(reservierungen.aggregate(pipeline))
    print(result[0])
    total_people = result[0]['total_people'] if result else 0

    return jsonify({'total_people': total_people}), 200

if __name__ == '__main__':
    app.run(debug=True)
