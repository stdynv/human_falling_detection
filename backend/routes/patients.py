from flask import Blueprint, request, jsonify

patients_bp = Blueprint('patients_bp', __name__)

patients = []

def find_item(items, item_id):
    for item in items:
        if item['id'] == item_id:
            return item
    return None

def get_next_id(items):
    if items:
        return max(item['id'] for item in items) + 1
    else:
        return 1

@patients_bp.route('/', methods=['POST'])
def create_patient():
    data = request.get_json()
    patient = {
        'id': get_next_id(patients),
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'date_of_birth': data.get('date_of_birth'),
        'gender': data.get('gender'),
        'phone_number': data.get('phone_number'),
        'email': data.get('email'),
        'address': data.get('address'),
        'medical_history': data.get('medical_history'),
        'room_id': data.get('room_id'),
        'admission_date': data.get('admission_date')
    }
    patients.append(patient)
    return jsonify(patient), 201

@patients_bp.route('/', methods=['GET'])
def get_patients():
    return jsonify(patients), 200

@patients_bp.route('/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = find_item(patients, patient_id)
    if patient:
        return jsonify(patient), 200
    return jsonify({'error': 'Patient not found'}), 404

@patients_bp.route('/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    patient = find_item(patients, patient_id)
    if patient:
        data = request.get_json()
        patient.update({
            'first_name': data.get('first_name', patient['first_name']),
            'last_name': data.get('last_name', patient['last_name']),
            'date_of_birth': data.get('date_of_birth', patient['date_of_birth']),
            'gender': data.get('gender', patient['gender']),
            'phone_number': data.get('phone_number', patient['phone_number']),
            'email': data.get('email', patient['email']),
            'address': data.get('address', patient['address']),
            'medical_history': data.get('medical_history', patient['medical_history']),
            'room_id': data.get('room_id', patient['room_id']),
            'admission_date': data.get('admission_date', patient['admission_date'])
        })
        return jsonify(patient), 200
    return jsonify({'error': 'Patient not found'}), 404

@patients_bp.route('/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    patient = find_item(patients, patient_id)
    if patient:
        patients.remove(patient)
        return jsonify({'message': 'Patient deleted'}), 200
    return jsonify({'error': 'Patient not found'}), 404
