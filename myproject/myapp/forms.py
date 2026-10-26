from django import forms
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from .models import Review


class RegisterForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "login",
            "placeholder": "Username kiriting",
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "login",
            "placeholder": "Parol kiriting",
        })
    )

    captcha = CaptchaField()

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Bunday username allaqachon mavjud!"
            )

        return username


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

        widgets = {
            "rating": forms.Select(attrs={
                "class": "form-control"
            }),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Mahsulot haqida fikringiz?"
            })
        }
