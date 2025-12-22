# The models always end up giving me a headache
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
import random


class User(AbstractUser):
    is_teacher = models.BooleanField(default=False)


GRADIENT_PAIRS = [
    ("#ff9966", "#ff5e62"),  # warm sunset
    ("#36D1DC", "#5B86E5"),  # teal → blue
    ("#7F00FF", "#E100FF"),  # purple → magenta
    ("#FF512F", "#DD2476"),  # red → pink
    ("#11998e", "#38ef7d"),  # green → mint
    ("#fc4a1a", "#f7b733"),  # orange → yellow
    ("#24C6DC", "#514A9D"),  # teal → violet
    ("#4568DC", "#B06AB3"),  # soft blue → purple
    ("#43cea2", "#185a9d"),  # aqua → deep blue
    ("#ee0979", "#ff6a00"),  # pink → orange
]



class Classroom(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="classes")
    code = models.CharField(max_length=8, unique=True, blank=True)

    # Optional teacher-uploaded banner
    banner_image = models.ImageField(
        upload_to="class_banners/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])]
    )

    gradient_start = models.CharField(max_length=7, blank=True)
    gradient_end = models.CharField(max_length=7, blank=True)

    def save(self, *args, **kwargs):

        # Generate class code once
        if not self.code:
            self.code = get_random_string(8).upper()

        # Assign gradient only if not already set
        if not self.gradient_start or not self.gradient_end:
            start, end = random.choice(GRADIENT_PAIRS)
            self.gradient_start = start
            self.gradient_end = end

        super().save(*args, **kwargs)



class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("student", "classroom")


class Assignment(models.Model):
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title