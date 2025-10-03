from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

try:
    from telegram.ext import Application
except ImportError:
    Application = None  # Telegram notifications disabled if library missing

# Set up logging
logger = logging.getLogger(__name__)

# -----------------------------
# Specialty Model
# -----------------------------
class Specialty(models.Model):
    name = models.CharField(_("Name"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("ឯកទេស")
        verbose_name_plural = _("ឯកទេស")

    def __str__(self):
        return self.name


# -----------------------------
# Position Model
# -----------------------------
class Position(models.Model):
    name = models.CharField(_("Name"), max_length=50, unique=True)
    order = models.SmallIntegerField(_("Order"), default=0)

    class Meta:
        verbose_name = _("តួនាទី")
        verbose_name_plural = _("តួនាទី")

    def __str__(self):
        return self.name


# -----------------------------
# Teacher Model
# -----------------------------
class Teacher(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = "Male", _("ប្រុស")
        FEMALE = "Female", _("ស្រី")
        OTHER = "Other", _("ផ្សេងទៀត")

    class StatusChoices(models.TextChoices):
        ACTIVE = "ACTIVE", _("សកម្ម")
        INACTIVE = "INACTIVE", _("អសកម្ម")
        RETIRED = "RETIRED", _("ចូលនិវត្តន៍")
        MOVED = "MOVED", _("បានផ្លាស់ប្តូរ")

    tid = models.CharField(_("លេខសម្គាល់គ្រូ"), max_length=191, unique=True)
    family_name = models.CharField(_("នាមត្រកូល"), max_length=50)
    given_name = models.CharField(_("នាមខ្លួន"), max_length=50)
    status = models.CharField(_("ស្ថានភាព"), max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    id_card_number = models.CharField(_("លេខអត្តសញ្ញាណប័ណ្ណ"), max_length=191, unique=True)
    date_of_birth = models.DateField(_("ថ្ងៃខែឆ្នាំកំណើត"))
    email = models.EmailField(_("អ៊ីមែល"), max_length=191, unique=True)
    gender = models.CharField(_("ភេទ"), max_length=10, choices=GenderChoices.choices)
    phone_number = models.CharField(_("លេខទូរស័ព្ទ"), max_length=20, unique=True)
    place_of_birth = models.TextField(_("ទីកន្លែងកំណើត"), blank=True, null=True)
    position = models.ForeignKey(Position, verbose_name=_("តួនាទី"), on_delete=models.CASCADE)
    enrolled_date = models.DateField(_("កាលបរិច្ឆេទចុះឈ្មោះ"))
    specialties = models.ManyToManyField(Specialty, verbose_name=_("ជំនាញ"), blank=True)
    profile_image = models.ImageField(_("រូបភាពប្រវត្តិរូប"), upload_to="teacher_profiles/", blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("គណនីអ្នកប្រើប្រាស់"), on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = _("គ្រូ")
        verbose_name_plural = _("គ្រូបង្រៀន")

    def __str__(self):
        return f"{self.family_name} {self.given_name}"


# -----------------------------
# Delete old profile image on update
# -----------------------------
@receiver(pre_save, sender=Teacher)
def auto_delete_old_profile_image(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_file = sender.objects.get(pk=instance.pk).profile_image
    except sender.DoesNotExist:
        return False
    new_file = instance.profile_image
    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


# -----------------------------
# LeaveRequest Model
# -----------------------------
class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', _('រង់ចាំ')),
        ('approved', _('បានអនុម័ត')),
        ('rejected', _('បានបដិសេធ')),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name=_("គ្រូ")
    )
    start_date = models.DateField(_("កាលបរិច្ឆេទចាប់ផ្តើម"))
    end_date = models.DateField(_("កាលបរិច្ឆេទបញ្ចប់"))
    reason = models.TextField(_("ហេតុផល"), max_length=500)
    status = models.CharField(_("ស្ថានភាព"), max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("បានបង្កើតនៅ"))
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
        verbose_name=_("អនុម័តដោយ")
    )

    class Meta:
        verbose_name = _("សំណើច្បាប់ឈប់សម្រាក")
        verbose_name_plural = _("សំណើច្បាប់ឈប់សម្រាក")
        ordering = ['-created_at']

    def __str__(self):
        name = self.teacher.user.get_full_name() if self.teacher.user else f"{self.teacher.family_name} {self.teacher.given_name}"
        return f"{name} - {self.start_date} ដល់ {self.end_date}"

    async def send_telegram_notification(self):
        if Application is None:
            logger.warning("Telegram Application not installed. Skipping notification.")
            return
        try:
            app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            chat_id = settings.TELEGRAM_CHAT_ID
            name = self.teacher.user.get_full_name() if self.teacher.user else f"{self.teacher.family_name} {self.teacher.given_name}"
            message = (
                f"🔔 *សំណើច្បាប់ឈប់សម្រាកសម្រាប់* 🔔\n\n"
                f"👤 ឈ្មោះគ្រូ: *{name}*\n\n"
                f"📅 កាលបរិច្ឆេទ: {self.start_date} ដល់ {self.end_date}\n\n"
                
                f"📝 ហេតុផល: *{self.reason}*\n\n"
                f"📌 ស្ថានភាព: {self.get_status_display()}\n"
                # f" បានផ្ញើនៅ: {datetime.now(ZoneInfo(settings.TIME_ZONE))}"
            )
            await app.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
            logger.info(f"Telegram notification sent for LeaveRequest ID={self.id}")
        except Exception as e:
            logger.error(f"Failed to send Telegram notification for LeaveRequest ID={self.id}: {e}")


# -----------------------------
# Signal: Trigger Telegram after create or status change
# -----------------------------
@receiver(post_save, sender=LeaveRequest)
def trigger_telegram_notification(sender, instance, created, **kwargs):
    """
    Trigger Telegram notification:
    - When a new leave request is created
    - When status changes from pending
    """
    import asyncio
    if created or instance.status != 'pending':
        asyncio.run(instance.send_telegram_notification())
