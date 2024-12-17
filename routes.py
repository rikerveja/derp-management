from flask import request, jsonify
from app import app, db
from models import User, SerialNumber, Server
import random, string

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/generate_serial', methods=['POST'])
def generate_serial():
    data = request.json
    duration_days = data.get('duration_days')
    serial_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    serial = SerialNumber(code=serial_code, duration_days=duration_days)
    db.session.add(serial)
    db.session.commit()
    return jsonify({"serial_code": serial_code, "duration_days": duration_days})

@app.route('/api/serials', methods=['GET'])
def list_serials():
    serials = SerialNumber.query.all()
    return jsonify([{ "code": s.code, "duration": s.duration_days, "status": s.status } for s in serials])
