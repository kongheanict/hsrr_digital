from django.db import models
from apps.core.models import Major
from django.utils.translation import gettext_lazy as _

class ClassLevel(models.Model):
    name = models.CharField(_("កម្រិតថ្នាក់"), max_length=50)  # e.g., "ថ្នាក់ទី 7", "ថ្នាក់ទី 8"

    class Meta:
        verbose_name = _("កម្រិតថ្នាក់")
        verbose_name_plural = _("កម្រិតថ្នាក់")

    def __str__(self):
        return f"{self.name}"


class SchoolClass(models.Model):
    name = models.CharField(_("ថ្នាក់"), max_length=20)  # ឧ. "7A", "8B"
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

    class Meta:
        verbose_name = _("ថ្នាក់រៀន")
        verbose_name_plural = _("ថ្នាក់រៀន")

    def __str__(self):
        return f"{self.name}"
