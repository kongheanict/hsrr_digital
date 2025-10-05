from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field
from apps.teachers.models import Teacher
from apps.classes.models import SchoolClass
from apps.students.models import Student

class QuizCategory(models.Model):
    name = models.CharField(_("ឈ្មោះ"), max_length=100, unique=True)
    description = models.TextField(_("ពិពណ៌នា"), blank=True, null=True)

    class Meta:
        verbose_name = _("ប្រភេទតេស្ត")
        verbose_name_plural = _("ប្រភេទតេស្ត")

    def __str__(self):
        return self.name


class Quiz(models.Model):
    STATUS_CHOICES = (
        ("DRAFT", _("ព្រាង")),
        ("RELEASE", _("ប្រកាស")),
        ("PUBLISH", _("ផ្សព្វផ្សាយ")),
        ("ENDED", _("បានបញ្ចប់")),
    )

    title = models.CharField(_("ចំណងជើង"), max_length=200)
    description = models.TextField(_("ពិពណ៌នា"), blank=True, null=True)
    category = models.ForeignKey(
        QuizCategory, on_delete=models.CASCADE, related_name="quizzes", verbose_name=_("ប្រភេទ")
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="quizzes", verbose_name=_("គ្រូបង្រៀន")
    )
    classes = models.ManyToManyField(
        SchoolClass, related_name="quizzes", verbose_name=_("ចាត់ថ្នាក់រៀន")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    time_limit = models.DurationField(
        _("រយៈពេល"), null=True, blank=True, help_text=_("Time limit for the quiz (e.g., 30 minutes).")
    )
    start_time = models.DateTimeField(
        _("ពេលចាប់ផ្ដើម"), null=True, blank=True, help_text=_("When the quiz becomes available.")
    )
    status = models.CharField(
        _("ស្ថានភាព"), max_length=20, choices=STATUS_CHOICES, default="DRAFT"
    )

    # New fields for difficulty-based question selection
    num_easy_questions = models.PositiveIntegerField(
        _("ចំនួនសំណួរស្រួល"), default=0, help_text=_("ចំនួនសំណួរស្រួលដែលត្រូវជ្រើសដោយចៃដន្យសម្រាប់ការប្រឡងនីមួយៗ។")
    )
    num_medium_questions = models.PositiveIntegerField(
        _("ចំនួនសំណួរមធ្យម"), default=0, help_text=_("ចំនួនសំណួរមធ្យមដែលត្រូវជ្រើសដោយចៃដន្យសម្រាប់ការប្រឡងនីមួយៗ។")
    )
    num_hard_questions = models.PositiveIntegerField(
        _("ចំនួនសំណួរពិបាក"), default=0, help_text=_("ចំនួនសំណួរពិបាកដែលត្រូវជ្រើសដោយចៃដន្យសម្រាប់ការប្រឡងនីមួយៗ។")
    )

    allow_check_answer = models.BooleanField(
        _("បើកអោយមើលចម្លើយ"), default=False, help_text=_("Allow students to view their answers after submission.")
    )
    allow_see_score = models.BooleanField(
        _("បើកអោយមើលពិន្ទុ"), default=False, help_text=_("Allow students to see their score after submission.")
    )

    class Meta:
        verbose_name = _("កម្រងតេស្ត")
        verbose_name_plural = _("កម្រងតេស្ត")

    def __str__(self):
        return self.title

    def clean(self):
        if self.time_limit and self.time_limit.total_seconds() <= 0:
            raise ValidationError(_("Time limit must be positive."))
        if self.status == "PUBLISH" and not self.start_time:
            raise ValidationError(_("Publish status requires a start time."))
        if self.start_time and isinstance(self.start_time, (list, tuple)):
            raise ValidationError(_("Start time must be a single datetime value."))

    @property
    def total_questions_per_attempt(self):
        """Total questions selected per student attempt."""
        return self.num_easy_questions + self.num_medium_questions + self.num_hard_questions


class Question(models.Model):
    QUESTION_TYPES = (
        ("MCQ_SINGLE", _("Multiple Choice (Single Answer)")),
        ("MCQ_MULTI", _("Multiple Choice (Multiple Answers)")),
        ("SHORT", _("Short Answer")),
    )

    DIFFICULTY_CHOICES = (
        ("EASY", _("ស្រួល")),
        ("MEDIUM", _("មធ្យម")),
        ("HARD", _("ពិបាក")),
    )

    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="questions", verbose_name=_("កម្រងតេស្ត")
    )
    text = CKEditor5Field(_("សំណួរ"), config_name='extends', null=True, blank=True)
    question_type = models.CharField(_("ប្រភេទសំណួរ"), max_length=20, choices=QUESTION_TYPES)
    difficulty = models.CharField(
        _("កម្រិតសំណួរ"), max_length=10, choices=DIFFICULTY_CHOICES, default="MEDIUM"
    )
    order = models.PositiveIntegerField(_("លំដាប់"), default=0)
    points = models.PositiveIntegerField(_("ពិន្ទុ"), default=1)

    class Meta:
        verbose_name = _("សំណួរ")
        verbose_name_plural = _("សំណួរ")
        ordering = ("quiz", "order")

    def __str__(self):
        return f"{self.text[:50]}..."


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options", verbose_name=_("Question")
    )
    text = models.CharField(_("ចម្លើយ"), max_length=255)
    is_correct = models.BooleanField(_("ត្រឹមត្រូវ"), default=False)

    class Meta:
        verbose_name = _("ជម្រើសចម្លើយ")
        verbose_name_plural = _("ជម្រើសចម្លើយ")

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="quiz_attempts", verbose_name=_("សិស្ស")
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="attempts", verbose_name=_("កម្រងតេស្ត")
    )
    start_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(_("ពិន្ទុ"), null=True)
    completed_at = models.DateTimeField(_("បញ្ចប់នៅ"), null=True, blank=True)

    class Meta:
        verbose_name = _("ការប្រឡងតេស្ត")
        verbose_name_plural = _("ការប្រឡងតេស្ត")
        unique_together = ("student", "quiz")  # One attempt per student per quiz

    def __str__(self):
        return f"{self.student} - {self.quiz} ({self.score})"

    def select_questions(self):
        """
        Randomly select questions for this attempt based on quiz settings.
        Call this when creating/starting the attempt (e.g., in a view).
        Returns a list of selected Question instances in random order.
        """
        from random import sample, shuffle

        selected = []

        # Easy questions
        easy_qs = list(self.quiz.questions.filter(difficulty="EASY"))
        num_easy = min(self.quiz.num_easy_questions, len(easy_qs)) if self.quiz.num_easy_questions > 0 else 0
        if num_easy > 0:
            selected.extend(sample(easy_qs, num_easy))

        # Medium questions
        medium_qs = list(self.quiz.questions.filter(difficulty="MEDIUM"))
        num_medium = min(self.quiz.num_medium_questions, len(medium_qs)) if self.quiz.num_medium_questions > 0 else 0
        if num_medium > 0:
            selected.extend(sample(medium_qs, num_medium))

        # Hard questions
        hard_qs = list(self.quiz.questions.filter(difficulty="HARD"))
        num_hard = min(self.quiz.num_hard_questions, len(hard_qs)) if self.quiz.num_hard_questions > 0 else 0
        if num_hard > 0:
            selected.extend(sample(hard_qs, num_hard))

        # Shuffle the combined list for random presentation order
        shuffle(selected)

        # Create QuizAttemptQuestion instances for this attempt
        for i, question in enumerate(selected):
            QuizAttemptQuestion.objects.get_or_create(
                attempt=self,
                question=question,
                defaults={"order": i + 1}
            )

        return selected


class QuizAttemptQuestion(models.Model):
    """
    Links selected questions to a specific attempt for randomization per student.
    """
    attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE, related_name="selected_questions", verbose_name=_("ការប្រឡង")
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, verbose_name=_("សំណួរ")
    )
    order = models.PositiveIntegerField(_("លំដាប់"), default=0)

    class Meta:
        verbose_name = _("សំណួរក្នុងការប្រឡង")
        verbose_name_plural = _("សំណួរក្នុងការប្រឡង")
        unique_together = ("attempt", "question")
        ordering = ("order",)


class StudentResponse(models.Model):
    # Keep old fields temporarily for migration compatibility
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="quiz_responses", verbose_name=_("សិស្ស")
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="responses", verbose_name=_("កម្រងតេស្ត")
    )
    # New field: nullable for migration
    attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE, related_name="responses", verbose_name=_("ការប្រឡង"), null=True, blank=True
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="responses", verbose_name=_("សំណួរ")
    )
    selected_options = models.ManyToManyField(
        AnswerOption, blank=True, verbose_name=_("ជម្រើសដែលបានជ្រើស")
    )
    text_answer = models.TextField(_("ចម្លើយសរសេរ"), blank=True, null=True)
    points_earned = models.FloatField(_("ពិន្ទុទទួលបាន"), null=True, blank=True)
    submitted_at = models.DateTimeField(_("ដាក់ស្នើនៅ"), auto_now_add=True)

    class Meta:
        verbose_name = _("ចម្លើយសិស្ស")
        verbose_name_plural = _("ចម្លើយសិស្ស")
        # Temporarily remove unique_together to avoid migration error; add later
        # unique_together = ("attempt", "question")

    def __str__(self):
        return f"ចម្លើយពី {self.attempt.student if self.attempt else self.student} - សំណួរ: {self.question}"

    @property
    def student(self):
        return self.attempt.student if self.attempt else self.student

    @property
    def quiz(self):
        return self.attempt.quiz if self.attempt else self.quiz