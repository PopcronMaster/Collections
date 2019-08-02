from flask import Flask
from App.views import blue
from App.exts import init_exts

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("BASE_DIR:", BASE_DIR)


def create_app():
    # 配置static和templates路径
    static_path = os.path.join(BASE_DIR, 'static')  # 静态文件路径
    template_path = os.path.join(BASE_DIR, 'templates')  # 模板文件路径

    app = Flask(__name__, static_folder=static_path, template_folder=template_path)
    app.config['ENV'] = 'development'  # 配置成开发环境

    # 数据库配置
    # sqlite
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost:3306/plugindb"

    # 禁止对象追踪修改
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 加载Flask插件
    init_exts(app)

    # 注册蓝图
    app.register_blueprint(blue)

    return app

