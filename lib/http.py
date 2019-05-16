import json

from django.http import HttpResponse
from django.conf import settings


def render_json(code=0, data=None):
    data_json = {
        'code': code,
        'data': data
    }
    if settings.DEBUG:
        data = json.dumps(data_json, indent=4, sort_keys=True, ensure_ascii=False)
    else:
        data = json.dumps(data_json, separators=[',', ':'], ensure_ascii=False)
    return HttpResponse(data)
