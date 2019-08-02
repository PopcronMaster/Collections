

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from utils.settings import Base


def create_db():
    # 创建数据库
    Base.metadata.create_all()
    # 删除数据表
    # Base.metadata.drop_all()


class User(Base):
    """
    用户模型
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(10), unique=False, nullable=False)
    password = Column(String(255), nullable=False)
    token = relationship('UserToken', backref='user')
    room = relationship('UserRoom', backref='user')

    __tablename__ = 'user'


class UserToken(Base):
    """
    用户Token模型
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(50), unique=True, nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    out_time = Column(DateTime, nullable=False)

    __tablename__ = 'user_token'


class UserRoom(Base):
    """
    房间模型
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 朋友的id
    user_id = Column(ForeignKey('user.id'), nullable=False)
    # 自己的id
    room = Column(Integer, nullable=False)

    __tablename__ = 'user_room'
