from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

class Specialty(models.Model):
    name = models.CharField(_("Name"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("Specialty")
        verbose_name_plural = _("Specialties")

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(_("Name"), max_length=50, unique=True)
    order = models.SmallIntegerField(_("Order"), default=0)

    class Meta:
        verbose_name = _("Position")
        verbose_name_plural = _("Positions")

    def __str__(self):
        return self.name


class Teacher(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = "Male", _("Male")
        FEMALE = "Female", _("Female")
        OTHER = "Other", _("Other")

    class StatusChoices(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        INACTIVE = "INACTIVE", _("Inactive")
        RETIRED = "RETIRED", _("Retired")
        MOVED = "MOVED", _("Moved")

    tid = models.CharField(_("Teacher ID"), max_length=191, unique=True)
    family_name = models.CharField(_("Family Name"), max_length=50)
    given_name = models.CharField(_("Given Name"), max_length=50)
    status = models.CharField(_("Status"), max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    id_card_number = models.CharField(_("ID Card Number"), max_length=191, unique=True)
    date_of_birth = models.DateField(_("Date of Birth"))
    email = models.EmailField(_("Email"), max_length=191, unique=True)
    gender = models.CharField(_("Gender"), max_length=10, choices=GenderChoices.choices)
    phone_number = models.CharField(_("Phone Number"), max_length=20, unique=True)
    place_of_birth = models.TextField(_("Place of Birth"), blank=True, null=True)
    position = models.ForeignKey(Position, verbose_name=_("Position"), on_delete=models.CASCADE)
    enrolled_date = models.DateField(_("Enrolled Date"))
    specialties = models.ManyToManyField(Specialty, verbose_name=_("Specialties"), blank=True)
    profile_image = models.ImageField(_("Profile Image"), upload_to="teacher_profiles/", blank=True, null=True)

    user = models.OneToOneField(User, verbose_name=_("User Account"), on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = _("Teacher")
        verbose_name_plural = _("Teachers")

    def __str__(self):
        return f"{self.family_name} {self.given_name}"
    
# -----------------------------
# Delete old profile image on update
# -----------------------------
@receiver(pre_save, sender=Teacher)
def auto_delete_old_profile_image(sender, instance, **kwargs):
    """Deletes old file from filesystem when updating to a new file."""
    if not instance.pk:
        return False  # new object, nothing to delete

    try:
        old_file = sender.objects.get(pk=instance.pk).profile_image
    except sender.DoesNotExist:
        return False

    new_file = instance.profile_image
    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
