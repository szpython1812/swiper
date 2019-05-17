from django.db import models

# Create your models here.
"""
vip
    vip1
    vip2
    vip3
    
每个vip等级对应不同的权限
vip1: 喜欢,不喜欢
vip2: 超级喜欢,查看喜欢我的人
vip3: 超级喜欢,查看喜欢我的人, 反悔

用户:



权限:


vip和用户: 多对一, 在多的那一端增加一个字段.

vip和权限: 多对多, 需要创建中间表.

用户权限 : 没有直接的关系, 通过vip表进行关联.

用户, 组, 权限, auth,group permissions,user
"""


class Vip(models.Model):
    name = models.CharField(max_length=64, verbose_name='会员名称')
    level = models.IntegerField(default=1, verbose_name='会员等级')
    price = models.FloatField(verbose_name='会员价格')

    # 这个vip所具有的权限
    def perms(self):
        # 根据vip id去关系表中找到对应perm_id
        perm_list = VipPerm.objects.filter(vip_id=self.id).only('perm_id')
        perm_id_list = [p.perm_id for p in perm_list]
        # 根据id_list找权限
        vip_perms = Permission.objects.filter(id__in=perm_id_list)
        return vip_perms

    # 判断是否具有某权限
    def has_perm(self, perm):
        for vip_perm in self.perms():
            if perm == vip_perm.name:
                return True
        else:
            return False


    def __str__(self):
        return f'<{self.name} {self.level}>'


class Permission(models.Model):
    name = models.CharField(max_length=64, verbose_name='权限名称')
    description = models.CharField(max_length=256, verbose_name='权限描述')

    def __str__(self):
        return f'<{self.name}>'


class VipPerm(models.Model):
    """vip和权限的关系表"""
    perm_id = models.IntegerField(verbose_name='权限id')
    vip_id = models.IntegerField(verbose_name='vipid')

