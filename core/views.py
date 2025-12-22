from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden #I need this right??
from .models import User, Classroom, Enrollment, Assignment
from django.utils import timezone

def index(request):
    return render(request, "index.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")
        role = request.POST.get("role")  # "student" or "teacher"

        if not username or not email or not password or not confirmation or not role:
            return render(request, "register.html", {
                "message": "All fields are required."
            })

        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_teacher = (role == "teacher")
            user.save()

        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })

        login(request, user)
        return redirect("dashboard")

    return render(request, "register.html")



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username:
            return render(request, "login.html", {
                "message": "Username is required."
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })

    return render(request, "login.html")





def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def dashboard(request):
    user = request.user

    if user.is_teacher:
        classes = Classroom.objects.filter(teacher=user)
    else:
        classes = Classroom.objects.filter(enrollment__student=user)

    return render(request, "dashboard.html", {
        "classes": classes
    })

@login_required
def create_classroom(request):
    if not request.user.is_teacher:
        return HttpResponseForbidden("Only teachers can create classes.")

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")

        if not name:
            return render(request, "create_class.html", {
                "message": "Class name is required."
            })

        classroom = Classroom.objects.create(
            name=name,
            description=description,
            teacher=request.user
        )

        return redirect("class_detail", id=classroom.id)

    return render(request, "create_class.html")


@login_required
def join_classroom(request):
    if request.user.is_teacher:
        return HttpResponseForbidden("Teachers cannot join classes.")

    if request.method == "POST":
        code = request.POST.get("code", "").strip().upper()

        if not code:
            return render(request, "join_class.html", {
                "message": "Please enter a class code."
            })

        try:
            classroom = Classroom.objects.get(code=code)
        except Classroom.DoesNotExist:
            return render(request, "join_class.html", {
                "message": "No class found with that code."
            })

        # prevent duplicate join
        if Enrollment.objects.filter(student=request.user, classroom=classroom).exists():
            return render(request, "join_class.html", {
                "message": "You are already enrolled in this class."
            })

        Enrollment.objects.create(student=request.user, classroom=classroom)
        return redirect("class_detail", id=classroom.id)

    return render(request, "join_class.html")


@login_required
def create_assignment(request, class_id):
    classroom = get_object_or_404(Classroom, id=class_id)

    # Teachers only
    if not request.user.is_teacher or classroom.teacher != request.user:
        return HttpResponseForbidden("You cannot create assignments for this class.")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        due_date = request.POST.get("due_date")  # optional

        if not title:
            return render(request, "create_assignment.html", {
                "message": "Title is required.",
                "classroom": classroom
            })

        assignment = Assignment.objects.create(
            classroom=classroom,
            title=title,
            description=description,
            due_date=due_date if due_date else None,
        )

        return redirect("class_detail", id=classroom.id)

    return render(request, "create_assignment.html", {
        "classroom": classroom
    })


@login_required
def class_appearance(request, id):
    classroom = get_object_or_404(Classroom, id=id)

    # Only the teacher who owns the class can customize it
    if not request.user.is_teacher or classroom.teacher != request.user:
        return HttpResponseForbidden("Only the teacher for this class can customize its appearance.")

    message = None

    if request.method == "POST":
        # Remove banner → fall back to gradient
        if "remove_banner" in request.POST:
            if classroom.banner_image:
                classroom.banner_image.delete(save=False)
                classroom.banner_image = None
            classroom.save()
            message = "Banner removed. Using gradient instead."

        # Regenerate gradient (new random theme)
        elif "regen_gradient" in request.POST:
            classroom.gradient_start = ""
            classroom.gradient_end = ""
            classroom.save()
            message = "Gradient updated."

        # Upload / change banner image
        else:
            banner = request.FILES.get("banner_image")
            if banner:
                classroom.banner_image = banner
                classroom.save()
                message = "Banner updated."
            else:
                message = "Please choose an image before saving."

    return render(request, "class_appearance.html", {
        "classroom": classroom,
        "message": message,
    })

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    # Optional: permission check (recommended)
    if request.user.is_teacher:
        if assignment.classroom.teacher != request.user:
            return HttpResponseForbidden("You do not have access to this assignment.")
    else:
        if not Enrollment.objects.filter(
            student=request.user,
            classroom=assignment.classroom
        ).exists():
            return HttpResponseForbidden("You are not enrolled in this class.")

    return render(request, "inspect_assignment.html", {
        "assignment": assignment
    })


@login_required
def class_detail(request, id):
    classroom = get_object_or_404(Classroom, id=id)

    # permission checks (unchanged)
    if request.user.is_teacher:
        if classroom.teacher != request.user:
            return HttpResponseForbidden("You do not teach this class.")
    else:
        if not Enrollment.objects.filter(student=request.user, classroom=classroom).exists():
            return HttpResponseForbidden("You are not enrolled in this class.")

    today = timezone.now().date()  #YES!! We know EXACTLY what time it is for you... BOOO!!

    active_assignments = classroom.assignments.exclude(
    due_date__lt=today
)

    past_assignments = classroom.assignments.filter(
        due_date__lt=today
    )

    return render(request, "class_detail.html", {
    "classroom": classroom,
    "active_assignments": active_assignments.order_by("due_date", "id"),
    "past_assignments": past_assignments.order_by("-due_date"),
    "today": today,
})