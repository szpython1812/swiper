from django.db.models import Q
from django.shortcuts import render
from django.core.cache import cache
import datetime
from django.core.cache.backends import locmem
from redis import Redis

# Create your views here.
from common import keys, errors
from lib.cache import rds
from lib.http import render_json
from social import logic
from social.models import Swipe, Friend
from swiper import config
from user.models import User
from vip.logic import need_perm


def get_recmd_list(request):
    """获取推荐列表"""
    user = request.user
    users = logic.get_recmd_list(user)
    return render_json(data=[user.to_dict() for user in users])


def like(request):
    sid = int(request.POST.get('sid'))
    user = request.user
    result = logic.like(user, sid)

    # 喜欢, 被滑的人加5分.
    rds.zincrby(keys.HOT_RANK, config.LIKE_SCORE, sid)
    return render_json(data=result)


@need_perm('superlike')
def superlike(request):
    sid = int(request.POST.get('sid'))
    user = request.user
    result = logic.superlike(user, sid)
    rds.zincrby(keys.HOT_RANK, config.SUPERLIKE_SCORE, sid)
    return render_json(data=result)


def dislike(request):
    sid = int(request.POST.get('sid'))
    user = request.user
    Swipe.dislike(user.id, sid)
    rds.zincrby(keys.HOT_RANK, config.DISLIKE_SCORE, sid)
    return render_json(data={'msg': 'ok'})


@need_perm('rewind')
def rewind(request):
    """反悔 (每天允许反悔3 次)"""
    # 把已经反悔的次数存到缓存中.
    # 取出次数

    user = request.user
    result = logic.rewind(user)
    if result:
        return render_json(data={'rewind': 'ok'})
    return render_json(code=errors.EXCEED_REWIND_TIMES, data='超过最大反悔次数')


@need_perm('show_liked_me')
def get_like_me_list(request):
    """查看喜欢我的人"""
    users = logic.get_liked_me(request.user)
    return render_json(data=[user.to_dict() for user in users])


def  get_friends_list(request):
    """查看 好友列表"""
    user = request.user

    data = logic.get_friends_list(user)
    return render_json(data=data)


def get_friend_info(request):
    """查看好友信息"""
    friend_id = request.GET.get('sid')
    friend = User.objects.get(id=friend_id)
    return render_json(data=friend.to_dict())


def get_top_n(request):
    data = logic.get_top_n(config.TOP_NUM)
    return render_json(data=data)
