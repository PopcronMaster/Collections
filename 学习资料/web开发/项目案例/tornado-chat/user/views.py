
from datetime import datetime, timedelta

import tornado.web
import tornado.websocket

from user.forms import RegisterForm, LoginForm
from user.models import User, create_db, UserToken, UserRoom
from utils.functions import get_token, login_required
from utils.settings import session


class InitDbHandlers(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        create_db()
        self.write('同步数据库成功')


class RegisterHandlers(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):

        self.render('register.html')

    def post(self, *args, **kwargs):
        form = RegisterForm()
        result, data, errors = form.check_valid(self)
        if result:
            # 如果校验成功, 将数据进行保存并设置token
            user = User()
            user.username = data['account']
            user.password = data['password']
            # 事务提交，将数据保存到数据库中
            session.add(user)
            session.commit()

            self.redirect('/login/')
            return
        self.render('register.html', errors=errors)


class LoginHandlers(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):

        self.render('login.html')

    def post(self, *args, **kwargs):

        form = LoginForm()
        result, data, errors = form.check_valid(self)
        if result:
            # 1. 判断账号是否存在
            user = session.query(User).filter(User.username == data['account']).first()
            if not user:
                errors['account'] = '账号不存在'
                self.render('login.html', errors=errors)
            # 2. 判断密码是否正确
            if user.password != data['password']:
                errors['password'] = '密码错误'
                self.render('login.html', errors=errors)
            # 3. 向cookie和user_token表中存储数据
            token = get_token()
            self.set_secure_cookie('token', token, expires_days=1)

            user_token = UserToken()
            user_token.user_id = user.id
            user_token.token = token
            user_token.out_time = datetime.now() + timedelta(days=1)
            session.add(user_token)
            session.commit()
            # 4. 重定向到首页
            self.redirect('/home/')
            return
        self.render('login.html', errors=errors)


class HomeHandlers(tornado.web.RequestHandler):

    @login_required
    def get(self, *args, **kwargs):

        self.render('home.html')


class ManyChatHandlers(tornado.web.RequestHandler):

    @login_required
    def get(self, *args, **kwargs):

        self.render('chat.html')


class OneChatHandlers(tornado.web.RequestHandler):

    @login_required
    def get(self, *args, **kwargs):

        self.render('one_chat.html')


class RoomChatHandlers(tornado.web.RequestHandler):

    @login_required
    def get(self, *args, **kwargs):

        room_id = self.get_argument('room')
        print(room_id)
        user_room = session.query(UserRoom).filter(UserRoom.room == room_id).all()
        if len(user_room) >= 2:
            # 如果有房间号且判断房间信息大于等于两条数据，则不让进入该房间
            res = {'code': 1001, 'msg': '该房间已满，请换一个房间号'}
        else:
            # 创建房间的用户信息
            room = UserRoom()
            room.user_id = self.request.user.id
            room.room = room_id
            session.add(room)
            session.commit()
            res = {'code': 200, 'msg': '请求成功'}

        self.write(res)


class ChatHandlers(tornado.websocket.WebSocketHandler):

    # 定义一个集合，用来保存在线的所有用户
    online_users = set()

    @login_required
    def open(self, *args, **kwargs):
        # 当有新的用户上线，将该用户加入到列表online_users中
        self.online_users.add(self)
        # 将新用户加入的信息发送给所有的在线用户
        for user in self.online_users:
            user.write_message('系统提示:欢迎{}进入聊天室'.format(self.request.user.username))

    @login_required
    def on_message(self, message):
        # 重写on_message方法，当聊天消息有更新时自动触发的函数
        # 将在线用户发送的消息通过服务器转发给所有的在线用户
        for user in self.online_users:
            if user != self:
                user.write_message('{name}说:{msg}'.format(name=self.request.user.username, msg=message))

    @login_required
    def on_close(self):
        # 重写on_close方法，当有用户离开时自动触发的函数
        # 先将用户从列表中移除
        self.online_users.remove(self)
        # 将该用户离开的消息发送给所有在线的用户
        for user in self.online_users:
            user.write_message('系统提示:{name}离开了聊天室~'.format(name=self.request.user.username))


class NewChatHandlers(tornado.websocket.WebSocketHandler):

    # 定义一个集合，用来保存一对一聊天的用户信息
    # 存储格式为{'房间号': [对象1，对象2], '房间号': [对象3，对象4].....}
    online_users_info = {}

    @login_required
    def open(self, *args, **kwargs):

        user_room = session.query(UserRoom).filter(UserRoom.user_id == self.request.user.id).first()
        room = self.online_users_info.get(user_room.room)
        if room:
            room.append(self)
        else:
            room = [self]
        self.online_users_info[user_room.room] = room
        # 对在线对两个用户进行广播信息
        for user in room:
            user.write_message('系统提示:您的好友{}已进入{}聊天室'.format(self.request.user.username, user_room.room))

    @login_required
    def on_message(self, message):
        user_room = session.query(UserRoom).filter(UserRoom.user_id == self.request.user.id).first()
        room = self.online_users_info.get(user_room.room)

        for user in room:
            if user != self:
                user.write_message('{name}说:{msg}'.format(name=self.request.user.username, msg=message))

    @login_required
    def on_close(self):
        # 重写on_close方法，当有用户离开时自动触发的函数
        user_room = session.query(UserRoom).filter(UserRoom.user_id == self.request.user.id).first()
        room = self.online_users_info.get(user_room.room)
        # 先将用户从列表中移除
        room.remove(self)
        # 删除数据库UserRoom内的信息
        session.delete(user_room)
        session.commit()
        # 将该用户离开的消息发送给所有在线的用户
        for user in room:
            user.write_message('系统提示:{name}离开了聊天室~'.format(name=self.request.user.username))

