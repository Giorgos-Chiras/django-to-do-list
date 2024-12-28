from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import TaskForm, EditTaskForm
from ..models import AddItem


@login_required(login_url='login')
def task_form(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = AddItem(
                text=form.cleaned_data['name'],
                due_date=form.cleaned_data['date'],
                picture=form.cleaned_data['image'],
                user=request.user
            )
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

    # Use get_object_or_404 to handle missing objects gracefully
    _object = get_object_or_404(AddItem, pk=part_id)

    # Toggle the completion status
    _object.completed = not _object.completed
    _object.save()

    # Redirect back to the referer
    return redirect(request.META.get('HTTP_REFERER'))
