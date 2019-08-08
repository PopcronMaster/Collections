from django.db import models


class Vip(models.Model):
    """vip模型"""
    name = models.CharField(max_length=64, verbose_name='会员名称')
    level = models.IntegerField(default=0, verbose_name='等级')
    price = models.FloatField(verbose_name='价格')

    def __str__(self):
        return f'<{self.name}>'

    def has_perm(self, perm_name):
        # 找到vip对应的权限,查看perm_name在不在我们查出来的权限中.
        relations = VipPermRelation.objects.filter(vip_id=self.id).only('perm_id')
        perm_id_list = [r.perm_id for r in relations]
        return Permission.objects.filter(id__in=perm_id_list).filter(name=perm_name).exists()


class Permission(models.Model):
    """权限模块"""
    name = models.CharField(max_length=64, verbose_name='权限名称')
    description = models.TextField(verbose_name='权限描述')

    def __str__(self):
        return f'<{self.name}>'


class VipPermRelation(models.Model):
    vip_id = models.IntegerField(verbose_name='vipid')
    perm_id = models.IntegerField(verbose_name='权限id')

