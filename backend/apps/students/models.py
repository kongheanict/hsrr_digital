from django.db import models
from apps.classes.models import SchoolClass
from apps.core.models import AcademicYear, Semester, Major
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


# ---------------------------
# សិស្ស
# ---------------------------
class Student(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", _("ប្រុស")
        FEMALE = "F", _("ស្រី")

    class StudentType(models.TextChoices):
        FULL_TIME = "ពេញម៉ោង", _("ពេញម៉ោង")
        PART_TIME = "ក្រៅម៉ោង", _("ក្រៅម៉ោង")

    student_id = models.CharField(_("លេខសម្គាល់សិស្ស"), max_length=20, unique=True)
    family_name = models.CharField(_("នាមត្រកូល"), max_length=100)
    given_name = models.CharField(_("នាមខ្លួន"), max_length=100)
    gender = models.CharField(_("ភេទ"), max_length=1, choices=Gender.choices)
    date_of_birth = models.DateField(_("ថ្ងៃខែឆ្នាំកំណើត"), null=True, blank=True)
    place_of_birth = models.TextField(_("ទីកន្លែងកំណើត"), blank=True, null=True)
    phone_number = models.CharField(_("លេខទូរស័ព្ទ"), max_length=20, blank=True, null=True)
    student_type = models.CharField(_("ប្រភេទសិស្ស"), max_length=20, choices=StudentType.choices)
    enrollment_date = models.DateField(_("កាលបរិច្ឆេទចុះឈ្មោះ"), null=True, blank=True)
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, verbose_name=_("ជំនាញ"), null=True, blank=True)

    user = models.OneToOneField(User, on_delete=models.SET_NULL, verbose_name=_("គណនីប្រើប្រាស់"), null=True, blank=True)

    class Meta:
        verbose_name = _("សិស្ស")
        verbose_name_plural = _("សិស្ស")

    def __str__(self):
        return f"{self.family_name} {self.given_name} ({self.student_id})"


# ---------------------------
# ការចុះឈ្មោះសិក្សា
# ---------------------------
class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("កំពុងរៀន")
        TRANSFERRED = "TRANSFERRED", _("ផ្ទេរចេញ")
        DROPOUT = "DROPOUT", _("បោះបង់")
        GRADUATED = "GRADUATED", _("បញ្ចប់ការសិក្សា")
        WITHDRAWN = "WITHDRAWN", _("ដកចេញ")

    student = models.ForeignKey(Student, verbose_name=_("សិស្ស"), on_delete=models.CASCADE, related_name="enrollments")
    school_class = models.ForeignKey(SchoolClass, verbose_name=_("ថ្នាក់"), on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, verbose_name=_("ឆ្នាំសិក្សា"), on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, verbose_name=_("ឆមាស"), null=True, blank=True)
    status = models.CharField(_("ស្ថានភាពចុះឈ្មោះ"), max_length=50, choices=Status.choices, default=Status.ACTIVE)
    enrolled_date = models.DateField(_("កាលបរិច្ឆេទចុះឈ្មោះ"))

    class Meta:
        unique_together = ("student", "academic_year", "semester")
        verbose_name = _("ការចុះឈ្មោះសិក្សា")
        verbose_name_plural = _("ការចុះឈ្មោះសិក្សា")

    def __str__(self):
        return f"{self.student} → {self.school_class} ({self.academic_year})"


# ---------------------------
# អាណាព្យាបាល
# ---------------------------
class Parent(models.Model):
    father_name = models.CharField(_("ឈ្មោះឪពុក"), max_length=100, blank=True, null=True)
    father_occupation = models.CharField(_("មុខរបរឪពុក"), max_length=100, blank=True, null=True)
    father_phone = models.CharField(_("ទូរស័ព្ទឪពុក"), max_length=20, blank=True, null=True)

    mother_name = models.CharField(_("ឈ្មោះម្ដាយ"), max_length=100, blank=True, null=True)
    mother_occupation = models.CharField(_("មុខរបរម្ដាយ"), max_length=100, blank=True, null=True)
    mother_phone = models.CharField(_("ទូរស័ព្ទម្ដាយ"), max_length=20, blank=True, null=True)

    students = models.ManyToManyField(Student, verbose_name=_("សិស្ស"), related_name="parents")

    class Meta:
        verbose_name = _("អាណាព្យាបាល")
        verbose_name_plural = _("អាណាព្យាបាល")

    def __str__(self):
        names = []
        if self.father_name:
            names.append(f"ឪពុក: {self.father_name}")
        if self.mother_name:
            names.append(f"ម្ដាយ: {self.mother_name}")
        return " / ".join(names) if names else _("អាណាព្យាបាល")
