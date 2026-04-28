from extensions import db
from datetime import date

class Violation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), nullable=False, index=True)
    violation_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    fine_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), default='Unpaid')
    qr_code_path = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Violation {self.vehicle_number} - {self.violation_type}>'


class Officer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Officer {self.username}>'
