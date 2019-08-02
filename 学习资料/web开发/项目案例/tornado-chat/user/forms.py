"""
表单验证类
"""

import re

# 第一种简单/复杂写法
# class MainForm():
#
#     def __init__(self):
#         # 定义账号只能为字母和数字，且长度为3到10位
#         self.account = "[0-1a-zA_Z]"
#         # 定义密码,且长度位5到10位
#         self.password = "(.*)"
#         self.password2 = "(.*)"
#
#     def check_valid(self, request):
#         # 校验结果值result, 校验成功，则返回True，校验失败，则返回False
#         result = True
#         # __dict__方法： 取当前类到普通字段和值
#         form_fields = self.__dict__
#         for key, value in form_fields.items():
#             # 取页面中提交到账号和密码
#             post_value = request.get_argument(key)
#             # 判断页面中提交到参数，是否匹配上后端设置到正则规则
#             if not re.match(value, post_value):
#                 result = False
#         return result


# 第二种写法（优化写法）
class BaseForm():

    def check_valid(self, request):
        # 校验结果值result, 校验成功，则返回True，校验失败，则返回False
        result = True
        # 校验到键值对
        value_dict = {}
        # 封装错误信息
        errors = {}
        # __dict__方法： 取当前类到普通字段和值
        form_fields = self.__dict__
        for key, value in form_fields.items():
            # 取页面中提交到账号和密码
            post_value = request.get_argument(key)
            # 判断页面中提交到参数，是否匹配上后端设置到正则规则
            if not re.match(value, post_value):
                result = False
                errors[key] = '{fields}字段校验失败'.format(fields=key)
            value_dict[key] = post_value
        return result, value_dict, errors


class RegisterForm(BaseForm):
    """
    注册表单验证
    """

    def __init__(self):

        # 定义账号只能为字母和数字，且长度为3到10位
        self.account = "^[0-9a-zA_Z]{3,10}$"
        # 定义密码,且长度位5到10位
        self.password = "^[0-9a-zA_Z]{5,10}$"
        self.password2 = "^[0-9a-zA_Z]{5,10}$"


class LoginForm(BaseForm):
    """
    登陆表单验证
    """

    def __init__(self):

        # 定义账号只能为字母和数字，且长度为3到10位
        self.account = "^[0-9a-zA_Z]{3,10}$"
        # 定义密码,且长度位5到10位
        self.password = "^[0-9a-zA_Z]{5,10}$"


