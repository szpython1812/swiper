from django.shortcuts import render
from django.core.cache import cache
import datetime

# Create your views here.
from common import keys, errors
from lib.http import render_json
from social import logic
from social.models import Swipe, Friend
from swiper import config
from user.models import User


def get_recmd_list(request):
    """获取推荐列表"""
    user = request.user
    users = logic.get_recmd_list(user)
    return render_json(data=[user.to_dict() for user in users])


def like(request):
    sid = int(request.POST.get('sid'))
    user = request.user
    result = logic.like(user, sid)
    return render_json(data=result)


def superlike(request):
    sid = int(request.POST.get('sid'))
    user = request.user
    result = logic.superlike(user, sid)
    return render_json(data=result)


def dislike(request):
    sid = int(request.POST.get('sid'))
    user = request.user
    Swipe.dislike(user.id, sid)
    return render_json(data={'msg': 'ok'})


def rewind(request):
    """反悔 (每天允许反悔3 次)"""
    # 把已经反悔的次数存到缓存中.
    # 取出次数

    user = request.user
    result = logic.rewind(user)
    if result:
        return render_json(data={'rewind': 'ok'})
    return render_json(code=errors.EXCEED_REWIND_TIMES, data='超过最大反悔次数')


def get_like_me_list(request):
    """查看喜欢我的人"""
    users = logic.get_liked_me(request.user)
    return render_json(data=[user.to_dict() for user in users])
