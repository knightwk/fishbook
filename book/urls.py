from django.urls import path

from book import views

app_name = 'book'

urlpatterns = [
    # 书籍添加
    path('addbook/', views.addbook, name='addbook'),
    # 书籍详情
    path('bookdetail/<int:book_id>/', views.book_detail, name='book_detail'),
    # 搜索图书
    path('search/', views.search, name='search'),

    # 请求书籍
    path('requestbook/<int:book_id>/', views.request_book, name='requestbook'),
    # 赠送书籍
    path('giftbook/<int:wish_id>/', views.giftbook, name='giftbook'),

    # 添加到心愿单
    path('addwish/<int:book_id>/', views.add_wish, name='add_wish'),
    # 心愿图书列表
    path('wishlist/', views.wish_list, name='wish_list'),
    # 撤销心愿
    path('redraw_from_wishes/<int:book_id>/', views.redraw_from_wishes, name='redraw_from_wishes'),

    # 赠书时判断是否有此书
    path('checkbook/<int:book_id>/', views.check_book, name='check_book'),
    # 添加到赠送单
    path('addgift/<int:book_id>/', views.add_gift, name='add_gift'),
    # 赠送列表
    path('giftlist/', views.gift_list, name='gift_list'),
    # 撤销赠送
    path('redraw_from_gifts/<int:book_id>/', views.redraw_from_gifts, name='redraw_from_gifts'),

    # 鱼漂
    path('pending/', views.pending, name='pending'),
    # 请求者撤销请求
    path('redraw_drift/<int:drift_id>/', views.redraw_drift, name='redraw_drift'),
    # 被请求者已邮寄
    path('mailed_drift/<int:drift_id>/', views.mailed_drift, name='mailed_drift'),
    # 被请求者拒绝邮寄
    path('reject_drift/<int:drift_id>/', views.reject_drift, name='reject_drift'),

    # 支付充值鱼豆
    path('pay/', views.pay, name='pay'),
    # 支付响应
    path('checkpay/', views.check_pay, name='checkpay'),
]
