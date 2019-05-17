import datetime

from django.core.cache import cache
from django.db.models import Q

from common import keys
from lib.cache import rds
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


        # 更新缓存
        rewind_times += 1
        timeout = 86400 - (now.hour * 3600 + now.minute * 60 + now.second)
        cache.set(key, rewind_times, timeout)

        # 处理top_n
        # if record.mark == 'like':
        #     rds.zincrby(keys.HOT_RANK, -config.LIKE_SCORE, record.sid)
        # elif record.makr == 'dislike':
        #     rds.zincrby(keys.HOT_RANK, -config.DISLIKE_SCORE, record.sid)
        # else:
        #     rds.zincrby(keys.HOT_RANK, -config.SUPERLIKE_SCORE, record.sid)
        # 以上代码修改为使用模式匹配
        score_mapping = {
            'like': config.LIKE_SCORE,
            'dislike': config.DISLIKE_SCORE,
            'superlike': config.SUPERLIKE_SCORE
        }
        rds.zincrby(keys.HOT_RANK, -score_mapping[record.mark], record.sid)

        record.delete()
        return True
    else:
        raise errors.EXCEED_REWIND_TIMES()


def get_liked_me(user):
    swipe = Swipe.objects.filter(sid=user.id, mark__in=['like', 'superlike']).only('uid')
    liked_me_list = [sw.uid for sw in swipe]
    users = User.objects.filter(id__in=liked_me_list)
    return users


def get_friends_list(user):
    friends = Friend.objects.filter(Q(uid1=user.id) | Q(uid2=user.id))

    # 取出对方的id
    sid_list = []
    for friend in friends:
        if friend.uid1 == user.id:
            sid_list.append(friend.uid2)
        else:
            sid_list.append(friend.uid1)

    friends_list = User.objects.filter(id__in=sid_list)
    data = [friend.to_dict() for friend in friends_list]
    return data


def get_top_n(num):
    # [[b'6', 7.0], [b'5', 5.0], [b'4', 5.0], [b'3', 5.0], [b'9', -5.0]]
    data = rds.zrevrange(keys.HOT_RANK, 0, num, withscores=True)
    cleaned = [(int(id), int(score)) for (id, score) in data]
    # 根据id找到用户
    uid_list = [id for (id, _) in cleaned]
    # users = []
    # for循环中访问数据库太多次.
    # for uid in uid_list:
    #     user = User.objects.get(id=uid)
    #     user.append(user)
    users = User.objects.filter(id__in=uid_list)
    users = sorted(users, key=lambda user: uid_list.index(user.id))
    top_n = []
    for rank, (_, score), user in zip(range(1, num + 1), cleaned, users):
        user_dict = user.to_dict()
        user_dict['rank'] = rank
        user_dict['score'] = score
        top_n.append(user_dict)

    return top_n
