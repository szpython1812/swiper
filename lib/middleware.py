from django.utils.deprecation import MiddlewareMixin

from common import errors
from lib.http import render_json
from user.models import User


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 从session中拿 uid,如果能拿到,就说明登录了,如果拿不到就说明没登录 .
        WHITE_URL = ['/api/user/submit/phonenum/',
                     '/api/user/submit/vcode/']
        if request.path in WHITE_URL:
            return
        uid = request.session.get('uid')
        if uid:
            # 获取对象
            try:
                user = User.objects.get(id=uid)
                request.user = user
                return
            except User.DoesNotExist:
                return render_json(code=errors.USER_NOT_EXIST, data='用户不存在')
        else:
            return render_json(code=errors.LOGIN_REQUIRED, data='请登录')


class LogicErrMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, errors.LogicErr):
            return render_json(code=exception.code, data=exception.data)
        return
