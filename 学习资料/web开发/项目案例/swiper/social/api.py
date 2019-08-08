import datetime

from django.core.cache.backends import locmem
from django.db.models import Q
from redis import Redis

from common import keys, errors
from lib.cache import rds
from lib.http import render_json
from social.models import Swiped, Friend
from swiper import config
from user.models import User
from vip.logic import need_perm
from .logic import get_rmcd_list_logic
from social import logic


def get_recd_list(request):
    """获取推荐列表"""
    # 返回一个列表,列表中每一项是一个用户
    user = request.user
    data = get_rmcd_list_logic(user)
    return render_json(data=data)


def like(request):
    """右滑,即 喜欢"""
    sid = int(request.POST.get('sid'))
    user = request.user
    # 在swiped表中创建一条记录
    flag = logic.like(user, sid)

    # 喜欢,加5分
    rds.zincrby(config.HOT_RANK, config.LIKE_SCORE, sid)

    return render_json(data={'matched': flag})


def dislike(request):
    """左滑,不喜欢"""
    sid = int(request.POST.get('sid'))
    user = request.user
    # 在swiped表中创建一条记录
    Swiped.dislike(uid=user.id, sid=sid)

    # 不喜欢减5分
    rds.zincrby(config.HOT_RANK, config.DISLIKE_SCORE, sid)
    return render_json()


def superlike(request):
    """上滑,即超级 喜欢"""
    sid = int(request.POST.get('sid'))
    user = request.user
    # 在swiped表中创建一条记录
    flag = logic.superlike(user, sid)

    # 喜欢,加7分
    rds.zincrby(config.HOT_RANK, config.SUPERLIKE_SCORE, sid)

    return render_json(data={'matched': flag})


@need_perm('show_liked_me')
def get_liked_me(request):
    user = request.user
    users = logic.get_liked_me(user)
    data = [user.to_dict() for user in users]
    return render_json(data=data)


@need_perm('rewind')
def rewind(request):
    """允许反悔上一次的 操作, 每天3次机会"""
    # 本质上就是把Swiped表中的记录删掉.

    user = request.user

    logic.rewind(user)
    return render_json()



def get_friends_list(request):
    user = request.user
    data = logic.get_friends_list(user)
    return render_json(data=data)


def get_top_n(request):
    data = logic.get_top_n()
    return render_json(data=data)


