import random
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import smtplib
import os
from email.mime.text import MIMEText

from django.contrib.auth.models import User
from django.core.cache import cache

from .forms import TaskForm, RegisterForm, EditTaskForm, ContactForm, subject_choices, ConfirmEmailForm
from .models import AddItem
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.shortcuts import render, redirect


def send_email(message, subject, to_email=None):
    from_email = "chiras.to.do.list@gmail.com"
    email_password = os.getenv('EMAIL_HOST_PASSWORD')

    # Create the SMTP connection
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Encrypt connection
        server.login(from_email, email_password)

        if to_email is None:
            server.sendmail(from_email, from_email, subject,message.as_string())

        else:
            server.sendmail(from_email, to_email, subject,message.as_string())


def register_form(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Get user email and generate OTP
            user_email = form.cleaned_data['email']
            user_authentication_code = random.randint(100000, 999999)

            # Send the OTP via email
            message = f"Your one-time password is: {user_authentication_code}"
            subject = "To Do List: Your One-Time Password"

            send_email(
                MIMEText(message, 'plain'),
                "To Do List: Your One-Time Password",
                user_email
            )

            # Cache OTP and form data
            cache.set(f"otp_{user_email}", user_authentication_code, timeout=300)
            cache.set(f"form_data_{user_email}", form.cleaned_data, timeout=300)
            cache.set("current_email", user_email, timeout=300)

            # Redirect to OTP confirmation
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

            # Retrieve user entered token
            entered_otp = form.cleaned_data['token']

            # Retrieve cached OTP and form data
            user_email = cache.get("current_email")
            cached_otp = cache.get(f"otp_{user_email}")
            form_data = cache.get(f"form_data_{user_email}")

            if not user_email or not cached_otp or not form_data:
                form.add_error(None, "Session expired. Please register again.")
                return render(request, "register.html", {"form": form})

            # Check if user entered OTP is correct
            if str(entered_otp) == str(cached_otp):
                try:

                    # Create the user using form data
                    user = User(
                        username=form_data['username'],
                        email=form_data['email'],
                    )
                    user.set_password(form_data['password1'])
                    user.save()

                    # Authenticate and log in the user
                    new_user = authenticate(
                        username=form_data['username'],
                        password=form_data['password1'],
                    )

                    if new_user is not None:
                        login(request, new_user)

                    # Clear cache
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
def task_form(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = AddItem(
                text=form.cleaned_data['name'],
                due_date=form.cleaned_data['date'],
                picture=form.cleaned_data.get('image'),
                user=request.user
            )
            task.save()
            return redirect('index')
    else:
        form = TaskForm()

    return render(request, "todolist/edit.html", {"form": form})


def edit_task(request, part_id=None):
    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    if part_id is None:
        return redirect('index')

    _object = AddItem.objects.get(pk=part_id)
    if request.method == "POST":
        form = EditTaskForm(request.POST, request.FILES, instance=_object)
        if form.is_valid():
            form.save()
            return redirect('index')

    else:
        form = EditTaskForm(instance=_object)

    return render(request, "todolist/edit_task.html", {"form": form, "part_id": part_id})


@login_required(login_url='login')
def delete_view(request, part_id=None):
    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    if part_id is None:
        return redirect("index")

    _object = AddItem.objects.get(pk=part_id)
    _object.delete()
    render(request, 'todolist/index.html')
    return redirect('index')


@login_required(login_url='login')
def logout_view(request):
    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    logout(request)
    return render(request, 'todolist/logout.html')


def change_confirmation_view(request, part_id=None):
    if not request.META.get('HTTP_REFERER'):
        return redirect('index')

    if part_id is None:
        return redirect("index")

    _object = AddItem.objects.get(pk=part_id)
    _object.completed = not _object.completed
    _object.save()
    render(request, 'todolist/index.html')
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@login_required(login_url='login')
def about_view(request):
    form = ContactForm(request.POST)

    if request.method == "POST":

        user_email = request.user.email
        if form.is_valid():

            # Get cleaned data from the form
            user_name = form.cleaned_data['name']
            message = form.cleaned_data['message']
            subject = form.cleaned_data['subject']

            for id, name in subject_choices:
                if id == subject:
                    subject = name
                    break

            msg = MIMEText(message)
            msg["Subject"] = f"New contact from {user_name} ({user_email}) Subject: {subject}"

            send_email(msg, msg['Subject'])

            return redirect('index')

    return render(request, 'todolist/about.html', {"form": form})


class all_to_do(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = AddItem
    template_name = "todolist/index.html"

    def get_queryset(self):
        return AddItem.objects.filter(user=self.request.user).order_by('due_date')


class completed_view(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = AddItem
    template_name = "todolist/completed.html"

    def get_queryset(self):
        return AddItem.objects.filter(user=self.request.user, completed=True)


class incomplete_view(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = AddItem
    template_name = "todolist/incomplete.html"

    def get_queryset(self):
        return AddItem.objects.filter(user=self.request.user, completed=False)


class home_view(TemplateView):
    template_name = "todolist/home.html"
