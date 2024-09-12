from flask import Blueprint, jsonify, request
import logging
import pytz
from config import Config
from datetime import datetime

local_tz = pytz.timezone('Europe/Paris')

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

@incidents_bp.route('/create', methods=['POST'])

def create_incident():
    try:
        conn = Config.get_db_connection()
        if conn is None:
            # logging.error('Database connection failed.')
            return jsonify({'error': 'Database connection failed'}), 500
        data = request.get_json()
        sql = """INSERT INTO Incidents (raspberry_id, incident_date, description, video_url, status)
                 VALUES (?, ?, ?, ?, ?)"""
        values = (
            data['raspberry_id'], datetime.now(local_tz),
            data['description'], data['video_url'], data['status']
        )
        
        # Log the SQL query for debugging
        logging.info(f"Executing SQL: {sql} with values {values}")
        
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Incident recorded successfully'}), 201

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return jsonify({'error': 'An error occurred'}), 500


