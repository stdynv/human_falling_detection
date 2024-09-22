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

        # Emit the notification
        socketio.emit(
            "notification",
            {
                "message": message,
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
        # Utilisation de YEAR() et MONTH() pour extraire l'année et le mois
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

        # Formater les résultats
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