import datetime

from django.core.cache import cache
from common import keys
from social.models import Swipe, Friend
from swiper import config
from user.models import User
from common import errors



def like(user, sid):
    Swipe.like(user.id, sid)
    # 判断对方是否喜欢我们
    if Swipe.has_like_someone(sid):
        # 建立好友关系.
        Friend.make_friends(user.id, sid)
        return {'match': True}
    else:
        return {'match': False}


def superlike(user, sid):
    Swipe.superlike(user.id, sid)
    # 判断对方是否喜欢我们
    if Swipe.has_like_someone(sid):
        # 建立好友关系.
        Friend.make_friends(user.id, sid)
        return {'match': True}
    else:
        return {'match': False}


def get_recmd_list(user):
    # 取出已经滑过的人
    swiped = Swipe.objects.filter(uid=user.id).only('sid')
    swiped_list = [sw.id for sw in swiped]
    # 把自己也排除
    swiped_list.append(user.id)

    curr_year = datetime.datetime.now().year
    max_birth_year = curr_year - user.profile.min_dating_age
    min_birth_year = curr_year - user.profile.max_dating_age

    users = User.objects.filter(
        location=user.profile.location,
        birth_year__range=(min_birth_year, max_birth_year),
        sex=user.profile.dating_sex
    ).exclude(id__in=swiped_list)[:20]
    # [:20] = select xxx, xxx from User limit 20
    return users


def rewind(user):
    now = datetime.datetime.now()
    key = keys.REWIND_KEY % (user.id, now.date())
    rewind_times = cache.get(key, 0)
    # 取出的次数和最大允许反悔次数做对比.
    if rewind_times < config.REWIND_TIMES:
        # 执行反悔操作.
        # 删除Swipe中的记录.如果有好友关系,也需要一并取消.
        record = Swipe.objects.filter(uid=user.id).latest(
            field_name='swipe_time')
        uid1, uid2 = (user.id, record.sid) if user.id < record.sid else (
        record.sid, user.id)
        Friend.objects.filter(uid1=uid1, uid2=uid2).delete()
        record.delete()

        # 更新缓存
        rewind_times += 1
        timeout = 86400 - (now.hour * 3600 + now.minute * 60 + now.second)
        cache.set(key, rewind_times, timeout)
        return True
    else:
        raise errors.EXCEED_REWIND_TIMES()


def get_liked_me(user):
    swipe = Swipe.objects.filter(sid=user.id, mark__in=['like', 'superlike']).only('uid')
    liked_me_list = [sw.uid for sw in swipe]
    users = User.objects.filter(id__in=liked_me_list)
    return users
