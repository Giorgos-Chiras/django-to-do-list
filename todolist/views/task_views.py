import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import make_aware
from django.contrib import messages
from ..forms import TaskForm, EditTaskForm, SetNotificationForm
from ..models import AddItem
from datetime import  datetime
from ..tasks import schedule_email


@login_required(login_url='login')
def task_form(request):
    if request.method == "POST":
        form = TaskForm(request.POST,request.FILES)
        if form.is_valid():

            #Create the object and save it
            task = AddItem(
                text=form.cleaned_data['name'],
                due_date=form.cleaned_data['date'],
                user=request.user
                )

            if form.cleaned_data['image']:
                print("Image added")
                task.picture = form.cleaned_data['image']

            task.save()

            return redirect('index')
    else:
        form = TaskForm()

    return render(request, "todolist/add-task.html", {"form": form})

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
    render(request, 'todolist/all_tasks.html')
    return redirect('index')


def change_confirmation_view(request, part_id=None):

    if not request.META.get('HTTP_REFERER') or part_id is None:
        return redirect('index')

    _object = get_object_or_404(AddItem, pk=part_id)

    # Toggle the completion status
    _object.completed = not _object.completed
    _object.save()

    # Redirect back to the referer
    return redirect(request.META.get('HTTP_REFERER'))


def set_notification(request, part_id=None):
    if not request.META.get('HTTP_REFERER') or part_id is None:
        return redirect('index')

    # Fetch the associated object
    object = get_object_or_404(AddItem, pk=part_id)

    if request.method == "POST":
        form = SetNotificationForm(request.POST)
        if form.is_valid():

            # Email subject
            subject = f"Reminder: Task '{object.text}' is Due Soon"

            # Format the due date for the email message
            formatted_due_date = object.due_date.strftime('%A, %B %d, %Y')

            # Email body message
            message = (
                f"Hello {request.user.first_name},\n\n"
                f"This is a friendly reminder that your task '{object.text}' is due on {formatted_due_date}.\n"
                f"Please make sure to complete it on time.\n\n"
                f"Best regards,\n"
                f"Your To-Do App"
            )



            # Get recipient email
            recipient = request.user.email

            # Get notification date and time from form
            notification_date = form.cleaned_data['notification_date']
            notification_time = form.cleaned_data['notification_time']

            # Combine the date and time into a single datetime object
            send_date = datetime.combine(notification_date, notification_time)

            # Make send_date timezone-aware
            send_date = make_aware(send_date)

            # Get the current time as a timezone-aware datetime
            now = datetime.now()
            now = make_aware(now) if not now.tzinfo else now  # Ensure the current time is aware

            # Calculate the delay (seconds) until the scheduled time
            delay = (send_date - now).total_seconds()

            print(f"Scheduled time: {send_date}")
            print(f"Current time: {now}")
            print(f"Calculated delay: {delay} seconds")

            if delay > 0:
                # Schedule the email task to be sent after the delay
                print("Scheduling email task with delay")
                schedule_email.apply_async((message, subject, recipient), countdown=delay)
                messages.success(request, "Email scheduled successfully")

                return redirect(request.META.get('HTTP_REFERER'))

            else:
                messages.error(request, 'Scheduled time must be in the future.')

    else:
        form = SetNotificationForm()

    return render(request, "todolist/set_notification.html", {"form": form, "object": object})



