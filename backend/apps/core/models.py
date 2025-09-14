# core/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class AcademicYear(models.Model):
    name = models.CharField(_("ឆ្នាំសិក្សា"), max_length=20)  # ឧ. "2024-2025"
    status = models.BooleanField(_("ស្ថានភាព"),default=0)
    start_date = models.DateField(_("ថ្ងៃចាប់ផ្តើម"))
    end_date = models.DateField(_("ថ្ងៃបញ្ចប់"))

    class Meta:
        verbose_name = _("ឆ្នាំសិក្សា")
        verbose_name_plural = _("ឆ្នាំសិក្សា")

    def __str__(self):
        return self.name


class Semester(models.Model):
    year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="semesters",
        verbose_name=_("ឆ្នាំសិក្សា")
    )
    name = models.CharField(_("ឆមាស"), max_length=20)  # ឧ. "ឆមាសទី១"
    status = models.BooleanField(_("ស្ថានភាព"),default=0)
    start_date = models.DateField(_("ថ្ងៃចាប់ផ្តើម"))
    end_date = models.DateField(_("ថ្ងៃបញ្ចប់"))

    class Meta:
        verbose_name = _("ឆមាស")
        verbose_name_plural = _("ឆមាស")

    def __str__(self):
        return f"{self.name} ({self.year})"


class Major(models.Model):
    name = models.CharField(_("ប្រភេទថ្នាក់"), max_length=100)

    class Meta:
        verbose_name = _("ប្រភេទថ្នាក់")
        verbose_name_plural = _("ប្រភេទថ្នាក់")

    def __str__(self):
        return self.name
