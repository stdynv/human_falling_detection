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
        # Step 1: Fetch the JSON data from the request
        data = request.get_json()
        incident_date = datetime.now()

        # Step 2: Create a new incident record
        new_incident = Incident(
            raspberry_id=data['raspberry_id'],
            incident_date=incident_date,
            description=data['description'],
            video_url=data['video_url'],
            status=data['status']
        )

        # Step 3: Save the new incident to the database
        db.session.add(new_incident)
        db.session.commit()

        # Step 4: Fetch the room associated with the incident via raspberry_id
        room = Room.query.filter_by(raspberry_id=new_incident.raspberry_id).first()

        if room:
            # Step 5: If room is found, emit the custom message with room number and video URL
            message = f"A person has fallen in Room {room.room_number}"
            logging.info(f"Emitting new incident: {new_incident.incident_id} in Room {room.room_number}")
            
            # Emit the message along with the video URL
            socketio.emit('new_incident', {
                'message': message,
                'video_url': new_incident.video_url  # Send video URL as well
            })
        else:
            # Emit a message if no room is associated with the raspberry_id
            logging.warning(f"No room found for raspberry_id: {new_incident.raspberry_id}")
            socketio.emit('new_incident', {
                'message': "A person has fallen, but no room was found.",
                'video_url': new_incident.video_url  # Send video URL even if no room is found
            })

        return jsonify({'message': 'Incident created successfully'}), 201

    except Exception as e:
        logging.error(f"Error while creating an incident: {e}")
        return jsonify({'error': f'An error occurred while creating the incident: {e}'}), 500
