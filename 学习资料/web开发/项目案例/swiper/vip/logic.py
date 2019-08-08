from common import errors


def need_perm(perm_name):
    def wrapper(view_func):
        def inner(request, *args, **kwargs):
            # 判断是否具有某个权限
            # 判断当前登录的用户是否具有某个权限
            # 判断当前登录用户的vip等级是否具有某个权限
            user = request.user
            if user.vip.has_perm(perm_name):
                response = view_func(request, *args, **kwargs)
                return response
            else:
                raise errors.PermissionErr
        return inner
    return wrapper
