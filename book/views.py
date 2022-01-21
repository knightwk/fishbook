import random
import time
import uuid

from alipay import AliPay
from django.contrib.auth import login
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from book.models import Book, UserBook, Wish, Gift, Drift
from book.task import send_mail_gift, send_mail_req
from fishbook.settings import PUBLIC_KEY, PRIVATE_KEY
from user.models import User


# 上传书籍
def addbook(request):
    if request.method == "POST":
        # 获取书籍信息
        bookname = request.POST.get('bookname')
        author = request.POST.get('author')
        binding = request.POST.get('binding')
        publisher = request.POST.get('publisher')
        pubdate = request.POST.get('pubdate')
        price = request.POST.get('price')
        pages = request.POST.get('pages')
        isbn = request.POST.get('isbn')
        summary = request.POST.get('summary')
        image = request.FILES.get('image')
        # 通过ISBN唯一标识获取书籍
        books = Book.objects.filter(isbn=isbn)
        # 判断该书是否已存在
        if books.exists():
            # 存在则告诉用户该书已经上传过
            return render(request, 'book/add_book.html', {"msg": "该书已被上传过！"})
        # 上传该书籍
        book = Book.objects.create(bookname=bookname,
                                   author=author,
                                   binding=binding,
                                   publisher=publisher,
                                   pubdate=pubdate,
                                   price=price,
                                   pages=pages,
                                   isbn=isbn,
                                   summary=summary,
                                   image=image)
        # 获取上传书籍用户
        user = User.objects.get(pk=request.user.id)
        # 上传用户鱼豆+1
        user.beans += 1
        user.save()
        # 关联书籍与上传者
        UserBook.objects.create(user_id=user.id, book_id=book.id)
        return redirect(reverse('index'))
    # 当用户赠送的书未上传时，获取同名书籍信息
    book_id = request.GET.get('book_id')
    if book_id:
        book = Book.objects.get(id=book_id)
    return render(request, 'book/add_book.html', locals())


def book_detail(request, book_id):
    # 获取要查看详情的书籍
    book = Book.objects.get(pk=book_id)
    # 获取同名同作者书籍的id
    book_ids = [
        i['id'] for i in list(
            Book.objects.filter(
                Q(bookname=book.bookname)
                & Q(author=book.author)).values('id'))
    ]
    # 查看心愿单中该书的需要情况
    wishes = Wish.objects.filter(book_id__in=book_ids)
    # 获取该用户的心愿图书id
    wishes_book_id = list(
        Wish.objects.filter(user_id=request.user.id).values('book_id'))
    wishes_book_id = [i['book_id'] for i in wishes_book_id]

    # 查看赠送单中该书赠送情况
    gifts = Gift.objects.filter(book_id__in=book_ids)
    # 获取该用户赠送的图书id
    gifts_book_id = list(
        Gift.objects.filter(user_id=request.user.id).values('book_id'))
    gifts_book_id = [i['book_id'] for i in gifts_book_id]
    return render(
        request, 'book/book_detail.html', {
            "book": book,
            "wishes_book_id": wishes_book_id,
            "wishes": wishes,
            "gifts_book_id": gifts_book_id,
            "gifts": gifts
        })


# 添加到心愿图书
def add_wish(request, book_id):
    if not request.user.is_authenticated:
        return redirect(reverse('user:login'))
    # 获取用户信息
    user = User.objects.get(pk=request.user.id)
    # 创建一个心愿单
    Wish.objects.create(book_id=book_id,
                        user_id=user.id,
                        nickname=user.nickname)
    return redirect(reverse('book:book_detail', args=(book_id, )))


# 心愿图书列表
def wish_list(request):
    # 获取当前用户心愿图书
    wishes = Wish.objects.filter(Q(user_id=request.user.id) & Q(launched=0))
    # 获取当前用户心愿图书的信息
    wish_books = [Book.objects.get(pk=wish.book_id) for wish in wishes]
    return render(request, 'my_wish.html', {
        "wishes": wishes,
        "wish_books": wish_books
    })


# 添加到赠送图书
def add_gift(request, book_id):
    # 获取用户信息
    user = User.objects.get(pk=request.user.id)
    # 创建赠送单
    Gift.objects.create(book_id=book_id,
                        user_id=user.id,
                        nickname=user.nickname)
    # 用户鱼豆+1
    user.beans += 1
    user.save()
    return redirect(reverse('book:book_detail', args=(book_id, )))


# 赠送图书列表
def gift_list(request):
    # 获取当前用户赠送的图书
    gifts = Gift.objects.filter(Q(user_id=request.user.id) & Q(launched=0))
    # 获取当前用户赠送图书的信息
    gift_books = [Book.objects.get(pk=gift.book_id) for gift in gifts]
    return render(request, 'my_gifts.html', {
        "gifts": gifts,
        "gift_books": gift_books
    })


# 撤销赠送
def redraw_from_gifts(request, book_id):
    # 获取赠送单
    gift = Gift.objects.get(book_id=book_id)
    # 删除该赠送单
    gift.delete()
    return redirect(reverse('book:gift_list'))


# 请求书
def request_book(request, book_id):
    # 判断用户是否登录
    if not request.user.is_authenticated:
        try:
            # 请求邮件中获取被请求用户信息登录
            token = request.GET.get('token')
            wish = cache.get(token)
            req_user = User.objects.get(pk=wish.user_id)
            login(request, req_user)
            return redirect(reverse('book:requestbook', args=[wish.book_id]))
        except:
            return redirect(reverse('user:login'))
    # 获取请求用户信息
    req_user = User.objects.get(pk=request.user.id)
    # 用户鱼豆不足时，进行充值
    if req_user.beans < 2:
        return render(request, 'not_enough_beans.html')
    # 获取该条预赠书记录
    record_gift = Gift.objects.get(book_id=book_id)
    # 获取接受/送出书籍数量
    send_books = Gift.objects.filter(
        Q(user_id=record_gift.user_id) & Q(launched=1)).count()
    receive_books = Wish.objects.filter(
        Q(user_id=record_gift.user_id) & Q(launched=1)).count()
    send_receive = str(send_books) + "/" + str(receive_books)
    # 获取赠书人信息
    gift_user = User.objects.get(pk=record_gift.user_id)
    book = Book.objects.get(pk=book_id)

    if request.method == "POST":
        # 创建交易单
        Drift.objects.create(recipient_name=request.POST.get('recipient_name'),
                             address=request.POST.get('address'),
                             message=request.POST.get('message'),
                             mobile=request.POST.get('mobile'),
                             isbn=book.isbn,
                             book_name=book.bookname,
                             book_author=book.author,
                             book_img=book.image,
                             requester_id=req_user.id,
                             requester_nickname=req_user.nickname,
                             gifter_id=gift_user.id,
                             gift_id=record_gift.id,
                             gifter_nickname=gift_user.nickname)
        # 查找该用户的所有交易单
        drifts = Drift.objects.filter(
            Q(requester_id=req_user.id) | Q(gifter_id=req_user.id))
        # 保存被请求用户信息
        uu_id = str(uuid.uuid4()).replace('-', '')
        timestamp = str(time.time()).split('.')[0]
        token = uu_id + timestamp
        cache.set(token, gift_user)
        # 发送通知邮件
        send_mail_gift.delay(gift_user.id, req_user.id, book.id, token)
        return render(request, 'pending.html', {"drifts": drifts})
    return render(
        request, 'drift.html', {
            "gift_user": gift_user,
            "book": book,
            "req_user": req_user,
            "send_receive": send_receive
        })


# 撤销心愿清单中的书
def redraw_from_wishes(request, book_id):
    # 获取该书的心愿单并删除
    wish = Wish.objects.filter(Q(book_id=book_id) & Q(launched=0))
    wish.delete()
    return redirect(reverse('book:wish_list'))


# 鱼漂
def pending(request):
    if not request.user.is_authenticated:
        try:
            # 获取被请求书用户的信息并登录
            token = request.GET.get('token')
            gift_user = cache.get(token)
            login(request, gift_user)
            return redirect(reverse('book:pending'))
        except:
            return redirect(reverse('user:login'))
    # 获取请求用户信息
    req_user = User.objects.get(pk=request.user.id)
    # 获取当前用户的所有交易单
    drifts = Drift.objects.filter(
        Q(requester_id=req_user.id) | Q(gifter_id=req_user.id))
    return render(request, 'pending.html', {"drifts": drifts})


# 请求用户撤销交易单
def redraw_drift(request, drift_id):
    # 获取当前交易单
    drift = Drift.objects.get(pk=drift_id)
    # 获取当前交易的书籍
    book = Book.objects.get(isbn=drift.isbn)
    # 修改心愿单中交易书籍状态
    wish = Wish.objects.filter(
        Q(book_id=book.id) | Q(user_id=request.user.id)).update(launched=0)
    drift.delete()
    return redirect(reverse('book:pending'))


# 赠书用户已邮寄
def mailed_drift(request, drift_id):
    # 修改订单状态
    drift = Drift.objects.get(pk=drift_id)
    drift.status = 1
    drift.save()
    # 获取邮寄的书
    book = Book.objects.get(isbn=drift.isbn)
    # 修改心愿单中该书的状态
    wish = Wish.objects.filter(
        Q(book_id=book.id) | Q(user_id=drift.requester_id)).first()
    wish.launched = 1
    wish.save()
    # 修改赠送单中该书的状态
    gift = Gift.objects.filter(
        Q(book_id=book.id) | Q(user_id=drift.gifter_id)).first()
    gift.launched = 1
    gift.save()
    # 修改用户鱼豆数量
    user = User.objects.get(pk=request.user.id)
    user.beans += 2
    user.save()
    return redirect(reverse('book:pending'))


# 赠书用户已拒绝
def reject_drift(request, drift_id):
    # 修改订单状态
    drift = Drift.objects.get(pk=drift_id)
    drift.status = 2
    drift.save()
    return redirect(reverse('book:pending'))


# 请求支付的路由
def pay(request):
    money = request.GET.get('money')
    try:
        alipay_public_key_string = open(PUBLIC_KEY).read()
        app_private_key_string = open(PRIVATE_KEY).read()

        alipay = AliPay(
            appid="2021000116696479",
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )

        # 如果你是 Python 3的用户，使用默认的字符串即可
        subject = "购买豆豆"

        trade_no = str(time.time()).replace('.', '')
        ran = ''
        s = '1234567890'
        for i in range(5):
            r = random.choice(s)
            ran += r
        trade_no += ran
        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=trade_no,
            total_amount=money,
            subject=subject,
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )

        # 沙箱环境的网关
        alipay_url = 'https://openapi.alipaydev.com/gateway.do?'

        url = alipay_url + order_string
        return JsonResponse({'status': 200, 'url': url, 'orderid': trade_no})
    except:
        return JsonResponse({'status': 500, 'msg': '支付失败请重试'})


def check_pay(request):
    orderid = request.POST.get('orderid')
    if not orderid:
        return JsonResponse({'status': 500, 'msg': '必须传递订单号'})

    alipay_public_key_string = open(PUBLIC_KEY).read()
    app_private_key_string = open(PRIVATE_KEY).read()

    alipay = AliPay(
        appid="2021000116696479",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    while True:
        response = alipay.api_alipay_trade_query(orderid)
        print(response)
        # 判断response的结果
        if response.get('code') == '10000' and response.get(
                'trade_status') == 'TRADE_SUCCESS':
            money = int(float(response.get('total_amount')))
            request.user.beans += (money * 2)
            request.user.save()
            return JsonResponse({'status': 200, 'msg': '支付成功！'})
        elif response.get('code') == '40004' or (
                response.get('code') == '10000'
                and response.get('trade_status') == 'WAIT_BUYER_PAY'):
            time.sleep(3)
            continue
        else:
            print(response.get('code'))
            print(response.get('trade_status'))
            return JsonResponse({'status': 500, 'msg': '支付失败！'})


# 向某人赠书
def giftbook(request, wish_id):
    # 获取赠书者
    gift_user = User.objects.get(pk=request.user.id)
    # 获取该心愿单
    wish = Wish.objects.get(pk=wish_id)
    # 找到该书信息
    book = Book.objects.get(pk=wish.book_id)
    # 获取请求用户并保存其信息
    req_user = User.objects.get(pk=wish.user_id)
    uu_id = str(uuid.uuid4()).replace('-', '')
    timestamp = str(time.time()).split('.')[0]
    token = uu_id + timestamp
    cache.set(token, wish)
    # 发送右键通知请求者
    send_mail_req.delay(gift_user.id, req_user.id, book.id, token)
    return redirect(reverse('book:book_detail', args=[book.id]))


# 赠送此书时校验
def check_book(request, book_id):
    if not request.user.is_authenticated:
        data = {
            "status": 401,
            "msg": "您目前未登录，请登录！",
            "url": "user/login/",
        }
        return JsonResponse(data)
    # 获取当前用户的上传书籍id
    book_ids = [
        i['book_id'] for i in UserBook.objects.filter(
            user_id=request.user.id).values('book_id')
    ]
    if book_id not in book_ids:
        data = {
            "status": 400,
            "msg":
            f"该书您还未上传，无法赠送！请点击<a href='/book/addbook/?book_id={book_id}'>上传</a>先上传此书！",
            "url": "book/book_detail/",
        }
        return JsonResponse(data)
    data = {
        "status": 200,
        "msg": "该书已上传，可以赠送！",
        "url": "book/addgift/",
    }
    return JsonResponse(data)


def search(request):
    # 获取搜索关键字
    q = request.GET.get('q')
    # 获取数据集
    books = Book.objects.filter(Q(bookname__contains=q) | Q(isbn__contains=q))
    # 获取页码
    page = int(request.GET.get("page", 1))
    # 获取每页显示数据量
    per_page = int(request.GET.get("per_page", 1))
    # 获取分页器
    paginator = Paginator(books, per_page)
    # 获取总页数
    page_range = paginator.page_range
    # 获取当前页数据
    page_single = paginator.page(page)
    return render(request, 'search_result.html', locals())
