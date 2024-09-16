from flask import Blueprint, request, jsonify
from extensions import db
from models import Room

rooms_bp = Blueprint('rooms_bp', __name__)

# Create a new room
@rooms_bp.route('/create', methods=['POST'])
def create_room():
    try:
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
        return jsonify({'message': 'Room created successfully'}), 201
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create room: {str(e)}'}), 500

# Get all rooms
@rooms_bp.route('/', methods=['GET'])
def get_rooms():
    try:
        rooms = Room.query.all()
        if not rooms:
            return jsonify({'message': 'No rooms found'}), 404
        return jsonify([{
            'room_id': room.room_id,
            'room_number': room.room_number,
            'floor': room.floor,
            'type': room.type,
            'occupied': room.occupied,
            'raspberry_id': room.raspberry_id
        } for room in rooms]), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch rooms: {str(e)}'}), 500

# Get a specific room by ID
@rooms_bp.route('/<int:room_id>', methods=['GET'])
def get_room(room_id):
    try:
        room = Room.query.get(room_id)
        if room is None:
            return jsonify({'error': 'Room not found'}), 404
        return jsonify({
            'room_id': room.room_id,
            'room_number': room.room_number,
            'floor': room.floor,
            'type': room.type,
            'occupied': room.occupied,
            'raspberry_id': room.raspberry_id
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch room: {str(e)}'}), 500

# Update room by room number
@rooms_bp.route('/<string:room_number>', methods=['PUT'])
def update_room_by_number(room_number):
    try:
        room = Room.query.filter_by(room_number=room_number).first()
        if room is None:
            return jsonify({'error': 'Room not found'}), 404
        
        data = request.get_json()
        room.room_number = data.get('room_number', room.room_number)
        room.floor = data.get('floor', room.floor)
        room.type = data.get('type', room.type)
        room.occupied = data.get('occupied', room.occupied)
        room.raspberry_id = data.get('raspberry_id', room.raspberry_id)
        
        db.session.commit()
        return jsonify({'message': 'Room updated successfully'}), 200
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update room: {str(e)}'}), 500

# Delete room by room number
@rooms_bp.route('/<string:room_number>', methods=['DELETE'])
def delete_room_by_number(room_number):
    try:
        room = Room.query.filter(db.func.lower(Room.room_number) == room_number.lower()).first()
        if room is None:
            return jsonify({'error': 'Room not found'}), 404
        
        db.session.delete(room)
        db.session.commit()
        return jsonify({'message': 'Room deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete room: {str(e)}'}), 500