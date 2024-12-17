from django.urls import path
from . import views

urlpatterns = [
    path("", views.all_to_do.as_view(), name="index"),

    path('about/', views.about_view, name="about"),

    path('completed/', views.completed_view.as_view(), name="completed"),

    path('incomplete/', views.incomplete_view.as_view(), name="incomplete"),

    path('register/', views.register_form, name="register"),

    path('login/', views.login, name="login"),

    path('', views.home_view.as_view(), name="home"),

    path('edit/',views.task_form, name="edit"),

    path('logout/', views.logout, name="logout"),

    path('delete/<part_id>',views.delete_view, name="delete"),

    path('status/<part_id>',views.change_confirmation_view, name="status"),

    path('edit_task/<part_id>',views.edit_task, name="edit_task"),

]