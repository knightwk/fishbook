from celery import shared_task
from django.core.mail import send_mail
from django.template import loader

from book.models import Book
from fishbook.settings import EMAIL_HOST_USER
from user.models import User


@shared_task
def send_mail_gift(gift_user_id, req_user_id, book_id, token):
    gift_user = User.objects.get(pk=gift_user_id)
    req_user = User.objects.get(pk=req_user_id)
    book = Book.objects.get(pk=book_id)
    subject = "用户请求赠书"
    message = loader.render_to_string(
        'email/get_gift.html',
        {
            "gift_user": gift_user,
            "req_user": req_user,
            "book": book,
            "token": token,
        }
    )
    send_mail(subject=subject, message=message, from_email=EMAIL_HOST_USER, recipient_list=[gift_user.email],
              html_message=message)


@shared_task
def send_mail_req(gift_user_id, req_user_id, book_id, token):
    gift_user = User.objects.get(pk=gift_user_id)
    req_user = User.objects.get(pk=req_user_id)
    book = Book.objects.get(pk=book_id)
    subject = "用户赠书"
    message = loader.render_to_string(
        'email/satisify_wish.html',
        {
            "gift_user": gift_user,
            "req_user": req_user,
            "book": book,
            "token": token,
        }
    )
    send_mail(subject=subject, message=message, from_email=EMAIL_HOST_USER, recipient_list=[req_user.email],
              html_message=message)
