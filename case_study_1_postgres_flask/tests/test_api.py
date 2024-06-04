import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000/api/v1'


def setup_module(module):
    """ Setup the database and server before any tests are run """
    # Initialize the test database and server
    pass


def teardown_module(module):
    """ Teardown the database and server after all tests are run """
    # Cleanup the test database and server
    pass


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
        'tid': tid,
        'personenzahl': personenzahl,
        'reservierungsdatum': reservierungsdatum,
        'reservierungsuhrzeit': reservierungsuhrzeit,
        'nachname': nachname,
        'vorname': vorname,
        'telefon': telefon
    }
    response = requests.post(f'{BASE_URL}/reservierungen', json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_table():

    for i in range(10):
        tischnummer = str(i)
        kapazitaet = 2 + i
        create_table(tischnummer, kapazitaet)


def test_add_reservations_next_7_days():
    tischnummer = 2
    kapazitaet = 2
    tid = 1

    start_date = datetime.now().date()
    for i in range(8):
        reservierungsdatum = (start_date + timedelta(days=i % 7)).strftime('%Y-%m-%d')
        reservierungsuhrzeit = '18:00'
        nachname = f'Mustermann_{i}'
        vorname = 'Max'
        telefon = f'012345678{i}'

        response = add_reservation(tid +i, 4, reservierungsdatum, reservierungsuhrzeit, nachname, vorname, telefon)
        assert 'KID' in response
        assert 'RID' in response


def test_cancel_reservation():
    # Add a reservation first
    payload = {
        'tid': 1,
        'personenzahl': 4,
        'reservierungsdatum': '2023-06-01',
        'reservierungsuhrzeit': '18:00',
        'nachname': 'Mustermann',
        'vorname': 'Max',
        'telefon': '0123456789'
    }
    response = requests.post(f'{BASE_URL}/reservierungen', json=payload)
    rid = response.json()['RID']

    # Now cancel the reservation
    response = requests.delete(f'{BASE_URL}/reservierungen/{rid}')
    assert response.status_code == 200
    assert response.json()['message'] == 'Reservation cancelled'


def test_modify_reservation():
    # Add a reservation first
    payload = {
        'tid': 1,
        'personenzahl': 4,
        'reservierungsdatum': '2023-06-01',
        'reservierungsuhrzeit': '18:00',
        'nachname': 'Mustermann',
        'vorname': 'Max',
        'telefon': '0123456789'
    }
    response = requests.post(f'{BASE_URL}/reservierungen', json=payload)
    rid = response.json()['RID']

    # Modify the reservation
    payload = {
        'tid': 2,
        'kid': response.json()['KID'],
        'status': 'active',
        'kommentar': 'Änderung'
    }
    response = requests.put(f'{BASE_URL}/reservierungen/{rid}', json=payload)
    assert response.status_code == 200
    assert response.json()['message'] == 'Reservation modified'


def test_display_occupancy():
    response = requests.get(f'{BASE_URL}/auslastung_7_tage')
    assert response.status_code == 200
    assert 'total_people' in response.json()


