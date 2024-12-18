# derp-management
以下是完整的 Server 模型代码：

from app import db
from sqlalchemy.sql import func

class Server(db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)  # 唯一标识符
    ip = db.Column(db.String(255), unique=True, nullable=False)  # 服务器 IP 地址
    region = db.Column(db.String(100), nullable=False)  # 服务器地区，如 "Shanghai"
    load = db.Column(db.Float, default=0.0)  # 当前服务器负载
    created_at = db.Column(db.DateTime, default=func.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())  # 更新时间

说明

    id: 自增主键，用于唯一标识每台服务器。
    ip: 服务器的 IP 地址，必须唯一。
    region: 服务器所属地区，例如 "Shanghai" 或 "Beijing"。
    load: 当前服务器负载，浮点数，用于标记服务器的负载情况（例如已分配的用户数或使用率）。
    created_at: 记录服务器添加的时间。
    updated_at: 自动更新记录修改的时间。


注意事项

    迁移目录仅需初始化一次：在项目初次使用 Flask-Migrate 时才需要 flask db init。以后不需要重复初始化。
    模型更新后需重新迁移：如果 models.py 中的模型有任何修改，都需要执行以下命令更新数据库：

flask db migrate -m "Description of changes"
flask db upgrade
