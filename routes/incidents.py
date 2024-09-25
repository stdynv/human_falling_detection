from flask import Blueprint, jsonify, request
import logging
from flask_socketio import emit
from datetime import datetime, timedelta
from sqlalchemy import func
from models import Incident, Room
from extensions import db, socketio
import pytz 

incidents_bp = Blueprint("incidents_bp", __name__)

tz = pytz.timezone('Europe/Paris')

# Endpoint pour créer un nouvel incident
@incidents_bp.route("/create", methods=["POST"])
def create_incident():
    try:
        data = request.get_json()
        incident_date = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        logging.info(incident_date)

        # Create new incident
        new_incident = Incident(
            raspberry_id=data["raspberry_id"],
            incident_date=incident_date,
            description=data["description"],
            video_url=data["video_url"],
            status=data["status"],
        )

        db.session.add(new_incident)
        db.session.commit()

        # Find associated room
        room = Room.query.filter_by(raspberry_id=new_incident.raspberry_id).first()

        if room:
            message = f"A person has fallen in Room {room.room_number}"
        else:
            message = "A person has fallen, but no room was found."

        # Emit the notification with incident ID
        socketio.emit(
            "notification",
            {
                "message": message,
                "incident_id": new_incident.incident_id,  # Ajouter l'ID de l'incident
                "incident_date": str(incident_date),
                "video_url": new_incident.video_url,
            },
        )
        logging.info(f"Notification emitted: {message}")

        return jsonify({"message": "Incident created successfully", "incident_id": new_incident.incident_id}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error while creating an incident: {e}")
        return jsonify({"error": f"An error occurred while creating the incident: {str(e)}"}), 500

# Endpoint pour obtenir les alertes actives (les incidents sans incident_date_fin)
@incidents_bp.route("/active-incidents", methods=["GET"])
def get_active_incidents():
    try:
        # Récupérer uniquement les incidents qui n'ont pas encore de date de fin (incident_date_fin est NULL)
        active_incidents = Incident.query.filter(Incident.incident_date_fin.is_(None)).all()

        active_incidents_list = [
            {
                "incident_id": incident.incident_id,
                "room_number": room.room_number,
                "incident_date": incident.incident_date.strftime("%Y-%m-%d %H:%M:%S"),
                "video_url": incident.video_url
            }
            for incident in active_incidents
            for room in Room.query.filter_by(raspberry_id=incident.raspberry_id)
        ]

        return jsonify({"active_incidents": active_incidents_list}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred while fetching active incidents: {str(e)}"}), 500

# Endpoint pour terminer un incident
@incidents_bp.route("/finish-incident/<int:incident_id>", methods=["POST"])
def finish_incident(incident_id):
    try:
        logging.info(f"Trying to finish incident {incident_id}")
        
        incident = Incident.query.get(incident_id)
        
        if not incident:
            logging.error(f"Incident {incident_id} not found")
            return jsonify({"error": "Incident not found"}), 404

        # Convertir incident.incident_date en un datetime avec fuseau horaire
        if incident.incident_date.tzinfo is None:
            incident.incident_date = tz.localize(incident.incident_date)

        # Enregistrer la date de fin et calculer le temps d'intervention
        incident.incident_date_fin = datetime.now(tz)
        incident_time = incident.incident_date_fin - incident.incident_date
        
        # Convertir timedelta en minutes
        intervention_time_in_minutes = incident_time.total_seconds() / 60  # Convertir secondes en minutes
        
        # Enregistrer la durée d'intervention sous forme de nombre (minutes)
        incident.intervention_time = intervention_time_in_minutes
        
        logging.info(f"Finished incident {incident_id}, intervention time: {intervention_time_in_minutes} minutes")
        
        db.session.commit()

        # Renvoyer la date de fin dans la réponse pour le frontend
        return jsonify({
            "message": "Incident finished successfully",
            "incident_date_fin": str(incident.incident_date_fin)  # Retourner la date de fin au frontend
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error while finishing the incident: {e}")
        return jsonify({"error": f"An error occurred while finishing the incident: {str(e)}"}), 500

# Endpoint pour obtenir les dernières 10 chutes
@incidents_bp.route("/latest-incidents", methods=["GET"])
def get_latest_incidents():
    try:
        incidents = db.session.query(Incident, Room).join(Room, Room.raspberry_id == Incident.raspberry_id).order_by(Incident.incident_date.desc()).limit(10).all()

        incidents_list = [
            {
                "room_number": room.room_number,
                "incident_date": incident.incident_date.strftime("%Y-%m-%d %H:%M:%S"),
                "description": incident.description,
                "video_url": incident.video_url,
                "status": incident.status,
            }
            for incident, room in incidents
        ]

        return jsonify({"incidents": incidents_list}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred while fetching incidents: {str(e)}"}), 500

# Endpoint pour obtenir les chutes d'aujourd'hui
@incidents_bp.route("/today-incidents", methods=["GET"])
def get_today_incidents():
    try:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        incidents_today = Incident.query.filter(Incident.incident_date >= today_start, Incident.incident_date < today_end).all()
        incidents_count = len(incidents_today)

        return jsonify({"incidents_count": incidents_count}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Endpoint pour obtenir le nombre de chutes par mois
@incidents_bp.route("/incidents-per-month", methods=["GET"])
def get_incidents_per_month():
    try:
        incidents_by_month = (
            db.session.query(
                func.concat(
                    func.cast(func.year(Incident.incident_date), db.String),
                    "-",
                    func.right("0" + func.cast(func.month(Incident.incident_date), db.String), 2)
                ).label("month"),
                func.count(Incident.incident_id).label("incident_count")
            )
            .group_by(func.year(Incident.incident_date), func.month(Incident.incident_date))
            .order_by(func.year(Incident.incident_date), func.month(Incident.incident_date))
            .all()
        )

        results = [
            {
                "month": month,
                "incident_count": incident_count
            }
            for month, incident_count in incidents_by_month
        ]

        return jsonify({"incidents_by_month": results}), 200

    except Exception as e:
        logging.error(f"Error fetching incidents per month: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
