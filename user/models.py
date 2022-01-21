from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    # 昵称
    nickname = models.CharField(max_length=8, null=False, blank=False)
    # 手机号码
    phone = models.CharField(max_length=11, unique=True, null=False, blank=False)
    # 邮箱
    email = models.EmailField(max_length=80, unique=True, null=False, blank=False)
    # 是否激活
    is_active = models.BooleanField(default=False)
    # 鱼豆数量
    beans = models.IntegerField(default=0)
    # 送出数量
    send_counter = models.IntegerField(default=0)
    # 收到数量
    receive_counter = models.IntegerField(default=0)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.username
