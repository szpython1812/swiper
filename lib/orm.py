from django.core.cache import cache
from django.db import models

from common import keys

"""
User.objects.get
User.objects.get_or_create()
user.save()

# 自己封装一个get, 用来从缓存中取数据
User.get()
"""

def get(cls, *args, **kwargs):
    # 针对pk和id的查询做一个缓存
    pk = kwargs.get('pk') or kwargs.get('id')
    key = keys.OBJ_KEY % pk
    # 从缓存中拿
    obj = cache.get(key)
    if not obj:
        # 从数据库中拿
        print('get object from db')
        obj = cls.objects.get(pk=pk)
        # 写入缓存
        cache.set(key, obj, 86400 * 14)
    return obj


def get_or_create(cls, *args, **kwargs):
    # 针对pk和id的查询做一个缓存
    pk = kwargs.get('pk') or kwargs.get('id')
    key = keys.OBJ_KEY % pk
    # 从缓存中拿
    obj = cache.get(key)
    if not obj:
        # 从数据库中拿
        print('get object from db')
        obj = cls.objects.get_or_create(*args, **kwargs)
        # 写入缓存
        cache.set(key, obj, 86400 * 14)
    return obj


def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
    # 先执行原先的保存动作.
    self._ori_save()
    # 然后更新缓存中的数据
    key = keys.OBJ_KEY % self.id
    cache.set(key, self, 86400 * 14)


# 猴子补丁, monkey patch
def model_patch():
    # 给Model新增一个自己写的get方法.
    models.Model.get = classmethod(get)
    models.Model.get_or_create = get_or_create()

    models.Model._ori_save = models.Model.save
