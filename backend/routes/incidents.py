from flask import Blueprint, jsonify, request
# # from flask_socketio import SocketIO, emit
from config import Config
from datetime import datetime

incidents_bp = Blueprint('incidents_bp', __name__)

@incidents_bp.route('/', methods=['GET'])
def get_incidents():
    conn = Config.get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Incidents ORDER BY incident_date DESC")
    
    incidents = []
    for row in cursor.fetchall():
        incidents.append({
            'raspberry_id': row.raspberry_id,
            'incident_date': row.incident_date,
            'description': row.description,
            'video_url': row.video_url,
            'status' : row.status
        })

    # emit('notifications',incidents)
    
    conn.close()
    return jsonify(incidents)

@incidents_bp.route('/', methods=['POST'])

def create_incident():
    conn = Config.get_db_connection()
    data = request.json
    sql = """INSERT INTO Incidents (raspberry_id, incident_date, description, video_url,status)
             VALUES (?, ?, ?, ?, ?)"""
    
    values = (
        data['raspberry_id'], datetime.now(), 
        data['description'], data['video_url'],data['status']
    )

    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Incident recorded successfully'}), 201

# real time avec socketio : communication RT avec frontend
