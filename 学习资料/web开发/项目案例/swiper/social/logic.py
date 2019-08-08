import datetime

from django.core.cache import cache
from django.db.models import Q

from common import keys, errors
from lib.cache import rds
from social.models import Swiped, Friend
from swiper import config
from user.models import User


def get_rmcd_list_logic(user):
    now = datetime.datetime.now()

    max_birth_year = now.year - user.profile.min_dating_age
    min_birth_year = now.year - user.profile.max_dating_age

    # 去处已经滑过的用户
    # select sid from swiped where uid = user.id
    swiped_list = Swiped.objects.filter(uid=user.id).only('sid')
    # 把sid取出来
    sid_list = [s.sid for s in swiped_list]
    # 把自己也去掉
    sid_list.append(user.id)
    users = User.objects.filter(location=user.profile.location,
                                birth_year__range=[min_birth_year,
                                                   max_birth_year],
                                sex=user.profile.dating_sex).exclude(
        id__in=sid_list)[:20]
    # select *  from user where xxx limit 30
    data = [user.to_dict() for user in users]
    return data


def like(user, sid):
    Swiped.like(uid=user.id, sid=sid)
    # 判断对方是否喜欢自己.如果喜欢的话,建立好友关系
    if Swiped.has_liked_me(uid=sid, sid=user.id):
        # 建立好友关系
        Friend.make_friend(uid1=user.id, uid2=sid)
        return True
    return False


def superlike(user, sid):
    Swiped.superlike(uid=user.id, sid=sid)
    # 判断对方是否喜欢自己.如果喜欢的话,建立好友关系
    if Swiped.has_liked_me(uid=sid, sid=user.id):
        # 建立好友关系
        Friend.make_friend(uid1=user.id, uid2=sid)
        return True
    return False


def get_liked_me(user):
    """查看喜欢我的人"""
    swiped_list = Swiped.objects.filter(sid=user.id, mark__in=['like', 'superlike']).only('uid')
    uid_list = [s.uid for s in swiped_list]
    # 不推荐写法,性能极差,每次都会访问数据库
    # users = []
    # for uid in uid_list:
    #     users.append(User.get(id=uid))

    # 推荐写法, 只访问一次数据库
    users = User.objects.filter(id__in=uid_list)
    return users


def rewind(user):
    # 从缓存中取出已经执行反悔次数
    key = keys.REWIND_KEY % user.id
    rewind_times = cache.get(key, 0)
    if rewind_times < config.REWIND_TIMES:
        record = Swiped.objects.filter(uid=user.id).latest('time')
        # 如果有好友关系, 解除好友关系.
        uid1, uid2 = (user.id, record.sid) if user.id < record.sid else (
        record.sid, user.id)
        if Friend.is_friend(uid1=uid1, uid2=uid2):
            Friend.get(uid1=uid1, uid2=uid2).delete()


        # 更新已执行的反悔次数
        now = datetime.datetime.now()
        timeout = 86400 - (now.hour * 3600 + now.minute * 60 + now.second)
        cache.set(key, rewind_times + 1, timeout)

        # 反悔之后更新排行榜得分
        # if record.mark == 'like':
        #     rds.zincrby(config.HOT_RANK, -config.LIKE_SCORE, record.sid)
        # elif record.mark == 'dislike':
        #     rds.zincrby(config.HOT_RANK, -config.DISLIKE_SCORE, record.sid)
        # else:
        #     rds.zincrby(config.HOT_RANK, -config.SUPERLIKE_SCORE, record.sid)
        # 使用模式匹配来优化以上代码
        mapping = {
            'like': config.LIKE_SCORE,
            'dislike': config.DISLIKE_SCORE,
            'superlike': config.SUPERLIKE_SCORE
        }
        rds.zincrby(config.HOT_RANK, -mapping[record.mark], record.sid)

        record.delete()
    else:
        raise errors.ExceedRewindTimes


def get_friends_list(user):
    friends = Friend.objects.filter(Q(uid1=user.id) | Q(uid2=user.id))
    # 把对方的id查出来.
    friends_id_list = []
    for friend in friends:
        if friend.uid1 == user.id:
            friends_id_list.append(friend.uid2)
        else:
            friends_id_list.append(friend.uid1)

    users = User.objects.filter(id__in=friends_id_list)
    data = [user.to_dict() for user in users]
    return data


def get_top_n():
    """
        返回的是用户信息,带着排名
        { 'code': 0,
            'data': [
            {
            'rank': 1,
            'score': 100
            'id': 2,
            'phonenum': 18676689715,
            'nickname': xxx,
            },
            {
            'rank': 2,
            'score': 99,
            ...
            }
            ]
        }
        """
    # [[b'2', 12.0], [b'103', 7.0], [b'101', 5.0], [b'100', 5.0], [b'102', -5.0]]
    hot_rank = rds.zrevrange(config.HOT_RANK, 0, config.TOP_N, withscores=True)
    # 清洗一下数据
    cleaned_data = [(int(id), int(score)) for (id, score) in hot_rank]
    # 取出用户id
    user_id_list = [id for (id, score) in cleaned_data]
    # queryset会自动的按照model的id进行排序.升序
    users = User.objects.filter(id__in=user_id_list)
    sorted_users = sorted(users, key=lambda user: user_id_list.index(user.id))

    # 拼接数据
    data = []
    for rank, (_, score), user in zip(range(1, config.TOP_N + 1), cleaned_data,
                                      sorted_users):
        top_n_dict = dict()
        top_n_dict['rank'] = rank
        top_n_dict['score'] = score
        top_n_dict.update(user.to_dict())
        data.append(top_n_dict)
    return data
