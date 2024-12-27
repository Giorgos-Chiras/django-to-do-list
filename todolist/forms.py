# forms.py
from random import choices

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.template.context_processors import request

from todolist.models import AddItem


class TaskForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    image = forms.ImageField(required=False)


class EditTaskForm(forms.ModelForm):
    class Meta:
        model = AddItem
        fields = ['text', 'due_date', 'picture']
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'}), }


class EditPasswordForm(forms.Form):
    old_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Old password'}))
    new_password= forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        email = cleaned_data.get('email')
        email_list = list(User.objects.values_list("email", flat=True))

        if email in email_list:
            raise forms.ValidationError("Email already registered")

        return cleaned_data

    def save(self, commit=True):
        user = User(username=self.cleaned_data['username'],
                    email=self.cleaned_data['email'],
                    password=self.cleaned_data['password1'])

        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


subject_choices = (
    ('1', "Account Issues"),
    ('2', "Task Management"),
    ('3', "Feature Requests"),
    ('4', "Bug Reports"),
    ('5', "General Inquiry"),
    ('6', "Feedback"),
    ("7", "Other"))


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    subject = forms.ChoiceField(choices=subject_choices)
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your message'}))


class ConfirmEmailForm(forms.Form):
    token = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Token'}), max_length=6)

class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'New Email'}))

