# forms.py
from random import choices

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from todolist.models import AddItem


#Form to add new task to your List
class TaskForm(forms.Form):

    name = forms.CharField(max_length=100, required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    image = forms.ImageField(required=False)


#Model form that takes a task and allows you to edit it
class EditTaskForm(forms.ModelForm):

    class Meta:
        model = AddItem
        fields = ['text', 'due_date', 'picture']
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'}), }


#Form to change your password
class EditPasswordForm(forms.Form):

    old_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Old password'}))
    new_password= forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))


#Custom registration form
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'e.g. myemail@address.com'}))
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '').lower()

        # Validate email case-insensitively
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email already registered")

        return cleaned_data


    def save(self, commit=True):
        user = User(username=self.cleaned_data['username'],
                    email=self.cleaned_data['email'].lower(),
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
    token = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. 123456'}), max_length=6)

class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'e.g. myemail@address.com'}))

    def clean_new_email(self):
        return self.cleaned_data['new_email'].lower()

class EmailForm(forms.Form):
    email=forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'e.g. myemail@address.com'}))

    def clean_email(self):
        return self.cleaned_data['email'].lower()

class ChooseNewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}))
    confirm_password= forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

class SetNotificationForm(forms.Form):
    notification_date=forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    notification_time=forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=True)