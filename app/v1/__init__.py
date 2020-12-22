from flask import Blueprint, Response
from flask_cors import CORS
import requests
from app import db

from app.models.letter import Letter

v1 = Blueprint("v1", __name__)
CORS(v1)


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
    resp = requests.get('https://api.laposte.fr/suivi/v2/idships/' + track_id,
                        headers={'Content-Type': 'application/json',
                                 'X-Okapi-Key': 'CPi92XSI3FB+FPPTjMMmJODI3/uM0fRlXQMEcgpZFfavvDOh1eSCvjgX5LyMCzzE'})
    if resp.status_code != 200:
        status_code = Response(status=resp.status_code)
        return status_code
    data = resp.json()
    timeline = data['shipment']['timeline']
    for stat in timeline:
        if not stat['status']:
            break
        status = str(stat['id'])+' '+stat['shortLabel']
    if status is not None:
        response['status'] = status
    else:
        response['status'] = 'Not yet processed'
    response['tracking_number'] = track_id
    new_db_entry = Letter(tracking_number=response['tracking_number'], status=response['status'])
    db.session.add(new_db_entry)
    db.session.commit()
    return response
