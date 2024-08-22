from flask import Blueprint, jsonify, request
from config import Config

notifications_bp = Blueprint('notifications_bp', __name__)

@notifications_bp.route('/', methods=['GET'])
def get_notifications():
    conn = Config.get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Notifications")
    
    notifications = []
    for row in cursor.fetchall():
        notifications.append({
            'notification_id': row.notification_id,
            'incident_id': row.incident_id,
            'room_id': row.room_id,
            'notification_date': row.notification_date,
            'status': row.status,
            'message': row.message
        })
    
    conn.close()
    return jsonify(notifications)

@notifications_bp.route('/', methods=['POST'])
def create_notification():
    conn = Config.get_db_connection()
    data = request.json
    sql = """INSERT INTO Notifications (incident_id, room_id, notification_date, status, message)
             VALUES (?, ?, ?, ?, ?)"""
    
    values = (
        data['incident_id'], data['room_id'], data['notification_date'], data['status'], data['message']
    )

    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Notification sent successfully'}), 201

# Additional CRUD routes for notifications can be added here
