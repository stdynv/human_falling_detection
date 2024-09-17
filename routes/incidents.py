from flask import Blueprint, jsonify, request
import logging
from flask_socketio import emit
from datetime import datetime
from models import Incident, Room
from extensions import db, socketio

incidents_bp = Blueprint('incidents_bp', __name__)

@incidents_bp.route('/create', methods=['POST'])
def create_incident():
    try:
        data = request.get_json()
        incident_date = datetime.now()

        # Create new incident
        new_incident = Incident(
            raspberry_id=data['raspberry_id'],
            incident_date=incident_date,
            description=data['description'],
            video_url=data['video_url'],
            status=data['status']
        )

        db.session.add(new_incident)
        db.session.commit()  # Commit the new incident to the database

        # Find associated room
        room = Room.query.filter_by(raspberry_id=new_incident.raspberry_id).first()

        if room:
            message = f"A person has fallen in Room {room.room_number}"
            logging.info(f"Emitting new incident: {new_incident.incident_id} in Room {room.room_number}")
        else:
            message = "A person has fallen, but no room was found."
            logging.warning(f"No room found for raspberry_id: {new_incident.raspberry_id}")

        # Emit the notification
        try:
            socketio.emit('notification', {
                'message': message,
                'video_url': new_incident.video_url
            })
            logging.info(f'Notification emitted: {message}')
        except Exception as e:
            logging.error(f"Error emitting WebSocket message: {e}")

        # Return success response
        return jsonify({'message': 'Incident created successfully', 'incident_id': new_incident.id}), 201

    except Exception as e:
        # Roll back the transaction in case of error
        db.session.rollback()
        logging.error(f"Error while creating an incident: {e}")
        return jsonify({'error': f'An error occurred while creating the incident: {str(e)}'}), 500
