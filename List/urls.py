from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from todolist.views import *

urlpatterns = [
    path('todolist/',include("todolist.urls")),

    path('admin/', admin.site.urls),

    path('about/', about_view, name="about"),

    path('completed/',completed_view.as_view(), name="completed"),

    path('incomplete/',incomplete_view.as_view(), name="incomplete"),

    path('register/',register_form, name="register"),

    path('login/',login_form, name="login"),

    path('',home_view.as_view(),name='home'),

    path('edit/',task_form, name="edit"),

    path('logout/',logout_view,name="logout"),

    path('delete/<int:part_id>/',delete_view,name="delete"),

    path('status/<part_id>', change_confirmation_view, name="status"),

    path('edit_task/<part_id>', edit_task, name="edit_task"),

]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)