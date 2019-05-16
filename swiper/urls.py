"""swiper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from user import api as user_api
urlpatterns = [
    url(r'^api/user/submit/phonenum/$', user_api.submit_phonenum),
    url(r'^api/user/submit/vcode/$', user_api.submit_vcode),
    url(r'^api/user/get/profile/$', user_api.get_profile),
    url(r'^user/form/$', user_api.get_form),
    url(r'^api/user/edit/profile/$', user_api.edit_profile),
    url(r'^api/user/upload/avatar/$', user_api.upload_avatar),

]
