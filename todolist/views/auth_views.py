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

from ..forms import RegisterForm, ConfirmEmailForm, EditPasswordForm, ChangeEmailForm, EmailForm, ChooseNewPasswordForm
from .email_views import send_email


# View for registering
def register_form(request):
    # Can't register if already authenticated
    if request.user.is_authenticated:
        return redirect('index')

    # Set the form
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user_email = form.cleaned_data['email']

            # Create a random code which will be sent to the user to authenticate their email address
            user_authentication_code = random.randint(100000, 999999)

            message = f"Your one-time password is: {user_authentication_code}"

            msg = MIMEText(message)
            msg["Subject"] = "To Do List: Your One-Time Password"

            send_email(msg, msg["Subject"], user_email)

            # Cache the code and email
            cache.set(f"otp_{user_email}", user_authentication_code, timeout=300)
            cache.set(f"form_data_{user_email}", form.cleaned_data, timeout=300)
            cache.set("current_email", user_email, timeout=300)

            return redirect("confirm_email")

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def confirm_email_view(request):
    # Can only be accessed when redirected
    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    if request.method == 'POST':
        form = ConfirmEmailForm(request.POST)

        if form.is_valid():
            # Get from data and cached data
            entered_otp = form.cleaned_data['token']
            user_email = cache.get("current_email")
            cached_otp = cache.get(f"otp_{user_email}")
            form_data = cache.get(f"form_data_{user_email}")

            # Check if cached data is still valid
            if not user_email or not cached_otp or not form_data:
                form.add_error(None, "Session expired. Please register again.")
                return render(request, "register.html", {"form": form})

            # Check if code entered is correct
            if str(entered_otp) == str(cached_otp):

                # Create and save the user
                try:
                    user = User(username=form_data['username'], email=form_data['email'])
                    user.set_password(form_data['password1'])
                    user.save()

                    # Authenticate and login the user
                    new_user = authenticate(username=form_data['username'], password=form_data['password1'])
                    if new_user is not None:
                        login(request, new_user)

                    # Delete the cache
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
    # Can't login if already authenticated
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == "POST":
        # Retireve the username and password from database
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate  user
        user = authenticate(request, username=username, password=password)

        # Check if credentials are valid
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            error_message = "Invalid username or password."
            return render(request, "login.html", {"error_message": error_message})

    return render(request, "login.html")


@login_required(login_url='login')
# Logout the user
def logout_view(request):
    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    logout(request)
    return render(request, 'todolist/logout.html')


@login_required(login_url='login')
def change_user_password(request):
    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    form = EditPasswordForm(request.POST)

    if request.method == "POST":
        # Get user data
        user = request.user

        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            # Validate if the old password is the same as the entered one
            if user.check_password(old_password):
                if str(new_password) == str(confirm_password):
                    try:
                        # Validate password strength
                        validate_password(new_password)

                        # Change the password and save
                        user.set_password(new_password)
                        messages.success(request, "Password changed successfully!")
                        user.save()
                        login(request, user)

                        return redirect('settings')

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
    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    form = ChangeEmailForm(request.POST)

    if request.method == "POST":
        if form.is_valid():

            old_email = request.user.email.lower()
            new_email = form.cleaned_data['new_email']

            # Check if old email is the same as the new one
            if old_email == new_email:
                messages.error(request, "New Email Address cannot be the same as the old one")
                return redirect('change_email')

            # Create a random code, cache the data and send an email
            user_authentication_code = random.randint(100000, 999999)

            cache.set("cached_email", new_email, timeout=300)
            cache.set("cached_authentication_code", user_authentication_code, timeout=300)

            message = f"Your one-time password is: {user_authentication_code}"
            msg = MIMEText(message)
            msg["Subject"] = "To Do List: Your One-Time Password"

            send_email(msg, msg["Subject"], new_email)

            return redirect('change_email_confirmation')

    else:
        form = ChangeEmailForm()

    return render(request, 'todolist/change_email.html', {"form": form})


def change_email_confirmation(request):
    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    if request.method == "POST":
        form = ConfirmEmailForm(request.POST)
        user = request.user

        if form.is_valid():
            # Get user entered token and cached data
            user_entered_token = form.cleaned_data['token']

            cached_email = cache.get("cached_email")
            cached_authentication_code = cache.get("cached_authentication_code")

            # Check whether the cached data is still valid
            if not cached_email or not cached_authentication_code:
                messages.error(request, "Session expired.")
                return redirect('settings')

            # Check whether user entered code is correct
            if str(user_entered_token) == str(cached_authentication_code):
                user.email = cached_email
                user.save()

                # Delete cached data
                cache.delete(f"current_email")
                cache.delete(f"current_authentication_code")

                messages.success(request, "Email has been changed successfully!")
                return redirect("settings")
            else:
                messages.error(request, "Invalid code. Please try again.")
                return redirect("change_email_confirmation")

    else:
        form = ConfirmEmailForm()

    return render(request, "change_email_confirmation.html", {"form": form})


def choose_email(request):
    user = request.user

    if user.is_authenticated:
        return redirect("index")

    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            #Check whether email is associated with an account
            email = form.cleaned_data['email']
            email_list = list(User.objects.values_list("email", flat=True))

            if email not in email_list:
                messages.error(request, "Email is not associated with any accounts.")
                return redirect("choose_email")

            #Send verification email and cache data
            user_email = form.cleaned_data['email']

            user_authentication_code = random.randint(100000, 999999)

            cache.set("cached_code", user_authentication_code, timeout=300)
            cache.set("user_email", user_email, timeout=600)

            message = f"Your one-time password is: {user_authentication_code}"
            msg = MIMEText(message)
            msg["Subject"] = "To Do List: Your One-Time Password"
            cache.set("cached_authentication_code", user_authentication_code, timeout=300)

            send_email(msg, msg["Subject"], user_email)
            return redirect("forgot_password_confirmation")

    else:
        form = EmailForm()

    return render(request, "todolist/choose_email.html", {"form": form})


def forgot_password_confirmation(request):
    user = request.user

    if user.is_authenticated:
        return redirect("index")

    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    if request.method == "POST":
        form = ConfirmEmailForm(request.POST)

        #Get cached data
        cached_code = cache.get("cached_code")

        if form.is_valid():
            entered_code = form.cleaned_data['token']

            #Check whether cached data is valid
            if not cached_code:
                messages.error(request, "Session has expired")
                return redirect("login")

            #Check if entered code is correct
            if str(cached_code) == str(entered_code):
                cache.delete(f"cached_code")
                return redirect("forgot_password")

    else:
        form = ConfirmEmailForm()

    return render(request, "todolist/forgot_password_confirmation.html", {"form": form})


def forgot_password(request):

    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    if request.method == "POST":
        form = ChooseNewPasswordForm(request.POST)

        if form.is_valid():
            user_email = cache.get("user_email")

            #Check cached data
            if not user_email:
                messages.error(request, "Session has expired")
                return redirect("login")

            user = User.objects.get(email=user_email)
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            try:
                #Check new password strength
                validate_password(new_password)

                if str(new_password) == str(confirm_password):

                    #Delete cached data and set new password
                    cache.delete(f"user_email")
                    user.set_password(new_password)

                    messages.success(request, "Password changed successfully!")

                    user.save()
                    login(request, user)
                    return redirect("settings")

                else:

                    messages.error(request, "Password do not match.")
                    return redirect("forgot_password")

            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)

                return redirect("forgot_password")
    else:
        form = ChooseNewPasswordForm()

    return render(request, "todolist/forgot_password.html", {"form": form})
