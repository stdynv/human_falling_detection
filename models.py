from extensions import db

class Room(db.Model):
    __tablename__ = 'Rooms'

    room_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), nullable=False)
    floor = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(20))
    occupied = db.Column(db.Boolean, default=False)
    raspberry_id = db.Column(db.String(100))
