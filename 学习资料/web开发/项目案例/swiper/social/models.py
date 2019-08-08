from django.db import models

# Create your models here.


class Swiped(models.Model):
    """
    滑动记录表"""
    MARK = (
        ('like', 'like'),
        ('dislike', 'dislike'),
        ('superlike', 'superlike')
    )

    uid = models.IntegerField(verbose_name='用户自身id')
    sid = models.IntegerField(verbose_name='被滑的陌生人id')
    mark = models.CharField(choices=MARK, max_length=16, verbose_name='滑动类型')
    time = models.DateTimeField(auto_now_add=True, verbose_name='滑动的时间')

    @classmethod
    def like(cls, uid, sid):
        Swiped.objects.create(uid=uid, sid=sid, mark='like')

    @classmethod
    def superlike(cls, uid, sid):
        Swiped.objects.create(uid=uid, sid=sid, mark='superlike')

    @classmethod
    def dislike(cls, uid, sid):
        Swiped.objects.create(uid=uid, sid=sid, mark='dislike')

    @classmethod
    def has_liked_me(cls, uid, sid):
        return Swiped.objects.filter(uid=uid, sid=sid).exists()


class Friend(models.Model):
    uid1 = models.IntegerField()
    uid2 = models.IntegerField()

    @classmethod
    def make_friend(cls, uid1, uid2):
        """永远保证创建好友关系的时候,uid1小于uid2"""
        uid1, uid2 = (uid1, uid2) if uid1 < uid2 else (uid2, uid1)
        Friend.objects.create(uid1=uid1, uid2=uid2)

    @classmethod
    def is_friend(cls, uid1, uid2):
        return Friend.objects.filter(uid1=uid1, uid2=uid2).exists()




