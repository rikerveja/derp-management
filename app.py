import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)

# 配置 SQLite 数据库路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'derp_management.db')
logger.info(f"Using database at: {db_path}")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# 数据库初始化
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 确保数据库表在启动时创建
try:
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully!")
except Exception as e:
    logger.error(f"Error initializing database: {e}")

# 导入路由
from routes import *

# 运行 Flask 应用
if __name__ == "__main__":
    logger.info("Starting Flask application...")
    app.run(host="0.0.0.0", port=8000, debug=True)
