from django.core.paginator import Paginator
from django.shortcuts import render

from book.models import Book, Drift


def index(request):
    # 获取已经完成邮寄的图书isbn
    drifts = [d['isbn'] for d in Drift.objects.filter(status=1).values('isbn')]
    # 获取所有上传未邮寄的图书
    books = Book.objects.exclude(isbn__in=drifts).order_by('-add_date')
    # 页码
    page = int(request.GET.get('page', 1))
    # 每一页的数据
    per_page = int(request.GET.get('per_page', 2))
    # 分页器
    paginator = Paginator(books, per_page)
    # 获取单页数据项
    page_single = paginator.page(page)
    # 获取页码
    page_range = paginator.page_range
    return render(request, 'index.html', locals())
