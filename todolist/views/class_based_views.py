from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic import TemplateView
from ..models import AddItem


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
