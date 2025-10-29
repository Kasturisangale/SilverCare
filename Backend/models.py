from datetime import datetime
from Backend.extensions import db 
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='senior_citizen') # role: senior_citizen, caregiver, admin
    profile_picture = db.Column(db.String(200))
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    relation = db.Column(db.String(50), nullable=True)

    # Relationships
    medicines = db.relationship('UserMedMap', backref='user', lazy=True)
    health_entries = db.relationship('DailyHealthEntry', backref='user', lazy=True)
    caregivers = db.relationship('CaregiverSeniorMap', foreign_keys='CaregiverSeniorMap.senior_id', backref='senior', lazy=True)
    seniors = db.relationship('CaregiverSeniorMap', foreign_keys='CaregiverSeniorMap.caregiver_id', backref='caregiver', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Medicine(db.Model):
    __tablename__ = 'medicine'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='pending') #approved, pending, rejected
    
    # Fixed relationship
    user_med_maps = db.relationship('UserMedMap', backref=db.backref('medicine', passive_deletes=True), lazy=True, cascade='all, delete-orphan')

class UserMedMap(db.Model):
    __tablename__ = 'user_med_map'
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id', name='fk_user_med_map_medicine_id',ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_user_med_map_user_id'), nullable=False)
    dosage = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    breakfast_before = db.Column(db.Boolean, default=False)
    breakfast_after = db.Column(db.Boolean, default=False)
    lunch_before = db.Column(db.Boolean, default=False)
    lunch_after = db.Column(db.Boolean, default=False)
    dinner_before = db.Column(db.Boolean, default=False)
    dinner_after = db.Column(db.Boolean, default=False)
    
    statuses = db.relationship('Status', backref='user_med_map', lazy=True, cascade="all, delete-orphan")

class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    user_med_map_id = db.Column(db.Integer, db.ForeignKey('user_med_map.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    breakfast_before = db.Column(db.Boolean, nullable=True) 
    breakfast_after = db.Column(db.Boolean, nullable=True)
    lunch_before = db.Column(db.Boolean, nullable=True)
    lunch_after = db.Column(db.Boolean, nullable=True)
    dinner_before = db.Column(db.Boolean, nullable=True)
    dinner_after = db.Column(db.Boolean, nullable=True)    

class DailyHealthEntry(db.Model):
    __tablename__ = 'daily_health_entry'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    bp_systolic = db.Column(db.Float)
    bp_diastolic = db.Column(db.Float)

    sugar_level = db.Column(db.Float)

class CaregiverSeniorMap(db.Model):
    __tablename__ = 'caregiver_senior_map'
    id = db.Column(db.Integer, primary_key=True)
    caregiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    senior_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected


class MedicineReminder(db.Model):
    __tablename__ = 'medicine_reminder'
    id = db.Column(db.Integer, primary_key=True)
    user_med_map_id = db.Column(db.Integer, db.ForeignKey('user_med_map.id'), nullable=False)
    reminder_time = db.Column(db.String(20), nullable=False)  # e.g., 'breakfast_before'
    notification_type = db.Column(db.String(20), nullable=False)  # 'push', 'sms', 'email'
    message = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean, default=True)
    user_med_map = db.relationship('UserMedMap', backref='reminders')

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)     # Caregiver or Senior
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)   # Senior or Caregiver

    type = db.Column(db.String(20), nullable=False)   # 'sos' or 'poke'
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=True) # only for poke alerts
    slot = db.Column(db.String(50), nullable=True)    # e.g. 'Breakfast before'

    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_notifications')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_notifications')
    medicine = db.relationship('Medicine', foreign_keys=[medicine_id])
