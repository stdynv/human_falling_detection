import eventlet
eventlet.monkey_patch()  # C'est important pour activer le mode non-bloquant


from flask import Blueprint, jsonify, request
import logging
from flask_socketio import emit
from datetime import datetime
from models import Incident, Room
from extensions import db, socketio  # Import socketio

# Create the Blueprint for incidents
incidents_bp = Blueprint('incidents_bp', __name__)

# Route for creating an incident
@incidents_bp.route('/create', methods=['POST'])
def create_incident():
    try:
        # Fetch the JSON data from the request
        data = request.get_json()
        incident_date = datetime.now()

        # Create a new incident record
        new_incident = Incident(
            raspberry_id=data['raspberry_id'],
            incident_date=incident_date,
            description=data['description'],
            video_url=data['video_url'],
            status=data['status']
        )

        # Save the new incident to the database
        db.session.add(new_incident)
        db.session.commit()

        # Fetch the room associated with the incident via raspberry_id
        room = Room.query.filter_by(raspberry_id=new_incident.raspberry_id).first()

        # Emit message based on room existence
        if room:
            message = f"A person has fallen in Room {room.room_number}"
            logging.info(f"Emitting new incident: {new_incident.incident_id} in Room {room.room_number}")
        else:
            message = "A person has fallen, but no room was found."
            logging.warning(f"No room found for raspberry_id: {new_incident.raspberry_id}")

        try:
            # Emit the message along with the video URL
            socketio.emit('new_incident', {
                'message': message,
                'video_url': new_incident.video_url
            })
        except Exception as e:
            logging.error(f"Error emitting WebSocket message: {e}")

        return jsonify({'message': 'Incident created successfully'}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error while creating an incident: {e}")
        return jsonify({'error': f'An error occurred while creating the incident: {e}'}), 500
