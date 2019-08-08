from django.utils.deprecation import MiddlewareMixin


from common import errors
from common.errors import LogicErr
from lib.http import render_json

from user.models import User


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 给每一个request加上一个user
        # print('auth middleware ....')
        URL_WHITE_LIST = [
            '/api/user/submit/phone/',
            '/api/user/submit/vcode/'
        ]
        if request.path in URL_WHITE_LIST:
            return

        uid = request.session.get('uid', None)
        if uid is None:
            # 说明没登录
            return render_json(code=errors.LOGIN_REQUIRED, data='请登录')
        request.user = User.get(id=uid)


class LogicErrMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, LogicErr):
            return render_json(code=exception.code, data=exception.data)
        return
