"""发送短信 验证码"""
import random

import requests
from django.core.cache import cache

from swiper import config
from lib.http import render_json
from common import errors
from common import keys
from worker import celery_app

# 1000 - 9999
def gen_vcode(size=4):
    # 1000 = 10 ** (size - 1)
    # 9999 = 10 ** size
    start = 10 ** (size - 1)
    end = 10 ** size - 1
    return random.randint(start, end)


@celery_app.task
def send_vcode(phone):
    vcode = gen_vcode()
    # 加入缓存中
    cache.set(keys.VCODE_KEY % phone, str(vcode), timeout=180)
    params = config.YZX_PARAMS.copy()
    params['param'] = vcode
    params['mobile'] = phone
    resp = requests.post(config.YZX_URL, json=params)

    if resp.status_code == 200:
        # 通信正常
        result = resp.json()
        if result['code'] != '000000':
            # 短信发送有误
            return False, '短信发送有误'
        else:
            return True, 'OK'
    else:
        return render_json(code=errors.SMS_SERVER_ERROR, data='访问短信服务平台异常')
