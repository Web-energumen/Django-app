from django.contrib.auth.forms import (AuthenticationForm, UserChangeForm,
                                       UserCreationForm)

from .models import User


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2',
        ]


class ProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = [
            'image',
            'first_name',
            'last_name',
            'username',
            'email',
        ]
