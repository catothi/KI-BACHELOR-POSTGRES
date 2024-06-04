from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import os
from mongosanitizer.sanitizer import sanitize

app = Flask(__name__)

# Database connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'reservierung_db'

def get_db_connection():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({"message": "Bad Request", "details": str(error)}), 400)

@app.errorhandler(409)
def conflict(error):
    return make_response(jsonify({"message": "Conflict", "details": str(error)}), 409)

# Sanitizer function
def sanitize_pipeline(pipeline):
    sanitized_pipeline = sanitize(pipeline)
    if sanitized_pipeline != pipeline:
        raise ValueError("Potenziell unsichere Abfrage erkannt und bereinigt.")
    return sanitized_pipeline

# User Story 1: Create tables
@app.route('/api/v1/tische', methods=['POST'])
def create_table():
    data = request.get_json(force=True, silent=True)

    if data is None:
        return bad_request("Invalid JSON data")

    if not all(field in data for field in ['kapazitaet', 'tischnummer']):
        return bad_request("kapazitaet and tischnummer are required fields")

    if not isinstance(data['kapazitaet'], int):
        return bad_request("kapazitaet must be an integer")

    if not isinstance(data['tischnummer'], str):
        return bad_request("tischnummer must be a string")

    # Sanitize input data
    data = sanitize(data)
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
    data = request.get_json(force=True, silent=True)

    required_fields = ['tische', 'personenzahl', 'reservierungsdatum', 'reservierungsuhrzeit', 'nachname', 'vorname', 'telefon']
    if not all(field in data for field in required_fields):
        return bad_request("Required fields are missing")

    # Input validation and sanitization
    try:
        data = sanitize(data)
        tische_input = data['tische']
        kommentar = data.get('kommentar', '')
        personenzahl = int(data['personenzahl'])
        reservierungsdatum = datetime.strptime(data['reservierungsdatum'], '%Y-%m-%d').date()
        reservierungsuhrzeit = data['reservierungsuhrzeit']
        kunde = {
            "nachname": data['nachname'],
            "vorname": data['vorname'],
            "telefon": data['telefon']
        }
    except (ValueError, KeyError, TypeError) as e:
        return bad_request(f"Invalid data format: {e}")

    db = get_db_connection()
    tische_col = db.tische

    tische = []
    for tisch in tische_input:
        tischnummer = tisch['tischnummer']
        tisch_doc = tische_col.find_one({"tischnummer": tischnummer})
        if not tisch_doc:
            return bad_request(f"Tisch mit Nummer {tischnummer} existiert nicht")
        tische.append({"tischnummer": tischnummer})

    reservation = {
        "status": "active",
        "kommentar": kommentar,
        "personenzahl": personenzahl,
        "reservierungsdatum": reservierungsdatum,  # Store as datetime.date
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


# User Story 3: Update reservation status
@app.route('/api/v1/reservierungen/<reservation_id>/status', methods=['PATCH'])
def update_reservation_status(reservation_id):
    data = request.get_json(force=True, silent=True)
    if not data or 'status' not in data:
        return bad_request("Status is required")

    new_status = data['status']
    if new_status not in ['active', 'cancelled', 'completed']:
        return bad_request("Invalid status")

    db = get_db_connection()
    reservierungen = db.reservierungen

    result = reservierungen.update_one({'_id': ObjectId(reservation_id)}, {'$set': {'status': new_status}})

    if result.modified_count == 0:
        return jsonify({"message": "Reservation not found or status not changed"}), 404

    return jsonify({"message": "Reservation status updated successfully"}), 200
# User Story 4: Delete reservation by ID
@app.route('/api/v1/reservierungen/<reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id):
    db = get_db_connection()
    reservierungen = db.reservierungen

    result = reservierungen.delete_one({'_id': ObjectId(reservation_id)})

    if result.deleted_count == 0:
        return jsonify({"message": "Reservation not found"}), 404

    return jsonify({"message": "Reservation deleted successfully"}), 200



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
                                start_date
                            ]
                        },
                        {
                            '$lte': [
                                {'$dateFromString': {'dateString': '$reservierungsdatum', 'format': '%Y-%m-%d'}},
                                end_date
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

    # No need to sanitize this pipeline as it doesn't use user input
    result = reservierungen.aggregate(pipeline)
    total_people = next(result, {}).get('total_people', 0)

    return jsonify({'total_people': total_people}), 200

if __name__ == '__main__':
    app.run(debug=True)
