import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api/v1"

def create_table(tischnummer, kapazitaet):
    payload = {
        'kapazitaet': kapazitaet,
        'tischnummer': tischnummer
    }
    response = requests.post(f'{BASE_URL}/tische', json=payload)
    assert response.status_code == 201
    return response.json()['Primary Key in DB']

def add_reservation(tid, personenzahl, reservierungsdatum, reservierungsuhrzeit, nachname, vorname, telefon):
    payload = {
        'tische': [{'tischnummer': tid}],
        'personenzahl': personenzahl,
        'reservierungsdatum': reservierungsdatum,
        'reservierungsuhrzeit': reservierungsuhrzeit,
        'nachname': nachname,
        'vorname': vorname,
        'telefon': telefon
    }
    response = requests.post(f'{BASE_URL}/reservierungen', json=payload)
    assert response.status_code == 201
    return response.json()['RID']

def test_create_table():
    tischnummer = 1
    kapazitaet = 4
    create_table(tischnummer, kapazitaet)


def test_add_reservations_next_7_days():
    tischnummer = "2"
    kapazitaet = 4
    tid = create_table(tischnummer, kapazitaet)

    start_date = datetime.now().date()
    for i in range(8):
        reservierungsdatum = (start_date + timedelta(days=i % 7)).strftime('%Y-%m-%d')
        reservierungsuhrzeit = '18:00'
        nachname = f'Mustermann_{i}'
        vorname = 'Max'
        telefon = f'012345678{i}'

        response = add_reservation(tischnummer, 4, reservierungsdatum, reservierungsuhrzeit, nachname, vorname, telefon)
        assert response is not None



def test_display_occupancy():
    response = requests.get(f'{BASE_URL}/auslastung_7_tage')
    assert response.status_code == 200
    assert 'total_people' in response.json()