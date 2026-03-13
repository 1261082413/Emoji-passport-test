import time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from .models import UserAccount, LoginAttempt, SurveyResponse
from .forms import (
    TextRegisterForm,
    EmojiRegisterForm,
    MixRegisterForm,
    LoginForm,
    SurveyForm,
)


def home(request):
    return render(request, "accounts/home.html")


def register_step1(request):
    if request.method == "GET":
        form = TextRegisterForm()
        return render(request, "accounts/register_step1.html", {"form": form})

    form = TextRegisterForm(request.POST)
    if not form.is_valid():
        return render(request, "accounts/register_step1.html", {"form": form})

    username = form.cleaned_data["username"].strip()
    password = form.cleaned_data["password"]

    if UserAccount.objects.filter(username=username, password_type="text").exists():
        form.add_error("username", "This username already has a text password account.")
        return render(request, "accounts/register_step1.html", {"form": form})

    UserAccount.objects.create(
        username=username,
        password_hash=make_password(password),
        password_type="text",
    )

    request.session["unlock_username"] = username
    return render(
        request,
        "accounts/register_step1.html",
        {
            "form": TextRegisterForm(),
            "show_unlock_modal": True,
        },
    )


def register_emoji(request):
    unlock_username = request.session.get("unlock_username")

    if request.method == "GET":
        initial_data = {}
        if unlock_username:
            initial_data["username"] = unlock_username
        form = EmojiRegisterForm(initial=initial_data)
        return render(request, "accounts/register_emoji.html", {"form": form})

    form = EmojiRegisterForm(request.POST)
    if not form.is_valid():
        return render(request, "accounts/register_emoji.html", {"form": form})

    username = form.cleaned_data["username"].strip()
    password = form.cleaned_data["password"]

    if UserAccount.objects.filter(username=username, password_type="emoji").exists():
        form.add_error("username", "This username already has an emoji password account.")
        return render(request, "accounts/register_emoji.html", {"form": form})

    UserAccount.objects.create(
        username=username,
        password_hash=make_password(password),
        password_type="emoji",
    )

    request.session["unlock_username"] = username
    return render(
        request,
        "accounts/register_emoji.html",
        {
            "form": EmojiRegisterForm(initial={"username": username}),
            "show_mix_modal": True,
        },
    )


def register_mix(request):
    unlock_username = request.session.get("unlock_username")

    if request.method == "GET":
        initial_data = {}
        if unlock_username:
            initial_data["username"] = unlock_username
        form = MixRegisterForm(initial=initial_data)
        return render(request, "accounts/register_mix.html", {"form": form})

    form = MixRegisterForm(request.POST)
    if not form.is_valid():
        return render(request, "accounts/register_mix.html", {"form": form})

    username = form.cleaned_data["username"].strip()
    password = form.cleaned_data["password"]

    if UserAccount.objects.filter(username=username, password_type="mix").exists():
        form.add_error("username", "This username already has a mix password account.")
        return render(request, "accounts/register_mix.html", {"form": form})

    UserAccount.objects.create(
        username=username,
        password_hash=make_password(password),
        password_type="mix",
    )

    messages.success(request, "Mix password registered successfully. You can now log in.")
    return redirect("login")


def login_view(request):
    if request.method == "GET":
        request.session["login_start_ts"] = time.time()
        form = LoginForm()
        return render(request, "accounts/login.html", {"form": form})

    form = LoginForm(request.POST)
    if not form.is_valid():
        return render(request, "accounts/login.html", {"form": form})

    username = form.cleaned_data["username"].strip()
    password = form.cleaned_data["password"]
    password_type = form.cleaned_data["password_type"]

    start_ts = request.session.get("login_start_ts")
    duration_ms = int((time.time() - float(start_ts)) * 1000) if start_ts else 0

    account = UserAccount.objects.filter(
        username=username,
        password_type=password_type
    ).first()

    if account is None:
        LoginAttempt.objects.create(
            username=username,
            password_type=password_type,
            duration_ms=duration_ms,
            success=False,
        )
        messages.error(request, "Login failed. Account not found for this password type.")
        return redirect("login")

    ok = check_password(password, account.password_hash)

    LoginAttempt.objects.create(
        username=username,
        password_type=password_type,
        duration_ms=duration_ms,
        success=ok,
    )

    if not ok:
        account.failed_count += 1
        account.save(update_fields=["failed_count"])
        messages.error(request, "Login failed. Wrong password.")
        return redirect("login")

    request.session["logged_in_user"] = username

    if password_type == "text":
        request.session["text_logged_in"] = True
    elif password_type == "emoji":
        request.session["emoji_logged_in"] = True
    elif password_type == "mix":
        request.session["mix_logged_in"] = True

    text_done = request.session.get("text_logged_in", False)
    emoji_done = request.session.get("emoji_logged_in", False)
    mix_done = request.session.get("mix_logged_in", False)

    if text_done and emoji_done and mix_done:
        if not SurveyResponse.objects.filter(username=username).exists():
            return redirect("survey")

    messages.success(request, f"{password_type.title()} login success!")
    return redirect("dashboard")


def survey_view(request):
    username = request.session.get("logged_in_user")
    if not username:
        return redirect("login")

    if SurveyResponse.objects.filter(username=username).exists():
        messages.info(request, "You already submitted the survey.")
        return redirect("dashboard")

    if request.method == "GET":
        form = SurveyForm()
        return render(request, "accounts/survey.html", {"form": form})

    form = SurveyForm(request.POST)
    if not form.is_valid():
        return render(request, "accounts/survey.html", {"form": form})

    SurveyResponse.objects.create(
        username=username,
        used_password_type=form.cleaned_data["used_password_type"],
        easier_to_remember=form.cleaned_data["easier_to_remember"],
        faster_to_type=form.cleaned_data["faster_to_type"],
        real_life_choice=form.cleaned_data["real_life_choice"],
        comments=form.cleaned_data["comments"],
    )

    messages.success(request, "Survey submitted successfully.")
    return redirect("dashboard")


def dashboard(request):
    username = request.session.get("logged_in_user")
    if not username:
        return redirect("login")

    attempts = LoginAttempt.objects.filter(username=username).order_by("-created_at")[:20]
    total = LoginAttempt.objects.filter(username=username).count()
    success_n = LoginAttempt.objects.filter(username=username, success=True).count()
    success_rate = round((success_n / total * 100), 1) if total else 0.0

    text_account = UserAccount.objects.filter(username=username, password_type="text").first()
    emoji_account = UserAccount.objects.filter(username=username, password_type="emoji").first()
    mix_account = UserAccount.objects.filter(username=username, password_type="mix").first()
    survey_done = SurveyResponse.objects.filter(username=username).exists()

    return render(
        request,
        "accounts/dashboard.html",
        {
            "username": username,
            "text_account": text_account,
            "emoji_account": emoji_account,
            "mix_account": mix_account,
            "success_rate": success_rate,
            "attempts": attempts,
            "survey_done": survey_done,
            "text_logged_in": request.session.get("text_logged_in", False),
            "emoji_logged_in": request.session.get("emoji_logged_in", False),
            "mix_logged_in": request.session.get("mix_logged_in", False),
        },
    )


def logout_view(request):
    request.session.flush()
    messages.info(request, "Logged out.")
    return redirect("home")