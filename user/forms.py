from django import forms

from user.models import User


class UserFrom(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'password', 'phone', 'email']
