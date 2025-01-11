from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from todolist.views import change_email, change_email_confirmation, forgot_password, forgot_password_confirmation, \
    choose_email, set_notification

from todolist.views.auth_views import (
    register_form, login_form, logout_view, change_user_password, confirm_email_view
)
from todolist.views.task_views import (
    task_form, edit_task, delete_view, change_confirmation_view
)
from todolist.views.class_based_views import (
     completed_view, incomplete_view
)
from todolist.views.general_views import (about_view,settings_view, home_view )

urlpatterns = [
    path('todolist/',include("todolist.urls")),

    path('admin/', admin.site.urls),

    path('about/', about_view, name="about"),

    path('completed/',completed_view.as_view(), name="completed"),

    path('incomplete/',incomplete_view.as_view(), name="incomplete"),

    path('register/',register_form, name="register"),

    path('login/',login_form, name="login"),

    path('',home_view ,name='home'),

    path('add_task/', task_form, name="add-task"),

    path('logout/',logout_view,name="logout"),

    path('delete/<int:part_id>/',delete_view,name="delete"),

    path('status/<part_id>', change_confirmation_view, name="status"),

    path('edit_task/<part_id>', edit_task, name="edit_task"),

    path('confirm_email/', confirm_email_view, name="confirm_email"),

    path('edit_password/', change_user_password, name="edit_password"),

    path ('settings/',settings_view,name="settings"),

    path('change_email/',change_email,name="change_email"),

    path('change_email_confirmation/',change_email_confirmation, name="change_email_confirmation"),

    path('forgot_password/',forgot_password, name="forgot_password"),

    path('forgot_password_confirmation/',forgot_password_confirmation, name="forgot_password_confirmation"),

    path('choose_email/',choose_email, name="choose_email"),

    path('set_notification/<part_id>', set_notification, name="set_notification"),

    ]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

