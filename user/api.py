from django.core.cache import cache
from django.shortcuts import render
from django.http import HttpResponse

from user.logic import handler_avatar_upload
from user.models import User
from common import errors
from lib.http import render_json
from lib.sms import send_vcode
from common import keys
from user.forms import ContactForm
from user.forms import ProfileModelForm


# Create your views here.
def submit_phonenum(request):
    """提交手机号码"""
    phone = request.POST.get('phone')
    if phone:
        send_vcode.delay(phone)
        return render_json()
    else:
        return render_json(code=errors.PhoneNum_Empty, data='手机号码不能为空')


def submit_vcode(request):
    """提交短信验证码"""
    phone = request.POST.get('phone')
    vcode = request.POST.get('vcode')

    # 从缓存中取出vcode
    cached_vcode = cache.get(keys.VCODE_KEY % phone)
    if cached_vcode == vcode:
        # 验证码正确,可以登录或者注册.
        # try:
        #     user = User.objects.get(phonenum=phone)
        #     # 登录
        # except User.DoesNotExist:
        #     # 注册
        #     User.objects.create(phonenum=phone, nickname=phone)

        # 使用User.objects.get_or_create()来简化
        user, created = User.objects.get_or_create(phonenum=phone, nickname=phone)
        request.session['uid'] = user.id
        return render_json(code=0, data=user.to_dict())
    else:
        # 验证不正确
        return render_json(code=errors.VCODE_ERROR, data='验证码错误')


def get_profile(request):
    """获取个人交友资料"""
    user = User.objects.get(id=request.session['uid'])
    return render_json(code=0, data=user.profile.to_dict())


def get_form(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        # 判断form表单数据是否合法
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            cc_myself = form.cleaned_data['cc_myself']
            return render(request, 'form.html',  locals())
    return render(request, 'form.html',  {'form': form})


def edit_profile(request):
    """修改个人资料"""
    # form表单
    form = ProfileModelForm(request.POST)
    if form.is_valid():
        profile = form.save(commit=False)
        profile.id = request.session['uid']
        profile.save()
        return render_json(code=0, data=profile.to_dict())
    return render_json(code=errors.PROFILE_ERROR, data=form.errors)


def upload_avatar(request):
    """头像上传"""
    avatar = request.FILES.get('avatar')
    # 保存用户上传的文件到本地
    # 拼出文件路径
    uid = request.session['uid']
    handler_avatar_upload.delay(uid, avatar)
    return render_json()


