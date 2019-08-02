
import uuid
from functools import wraps

from user.models import UserToken, User
from utils.settings import session


def get_token():
    # 获取唯一到uuid值
    uid = uuid.uuid4().hex
    return uid


def login_required(func):
    # 登陆状态装饰器

    @wraps(func)
    def check(self, *args, **kwargs):
        token = self.get_secure_cookie('token')
        user_token = session.query(UserToken).filter(UserToken.token == token).first()
        if user_token:
            # 查询登陆用户，并赋值给request.user
            user = session.query(User).filter(User.id == user_token.user_id).first()
            self.request.user = user
            return func(self, *args, **kwargs)
        # 重定向到登陆地址
        return self.redirect('/login/')

    return check
