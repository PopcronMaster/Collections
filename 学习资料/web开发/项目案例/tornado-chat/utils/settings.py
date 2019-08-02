
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 项目根路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 静态文件路径
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# 模板文件路径
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')


# 数据库连接
db_url = 'mysql+pymysql://root:root@127.0.0.1:3306/tornado_chat'

# 创建引擎
engine = create_engine(db_url)

# 创建对象的基类，用以维持模型类和数据库表中的对应关系
Base = declarative_base(bind=engine)

# 创建和数据库连接会话
DbSession = sessionmaker(bind=engine)
# 创建会话对象
session = DbSession()
