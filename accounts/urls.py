from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_step1, name="register_step1"),
    path("register/emoji/", views.register_emoji, name="register_emoji"),
    path("register/mix/", views.register_mix, name="register_mix"),
    path("login/", views.login_view, name="login"),
    path("survey/", views.survey_view, name="survey"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
]