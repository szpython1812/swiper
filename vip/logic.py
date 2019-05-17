
# 写个装饰器,用来做权限验证
from common import errors


def need_perm(perm):
    def wrap(view_func):
        def inner(request, *args, **kwargs):
            # 判断用户是否具有perm权限
            # 先获取用户的vip等级, 然后再判断vip对应的权限中是否包含perm权限.
            user = request.user
            if user.vip.has_perm(perm):
                result = view_func(request, *args, **kwargs)
                return result
            else:
                raise errors.PermRequired()
        return inner
    return wrap
