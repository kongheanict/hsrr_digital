import pandas as pd
from django.contrib import admin, messages
from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
import nested_admin

from .models import QuizCategory, Quiz, Question, AnswerOption
from apps.teachers.models import Teacher

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
    class Meta:
        model = Quiz
        fields = "__all__"
        widgets = {"description": SmallTextarea()}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # Hide/disable teacher field for teacher users
        if self.request and not self.request.user.is_superuser and "teacher" in self.fields:
            self.fields["teacher"].disabled = True
            if not self.instance.pk:  # new object
                teacher = Teacher.objects.filter(user=self.request.user).first()
                if teacher:
                    self.initial["teacher"] = teacher

    def clean(self):
        cleaned_data = super().clean()
        if self.request:
            if not self.request.user.is_superuser:
                teacher = Teacher.objects.filter(user=self.request.user).first()
                cleaned_data["teacher"] = teacher
            else:
                if not cleaned_data.get("teacher"):
                    raise forms.ValidationError("Superadmin must assign a teacher to this quiz.")
        return cleaned_data


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"
        widgets = {"text": SmallTextarea()}


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
    extra = 1
    min_num = 1
    classes = ('collapse',)


class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    form = QuestionForm
    inlines = [AnswerOptionInline]
    extra = 1
    show_change_link = True


# -------------------------
# Excel Import Form
# -------------------------
class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label=_("Select Excel File"))


# -------------------------
# Admin Classes
# -------------------------
@admin.register(QuizCategory)
class QuizCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


class QuizAdmin(nested_admin.NestedModelAdmin):
    form = QuizForm
    list_display = ("title", "category", "teacher", "created_at")
    search_fields = ("title",)
    list_filter = ("category",)
    inlines = [QuestionInline]
    readonly_fields = ("created_at",)
    autocomplete_fields = ("teacher", "category")
    change_list_template = "admin/quizzes/quiz_changelist.html"
    class Media:
        css = {
            'all': ('admin_custom.css',)
        }

    # -------------------------
    # Limit queryset by user
    # -------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        teacher = Teacher.objects.filter(user=request.user).first()
        if teacher:
            return qs.filter(teacher=teacher)
        return qs.none()

    # -------------------------
    # Pass request to form
    # -------------------------
    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)

        class FormWithRequest(form_class):
            def __init__(self2, *args, **kwargs2):
                kwargs2["request"] = request
                super().__init__(*args, **kwargs2)

        return FormWithRequest

    # -------------------------
    # Auto-assign teacher on save
    # -------------------------
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            teacher = Teacher.objects.filter(user=request.user).first()
            if teacher:
                obj.teacher = teacher
        super().save_model(request, obj, form, change)

    # -------------------------
    # Excel Import URLs
    # -------------------------
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel),
                name="quizzes_import_excel",
            ),
            path(
                "download-template-quize/",
                self.admin_site.admin_view(self.download_template),
                name="download_template_quiz",
            ),
        ]
        return custom_urls + urls

    def download_template(self, request):
        from django.http import FileResponse
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
        import io


        wb = Workbook()
        ws = wb.active
        ws.title = "សិស្ស"

        headers = [
            "ប្រភេទ",
            "ចំណងជើងកិច្ចប្រឡង",
            "ពិពណ៌នា",
            "អត្ថបទសំណួរ",
            "ប្រភេទសំណួរ",   # MCQ_SINGLE, MCQ_MULTI, SHORT
            "ជម្រើស",
            "ត្រឹមត្រូវ",
        ]
        if request.user.is_superuser:
            headers.insert(1, "ឈ្មោះគ្រូ")  # បន្ថែមសម្រាប់ superadmin

        # Write headers with style
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")
            ws.column_dimensions[cell.column_letter].width = max(len(header) + 4, 15)

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="សិស្ស_template.xlsx")

    def import_excel(self, request):
        if request.method == "POST":
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                df = pd.read_excel(request.FILES["excel_file"]).fillna("")

                for _, row in df.iterrows():
                    # ប្រភេទ (ប្រើជាខ្មែរ)
                    category_name = row.get("ប្រភេទ") or _("Imported")
                    category, _ = QuizCategory.objects.get_or_create(name=category_name)

                    # គ្រូ
                    teacher = None
                    if request.user.is_superuser:
                        teacher_name = row.get("ឈ្មោះគ្រូ")
                        if teacher_name:
                            from teachers.models import Teacher
                            teacher = Teacher.objects.filter(name=teacher_name).first()
                    else:
                        if hasattr(request.user, "teacher"):
                            teacher = request.user.teacher

                    # បង្កើត Quiz
                    quiz, _ = Quiz.objects.get_or_create(
                        title=row["ចំណងជើងកិច្ចប្រឡង"],
                        category=category,
                        defaults={
                            "description": row.get("ពិពណ៌នា", ""),
                            "teacher": teacher,
                        },
                    )

                    # បង្កើតសំណួរ
                    question, _ = Question.objects.get_or_create(
                        quiz=quiz,
                        text=row["អត្ថបទសំណួរ"],
                        question_type=row["ប្រភេទសំណួរ"],  # MCQ_SINGLE, MCQ_MULTI, SHORT
                    )

                    # ជម្រើសសម្រាប់ MCQ
                    if row["ប្រភេទសំណួរ"] in ["MCQ_SINGLE", "MCQ_MULTI"]:
                        option_text = row.get("ជម្រើស")
                        if option_text:
                            AnswerOption.objects.get_or_create(
                                question=question,
                                text=option_text,
                                defaults={"is_correct": bool(row.get("ត្រឹមត្រូវ", False))},
                            )

                self.message_user(request, _("ការនាំចូលបានជោគជ័យ!"), level=messages.SUCCESS)
                return redirect("..")
        else:
            form = ExcelImportForm()

        return render(request, "admin/quizzes/import_quizzes.html", {"form": form})



# Register properly
admin.site.register(Quiz, QuizAdmin)
