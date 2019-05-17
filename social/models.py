from django.db import models

# Create your models here.


class Swipe(models.Model):
    MARK = (
        ('like', 'like'),
        ('dislike', 'dislike'),
        ('superlike', 'superlike'),
    )
    uid = models.IntegerField(verbose_name='滑动者id')
    sid = models.IntegerField(verbose_name='被滑者id')
    mark = models.CharField(choices=MARK, max_length=20, verbose_name='滑动类型')
    swipe_time = models.DateTimeField(auto_now_add=True, verbose_name='滑动时间')

    # 喜欢
    @classmethod
    def like(cls, uid, sid):
        cls.objects.create(uid=uid, sid=sid, mark='like')

    @classmethod
    def superlike(cls, uid, sid):
        cls.objects.create(uid=uid, sid=sid, mark='superlike')

    @classmethod
    def dislike(cls, uid, sid):
        cls.objects.create(uid=uid, sid=sid, mark='dislike')

    # 判断是否喜欢某人
    @classmethod
    def has_like_someone(cls, sid):
        return cls.objects.filter(uid=sid, mark__in=['like', 'superlike']).exists()


class Friend(models.Model):
    uid1 = models.IntegerField()
    uid2 = models.IntegerField()

    @classmethod
    def make_friends(cls, uid, sid):
        # 调整uid,和sid的大小,调整一下顺序
        uid1, uid2 = (uid, sid) if uid < sid else (sid, uid)
        cls.objects.create(uid1=uid1, uid2=uid2)




