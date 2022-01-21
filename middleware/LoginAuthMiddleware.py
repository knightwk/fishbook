from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

# 需要验证用户登录权限的
login_required = [
    # 用户相关
    '/user/personal/',
    '/user/changepwd/',
    # 心愿单
    '/book/wishlist/',
    # 赠送单
    '/book/giftlist/',
]


class LoginAuthMiddleware(MiddlewareMixin):
    def process_request(self, request, *args, **kwargs):
        # print('path:', request.path)
        if request.path in login_required:
            # 用户的登录验证
            if not request.user.is_authenticated:
                return render(request, 'auth/login.html')
