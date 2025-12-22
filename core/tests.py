from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

from core.models import Enrollment
from core.models import Classroom
from core.models import Assignment

User = get_user_model()

class AuthTests(TestCase):

    def test_register_requires_username(self):
        """Submitting register form without username should NOT break the server."""
        response = self.client.post(reverse("register"), {
            "email": "user@example.com",
            "password": "abc123",
            "confirmation": "abc123",
            # username missing on purpose!
        })

        # The page should reload, not crash
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "username", msg_prefix="Missing username should show error, not crash")

    def test_register_success(self):
        """A full proper submission should create a user."""
        response = self.client.post(reverse("register"), {
            "username": "testuser",
            "email": "test@example.com",
            "password": "abc12345",
            "confirmation": "abc12345",
            "role": "student",
        })

        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_login_requires_username(self):
        """Submitting login form without username should not crash."""
        response = self.client.post(reverse("login"), {
            "password": "password",
            # ❌❌❌ username missing
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username", msg_prefix="Login missing username should show error, not crash")

    def test_login_success(self):
        """A proper login should authenticate correctly."""
        user = User.objects.create_user(username="tester", email="t@e.com", password="pass1234")

        response = self.client.post(reverse("login"), {
            "username": "tester",
            "password": "pass1234"
        })

        self.assertEqual(response.status_code, 302)  # Redirect to dashboard.

class JoinClassTests(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(username="t1", password="pass", is_teacher=True)
        self.student = User.objects.create_user(username="s1", password="pass", is_teacher=False)
        self.classroom = Classroom.objects.create(name="Math", teacher=self.teacher)

    def test_student_can_join_class(self):
        self.client.login(username="s1", password="pass")
        response = self.client.post(reverse("join_classroom"), {"code": self.classroom.code})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Enrollment.objects.filter(student=self.student, classroom=self.classroom).exists())

    def test_invalid_code(self):
        self.client.login(username="s1", password="pass")
        response = self.client.post(reverse("join_classroom"), {"code": "WRONG123"})
        self.assertContains(response, "No class found")

    def test_teacher_cannot_join(self):
        self.client.login(username="t1", password="pass")
        response = self.client.get(reverse("join_classroom"))
        self.assertEqual(response.status_code, 403)
#remind me to never to this again.. (SPOILER: I END UP DOING MORE TESTS)

class CreateClassTests(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teach",
            email="t@example.com",
            password="pass",
            is_teacher=True
        )
        self.student = User.objects.create_user(
            username="stud",
            email="s@example.com",
            password="pass",
            is_teacher=False
        )

    def test_teacher_can_create_class(self):
        self.client.login(username="teach", password="pass")

        response = self.client.post(reverse("create_classroom"), {
            "name": "Biology",
            "description": "Science class"
        })

        # Should redirect to class detail page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Classroom.objects.filter(name="Biology").exists())

    def test_student_cannot_create_class(self):
        self.client.login(username="stud", password="pass")

        response = self.client.get(reverse("create_classroom"))

        self.assertEqual(response.status_code, 403)

    def test_missing_name_fails(self):
        self.client.login(username="teach", password="pass")

        response = self.client.post(reverse("create_classroom"), {
            "name": ""
        })

        # Should NOT redirect due to validation error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Class name is required")

class AssignmentTests(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher1",
            email="t@example.com",
            password="pass",
            is_teacher=True
        )
        self.student = User.objects.create_user(
            username="student1",
            email="s@example.com",
            password="pass",
            is_teacher=False
        )

        self.classroom = Classroom.objects.create(
            name="History",
            description="History class",
            teacher=self.teacher
        )

    def test_teacher_can_create_assignment(self):
        self.client.login(username="teacher1", password="pass")

        response = self.client.post(
            reverse("create_assignment", args=[self.classroom.id]),
            {
                "title": "Homework 1",
                "description": "Read Chapter 3",
                "due_date": "2025-12-01"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Assignment.objects.filter(title="Homework 1").exists()
        )

    def test_student_cannot_create_assignment(self):
        self.client.login(username="student1", password="pass")

        response = self.client.post(
            reverse("create_assignment", args=[self.classroom.id]),
            {
                "title": "Fake Assignment"
            }
        )

        self.assertEqual(response.status_code, 403)

    def test_missing_title_fails(self):
        self.client.login(username="teacher1", password="pass")

        response = self.client.post(
            reverse("create_assignment", args=[self.classroom.id]),
            {
                "title": ""
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Title is required")

    def test_assignment_shows_up_on_class_detail(self):
        # create assignment
        Assignment.objects.create(
            classroom=self.classroom,
            title="Essay",
            description="Write 2 pages"
        )

        # student must join class first
        Enrollment.objects.create(student=self.student, classroom=self.classroom)

        self.client.login(username="student1", password="pass")
        response = self.client.get(reverse("class_detail", args=[self.classroom.id]))

        self.assertContains(response, "Essay")

def test_past_assignment_moves_to_past_tab(self):
    # create past-due assignment
    past_date = timezone.now().date() - timedelta(days=1)

    assignment = Assignment.objects.create(
        classroom=self.classroom,
        title="Old Assignment",
        description="Should be past",
        due_date=past_date
    )

    # student must be enrolled
    Enrollment.objects.create(
        student=self.student,
        classroom=self.classroom
    )

    self.client.login(username="student1", password="pass")

    response = self.client.get(
        reverse("class_detail", args=[self.classroom.id])
    )

    # assignment SHOULD appear
    self.assertContains(response, "Old Assignment")

    # sanity check: page has Past tab
    self.assertContains(response, "Past")

    # optional but strong: ensure it does not show as active!
    active_section = response.content.decode().split('id="active"')[1]
    self.assertNotIn("Old Assignment", active_section)