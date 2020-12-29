import os
from datetime import datetime
import json
from flask import Blueprint, Response
from flask_cors import CORS
import requests
from app import db
import app.config

from app.models.letter import Letter
from app.models.letter_history import is_table_present, create_table, get_table

v1 = Blueprint("v1", __name__)
CORS(v1)

api_key = app.config[os.getenv("FLASK_CONFIG")].API_KEY


@v1.route('/ping', methods=['GET'])
def ep_ping():
    return "pong", 200


@v1.route('/letters', methods=['POST'])
def ep_setup_create_letter():
    # Example of ORM usage (SQLAlchemy)
    letter = Letter()
    letter.add()
    return f"All done : letter object {letter.id} has been created", 200


@v1.route('/getStatus/<track_id>', methods=['GET'])
def get_status(track_id):
    response = {}
    status = None
    resp = fetch_letter_status_la_poste(track_id)
    if resp.status_code != 200:
        status_code = Response(status=resp.status_code)
        return status_code
    data = resp.json()
    timeline = data['shipment']['timeline']
    for stat in timeline:
        if not stat['status']:
            break
        status = str(stat['id']) + ' ' + stat['shortLabel']
    if status is not None:
        response['status'] = status
    else:
        response['status'] = 'Not yet processed'
    response['tracking_number'] = track_id
    update_in_local_db(response)
    return response


@v1.route('/getStatusAllLetters', methods=['GET'])
def get_all_status():
    letters = get_all_letters()
    response = []
    for letter in letters:
        resp = get_status(letter.tracking_number)
        if isinstance(resp, Response) and resp.status_code == 404:
            temp = {'status': '404 not found', 'tracking_number': letter.tracking_number}
            response.append(temp)
        else:
            response.append(resp)
    return json.dumps(response)


@v1.route('/getStatusAsync', methods=['GET'])
def get_all_status_async():
    return None


def get_all_letters():
    query_entry = Letter.query.with_entities(Letter.tracking_number, Letter.status).all()
    return query_entry


def update_history(track_id, status):
    if is_table_present(track_id):
        obj = get_table(track_id)
    else:
        obj = create_table(track_id)
    new_db_entry = obj(timestamp=datetime.now(), status=status)
    db.session.add(new_db_entry)
    db.session.commit()


def fetch_letter_status_la_poste(track_id):
    return requests.get('https://api.laposte.fr/suivi/v2/idships/' + track_id,
                        headers={'Content-Type': 'application/json',
                                 'X-Okapi-Key': api_key})


def update_in_local_db(response):
    row = Letter.query.filter_by(tracking_number=response['tracking_number']).first()
    if row is None:
        new_db_entry = Letter(tracking_number=response['tracking_number'], status=response['status'])
        db.session.add(new_db_entry)
        db.session.commit()
    elif row.status != response['status']:
        update_history(response['tracking_number'], row.status)
        row.status = response['status']
        db.session.commit()
