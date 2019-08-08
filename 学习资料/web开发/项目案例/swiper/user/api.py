import logging
from django.core.cache import cache

from lib.sms import send_sms
from common import errors, keys
from lib.http import  render_json
from swiper import config
from user.models import User
from .forms import ProfileModelForm
from .logic import handler_upload_file

info = logging.getLogger('inf')

def submit_phone(request):
    """提交手机号码"""
    phone = request.POST.get('phone')

    # 给这个手机号码发短信
    send_sms.delay(phone)

    return render_json()


def submit_vcode(request):
    """提交验证码, 完成登录或者注册"""
    vcode = request.POST.get('vcode')
    phone = request.POST.get('phone')

    # 从缓存中取出vcode
    key = keys.VCODE_KEY % phone
    cached_vcode = cache.get(key)
    print(cached_vcode)
    if vcode == cached_vcode:
        # 验证码正确,可以登录或者注册
        # try:
        #     user = User.get(phonenum=phone)
        # except User.DoesNotExist:
        #     # 说明是注册
        #     # 创建用户
        #     user = User.objects.create(phonenum=phone, nickname=phone)

        user, created = User.get_or_create(phonenum=phone,
                        defaults={'nickname': phone})
        info.info(f'{user.nickname} 已登录')

        # print(created)
        # 写入session
        request.session['uid'] = user.id

        # 登录或注册成功之后,需要把用户信息返回给前端
        return render_json(data=user.to_dict())
    else:
        return render_json(code=errors.VCODE_ERROR, data='验证码错误')


def get_profile(request):
    """获取用户交友资料"""
    # 先从缓存 中获取数据
    user = request.user
    key = keys.PROFILE_KEY % user.id
    data = cache.get(key)
    if data is None:
        # 说明缓存中不存在数据
        # 从数据库拿
        data = user.profile.to_dict()
        print('getting profile from database...')
        # 数据存入缓存
        cache.set(key, data, timeout=1209600)
    return render_json(data=data)


def edit_profile(request):
    """django form"""
    form = ProfileModelForm(request.POST)

    if form.is_valid():
        # 数据合法的话,就取出数据,并更新profile
        profile = form.save(commit=False)
        profile.id = request.user.id
        profile.save()

        # 更新缓存中的profile数据
        cache.set(keys.PROFILE_KEY % request.user.id, profile.to_dict(), 1209600)
        return render_json(data=profile.to_dict())
    else:
        return render_json(code=errors.PROFILE_ERROR, data=form.errors)


def upload_avatar(request):
    # 保存用户上传的头像 到本地
    avatar = request.FILES.get('avatar')

    user = request.user
    handler_upload_file.delay(avatar, user.id)

    user.avatar = config.QN_CND_URL + keys.AVATAR_KEY % user.id
    user.save()
    return  render_json()









