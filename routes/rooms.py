from flask import Blueprint, request, jsonify
from config import Config  

rooms_bp = Blueprint('rooms_bp', __name__)
    

@rooms_bp.route('/', methods=['GET'])
def get_rooms():
    conn = Config.get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Rooms")
    
    rooms = []
    for row in cursor.fetchall():
        rooms.append({
            'room_id': row.room_id,
            'room_number': row.room_number,
            'floor': row.floor,
            'occupied': row.occupied,
            'raspberry_id' : row.raspberry_id
        })

    # emit('notifications',incidents)
    
    conn.close()
    return jsonify(rooms)


@rooms_bp.route('/<int:room_id>', methods=['GET'])
def get_rooms():
    conn = Config.get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Rooms where raspraspberry_id = ?")
    
    rooms = []
    for row in cursor.fetchall():
        rooms.append({
            'room_id': row.room_id,
            'room_number': row.room_number,
            'floor': row.floor,
            'occupied': row.occupied,
            'raspberry_id' : row.raspberry_id
        })

    # emit('notifications',incidents)
    
    conn.close()
    return jsonify(rooms)
    
@rooms_bp.route('/create', methods=['POST'])
def create_room():
    data = request.get_json()
    
    # Récupérer les données du JSON
    room_number = data['room_number']
    floor = data['floor']
    room_type = data['type']
    occupied = data['occupied']
    raspberry_id = data['raspberry_id']
    
    # Connexion à la base de données
    conn = Config.get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    # Exécution de la requête SQL pour insérer une nouvelle salle
    cursor.execute(
        '''
        INSERT INTO rooms (room_number, floor, type, occupied, raspberry_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (room_number, floor, room_type, occupied, raspberry_id)
    )
    
    # Valider les changements et fermer la connexion
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Room created'}), 201

"""@rooms_bp.route('/create', methods=['POST'])
def create_room():
    data = request.get_json()
    new_room = Room(
        room_number=data['room_number'],
        floor=data['floor'],
        type=data['type'],
        occupied=data['occupied'],
        raspberry_id=data['raspberry_id']
    )
    db.session.add(new_room)
    db.session.commit()
    return jsonify({'message': 'Room created'}), 201

@rooms_bp.route('/', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    return jsonify([{
        'room_id': room.room_id,
        'room_number': room.room_number,
        'floor': room.floor,
        'type': room.type,
        'occupied': room.occupied,
        'raspberry_id': room.raspberry_id
    } for room in rooms]), 200

@rooms_bp.route('/<int:room_id>', methods=['GET'])
def get_room(room_id):
    room = Room.query.get_or_404(room_id)
    return jsonify({
        'room_id': room.room_id,
        'room_number': room.room_number,
        'floor': room.floor,
        'type': room.type,
        'occupied': room.occupied,
        'raspberry_id': room.raspberry_id
    }), 200

@rooms_bp.route('/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    room = Room.query.get_or_404(room_id)
    data = request.get_json()
    room.room_number = data.get('room_number', room.room_number)
    room.floor = data.get('floor', room.floor)
    room.type = data.get('type', room.type)
    room.occupied = data.get('occupied', room.occupied)
    room.raspberry_id = data.get('raspberry_id', room.raspberry_id)
    db.session.commit()
    return jsonify({'message': 'Room updated'}), 200

@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    return jsonify({'message': 'Room deleted'}), 200"""
