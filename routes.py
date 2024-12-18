from flask import request, jsonify
from app import app, db
from models import User, Server, UserContainer
import random
import string

# 注册用户接口
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

# 添加用户与服务器的关联关系
@app.route('/api/add_user_server', methods=['POST'])
def add_user_server():
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')

    user = User.query.get(user_id)
    server = Server.query.get(server_id)

    if not user or not server:
        return jsonify({"message": "User or Server not found"}), 404

    if server.load >= 1.0:  # 示例逻辑：负载过高时拒绝分配
        return jsonify({"message": "Server load is too high to assign to user"}), 400

    user.servers.append(server)
    db.session.commit()

    return jsonify({"message": "User-Server relationship added successfully"}), 200

# 移除用户与服务器的关联关系
@app.route('/api/remove_user_server', methods=['POST'])
def remove_user_server():
    data = request.json
    user_id = data.get('user_id')
    server_id = data.get('server_id')

    user = User.query.get(user_id)
    server = Server.query.get(server_id)

    if not user or not server:
        return jsonify({"message": "User or Server not found"}), 404

    user.servers.remove(server)
    db.session.commit()

    return jsonify({"message": "User-Server relationship removed successfully"}), 200

# 获取用户关联的服务器列表
@app.route('/api/user_servers/<int:user_id>', methods=['GET'])
def get_user_servers(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    servers = [{"id": server.id, "ip": server.ip, "region": server.region, "load": server.load} for server in user.servers]
    return jsonify(servers), 200

# 获取服务器关联的用户列表
@app.route('/api/server_users/<int:server_id>', methods=['GET'])
def get_server_users(server_id):
    server = Server.query.get(server_id)

    if not server:
        return jsonify({"message": "Server not found"}), 404

    users = [{"id": user.id, "username": user.username, "email": user.email} for user in server.users]
    return jsonify(users), 200

# 移除所有与指定服务器关联的用户关系
@app.route('/api/remove_all_users_from_server/<int:server_id>', methods=['POST'])
def remove_all_users_from_server(server_id):
    server = Server.query.get(server_id)

    if not server:
        return jsonify({"message": "Server not found"}), 404

    users = server.users[:]
    for user in users:
        user.servers.remove(server)
    db.session.commit()

    return jsonify({"message": f"All users removed from server {server_id}"}), 200

# 自动分配服务器给用户（示例业务逻辑）
@app.route('/api/auto_assign_server', methods=['POST'])
def auto_assign_server():
    data = request.json
    user_id = data.get('user_id')
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    available_servers = Server.query.filter(Server.load < 1.0).all()

    if not available_servers:
        return jsonify({"message": "No available servers"}), 400

    # 示例：为用户分配负载最低的服务器
    selected_server = min(available_servers, key=lambda s: s.load)
    user.servers.append(selected_server)
    db.session.commit()

    return jsonify({"message": f"Server {selected_server.ip} assigned to user {user.username}"}), 200
