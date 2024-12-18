from flask import request, jsonify, abort
from app import app, db
from models import User, Server, UserContainer


# 添加用户
@app.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 检查字段是否完整
    if not username or not email or not password:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # 检查用户是否已存在
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"success": False, "message": "User already exists"}), 400

    # 创建新用户
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User added successfully", "user_id": user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 添加服务器
@app.route('/api/add_server', methods=['POST'])
def add_server():
    data = request.json
    ip = data.get('ip')
    region = data.get('region')
    load = data.get('load', 0.0)

    # 检查字段是否完整
    if not ip or not region:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # 检查服务器是否已存在
    existing_server = Server.query.filter_by(ip=ip).first()
    if existing_server:
        return jsonify({"success": False, "message": "Server already exists"}), 400

    # 创建新服务器
    server = Server(ip=ip, region=region, load=load)
    db.session.add(server)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Server added successfully", "server_id": server.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 添加用户与服务器的关联关系
@app.route('/api/add_user_server', methods=['POST'])
def add_user_server():
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')

    # 查询用户和服务器是否存在
    user = User.query.get(user_id)
    server = Server.query.get(server_id)

    if not user or not server:
        return jsonify({"success": False, "message": "User or Server not found"}), 404

    # 检查关联关系是否已经存在
    if server in user.servers:
        return jsonify({"success": False, "message": "User-Server relationship already exists"}), 400

    # 添加关联
    user.servers.append(server)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User-Server relationship added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 移除用户与服务器的关联关系
@app.route('/api/remove_user_server', methods=['POST'])
def remove_user_server():
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')

    # 查询用户和服务器是否存在
    user = User.query.get(user_id)
    server = Server.query.get(server_id)

    if not user or not server:
        return jsonify({"success": False, "message": "User or Server not found"}), 404

    # 检查关联关系是否存在
    if server not in user.servers:
        return jsonify({"success": False, "message": "User-Server relationship does not exist"}), 400

    # 移除关联
    user.servers.remove(server)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User-Server relationship removed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 获取用户关联的所有服务器
@app.route('/api/user_servers/<int:user_id>', methods=['GET'])
def get_user_servers(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    servers = [
        {"id": server.id, "ip": server.ip, "region": server.region, "load": server.load}
        for server in user.servers
    ]
    return jsonify({"success": True, "user_id": user.id, "servers": servers}), 200


# 添加用户容器
@app.route('/api/add_user_container', methods=['POST'])
def add_user_container():
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')
    port = data.get('port')
    stun_port = data.get('stun_port')

    # 查询用户和服务器是否存在
    user = User.query.get(user_id)
    server = Server.query.get(server_id)

    if not user or not server:
        return jsonify({"success": False, "message": "User or Server not found"}), 404

    # 检查端口是否冲突
    existing_container = UserContainer.query.filter_by(server_id=server_id, port=port).first()
    if existing_container:
        return jsonify({"success": False, "message": "Port already in use on this server"}), 400

    # 创建并添加容器
    container = UserContainer(user_id=user_id, server_id=server_id, port=port, stun_port=stun_port)
    db.session.add(container)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User container added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 移除用户容器
@app.route('/api/remove_user_container', methods=['POST'])
def remove_user_container():
    data = request.json
    container_id = data.get('container_id')

    # 查询容器是否存在
    container = UserContainer.query.get(container_id)
    if not container:
        return jsonify({"success": False, "message": "Container not found"}), 404

    # 删除容器
    db.session.delete(container)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User container removed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500


# 获取用户的所有容器
@app.route('/api/user_containers/<int:user_id>', methods=['GET'])
def get_user_containers(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    containers = [
        {
            "id": container.id,
            "server_id": container.server_id,
            "port": container.port,
            "stun_port": container.stun_port,
        }
        for container in user.containers
    ]
    return jsonify({"success": True, "user_id": user.id, "containers": containers}), 200
