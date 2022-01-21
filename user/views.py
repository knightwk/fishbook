import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from user.forms import UserFrom

# Create your views here.
from user.models import User
from user.task import send_email, send_email_forgetpwd


# 邮箱校验
def check_email(request):
    email = request.GET.get('email')
    users = User.objects.filter(email=email)
    if users.exists():
        data = {
            "status": 400,
            "msg": "该邮箱已被注册！",
        }
        return JsonResponse(data)
    data = {
        "status": 200,
        "msg": "该邮箱可以注册！",
    }
    return JsonResponse(data)


# 手机号校验
def check_phone(request):
    phone = request.GET.get('phone')
    users = User.objects.filter(phone=phone)
    if users.exists():
        data = {
            "status": 400,
            "msg": "该手机号已被注册！",
        }
        return JsonResponse(data)
    data = {
        "status": 200,
        "msg": "该手机号可以注册！",
    }
    return JsonResponse(data)


# 注册
@csrf_exempt
def register(request):
    if request.method == "POST":
        # 加载request.POST里面的数据
        uform = UserFrom(request.POST)
        if uform.is_valid():
            data = uform.cleaned_data
            # 创建用户
            try:
                user = User.objects.create_user(
                    username=data['phone'],
                    password=data['password'],
                    email=data['email'],
                    nickname=data['nickname'],
                    phone=data['phone']
                )
                if user:
                    # 发送激活邮件
                    code = str(uuid.uuid4()).replace('-', '')
                    # f放到缓存
                    cache.set(code, user)
                    # 发送邮件
                    send_email.delay(code, data['email'])
                    return HttpResponse("注册成功，快去邮箱激活吧！")
            except Exception as err:
                print("user register--------------->", err)
                return render(request, 'auth/register.html')
    return render(request, 'auth/register.html')


# 激活用户
def active(request):
    # 获取code的值
    code = request.GET.get('id')
    # 根据code找到对应的用户
    user = cache.get(code)
    if user:
        # 更新用户状态
        user.is_active = True
        user.save()
        # 跳转到登录页面
        return redirect(reverse('user:login'))
    else:
        return redirect(reverse('index'))


# 用户登录
def user_login(request):
    # 只有使用abstractuser才可以使用
    # 只能验证用户名和密码
    if request.method == "POST":
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        user = User.objects.filter(username=phone).first()
        # 该用户是否存在且激活
        if user and user.is_active:
            user = authenticate(username=phone, password=password)
            if user:
                # 完成了session的保存，放到request对象一份
                login(request, user)
                # books = Book.objects.all()
                return redirect(reverse('index'))
            return render(request, 'auth/login.html', {"msg": "密码输入错误！"})
        else:
            return render(request, 'auth/login.html', {"msg": "该用户不存在或者未激活！"})
    return render(request, 'auth/login.html')


# 忘记密码修改申请
def forgetpwdrequest(request):
    if request.method == "POST":
        # 邮箱
        email = request.POST.get('email')
        try:
            # 数据库查询该用户
            user = User.objects.get(email=email)
            code = str(uuid.uuid4()).replace('-', '')
            cache.set(code, user)
            send_email_forgetpwd(code, email)
            return HttpResponse("重置密码链接已发送成功，请前去邮箱查收！")
        except:
            return render(request, 'auth/forget_password_request.html', {"message": "不存在此邮箱用户！"})
    return render(request, 'auth/forget_password_request.html')


# 忘记密码修改
def forgetpwd(request):
    # 获取数据
    if request.method == "POST":
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        code = request.POST.get('code')
        # 判断新密码两次输入是否一致
        if password1 != password2:
            return render(request, 'auth/forget_password.html', {"msg": "两次密码输入不一致！"})
        # 获取用户信息并修改密码
        user = cache.get(code)
        user.set_password(password2)
        user.save()
        return render(request, 'auth/login.html', {"msg": "重置密码成功！"})
    code = request.GET.get('id')
    return render(request, 'auth/forget_password.html', {"code": code})


# 个人中心
def personal(request):
    return render(request, 'personal.html', {"user": request.user})


# 用户登出
def user_logout(request):
    logout(request)
    return redirect(reverse('index'))


# 个人中心修改密码
def changepwd(request):
    if request.method == "POST":
        # 获取数据
        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        # check_password()方法可以进行密码校验
        if not request.user.check_password(old_password):
            return render(request, 'auth/change_password.html', {"msg": "原密码输入有误！"})
        if new_password1 != new_password2:
            return render(request, 'auth/change_password.html', {"msg": "两次密码输入不一致！"})
        # set_password()方法可以设置密码
        request.user.set_password(make_password(new_password2))
        request.user.save()
        return render(request, 'personal.html', {"user": request.user, "msg": "修改密码成功！"})
    return render(request, 'auth/change_password.html', {"user": request.user})
