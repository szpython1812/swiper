"""定义各种错误码"""


class LogicErr(Exception):
    code = None
    data = None

    def __str__(self):
        return f'<{self.__class__.__name__}>'


# 异常类的工厂类
def gen_logic_err(name, data, code):
    return type(name, (LogicErr,), {'data': data, 'code': code})


PhoneNumEmpty = gen_logic_err(name='PhoneNumEmpty', data='手机号码为空', code=1001)
SmsServerError = gen_logic_err(name='SmsServerError', data='短信服务器错误', code=1002)
SmsError = gen_logic_err(name='SmsError', data='发送短信错误', code=1003)
VcodeError = gen_logic_err(name='VcodeError', data='验证码错误', code=1004)
ProfileError = gen_logic_err(name='ProfileError', data='', code=1005)
UserNotExist = gen_logic_err(name='UserNotExist', data='用户不存在', code=1006)
LoginRequired = gen_logic_err(name='LoginRequired', data='请登录', code=1007)
ExceedRewindTimes = gen_logic_err(name='ExceedRewindTimes', data='超出最大反悔次数', code=1008)
