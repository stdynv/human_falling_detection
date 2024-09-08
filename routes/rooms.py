from flask import Blueprint, request, jsonify

rooms_bp = Blueprint('rooms_bp', __name__)

rooms = []

def find_item(items, item_id):
    for item in items:
        if item['room_id'] == item_id:
            return item
    return None


def get_next_id(items):
    if items:
        return max(item['room_id'] for item in items) + 1
    else:
        return 1

@rooms_bp.route('/', methods=['POST'])
def create_room():
    data = request.get_json()
    room = {
        'room_id': get_next_id(rooms),
        'room_number': data.get('room_number'),
        'floor': data.get('floor'),
        'type': data.get('type'),
        'occupied': data.get('occupied'),
        'raspberry_id': data.get('raspberry_id')
    }
    rooms.append(room)
    return jsonify(room), 201

@rooms_bp.route('/', methods=['GET'])
def get_rooms():
    return jsonify(rooms), 200

@rooms_bp.route('/<int:room_id>', methods=['GET'])
def get_room(room_id):
    room = find_item(rooms, room_id)
    if room:
        return jsonify(room), 200
    return jsonify({'error': 'Room not found'}), 404


@rooms_bp.route('/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    room = find_item(rooms, room_id)
    if room:
        data = request.get_json()
        room.update({
            'room_number': data.get('room_number', room['room_number']),
            'floor': data.get('floor', room['floor']),
            'type': data.get('type', room['type']),
            'occupied': data.get('occupied', room['occupied']),
            'raspberry_id': data.get('raspberry_id', room['raspberry_id'])
        })
        return jsonify(room), 200
    return jsonify({'error': 'Room not found'}), 404

@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    room = find_item(rooms, room_id)
    if room:
        rooms.remove(room)
        return jsonify({'message': 'Room deleted'}), 200
    return jsonify({'error': 'Room not found'}), 404
