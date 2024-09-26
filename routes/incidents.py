from flask import Blueprint, jsonify, request
import logging
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
                "incident_id": new_incident.incident_id,
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


# Endpoint pour obtenir les incidents d'une chambre spécifique
@incidents_bp.route("/room/<int:room_number>/incidents", methods=["GET"])
def get_room_incidents(room_number):
    try:
        room = Room.query.filter_by(room_number=room_number).first()
        if not room:
            return jsonify({"error": "Room not found"}), 404

        incidents = Incident.query.filter_by(raspberry_id=room.raspberry_id).order_by(Incident.incident_date.desc()).all()

        incidents_list = [
            {
                "incident_id": incident.incident_id,
                "incident_date": incident.incident_date.strftime("%Y-%m-%d %H:%M:%S"),
                "description": incident.description,
                "video_url": incident.video_url,
                "status": incident.status,
            }
            for incident in incidents
        ]

        return jsonify({"incidents": incidents_list}), 200

    except Exception as e:
        logging.error(f"Error fetching incidents for room {room_number}: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


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
        
        # Calculer la différence en secondes et stocker dans intervention_time
        intervention_time_in_seconds = int(incident_time.total_seconds())
        incident.intervention_time = intervention_time_in_seconds
        
        logging.info(f"Finished incident {incident_id}, intervention time: {intervention_time_in_seconds} seconds")
        
        db.session.commit()

        return jsonify({
            "message": "Incident finished successfully",
            "incident_date_fin": str(incident.incident_date_fin)
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error while finishing the incident: {e}")
        return jsonify({"error": f"An error occurred while finishing the incident: {str(e)}"}), 500


# Endpoint pour obtenir les incidents actifs sans intervention_time
@incidents_bp.route("/active-incidents", methods=["GET"])
def get_active_incidents():
    try:
        incidents = db.session.query(Incident, Room).join(Room, Room.raspberry_id == Incident.raspberry_id).filter(Incident.intervention_time.is_(None)).all()

        active_incidents = [
            {
                "incident_id": incident.incident_id,
                "room_number": room.room_number,
                "incident_date": incident.incident_date.strftime("%Y-%m-%d %H:%M:%S"),
                "video_url": incident.video_url,
            }
            for incident, room in incidents
        ]

        return jsonify({"active_incidents": active_incidents}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred while fetching active incidents: {str(e)}"}), 500


# Nouvelle route pour calculer et mettre à jour intervention_time pour tous les incidents
@incidents_bp.route("/update-intervention-times", methods=["POST"])
def update_intervention_times():
    try:
        # Récupérer tous les incidents où intervention_time est NULL et où les deux dates sont présentes
        incidents = Incident.query.filter(
            Incident.intervention_time.is_(None),
            Incident.incident_date.isnot(None),
            Incident.incident_date_fin.isnot(None)
        ).all()

        # Pour chaque incident, calculer la différence en secondes entre incident_date et incident_date_fin
        updated_incidents = 0
        for incident in incidents:
            incident_time = incident.incident_date_fin - incident.incident_date
            intervention_time_in_seconds = int(incident_time.total_seconds())

            # Mettre à jour intervention_time
            incident.intervention_time = intervention_time_in_seconds
            updated_incidents += 1
            logging.info(f"Updated incident {incident.incident_id} with {intervention_time_in_seconds} seconds")

        # Commit les changements dans la base de données
        db.session.commit()

        # Retourner un message avec le nombre d'incidents mis à jour
        return jsonify({"message": f"{updated_incidents} incidents updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating intervention times: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Nouvelle route pour obtenir la moyenne des temps d'intervention des 10 dernières interventions
@incidents_bp.route("/average-last-10-interventions", methods=["GET"])
def average_last_10_interventions():
    try:
        # Récupérer les 10 dernières interventions avec intervention_time non nul
        last_10_interventions = Incident.query.filter(Incident.intervention_time.isnot(None)).order_by(Incident.incident_date_fin.desc()).limit(10).all()

        # Calculer la moyenne des temps d'intervention
        if not last_10_interventions:
            return jsonify({"average_intervention_time": 0}), 200

        total_time = sum(incident.intervention_time for incident in last_10_interventions)
        average_time = total_time / len(last_10_interventions)

        return jsonify({"average_intervention_time": average_time}), 200

    except Exception as e:
        logging.error(f"Error calculating average intervention time: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
