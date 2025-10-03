from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'អ្នកគ្រប់គ្រង'),
        ('teacher', 'គ្រូបង្រៀន'),
        ('student', 'សិស្ស'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = "អ្នកប្រើ"
        verbose_name_plural = "អ្នកប្រើ"
        app_label = 'authentication'

    def __str__(self):
        return self.username