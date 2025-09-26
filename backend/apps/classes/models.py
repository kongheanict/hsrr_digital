from django.db import models
from apps.core.models import Major, AcademicYear
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from apps.teachers.models import Teacher

class ClassLevel(models.Model):
    name = models.CharField(_("កម្រិតថ្នាក់"), max_length=50)

    class Meta:
        verbose_name = _("កម្រិតថ្នាក់")
        verbose_name_plural = _("កម្រិតថ្នាក់")

    def __str__(self):
        return f"{self.name}"

class SchoolClass(models.Model):
    name = models.CharField(_("ថ្នាក់"), max_length=20)
    level = models.ForeignKey(
        ClassLevel,
        on_delete=models.CASCADE,
        related_name="classes",
        verbose_name=_("កម្រិតថ្នាក់")
    )
    major = models.ForeignKey(
        Major,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("ប្រភេទថ្នាក់")
    )
    order = models.PositiveIntegerField(_("លំដាប់"), null=True, blank=True)
    students = models.ManyToManyField(
        User,
        related_name='school_classes',
        blank=True,
        verbose_name=_("students")
    )

    class Meta:
        verbose_name = _("ថ្នាក់រៀន")
        verbose_name_plural = _("ថ្នាក់រៀន")

    def __str__(self):
        return f"{self.name}"

class HomeroomTeacher(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="homeroom_assignments",
        verbose_name=_("គ្រូបន្ទុកថ្នាក់")
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="homeroom_teachers",
        verbose_name=_("ថ្នាក់")
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="homeroom_assignments",
        verbose_name=_("ឆ្នាំសិក្សា"),
        limit_choices_to={'status': True}
    )

    class Meta:
        verbose_name = _("គ្រូបន្ទុកថ្នាក់")
        verbose_name_plural = _("គ្រូបន្ទុកថ្នាក់")
        unique_together = ('teacher', 'school_class', 'academic_year')

    def __str__(self):
        return f"{self.teacher} - {self.school_class} ({self.academic_year})"