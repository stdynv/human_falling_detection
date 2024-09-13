from flask import Blueprint, jsonify, request
import logging
from flask_socketio import emit
from datetime import datetime
from models import Incident
from extensions import db, socketio  # Import socketio

# Create the Blueprint for incidents
incidents_bp = Blueprint('incidents_bp', __name__)

# Route for creating an incident
@incidents_bp.route('/create', methods=['POST'])
def create_incident():
    try:
        data = request.get_json()
        incident_date = datetime.now()
        new_incident = Incident(
            raspberry_id=data['raspberry_id'],
            incident_date=incident_date,
            description=data['description'],
            video_url=data['video_url'],
            status=data['status']
        )

        db.session.add(new_incident)
        db.session.commit()

        # Log the new incident creation and event emission
        logging.info(f"New incident created: {new_incident.description}")
        logging.info(f"Emitting new incident: {new_incident.incident_id}")

        # Emit the new incident event
        socketio.emit('new_incident', {
            'incident_id': new_incident.incident_id,
            'raspberry_id': new_incident.raspberry_id,
            'incident_date': new_incident.incident_date.isoformat(),
            'description': new_incident.description,
            'video_url': new_incident.video_url,
            'status': new_incident.status
        })

        return jsonify({'message': 'Incident created successfully'}), 201

    except Exception as e:
        logging.error(f"Error while creating an incident: {e}")
        return jsonify({'error': 'An error occurred while creating the incident'}), 500