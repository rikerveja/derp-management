from flask import request, jsonify
from app import app, db
from models import User, SerialNumber, Server
import random, string

# 用户注册接口
@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"message": "All fields are required", "success": False}), 400
        if '@' not in email:
            return jsonify({"message": "Invalid email format", "success": False}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists", "success": False}), 400

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully", "success": True}), 201

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}", "success": False}), 500


# 生成序列号接口
@app.route('/api/generate_serial', methods=['POST'])
def generate_serial():
    try:
        data = request.json
        duration_days = data.get('duration_days')
        if not duration_days:
            return jsonify({"message": "Duration days is required", "success": False}), 400

        while True:
            serial_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            if not SerialNumber.query.filter_by(code=serial_code).first():
                break

        serial = SerialNumber(code=serial_code, duration_days=duration_days)
        db.session.add(serial)
        db.session.commit()
        return jsonify({"serial_code": serial_code, "duration_days": duration_days, "success": True})

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}", "success": False}), 500


# 列出序列号接口
@app.route('/api/serials', methods=['GET'])
def list_serials():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status')

        query = SerialNumber.query
        if status:
            query = query.filter_by(status=status)

        serials = query.paginate(page=page, per_page=per_page, error_out=False)
        data = [{
            "code": s.code,
            "duration": s.duration_days,
            "status": s.status,
            "created_at": s.created_at
        } for s in serials.items]

        return jsonify({
            "message": "Serial numbers fetched successfully",
            "success": True,
            "data": data,
            "total": serials.total,
            "pages": serials.pages,
            "current_page": serials.page,
        })

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}", "success": False}), 500


# 将服务器信息（IP 和地区）录入数据库

@app.route('/api/add_server', methods=['POST'])
def add_server():
    data = request.json
    ip = data.get('ip')
    region = data.get('region')

    if not ip or not region:
        return jsonify({"message": "IP and region are required", "success": False}), 400

    if Server.query.filter_by(ip=ip).first():
        return jsonify({"message": "Server with this IP already exists", "success": False}), 400

    server = Server(ip=ip, region=region)
    db.session.add(server)
    db.session.commit()
    return jsonify({"message": "Server added successfully", "success": True}), 201
