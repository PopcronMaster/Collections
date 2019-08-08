from django.core.cache import cache
from django.db.models import Model

from common import keys


def get(cls, *args, **kwargs):
    # 只缓存根据id或者pk查询的模型
    pk = kwargs.get('id') or kwargs.get('pk')
    if pk is not None:
        # 先 从 缓存中获取数据
        key = keys.MODEL_KEY % (cls.__name__, pk)
        obj = cache.get(key)
        # 获取不到,调用原生的get方法从数据库获取.
        if obj is None:
            # 说明没有缓存
            # 调用模型原来的方法
            obj = cls.get(*args, **kwargs)
            print('从数据库获取对象...')
            # 设置缓存
            cache.set(key, obj, 14 * 86400)
        return obj
    else:
        obj = cls.get(*args, **kwargs)
        return obj


def get_or_create(cls, defaults=None, **kwargs):
    # 只缓存根据id或者pk查询的模型
    pk = kwargs.get('id') or kwargs.get('pk')
    if pk is not None:
        # 先 从 缓存中获取数据
        key = keys.MODEL_KEY % (cls.__name__, pk)
        obj = cache.get(key)
        # 获取不到,调用原生的get方法从数据库获取.
        if obj is None:
            # 说明没有缓存
            # 调用模型原来的方法
            obj = cls.get_or_create(defaults=None, **kwargs)
            print('从数据库获取对象...')
            # 设置缓存
            cache.set(key, obj, 14 * 86400)
        return obj
    else:
        obj = cls.get_or_create(defaults=None, **kwargs)
        return obj


def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
    # 更新缓存
    key = keys.MODEL_KEY % (self.__class__.__name__, self.id)
    cache.set(key, self, 14 * 86400)
    self._ori_save(force_insert=False, force_update=False, using=None,
             update_fields=None)


def model_patch():
    Model.get = classmethod(get)
    Model.get_or_create = classmethod(get_or_create)
    Model._ori_save = Model.save
    Model.save = save

