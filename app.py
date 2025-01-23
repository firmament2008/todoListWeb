from flask import Flask
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 初始化Flask应用
app = Flask(__name__)

# 配置应用
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
from extensions import init_extensions
init_extensions(app)

# 导入路由
from routes import todo_bp

# 注册蓝图
app.register_blueprint(todo_bp, url_prefix='/api/todos')

if __name__ == '__main__':
    app.run(debug=True, port=5001)