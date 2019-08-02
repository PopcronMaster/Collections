import time

from flask import Blueprint, render_template, request, g, current_app, jsonify

from App.exts import cache
from App.models import Person, db

blue = Blueprint('blue', __name__)


@blue.route('/')
def index():

    print("获取到钩子函数中传过来的g.age：", g.age)

    return render_template('index.html')


@blue.route('/home/')
@cache.cached(timeout=10)
def home():
    print("load data")
    time.sleep(5)
    return "home"


# 钩子函数: 中间件
# AOP: 面向切面编程
# before_request：在每次请求之前都会调用
@blue.before_request
def before():
    print("before_request:钩子函数")

    # 拦截
    # return "被我拦截了"

    # 检测是否是浏览器在访问
    ua = request.user_agent
    # print(ua)
    # print(type(ua))  # <class 'werkzeug.useragents.UserAgent'>
    if ua.string.find('python') != -1:
        # 是python爬虫
        return "小伙子，别爬了"

    # 防止ip频繁访问
    ip = request.remote_addr  # 客户端IP
    if cache.get(ip):
        return "小伙子，别爬了"
    else:
        # 将ip缓存在内存中，缓存时间为0.5秒
        cache.set(ip, 'aa', timeout=0.5)

    # g：全局对象
    g.age = 16
    # print(current_app.config)  # app的配置信息



# json: 一种数据格式
# jsonify(): 序列化
@blue.route('/api/')
def api():
    persons = Person.query.all()
    # print(persons)  # 列表中包含对象
    # [<Person 1>, <Person 2>, <Person 3>, <Person 4>]

    # 把列表中的对象转换成字典
    # person_list = list(map(lambda p:p.name, persons))
    #    ['zhangsan', 'lisi', 'wangwu', 'zhaoliu']
    person_list = list(map(lambda p: {"name": p.name, "age": p.age}, persons))
    # [{'name': 'zhangsan', 'age': 33}, {'name': 'zhaoliu', 'age': 66}]
    # print(person_list)

    return jsonify(person_list)


# 增删改查
# Http: GET, POST, PUT, DELETE
#   GET: 获取数据，查询数据库
#   POST: 增加数据，插入数据库
#   PUT: 修改数据，修改数据库
#   DELETE: 删除数据， 删除数据库
@blue.route('/person/', methods=['get', 'post', 'put', 'delete'])
def person():

    # get: 获取person
    if request.method == "GET":
        persons = Person.query.all()
        person_list = list(map(lambda p: {"name": p.name, "age": p.age}, persons))
        return jsonify(person_list)

    # post: 新增person
    elif request.method == "POST":
        name = request.form.get('name')
        age = request.form.get('age')

        p = Person()
        p.name = name
        p.age = age

        data = {
            "status": 1,
            "msg": 'ok'
        }
        try:
            db.session.add(p)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
            data['status'] = 0
            data['msg'] = 'fail'

        return jsonify(data)

    # put: 修改person
    elif request.method == "PUT":
        name = request.form.get('name')
        newage = request.form.get('newage')

        data = {
            "status": 1,
            "msg": 'ok'
        }
        p = Person.query.filter_by(name=name).first()
        if p:
            p.age = newage
            db.session.commit()
        else:
            data['status'] = 0
            data['msg'] = 'fail'

        return jsonify(data)

    # delete: 删除Person
    elif request.method == "DELETE":
        name = request.form.get('name')

        data = {
            "status": 1,
            "msg": 'ok'
        }
        p = Person.query.filter_by(name=name).first()
        if p:
            db.session.delete(p)
            db.session.commit()
        else:
            data['status'] = 0
            data['msg'] = 'fail'

        return jsonify(data)


