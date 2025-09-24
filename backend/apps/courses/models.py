from django.db import models
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.translation import gettext_lazy as _
from apps.classes.models import SchoolClass

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("title"))
    description = models.TextField(verbose_name=_("description"))
    cover_image = models.ImageField(upload_to='courses/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    classes = models.ManyToManyField(SchoolClass, related_name='accessible_courses', blank=True, verbose_name=_("classes"))

    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE, verbose_name=_("course"))
    title = models.CharField(max_length=200, verbose_name=_("title"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("order"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = _("lesson")
        verbose_name_plural = _("lessons")

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class LessonPart(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='parts', on_delete=models.CASCADE, verbose_name=_("lesson"))
    title = models.CharField(max_length=200, verbose_name=_("title"))
    content = CKEditor5Field(verbose_name=_("content"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("order"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = _("lesson part")
        verbose_name_plural = _("lesson parts")

    def __str__(self):
        return f"{self.title} ({self.lesson.title})"

class StudentCourseAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_assignments', verbose_name=_("student"))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_assignments', verbose_name=_("course"))
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name=_("assigned at"))

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = _("student course assignment")
        verbose_name_plural = _("student course assignments")

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

class StudentProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress', verbose_name=_("student"))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_progress', verbose_name=_("course"))
    completed = models.BooleanField(default=False, verbose_name=_("completed"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("completed at"))

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = _("student progress")
        verbose_name_plural = _("student progress")

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {'Completed' if self.completed else 'In Progress'}"