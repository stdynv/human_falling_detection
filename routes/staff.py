from flask import Blueprint, request, jsonify

staff_bp = Blueprint("staff_bp", __name__)

staff = []


def find_item(items, item_id):
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def get_next_id(items):
    if items:
        return max(item["id"] for item in items) + 1
    else:
        return 1


@staff_bp.route("/", methods=["POST"])
def create_staff():
    data = request.get_json()
    staff_member = {
        "id": get_next_id(staff),
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "role": data.get("role"),
        "phone_number": data.get("phone_number"),
        "email": data.get("email"),
        "assigned_room": data.get("assigned_room"),
    }
    staff.append(staff_member)
    return jsonify(staff_member), 201


@staff_bp.route("/", methods=["GET"])
def get_staff():
    return jsonify(staff), 200


@staff_bp.route("/<int:staff_id>", methods=["GET"])
def get_staff_member(staff_id):
    staff_member = find_item(staff, staff_id)
    if staff_member:
        return jsonify(staff_member), 200
    return jsonify({"error": "Staff member not found"}), 404


@staff_bp.route("/<int:staff_id>", methods=["PUT"])
def update_staff(staff_id):
    staff_member = find_item(staff, staff_id)
    if staff_member:
        data = request.get_json()
        staff_member.update(
            {
                "first_name": data.get("first_name", staff_member["first_name"]),
                "last_name": data.get("last_name", staff_member["last_name"]),
                "role": data.get("role", staff_member["role"]),
                "phone_number": data.get("phone_number", staff_member["phone_number"]),
                "email": data.get("email", staff_member["email"]),
                "assigned_room": data.get(
                    "assigned_room", staff_member["assigned_room"]
                ),
            }
        )
        return jsonify(staff_member), 200
    return jsonify({"error": "Staff member not found"}), 404


@staff_bp.route("/<int:staff_id>", methods=["DELETE"])
def delete_staff(staff_id):
    staff_member = find_item(staff, staff_id)
    if staff_member:
        staff.remove(staff_member)
        return jsonify({"message": "Staff member deleted"}), 200
    return jsonify({"error": "Staff member not found"}), 404
