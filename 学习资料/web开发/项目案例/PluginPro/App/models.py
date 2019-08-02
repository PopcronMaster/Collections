from App.exts import db


# 模型 => 类
class Person(db.Model):
    __tablename__ = 'person'  # 表名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True)
    age = db.Column(db.Integer, default=18)
    sex = db.Column(db.String(10), default='male')




