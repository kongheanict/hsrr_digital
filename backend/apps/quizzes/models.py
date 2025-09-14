from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.teachers.models import Teacher

class QuizCategory(models.Model):
    """Categories like Math, English, Science."""
    name = models.CharField(_("Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)

    class Meta:
        verbose_name = _("Quiz Category")
        verbose_name_plural = _("Quiz Categories")

    def __str__(self):
        return self.name


class Quiz(models.Model):
    """A quiz belongs to a category and can have many questions."""
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True, null=True)
    category = models.ForeignKey(
        QuizCategory, on_delete=models.CASCADE, related_name="quizzes", verbose_name=_("Category")
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="quizzes"
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Quiz")
        verbose_name_plural = _("Quizzes")

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = (
        ("MCQ_SINGLE", _("Multiple Choice (Single Answer)")),
        ("MCQ_MULTI", _("Multiple Choice (Multiple Answers)")),
        ("SHORT", _("Short Answer")),
    )

    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="questions", verbose_name=_("Quiz")
    )
    text = models.TextField(_("Question Text"))
    question_type = models.CharField(_("Question Type"), max_length=20, choices=QUESTION_TYPES)
    order = models.PositiveIntegerField(_("Order"), default=0)

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ("quiz", "order")

    def __str__(self):
        return f"{self.text[:50]}..."


class AnswerOption(models.Model):
    """Possible answers for multiple-choice questions."""
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
    """Tracks what a student answered."""
    student_id = models.IntegerField(_("Student ID"))  # Replace with ForeignKey if you have a Student model
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_("Question"))
    selected_options = models.ManyToManyField(
        AnswerOption, blank=True, verbose_name=_("Selected Options")
    )  # for MCQ_SINGLE & MCQ_MULTI
    text_answer = models.TextField(_("Text Answer"), blank=True, null=True)  # for SHORT
    submitted_at = models.DateTimeField(_("Submitted At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Student Response")
        verbose_name_plural = _("Student Responses")

    def __str__(self):
        return f"Response by Student {self.student_id}"
