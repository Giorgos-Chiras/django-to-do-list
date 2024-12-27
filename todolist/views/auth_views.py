import random
from email.mime.text import MIMEText

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages

from ..forms import RegisterForm, ConfirmEmailForm, EditPasswordForm, ChangeEmailForm
from .email_views import send_email



def register_form(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            user_authentication_code = random.randint(100000, 999999)
            message = f"Your one-time password is: {user_authentication_code}"

            msg = MIMEText(message)
            msg["Subject"] = "To Do List: Your One-Time Password"

            send_email(msg, msg["Subject"], user_email)

            cache.set(f"otp_{user_email}", user_authentication_code, timeout=300)
            cache.set(f"form_data_{user_email}", form.cleaned_data, timeout=300)
            cache.set("current_email", user_email, timeout=300)

            return redirect("confirm_email")

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def confirm_email_view(request):
    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    if request.method == 'POST':
        form = ConfirmEmailForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['token']
            user_email = cache.get("current_email")
            cached_otp = cache.get(f"otp_{user_email}")
            form_data = cache.get(f"form_data_{user_email}")

            if not user_email or not cached_otp or not form_data:
                form.add_error(None, "Session expired. Please register again.")
                return render(request, "register.html", {"form": form})

            if str(entered_otp) == str(cached_otp):
                try:
                    user = User(username=form_data['username'], email=form_data['email'])
                    user.set_password(form_data['password1'])
                    user.save()

                    new_user = authenticate(username=form_data['username'], password=form_data['password1'])
                    if new_user is not None:
                        login(request, new_user)

                    cache.delete(f"otp_{user_email}")
                    cache.delete(f"form_data_{user_email}")
                    cache.delete("current_email")

                    return redirect("index")

                except Exception as e:
                    form.add_error(None, "An error occurred while saving the user. Please try again.")
            else:
                form.add_error('token', "Invalid OTP. Please try again.")
                return render(request, "confirm_email.html", {"form": form})
    else:
        form = ConfirmEmailForm()

    return render(request, "confirm_email.html", {"form": form})


def login_form(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            error_message = "Invalid username or password."
            return render(request, "login.html", {"error_message": error_message})

    return render(request, "login.html")


@login_required(login_url='login')
def logout_view(request):
    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    logout(request)
    return render(request, 'todolist/logout.html')


@login_required(login_url='login')
def change_user_password(request):
    form = EditPasswordForm(request.POST)

    if request.method == "POST":
        user = request.user

        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            if user.check_password(old_password):
                if str(new_password) == str(confirm_password):
                    try:
                        validate_password(new_password)

                        user.set_password(new_password)
                        messages.success(request, "Password changed successfully!")
                        user.save()
                        login(request, user)

                        return redirect('edit_password')

                    except ValidationError as e:
                        for error in e.messages:
                            messages.error(request, error)
                else:
                    messages.error(request, "New passwords do not match.")
            else:
                messages.error(request, "Old password is incorrect.")
    else:
        form = EditPasswordForm()

    return render(request, 'todolist/edit_password.html', {"form": form})


@login_required(login_url='login')
def change_email(request):
    form=ChangeEmailForm(request.POST)

    if request.method=="POST":
        if form.is_valid():

            old_email = request.user.email
            new_email = form.cleaned_data['new_email']

            if old_email == new_email:
                messages.error(request, "New Email Address cannot be the same as the old one")
                return redirect('change_email')

            user_authentication_code = random.randint(100000, 999999)

            cache.set("cached_email", new_email, timeout=300)
            cache.set("cached_authentication_code", user_authentication_code, timeout=300)

            message = f"Your one-time password is: {user_authentication_code}"
            msg = MIMEText(message)
            msg["Subject"] = "To Do List: Your One-Time Password"

            send_email(msg, msg["Subject"], old_email)

            return redirect('change_email_confirmation')

    else:
        form = ChangeEmailForm()

    return render(request,'todolist/change_email.html',{"form":form})


def change_email_confirmation(request):
    if request.method == "POST":
        form=ConfirmEmailForm(request.POST)
        user=request.user

        if form.is_valid():
            user_entered_token=form.cleaned_data['token']

            cached_email = cache.get("cached_email")
            cached_authentication_code = cache.get("cached_authentication_code")

            if not cached_email or not cached_authentication_code:
                messages.error(request, "Session expired.")
                return redirect('change_email_confirmation')

            if str(user_entered_token) == str(cached_authentication_code):
                user.email=cached_email
                user.save()

                cache.delete(f"current_email")
                cache.delete(f"current_authentication_code")

                messages.success(request, "Email has been changed successfully!")
                return redirect("change_email_confirmation")
            else:
                messages.error(request, "Invalid code. Please try again.")
                return redirect("change_email_confirmation")

    else:
        form=ConfirmEmailForm()


    return render(request,"change_email_confirmation.html",{"form":form})







