from tempfile import template

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..forms import ContactForm
from .email_views import send_email
from email.mime.text import MIMEText
from ..forms import subject_choices


@login_required(login_url='login')
#View to manage contact form
def about_view(request):
    form = ContactForm(request.POST)

    if request.method == "POST":
        user_email = request.user.email

        if form.is_valid():

            user_name = form.cleaned_data['name']
            message = form.cleaned_data['message']
            subject = form.cleaned_data['subject']

            #Get subject as a string
            for id, name in subject_choices:
                if id == subject:
                    subject = name
                    break

            #Create and send email
            msg = MIMEText(message)
            msg["Subject"] = f"New contact from {user_name} ({user_email}) Subject: {subject}"

            send_email(msg, msg['Subject'])

            return redirect('index')

    return render(request, 'todolist/about.html', {"form": form})

@login_required(login_url='login')
def settings_view(request):
       return render(request, 'todolist/settings.html')

def home_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        return render(request, "todolist/home.html")

