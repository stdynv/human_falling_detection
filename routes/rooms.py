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

@rooms_bp.route('/create', methods=['POST'])
def create_room():
    try:
        # Obtenir la connexion à la base de données
        conn = Config.get_db_connection()  # Remplacer par ta méthode de connexion à la DB
        if conn is None:
            # logging.error('Database connection failed.')
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Récupérer les données de la requête
        data = request.get_json()
        
        # Définir la requête SQL
        sql = """INSERT INTO rooms (room_number, floor, type, occupied, raspberry_id)
                 VALUES (?, ?, ?, ?, ?)"""
        
        # Définir les valeurs de la requête
        values = (
            data['room_number'], 
            data['floor'], 
            data['type'], 
            data['occupied'], 
            data['raspberry_id']
        )
        
        # Log la requête SQL pour le débogage
        logging.info(f"Executing SQL: {sql} with values {values}")
        
        # Exécuter la requête SQL
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        
        # Fermer le curseur et la connexion
        cursor.close()
        conn.close()

        # Retourner un message de succès
        return jsonify({'message': 'Room created successfully'}), 201

    except Exception as e:
        # Log en cas d'erreur
        logging.error(f"Error occurred: {e}")
        return jsonify({'error': 'An error occurred'}), 500

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
