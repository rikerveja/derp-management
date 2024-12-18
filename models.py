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
    id = db.Column(db.Integer, primary_key=True)  # 唯一标识符
    ip = db.Column(db.String(255), unique=True, nullable=False)  # 服务器 IP 地址
    region = db.Column(db.String(100), nullable=False)  # 服务器地区，如 "Shanghai"
    load = db.Column(db.Float, default=0.0)  # 当前服务器负载
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())  # 更新时间

# 用户与服务器的多对多关系
from sqlalchemy.orm import relationship

# 用户与服务器的关联表
user_server_association = db.Table(
    'user_server_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id'))
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    servers = relationship('Server', secondary=user_server_association, back_populates='users')

class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(255), unique=True, nullable=False)
    region = db.Column(db.String(100), nullable=False)
    load = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    users = relationship('User', secondary=user_server_association, back_populates='servers')

# 为记录用户的 DERP 容器信息，新增一个模型
class UserContainer(db.Model):
    __tablename__ = 'user_containers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    stun_port = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    user = relationship('User', back_populates='containers')
    server = relationship('Server', back_populates='containers')

# 扩展用户和服务器模型以支持容器关系
class User(db.Model):
    # 添加：
    containers = relationship('UserContainer', back_populates='user')

class Server(db.Model):
    # 添加：
    containers = relationship('UserContainer', back_populates='server')

