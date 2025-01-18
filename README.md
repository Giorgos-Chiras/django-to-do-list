# To-Do List Website

Welcome to the To-Do List Website! This is a feature-rich task management application built with Django. It allows users to organize their tasks, set up notifications, and even contact the admin via a built-in contact form.  
You can visit the website by going to [https://django-to-do-list.up.railway.app/todolist/](https://django-to-do-list.up.railway.app/todolist/).

## Features

- **User Authorization**: Secure user registration, login, and logout functionality.
- **Task Management**:
  - Add, edit, and delete tasks effortlessly.
  - Schedule notifications via email to stay on top of your tasks.
- **Contact Form**: Get in touch with the admin for support or inquiries through the built-in contact form.

## How It Was Built

This website leverages the following technologies:

- **Django**: Backend framework to handle the core functionality, database interactions, and views.
- **HTML and CSS**: For the frontend.
- **Celery**: To handle task scheduling email notifications in the background.
- **Redis**: Used as the message broker for Celery to manage task queues and scheduling.
- **SQLite**: Default database used for development in Django.






