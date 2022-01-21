from django.urls import path

from user import views

app_name = 'user'
urlpatterns = [
    # 注册相关
    path('checkemail/', views.check_email),
    path('checkphone/', views.check_phone),
    path('register/', views.register, name='register'),
    path('active/', views.active, name='active'),
    # 登录
    path('login/', views.user_login, name='login'),
    # 忘记密码
    path('forgetpwdrequest/', views.forgetpwdrequest, name='forgetpwdrequest'),
    path('forgetpwd/', views.forgetpwd, name='forgetpwd'),
    # 个人中心
    path('personal/', views.personal, name='personal'),
    path('changepwd/', views.changepwd, name='changepwd'),
    path('logout/', views.user_logout, name='logout'),
]
