from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field
from apps.teachers.models import Teacher
from apps.classes.models import SchoolClass
from apps.students.models import Student

class QuizCategory(models.Model):
    name = models.CharField(_("Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)

    class Meta:
        verbose_name = _("Quiz Category")
        verbose_name_plural = _("Quiz Categories")

    def __str__(self):
        return self.name


class Quiz(models.Model):
    STATUS_CHOICES = (
        ("DRAFT", _("Draft")),
        ("RELEASE", _("Release")),
        ("PUBLISH", _("Publish")),
        ("ENDED", _("Ended")),
    )

    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True, null=True)
    category = models.ForeignKey(
        QuizCategory, on_delete=models.CASCADE, related_name="quizzes", verbose_name=_("Category")
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="quizzes", verbose_name=_("Teacher")
    )
    classes = models.ManyToManyField(
        SchoolClass, related_name="quizzes", verbose_name=_("Assigned Classes")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    time_limit = models.DurationField(
        _("Time Limit"), null=True, blank=True, help_text=_("Time limit for the quiz (e.g., 30 minutes).")
    )
    start_time = models.DateTimeField(
        _("Start Time"), null=True, blank=True, help_text=_("When the quiz becomes available.")
    )
    status = models.CharField(
        _("Status"), max_length=20, choices=STATUS_CHOICES, default="DRAFT"
    )

    allow_check_answer = models.BooleanField(
        _("Allow Check Answer"), default=False, help_text=_("Allow students to view their answers after submission.")
    )
    allow_see_score = models.BooleanField(
        _("Allow See Score"), default=False, help_text=_("Allow students to see their score after submission.")
    )

    class Meta:
        verbose_name = _("Quiz")
        verbose_name_plural = _("Quizzes")

    def __str__(self):
        return self.title

    def clean(self):
        if self.time_limit and self.time_limit.total_seconds() <= 0:
            raise ValidationError(_("Time limit must be positive."))
        if self.status == "PUBLISH" and not self.start_time:
            raise ValidationError(_("Publish status requires a start time."))
        if self.start_time and isinstance(self.start_time, (list, tuple)):
            raise ValidationError(_("Start time must be a single datetime value."))


class Question(models.Model):
    QUESTION_TYPES = (
        ("MCQ_SINGLE", _("Multiple Choice (Single Answer)")),
        ("MCQ_MULTI", _("Multiple Choice (Multiple Answers)")),
        ("SHORT", _("Short Answer")),
    )

    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="questions", verbose_name=_("Quiz")
    )
    text = CKEditor5Field(_("Question Text"))
    question_type = models.CharField(_("Question Type"), max_length=20, choices=QUESTION_TYPES)
    order = models.PositiveIntegerField(_("Order"), default=0)
    points = models.PositiveIntegerField(_("Points"), default=1)

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ("quiz", "order")

    def __str__(self):
        return f"{self.text[:50]}..."


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options", verbose_name=_("Question")
    )
    text = models.CharField(_("Answer Text"), max_length=255)
    is_correct = models.BooleanField(_("Is Correct"), default=False)

    class Meta:
        verbose_name = _("Answer Option")
        verbose_name_plural = _("Answer Options")

    def __str__(self):
        return self.text


class StudentResponse(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="quiz_responses", verbose_name=_("Student")
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="responses", verbose_name=_("Quiz")
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="responses", verbose_name=_("Question")
    )
    selected_options = models.ManyToManyField(
        AnswerOption, blank=True, verbose_name=_("Selected Options")
    )
    text_answer = models.TextField(_("Text Answer"), blank=True, null=True)
    points_earned = models.FloatField(_("Points Earned"), null=True, blank=True)  # <-- NEW
    submitted_at = models.DateTimeField(_("Submitted At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Student Response")
        verbose_name_plural = _("Student Responses")

    def __str__(self):
        return f"Response by {self.student} for {self.quiz}"


class QuizAttempt(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="quiz_attempts", verbose_name=_("Student")
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="attempts", verbose_name=_("Quiz")
    )
    start_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(_("Score"), null=True)
    completed_at = models.DateTimeField(_("Completed At"), null=True, blank=True)

    class Meta:
        verbose_name = _("Quiz Attempt")
        verbose_name_plural = _("Quiz Attempts")

    def __str__(self):
        return f"{self.student} - {self.quiz} ({self.score})"