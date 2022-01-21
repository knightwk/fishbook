from django.core.mail import send_mail

from celery import shared_task

from fishbook.settings import EMAIL_HOST_USER


@shared_task
def send_email(code, email):
    subject = "新注册用户激活"
    message = '亲爱的用户你好！欢迎注册xxx网站，当前正在进行用户激活，请点击链接激活：<a href="http://116.85.30.63:8000/user/active/?id={}">激活用户</a>' \
              '<br> 或者直接复制下面的地址访问：http://116.85.30.63:8000/user/active/?id={}'.format(code, code)
    send_mail(subject=subject,
              message=message,
              from_email=EMAIL_HOST_USER,
              recipient_list=[email],
              html_message=message)


@shared_task
def send_email_forgetpwd(code, email):
    subject = "密码忘记重置"
    message = '亲爱的用户你好！欢迎登录xxx网站，当前正在进行用户密码忘记重置，请点击链接重置：<a href="http://116.85.30.63:8000/user/forgetpwd/?id={}">重置密码</a>' \
              '<br> 或者直接复制下面的地址访问：http://116.85.30.63:8000/user/forgetpwd/?id={}'.format(code, code)
    send_mail(subject=subject,
              message=message,
              from_email=EMAIL_HOST_USER,
              recipient_list=[email],
              html_message=message)
