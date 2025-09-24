import pandas as pd
from django.contrib import admin, messages
from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as trans
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
import nested_admin
from django_ckeditor_5.widgets import CKEditor5Widget
from datetime import timedelta, datetime
from django.utils.dateparse import parse_datetime
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from django.db import transaction
from django.utils import timezone
import difflib

from .models import QuizCategory, Quiz, Question, AnswerOption, StudentResponse, QuizAttempt
from apps.teachers.models import Teacher
from apps.classes.models import SchoolClass
from .forms import ExcelImportForm

# -------------------------
# Small Textarea Widget
# -------------------------
class SmallTextarea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {}).update({"rows": 2, "style": "width: 90%;"})
        super().__init__(*args, **kwargs)

# -------------------------
# Forms
# -------------------------
class QuizForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "step": "1"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
    )

    class Meta:
        model = Quiz
        fields = "__all__"
        widgets = {
            "description": SmallTextarea(),
            "time_limit": forms.TextInput(
                attrs={"placeholder": "e.g., 00:30:00 for 30 minutes"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if self.request and not self.request.user.is_superuser and "teacher" in self.fields:
            self.fields["teacher"].disabled = True
            if not self.instance.pk:
                teacher = Teacher.objects.filter(user=self.request.user).first()
                if teacher:
                    self.initial["teacher"] = teacher

    def clean_start_time(self):
        start_time = self.cleaned_data.get("start_time")
        if start_time and isinstance(start_time, (list, tuple)):
            raise forms.ValidationError( trans ("Start time must be a single datetime, not a list."))
        return start_time

    def clean_time_limit(self):
        time_limit = self.cleaned_data.get("time_limit")
        if time_limit:
            try:
                h, m, s = map(int, str(time_limit).split(":"))
                if h < 0 or m < 0 or s < 0 or m > 59 or s > 59:
                    raise ValueError
                return time_limit
            except (ValueError, AttributeError):
                raise forms.ValidationError( trans ("Invalid time limit format. Use HH:MM:SS (e.g., 00:30:00)."))
        return time_limit

    def clean(self):
        cleaned_data = super().clean()
        if self.request:
            if not self.request.user.is_superuser:
                teacher = Teacher.objects.filter(user=self.request.user).first()
                if not teacher:
                    raise forms.ValidationError( trans ("No teacher profile associated with this user."))
                cleaned_data["teacher"] = teacher
            else:
                if not cleaned_data.get("teacher"):
                    raise forms.ValidationError( trans ("Superadmin must assign a teacher to this quiz."))
        return cleaned_data

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"
        widgets = {"text": CKEditor5Widget()}

class AnswerOptionForm(forms.ModelForm):
    class Meta:
        model = AnswerOption
        fields = "__all__"
        widgets = {"text": SmallTextarea()}

# -------------------------
# Nested Inlines
# -------------------------
class AnswerOptionInline(nested_admin.NestedTabularInline):
    model = AnswerOption
    form = AnswerOptionForm
    extra = 0
    min_num = 1
    classes = ("collapse",)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class AnswerOptionFormset(formset):
            def clean(self):
                super().clean()
                if not self.is_valid():
                    return
                question_type = self.instance.question.question_type if self.instance and hasattr(self.instance, 'question') and self.instance.question else None
                if question_type in ["MCQ_SINGLE", "MCQ_MULTI"]:
                    correct_options = sum(
                        1 for form in self.forms if form.cleaned_data.get("is_correct", False)
                    )
                    if correct_options < 1:
                        raise forms.ValidationError(
                             trans ("At least one option must be marked as correct for this question.")
                        )
                    if question_type == "MCQ_SINGLE" and correct_options > 1:
                        raise forms.ValidationError(
                             trans ("Only one option can be marked as correct for single-choice questions.")
                        )

        return AnswerOptionFormset

class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    form = QuestionForm
    inlines = [AnswerOptionInline]
    extra = 0
    show_change_link = True

# -------------------------
# Admin Classes
# -------------------------
@admin.register(QuizCategory)
class QuizCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)

@admin.register(Quiz)
class QuizAdmin(nested_admin.NestedModelAdmin):
    form = QuizForm
    list_display = ("title", "category", "teacher", "status", "start_time", "time_limit", "created_at")
    search_fields = ("title",)
    list_filter = ("category", "classes", "status")
    inlines = [QuestionInline]
    readonly_fields = ("created_at",)
    autocomplete_fields = ("teacher", "category")
    filter_horizontal = ("classes",)
    change_list_template = "admin/quizzes/quiz_changelist.html"
    change_form_template = "admin/quizzes/quiz_change.html"  # Custom change form template

    class Media:
        css = {"all": ("admin_custom.css",)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        teacher = Teacher.objects.filter(user=request.user).first()
        if teacher:
            return qs.filter(teacher=teacher)
        return qs.none()

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)

        class FormWithRequest(form_class):
            def __init__(self2, *args, **kwargs2):
                kwargs2["request"] = request
                super().__init__(*args, **kwargs2)

        return FormWithRequest

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            teacher = Teacher.objects.filter(user=request.user).first()
            if teacher:
                obj.teacher = teacher
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """Detect changes to AnswerOption.is_correct or SHORT question/answer text and recalculate scores."""
        quiz = form.instance
        original_answer_options = {}
        original_questions = {}
        if change:
            for question in quiz.questions.all():
                original_questions[question.id] = {
                    'text': question.text,
                    'question_type': question.question_type
                }
                for option in question.options.all():
                    original_answer_options[option.id] = {
                        'is_correct': option.is_correct,
                        'text': option.text
                    }

        super().save_related(request, form, formsets, change)

        answer_changed = False
        for question_formset in formsets:
            if hasattr(question_formset, 'forms'):
                for question_form in question_formset.forms:
                    question = question_form.instance
                    if isinstance(question, Question) and question.pk:
                        original = original_questions.get(question.id, {})
                        if question.question_type == 'SHORT' and original.get('text') != question.text:
                            answer_changed = True
                            LogEntry.objects.log_action(
                                user_id=request.user.id,
                                content_type_id=ContentType.objects.get_for_model(Question).pk,
                                object_id=question.pk,
                                object_repr=str(question),
                                action_flag=CHANGE,
                                change_message= trans ("Updated SHORT question text to: %s") % question.text
                            )
                    if hasattr(question_formset, 'nested_formsets'):
                        for answer_formset in question_formset.nested_formsets:
                            for answer_form in answer_formset.forms:
                                answer = answer_form.instance
                                if isinstance(answer, AnswerOption) and answer.pk:
                                    original_option = original_answer_options.get(answer.pk, {})
                                    if original_option.get('is_correct') != answer.is_correct:
                                        answer_changed = True
                                        LogEntry.objects.log_action(
                                            user_id=request.user.id,
                                            content_type_id=ContentType.objects.get_for_model(AnswerOption).pk,
                                            object_id=answer.pk,
                                            object_repr=str(answer),
                                            action_flag=CHANGE,
                                            change_message= trans ("Changed is_correct to %s for option: %s") % (
                                                answer.is_correct, answer.text
                                            )
                                        )
                                    if (hasattr(answer, 'question') and answer.question and 
                                        answer.question.question_type == 'SHORT' and 
                                        original_option.get('text') != answer.text):
                                        answer_changed = True
                                        LogEntry.objects.log_action(
                                            user_id=request.user.id,
                                            content_type_id=ContentType.objects.get_for_model(AnswerOption).pk,
                                            object_id=answer.pk,
                                            object_repr=str(answer),
                                            action_flag=CHANGE,
                                            change_message= trans ("Updated SHORT answer text to: %s") % answer.text
                                        )

        if answer_changed:
            attempts = QuizAttempt.objects.filter(quiz=quiz)
            for attempt in attempts:
                self.recalculate_quiz_attempt_score(attempt, request)
            if attempts:
                messages.info(request,  trans ("Recalculated scores for %d QuizAttempt(s) due to answer changes.") % len(attempts))

    def recalculate_quiz_attempt_score(self, attempt, request=None):
        """Recalculate the total score for a QuizAttempt based on StudentResponse."""
        quiz = attempt.quiz
        student = attempt.student
        student_responses = StudentResponse.objects.filter(
            student=student,
            quiz=quiz
        ).select_related('question').prefetch_related('selected_options')
        
        total_score = 0
        for question in quiz.questions.all():
            response = student_responses.filter(question=question).first()
            score = 0
            user_answer = response.selected_options.all().values_list('id', flat=True) if response and response.selected_options.exists() else []
            user_text_answer = response.text_answer if response else None

            if question.question_type in ["MCQ_SINGLE", "MCQ_MULTI"]:
                correct_option_ids = [opt.id for opt in question.options.all() if opt.is_correct]
                if user_answer:
                    if question.question_type == "MCQ_SINGLE" and len(user_answer) == 1 and user_answer[0] == correct_option_ids[0]:
                        score = question.points or 1
                    elif question.question_type == "MCQ_MULTI" and sorted(user_answer) == sorted(correct_option_ids):
                        score = question.points or 1
            elif question.question_type == "SHORT" and user_text_answer:
                correct_answer = question.options.first().text if question.options.exists() else None
                if correct_answer and user_text_answer.strip().lower() == correct_answer.lower():
                    score = question.points or 1
                else:
                    keywords = ["180", "degrees"]  # Customize for your needs
                    if user_text_answer and any(keyword in user_text_answer.lower() for keyword in keywords):
                        score = question.points or 1

            total_score += score

        if attempt.score != total_score:
            attempt.score = total_score
            attempt.save()
            if request:
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(attempt).pk,
                    object_id=attempt.pk,
                    object_repr=str(attempt),
                    action_flag=CHANGE,
                    change_message= trans ("Recalculated score to %s for quiz: %s") % (total_score, quiz.title)
                )

    def recalculate_all_attempts(self, request, queryset):
        """Admin action to recalculate scores for all QuizAttempts of selected quizzes."""
        total_attempts = 0
        for quiz in queryset:
            attempts = QuizAttempt.objects.filter(quiz=quiz)
            total_attempts += len(attempts)
            for attempt in attempts:
                self.recalculate_quiz_attempt_score(attempt, request)
        messages.success(request,  trans ("Successfully recalculated scores for %d QuizAttempt(s) across selected quizzes.") % total_attempts)

    recalculate_all_attempts.short_description =  trans ("Recalculate all QuizAttempt scores")

    def recalculate_quiz_scores(self, request, object_id):
        """Handle manual recalculation of QuizAttempt scores for a specific quiz."""
        try:
            quiz = Quiz.objects.get(id=object_id)
            attempts = QuizAttempt.objects.filter(quiz=quiz)

            for attempt in attempts:
                # call the attempt-level recalculation
                self.recalculate_quiz_attempt_score(attempt)  # ONLY pass attempt

            messages.success(
                request,
                trans ("Successfully recalculated scores for %d QuizAttempt(s) for quiz: %s") % (len(attempts), quiz.title)
            )
        except Quiz.DoesNotExist:
            messages.error(request, trans ("Quiz not found."))
        return redirect(reverse('admin:quizzes_quiz_change', args=[object_id]))


    def recalculate_quiz_attempt_score(self, attempt):
        """Recalculate a single QuizAttempt score based on current StudentResponses."""
        import difflib

        total_score = 0
        responses = StudentResponse.objects.filter(
            student=attempt.student,
            quiz=attempt.quiz
        ).select_related('question').prefetch_related('selected_options')

        for response in responses:
            question = response.question
            points_earned = 0

            if question.question_type == "MCQ_SINGLE":
                correct_option = question.options.filter(is_correct=True).first()
                if correct_option and response.selected_options.filter(id=correct_option.id).exists():
                    points_earned = question.points

            elif question.question_type == "MCQ_MULTI":
                all_options = set(question.options.values_list('id', flat=True))
                correct_options = set(question.options.filter(is_correct=True).values_list('id', flat=True))
                wrong_options = all_options - correct_options
                user_answers = set(response.selected_options.values_list('id', flat=True))

                num_correct = len(correct_options)
                num_wrong = len(wrong_options)

                num_correct_selected = len(user_answers & correct_options)
                num_wrong_selected = len(user_answers & wrong_options)

                # Partial credit with strict penalty
                score_from_correct = (question.points * num_correct_selected / num_correct) if num_correct else 0
                penalty_from_wrong = (question.points * num_wrong_selected / num_wrong) if num_wrong else 0

                points_earned = score_from_correct - penalty_from_wrong

                # Cap between 0 and full points
                points_earned = max(0, min(points_earned, question.points))


            elif question.question_type == "SHORT":
                correct_answer = question.options.filter(is_correct=True).first()
                if correct_answer and response.text_answer:
                    similarity = difflib.SequenceMatcher(
                        None,
                        response.text_answer.strip().lower(),
                        correct_answer.text.strip().lower()
                    ).ratio()
                    points_earned = round(question.points * similarity, 2)

            # Save points earned per question
            response.points_earned = points_earned
            response.save(update_fields=['points_earned'])

            total_score += points_earned

        attempt.score = round(total_score, 2)
        attempt.save(update_fields=['score'])

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel),
                name="quizzes_import_excel",
            ),
            path(
                "download-template-quiz/",
                self.admin_site.admin_view(self.download_template),
                name="download_template_quiz",
            ),
            path(
                "<path:object_id>/recalculate-scores/",
                self.admin_site.admin_view(self.recalculate_quiz_scores),
                name="quizzes_recalculate_scores",
            ),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        if request.method == "POST":
            form = ExcelImportForm(request.POST, request.FILES)
            if not form.is_valid():
                messages.error(request,  trans ("មានបញ្ហាក្នុងទម្រង់បញ្ចូល: សូមពិនិត្យឯកសារដែលបានផ្ទុកឡើង"))
                return render(request, "admin/quizzes/import_quizzes.html", {"form": form})

            try:
                df = pd.read_excel(request.FILES["excel_file"]).fillna("")
                if df.empty:
                    messages.error(request,  trans ("ឯកសារ Excel ទទេ។ សូមផ្តល់ទិន្នន័យ"))
                    return render(request, "admin/quizzes/import_quizzes.html", {"form": form})

                column_map = {
                    "Category": "Category",
                    "Quiz Title": "Quiz Title",
                    "Description": "Description",
                    "Classes": "Classes",
                    "Time Limit": "Time Limit",
                    "Start Time": "Start Time",
                    "Status": "Status",
                    "Allow Check Answer": "Allow Check Answer",
                    "Allow See Score": "Allow See Score",
                    "Question Text": "Question Text",
                    "Question Type": "Question Type",
                    "Option Text": "Option Text",
                    "Is Correct": "Is Correct",
                    "Teacher Name": "Teacher Name",
                    "Points": "Points",
                }
                df_columns = df.columns.str.strip()
                for col in df_columns:
                    for key in column_map:
                        if key.lower() in col.lower():
                            column_map[col] = column_map[key]

                required_columns = ["Quiz Title"]
                missing_columns = [col for col in required_columns if not any(col.lower() in c.lower() for c in df_columns)]
                if missing_columns:
                    messages.error(request,  trans ("ខ្វះជួរឈរ: %s. សូមប្រើទម្រង់ត្រឹមត្រូវ") % ", ".join(missing_columns))
                    return render(request, "admin/quizzes/import_quizzes.html", {"form": form})

                df = df.rename(columns=column_map)
                df = df[df[['Category', 'Quiz Title', 'Question Text']].notnull().any(axis=1)]

                current_quiz = None
                current_question = None
                answer_changed = False
                with transaction.atomic():
                    for index, row in df.iterrows():
                        try:
                            print(f"Row {index + 2}: Quiz Title={row.get('Quiz Title')}, Question Text={row.get('Question Text')}, "
                                  f"Status={row.get('Status')}, Is Correct={row.get('Is Correct')}, "
                                  f"Allow Check Answer={row.get('Allow Check Answer')}, Allow See Score={row.get('Allow See Score')}, "
                                  f"Teacher Name={row.get('Teacher Name')}")

                            if row.get("Quiz Title"):
                                category_name = row.get("Category") or "Imported"
                                category, _ = QuizCategory.objects.get_or_create(name=category_name)

                                teacher = None
                                if request.user.is_superuser:
                                    teacher_name = row.get("Teacher Name")
                                    if teacher_name:
                                        teacher = Teacher.objects.filter(given_name=teacher_name).first()
                                        if not teacher:
                                            messages.error(
                                                request,
                                                 trans ("គ្រូ '%s' មិនមាននៅក្នុងជួរទី %d") % (teacher_name, index + 2),
                                            )
                                            continue
                                else:
                                    teacher = Teacher.objects.filter(user=request.user).first()
                                    if not teacher:
                                        messages.error(
                                            request,
                                             trans ("គ្មានទម្រង់គ្រូសម្រាប់អ្នកប្រើប្រាស់នៅជួរទី %d") % (index + 2),
                                        )
                                        continue

                                class_names = row.get("Classes", "")
                                classes = []
                                if isinstance(class_names, str) and class_names.strip():
                                    class_names = [name.strip() for name in class_names.split(",")]
                                    classes = SchoolClass.objects.filter(name__in=class_names)
                                    if class_names and not classes:
                                        messages.warning(
                                            request,
                                             trans ("គ្មានថ្នាក់ត្រឹមត្រូវសម្រាប់ '%s' នៅជួរទី %d") % (row.get("Classes"), index + 2),
                                        )

                                time_limit = None
                                time_limit_str = row.get("Time Limit", "")
                                if time_limit_str:
                                    try:
                                        h, m, s = map(int, str(time_limit_str).split(":"))
                                        if h < 0 or m < 0 or s < 0 or m > 59 or s > 59:
                                            raise ValueError
                                        time_limit = timedelta(hours=h, minutes=m, seconds=s)
                                    except ValueError:
                                        messages.warning(
                                            request,
                                             trans ("ទម្រង់កំណត់ពេលវេលាមិនត្រឹមត្រូវនៅជួរទី %d: %s") % (index + 2, time_limit_str),
                                        )

                                start_time = None
                                start_time_str = row.get("Start Time", "")
                                if start_time_str:
                                    try:
                                        start_time = parse_datetime(str(start_time_str))
                                        if not start_time:
                                            raise ValueError("Invalid datetime format")
                                    except ValueError:
                                        messages.warning(
                                            request,
                                             trans ("ទម្រង់ពេលវេលាចាប់ផ្តើមមិនត្រឹមត្រូវនៅជួរទី %d: %s") % (index + 2, start_time_str),
                                        )

                                status = str(row.get("Status", "DRAFT")).upper()
                                status_choices = dict(Quiz.STATUS_CHOICES)
                                if status not in status_choices:
                                    messages.warning(
                                        request,
                                         trans ("ស្ថានភាពមិនត្រឹមត្រូវនៅជួរទី %d: %s. ប្រើ DRAFT") % (index + 2, status),
                                    )
                                    status = "DRAFT"

                                allow_check_answer = row.get("Allow Check Answer", False)
                                if isinstance(allow_check_answer, str):
                                    allow_check_answer = allow_check_answer.strip().lower() in ('true', '1', 'yes')
                                allow_see_score = row.get("Allow See Score", False)
                                if isinstance(allow_see_score, str):
                                    allow_see_score = allow_see_score.strip().lower() in ('true', '1', 'yes')

                                current_quiz, created = Quiz.objects.get_or_create(
                                    title=row["Quiz Title"],
                                    category=category,
                                    teacher=teacher,
                                    defaults={
                                        "description": row.get("Description", ""),
                                        "time_limit": time_limit,
                                        "start_time": start_time,
                                        "status": status,
                                        "allow_check_answer": allow_check_answer,
                                        "allow_see_score": allow_see_score,
                                    },
                                )
                                if not created:
                                    original_questions = {q.id: {'text': q.text, 'question_type': q.question_type} for q in current_quiz.questions.all()}
                                    original_options = {opt.id: {'is_correct': opt.is_correct, 'text': opt.text} for q in current_quiz.questions.all() for opt in q.options.all()}
                                if classes:
                                    current_quiz.classes.set(classes)
                                current_quiz.save()

                            if row.get("Question Text") and current_quiz:
                                points = row.get("Points", 1)
                                try:
                                    points = int(float(points)) if points else 1
                                except (ValueError, TypeError):
                                    points = 1
                                    messages.warning(
                                        request,
                                         trans ("ពិន្ទុមិនត្រឹមត្រូវនៅជួរទី %d: %s. ប្រើ 1") % (index + 2, row.get("Points")),
                                    )
                                question_type = row.get("Question Type", "MCQ_SINGLE")
                                if question_type not in dict(Question.QUESTION_TYPES):
                                    messages.warning(
                                        request,
                                         trans ("ប្រភេទសំណួរមិនត្រឹមត្រូវនៅជួរទី %d: %s. ប្រើ MCQ_SINGLE") % (index + 2, question_type),
                                    )
                                    question_type = "MCQ_SINGLE"
                                current_question, created = Question.objects.get_or_create(
                                    quiz=current_quiz,
                                    text=row["Question Text"],
                                    question_type=question_type,
                                    defaults={"points": points, "order": current_quiz.questions.count() + 1},
                                )
                                if not created and question_type == "SHORT":
                                    if original_questions.get(current_question.id, {}).get('text') != row["Question Text"]:
                                        answer_changed = True
                                        LogEntry.objects.log_action(
                                            user_id=request.user.id,
                                            content_type_id=ContentType.objects.get_for_model(Question).pk,
                                            object_id=current_question.pk,
                                            object_repr=str(current_question),
                                            action_flag=CHANGE,
                                            change_message= trans ("Updated SHORT question text to: %s") % row["Question Text"]
                                        )

                            if row.get("Option Text") and current_question:
                                is_correct_value = row.get("Is Correct", False)
                                if isinstance(is_correct_value, str):
                                    is_correct = is_correct_value.strip().lower() in ('true', '1', 'yes')
                                else:
                                    is_correct = bool(is_correct_value)
                                option, created = AnswerOption.objects.get_or_create(
                                    question=current_question,
                                    text=str(row["Option Text"]).strip(),
                                    defaults={"is_correct": is_correct},
                                )
                                if not created and original_options.get(option.id, {}).get('is_correct') != is_correct:
                                    answer_changed = True
                                    option.is_correct = is_correct
                                    option.save()
                                    LogEntry.objects.log_action(
                                        user_id=request.user.id,
                                        content_type_id=ContentType.objects.get_for_model(AnswerOption).pk,
                                        object_id=option.pk,
                                        object_repr=str(option),
                                        action_flag=CHANGE,
                                        change_message= trans ("Changed is_correct to %s for option: %s") % (is_correct, option.text)
                                    )
                                if not created and option.question.question_type == "SHORT" and original_options.get(option.id, {}).get('text') != option.text:
                                    answer_changed = True
                                    LogEntry.objects.log_action(
                                        user_id=request.user.id,
                                        content_type_id=ContentType.objects.get_for_model(AnswerOption).pk,
                                        object_id=option.pk,
                                        object_repr=str(option),
                                        action_flag=CHANGE,
                                        change_message= trans ("Updated SHORT answer text to: %s") % option.text
                                    )

                        except Exception as e:
                            messages.error(request,  trans ("មានបញ្ហានៅជួរទី %d: %s") % (index + 2, str(e)))
                            print(f"Error in row {index + 2}: {str(e)}")

                    if answer_changed:
                        attempts = QuizAttempt.objects.filter(quiz=current_quiz)
                        for attempt in attempts:
                            self.recalculate_quiz_attempt_score(attempt, request)
                        if attempts:
                            messages.info(request,  trans ("Recalculated scores for %d QuizAttempt(s) due to answer changes in import.") % len(attempts))

                    messages.success(request,  trans ("ការនាំចូល Excel សម្រេចដោយជោគជ័យ! បានដំណើរការជួរចំនួន %d") % len(df))
                    return redirect("..")
            except Exception as e:
                messages.error(request,  trans ("មានបញ្ហាអាន Excel: %s") % str(e))
                print(f"Excel read error: {str(e)}")
                return render(request, "admin/quizzes/import_quizzes.html", {"form": form})
        else:
            form = ExcelImportForm()
        return render(request, "admin/quizzes/import_quizzes.html", {"form": form})

    def download_template(self, request):
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Quiz Import Template"

            headers = [
                "Category", "Teacher Name", "Quiz Title", "Description", "Classes",
                "Time Limit", "Start Time", "Status", "Allow Check Answer", "Allow See Score",
                "Question Text", "Question Type", "Option Text", "Is Correct", "Points"
            ]

            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num, value=header)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center")
                ws.column_dimensions[cell.column_letter].width = max(len(header) + 4, 15)

            sample_data = [
                ["Mathematics", "Mok Kong", "Basic Math Quiz", "Test math skills", "Class 16A,Class 16B", "00:30:00", "2025-09-18 09:00:00", "PUBLISH", False, False, "What is 2 + 2?", "MCQ_SINGLE", "4", True, 1],
                ["", "", "", "", "", "", "", "", "", "", "", "3", False, ""],
                ["", "", "", "", "", "", "", "", "", "What is 5 x 3?", "MCQ_SINGLE", "15", True, 2],
                ["", "", "", "", "", "", "", "", "", "", "", "18", False, ""],
                ["", "", "", "", "", "", "", "", "", "What is the sum of angles in a triangle?", "SHORT", "", "", 2],
                ["Science", "", "General Science Quiz", "Test science knowledge", "Class 16B", "00:45:00", "2025-09-19 10:00:00", "RELEASE", False, False, "Which are fruits? (Select all)", "MCQ_MULTI", "Apple", True, 2],
                ["", "", "", "", "", "", "", "", "", "", "", "Carrot", False, ""],
                ["", "", "", "", "", "", "", "", "", "", "", "Banana", True, ""],
                ["", "", "", "", "", "", "", "", "", "What is the chemical symbol for water?", "SHORT", "", "", 1],
                ["", "", "", "", "", "", "", "", "", "Which planets are gas giants? (Select all)", "MCQ_MULTI", "Earth", False, 2],
                ["", "", "", "", "", "", "", "", "", "", "", "Jupiter", True, ""],
                ["", "", "", "", "", "", "", "", "", "", "", "Saturn", True, ""],
                ["", "", "", "", "", "", "", "", "", "What is Mars primarily composed of?", "SHORT", "", "", 1],
                ["", "", "", "", "", "", "", "", "", "What is the speed of light?", "MCQ_SINGLE", "300,000 km/s", True, 1],
                ["", "", "", "", "", "", "", "", "", "", "", "250,000 km/s", False, ""],
            ]

            for row_num, row_data in enumerate(sample_data, 2):
                for col_num, value in enumerate(row_data, 1):
                    cell_value = str(value) if value is not None else ""
                    ws.cell(row=row_num, column=col_num, value=cell_value)

            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(
                buffer,
                as_attachment=True,
                filename="quiz_import_template.xlsx",
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            import traceback
            print(f"Error in download_template: {e}\n{traceback.format_exc()}")
            wb = Workbook()
            ws = wb.active
            ws['A1'] = "Error creating template. Check logs."
            ws['A2'] = str(e)
            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename="error_template.xlsx")

# @admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "score", "completed_at")
    list_filter = ("quiz", "completed_at")
    search_fields = ("student__username",)

# @admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "question_type", "points")
    list_filter = ("quiz", "question_type")
    search_fields = ("text", "quiz__title")
    inlines = [AnswerOptionInline]

# @admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("question__quiz", "is_correct")
    search_fields = ("text", "question__text")

# @admin.register(StudentResponse)
class StudentResponseAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "question", "question_type", "selected_options_display", "text_answer", "modified_at")
    list_filter = ("quiz", "question__question_type", "student")
    search_fields = ("quiz__title", "question__text", "student__user__username", "text_answer")
    readonly_fields = ("modified_at", "created_at")
    date_hierarchy = "modified_at"

    def question_type(self, obj):
        return obj.question.question_type
    question_type.short_description =  trans ("Question Type")

    def selected_options_display(self, obj):
        return ", ".join(opt.text for opt in obj.selected_options.all()) or  trans ("None")
    selected_options_display.short_description =  trans ("Selected Options")
