SMS_ERROR = 1000
VCODE_ERROR = 1001
PROFILE_ERROR = 1002
QINIU_ERROR = 1003
LOGIN_REQUIRED = 1004
EXCEED_REWIND_TIMES = 1005


class LogicErr(Exception):
    data = None
    code = None

    def __str__(self):
        return f'<{self.__class__.__name} {self.code}>'


def gen_error_class(name, data, code):
    return type(name, (LogicErr,), {'data': data, 'code': code})


SmsError = gen_error_class('SmsError', code=1000, data='发送短信错误')
VcodeError = gen_error_class('VcodeError', code=1001, data='验证码错误')
ProfileError = gen_error_class('ProfileError', code=1002, data='个人资料错误')
QiniuError = gen_error_class('QiniuError', code=1003, data='上传七牛云错误')
LoginRequired = gen_error_class('LoginRequired', code=1004, data='请登录')
ExceedRewindTimes = gen_error_class('ExceedRewindTimes', code=1005, data='超过当日最大反悔次数')
PermissionErr = gen_error_class('PermissionErr', code=1006, data='权限不足, 请充值')
