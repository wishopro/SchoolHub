from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path("class/new/", views.create_classroom, name="create_classroom"),
    path("class/join/", views.join_classroom, name="join_classroom"),
    path("class/<int:id>/", views.class_detail, name="class_detail"),
    path("class/<int:class_id>/assignments/new/", views.create_assignment, name="create_assignment"),
    path("class/<int:id>/appearance/", views.class_appearance, name="class_appearance"),
path("assignment/<int:assignment_id>/", views.assignment_detail, name="assignment_detail"),

] 
