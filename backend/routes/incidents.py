from flask import Blueprint, jsonify, request
from config import Config

incidents_bp = Blueprint('incidents_bp', __name__)

@incidents_bp.route('/', methods=['GET'])
def get_incidents():
    conn = Config.get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Incidents")
    
    incidents = []
    for row in cursor.fetchall():
        incidents.append({
            'incident_id': row.incident_id,
            'room_id': row.room_id,
            'incident_type': row.incident_type,
            'incident_date': row.incident_date,
            'description': row.description,
            'video_url': row.video_url
        })
    
    conn.close()
    return jsonify(incidents)

@incidents_bp.route('/', methods=['POST'])
def create_incident():
    conn = Config.get_db_connection()
    data = request.json
    sql = """INSERT INTO Incidents (room_id, incident_type, incident_date, description, video_url)
             VALUES (?, ?, ?, ?, ?)"""
    
    values = (
        data['room_id'], data['incident_type'], data['incident_date'], data['description'], data['video_url']
    )

    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Incident recorded successfully'}), 201

# Additional CRUD routes for incidents can be added here
