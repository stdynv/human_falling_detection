from flask import Blueprint, jsonify, request
import logging
from flask_socketio import emit
from datetime import datetime
from models import Incident, Room
from extensions import db, socketio

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create the Blueprint for incidents
incidents_bp = Blueprint('incidents_bp', __name__)

# Route for creating an incident
@incidents_bp.route('/create', methods=['POST'])
def create_incident():
    try:
        # Fetch the JSON data from the request
        data = request.get_json()

        # Validate that required fields are present
        if not all(key in data for key in ['raspberry_id', 'description', 'video_url', 'status']):
            logging.error("Missing required fields in the request data")
            return jsonify({'error': 'Missing required fields'}), 400

        # Set the current timestamp for the incident
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

        # Create the notification message
        if room:
            message = f"A person has fallen in Room {room.room_number}"
            logging.info(f"Emitting new incident: {new_incident.incident_id} in Room {room.room_number}")
        else:
            message = "A person has fallen, but no room was found."
            logging.warning(f"No room found for raspberry_id: {new_incident.raspberry_id}")

        try:
            # Emit the message and video URL to all connected clients
            socketio.emit('notification', {
                'message': message,
                'video_url': new_incident.video_url
            }, broadcast=True)

            logging.info('Incident notification emitted to frontend')
        except Exception as e:
            logging.error(f"Error emitting WebSocket message: {e}")

        return jsonify({'message': 'Incident created successfully'}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error while creating an incident: {e}")
        return jsonify({'error': 'An internal error occurred while creating the incident'}), 500
