from extensions import db
import datetime
import pytz


class Room(db.Model):
    __tablename__ = "Rooms"

    room_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), nullable=False)
    floor = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(20))
    occupied = db.Column(db.Boolean, default=False)
    raspberry_id = db.Column(db.String(100))


class Incident(db.Model):
    __tablename__ = "Incidents"
    incident_id = db.Column(db.Integer, primary_key=True)
    raspberry_id = db.Column(db.String(50))
    incident_date = db.Column(db.DateTime, default=datetime.datetime.now())
    description = db.Column(db.String(200))
    video_url = db.Column(db.String(200))
    status = db.Column(db.String(20))
