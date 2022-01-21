from django.db import models

# Create your models here.
from user.models import User


class Book(models.Model):
    bookname = models.CharField(max_length=100, null=False, blank=False)  # '书名'
    author = models.CharField(max_length=100, null=False, blank=False)  # '作者'
    binding = models.BooleanField(choices=((0, '精装'), (1, '简装')))  # '装订'
    publisher = models.CharField(max_length=100, null=False, blank=False)  # '出版社'
    pubdate = models.DateField(null=False, blank=False)  # '出版年'
    price = models.FloatField(null=False, blank=False)  # '定价'
    pages = models.IntegerField(null=False, blank=False)  # '页数'
    isbn = models.CharField(max_length=30, null=False, blank=False)  # 'isbn'
    summary = models.TextField(null=False, blank=False)  # '内容简介'
    image = models.ImageField(upload_to='uploads/%Y/%m')  # '书籍图片'
    add_date = models.DateTimeField(auto_now=True)  # '添加日期'

    class Meta:
        db_table = 'book'

    def __str__(self):
        return self.bookname


class UserBook(models.Model):
    # 用户id
    user_id = models.IntegerField()
    # 书籍id
    book_id = models.IntegerField()

    class Meta:
        db_table = 'userbook'


class Wish(models.Model):
    # 0--》处于想要但无人赠送  1--》想要且已发出请求  2--》请求已被满足
    launched = models.IntegerField(default=0)
    add_date = models.DateField(auto_now=True)
    book_id = models.IntegerField()
    user_id = models.IntegerField()
    nickname = models.CharField(max_length=32)

    class Meta:
        db_table = 'wish'


class Gift(models.Model):
    launched = models.IntegerField(default=0)
    add_date = models.DateField(auto_now=True)
    book_id = models.IntegerField()
    user_id = models.IntegerField()
    nickname = models.CharField(max_length=32)

    class Meta:
        db_table = 'gift'


class Drift(models.Model):
    recipient_name = models.CharField(max_length=32)
    address = models.CharField(max_length=128)
    message = models.TextField()
    mobile = models.CharField(max_length=11)
    isbn = models.CharField(max_length=30)
    book_name = models.CharField(max_length=64)
    book_author = models.CharField(max_length=64)
    book_img = models.ImageField()
    requester_id = models.IntegerField()
    requester_nickname = models.CharField(max_length=32)
    gifter_id = models.IntegerField()
    gift_id = models.IntegerField()
    gifter_nickname = models.CharField(max_length=32)
    # 该交易单状态 0--》等待邮寄  1--》已邮寄  2--》拒绝
    status = models.IntegerField(default=0)
    add_date = models.DateField(auto_now=True)

    class Meta:
        db_table = 'drift'
