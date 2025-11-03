from django import forms
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField

#captcha
class CustomAuthenticationForm(AuthenticationForm):
    captcha = CaptchaField() 
