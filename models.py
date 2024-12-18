from app import db
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

# 用户与服务器的关联表（多对多关系）
user_server_association = db.Table(
    'user_server_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id')),
    db.UniqueConstraint('user_id', 'server_id'),
    db.MetaData(),
    __table_args__ = {'extend_existing': True}  # 允许重新定义
)

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    serial_numbers = db.relationship('SerialNumber', backref='user', lazy='dynamic')
    servers = relationship('Server', secondary=user_server_association, back_populates='users')
    containers = relationship('UserContainer', back_populates='user')  # 容器关联

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
    used_at = db.Column(db.DateTime, nullable=True, onupdate=func.now())

# 服务器模型
class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(255), unique=True, nullable=False)  # 服务器 IP 地址
    region = db.Column(db.String(100), nullable=False)  # 服务器地区
    load = db.Column(db.Float, default=0.0)  # 当前服务器负载
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    users = relationship('User', secondary=user_server_association, back_populates='servers')
    containers = relationship('UserContainer', back_populates='server')  # 容器关联

# 用户容器模型
class UserContainer(db.Model):
    __tablename__ = 'user_containers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    port = db.Column(db.Integer, nullable=False)  # DERP 端口
    stun_port = db.Column(db.Integer, nullable=False)  # STUN 端口
    created_at = db.Column(db.DateTime, default=func.now())
    user = relationship('User', back_populates='containers')
    server = relationship('Server', back_populates='containers')
