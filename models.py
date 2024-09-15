from extensions import db
import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash


class Room(db.Model):
    __tablename__ = 'Rooms'

    room_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), nullable=False)
    floor = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(20))
    occupied = db.Column(db.Boolean, default=False)
    raspberry_id = db.Column(db.String(100))

class Incident(db.Model):
    __tablename__ = 'Incidents'
    incident_id = db.Column(db.Integer, primary_key=True)
    raspberry_id = db.Column(db.String(50))
    incident_date = db.Column(db.DateTime, default=datetime.datetime.now())
    description = db.Column(db.String(200))
    video_url = db.Column(db.String(200))
    status = db.Column(db.String(20))

class Ehpad(db.Model):
    __tablename__ = 'ehpads'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password_hash):
        """Hashes the password for storage."""
        self.password_hash = generate_password_hash(password_hash)

    def check_password(self, password_hash):
        """Checks the password against the stored hash."""
        return check_password_hash(self.password_hash, password_hash)