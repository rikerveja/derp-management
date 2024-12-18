from app import db
from sqlalchemy.orm import validates
from sqlalchemy.sql import func

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    serial_numbers = db.relationship('SerialNumber', backref='user', lazy='dynamic')

    @validates('email')
    def validate_email(self, key, address):
        if '@' not in address:
            raise ValueError("Invalid email address")
        return address

# 序列号模型
class SerialNumber(db.Model):
    __tablename__ = 'serial_numbers'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), unique=True, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='unused')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    used_at = db.Column(db.DateTime, onupdate=func.now(), nullable=True)

# 服务器模型
class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(255), unique=True, nullable=False)
    region = db.Column(db.String(100), nullable=False)
    load = db.Column(db.Float, default=0.0)
