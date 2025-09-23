from django.contrib import admin, messages
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as trans
import pandas as pd
import io
from django.http import FileResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from datetime import datetime

from .models import Student, Enrollment, Parent
from apps.classes.models import SchoolClass
from apps.core.models import AcademicYear, Semester, Major

# -------------------------
# Small textarea widget
# -------------------------
class SmallTextarea(forms.Textarea):
    def __init_trans (self, *args, **kwargs):
        kwargs.setdefault("attrs", {}).update({"rows": 2, "style": "width: 90%;"})
        super().__init_trans (*args, **kwargs)

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = "__all__"
        widgets = {"place_of_birth": SmallTextarea()}

# -------------------------
# Inlines
# -------------------------
class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    autocomplete_fields = ["school_class", "academic_year", "semester"]
    fields = ("school_class", "academic_year", "semester", "status", "enrolled_date")
    verbose_name = trans ("ការចុះឈ្មោះ")
    verbose_name_plural = trans ("ការចុះឈ្មោះ")

class ParentInline(admin.TabularInline):
    model = Parent.students.through
    extra = 1
    verbose_name = trans ("អាណាព្យាបាល")
    verbose_name_plural = trans ("អាណាព្យាបាល")

# -------------------------
# Helpers
# -------------------------
def parse_date(value):
    """Parse Excel / string dates. Accept dd/mm/YYYY or YYYY-MM-DD or Excel serials."""
    if pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    s = str(value).strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except Exception:
        pass
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        pass
    try:
        return pd.to_datetime(s, dayfirst=True, errors="coerce").date()
    except Exception:
        return None

def khmer_status_to_code(kh):
    mapping = {
        "កំពុងរៀន": Enrollment.Status.ACTIVE,
        "ផ្ទេរចេញ": Enrollment.Status.TRANSFERRED,
        "បោះបង់": Enrollment.Status.DROPOUT,
        "បញ្ចប់ការសិក្សា": Enrollment.Status.GRADUATED,
        "ដកចេញ": Enrollment.Status.WITHDRAWN,
    }
    return mapping.get(str(kh).strip(), Enrollment.Status.ACTIVE)

def khmer_gender_to_code(kh):
    mapping = {
        "ប្រុស": "M",
        "ស្រី": "F",
        "ផ្សេងៗ": "O",
        "other": "O",
        "male": "M",
        "female": "F",
    }
    return mapping.get(str(kh).strip(), "")

def safe_str(value):
    """Convert value to string safely (handles numeric phone numbers)."""
    if value is None:
        return ""
    return str(value).strip()

# -------------------------
# Student Admin
# -------------------------
class StudentAdmin(admin.ModelAdmin):
    form = StudentForm
    list_display = (
        "student_id",
        "family_name",
        "given_name",
        "gender",
        "student_type",
        "get_class_name",
        "get_academic_year",
        "phone_number",
        "major",
        "image_tag",
        "user_link",
    )
    search_fields = ("student_id", "family_name", "given_name", "phone_number")
    autocomplete_fields = ["major"]
    readonly_fields = ("image_tag", "user")
    inlines = [EnrollmentInline, ParentInline]
    list_per_page = 25
    change_list_template = "admin/students/student_changelist.html"
    actions = ['assign_users_to_students']

    class Media:
        css = {"all": ("admin_custom.css",)}

    def image_tag(self, obj):
        if getattr(obj, "profile_image", None):
            return format_html(
                '<img src="{}" width="40" height="50" style="object-fit:cover;"/>',
                obj.profile_image.url,
            )
        return "-"
    image_tag.short_description = trans ("រូបថត")

    def user_link(self, obj):
        return obj.user.username if getattr(obj, "user", None) else "-"
    user_link.short_description = trans ("គណនីប្រើប្រាស់")

    def get_class_name(self, obj):
        enrollment = obj.enrollments.filter(status=Enrollment.Status.ACTIVE).first()
        if not enrollment:
            enrollment = obj.enrollments.first()
        return enrollment.school_class.name if enrollment and enrollment.school_class else "-"
    get_class_name.short_description = trans ("ថ្នាក់រៀន")
    get_class_name.admin_order_field = "enrollments__school_class__name"

    def get_academic_year(self, obj):
        enrollment = obj.enrollments.filter(status=Enrollment.Status.ACTIVE).first()
        if not enrollment:
            enrollment = obj.enrollments.first()
        return enrollment.academic_year.name if enrollment and enrollment.academic_year else "-"
    get_academic_year.short_description = trans ("ឆ្នាំសិក្សា")
    get_academic_year.admin_order_field = "enrollments__academic_year__name"

    def get_list_filter(self, request):
        from django.contrib import admin
        from django.utils.translation import gettext_lazy as _

        class ClassFilter(admin.SimpleListFilter):
            title = trans ("ថ្នាក់រៀន")
            parameter_name = "school_class"

            def lookups(self, request, model_admin):
                classes = SchoolClass.objects.all().order_by("order")
                return [(str(c.id), c.name) for c in classes]

            def queryset(self, request, queryset):
                val = self.value()
                if val:
                    return queryset.filter(enrollments__school_class__id=val)
                return queryset

        class YearFilter(admin.SimpleListFilter):
            title = trans ("ឆ្នាំសិក្សា")
            parameter_name = "academic_year"

            def lookups(self, request, model_admin):
                years = AcademicYear.objects.all().order_by("-name")
                return [(str(y.id), y.name) for y in years]

            def queryset(self, request, queryset):
                val = self.value()
                if val:
                    return queryset.filter(enrollments__academic_year__id=val)
                return queryset

            def value(self):
                v = super().value()
                if v is None:
                    latest = AcademicYear.objects.order_by("-name").first()
                    return str(latest.id) if latest else None
                return v

            def choices(self, changelist):
                for lookup, title in self.lookup_choices:
                    yield {
                        "selected": self.value() == str(lookup),
                        "query_string": changelist.get_query_string({self.parameter_name: lookup}, []),
                        "display": title,
                    }

        return (ClassFilter, YearFilter)

    def changelist_view(self, request, extra_context=None):
        year_param = "academic_year"
        if year_param not in request.GET:
            active = AcademicYear.objects.filter(status=True).first()
            if active:
                q = request.GET.copy()
                q[year_param] = str(active.id)
                request.GET = q
                request.META["QUERY_STRING"] = q.urlencode()
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-students/",
                self.admin_site.admin_view(self.import_students),
                name="import_students",
            ),
            path(
                "export-students/",
                self.admin_site.admin_view(self.export_students),
                name="export_students",
            ),
            path(
                "download-template/",
                self.admin_site.admin_view(self.download_template),
                name="download_template_students",
            ),
        ]
        return custom_urls + urls

    def download_template(self, request):
        wb = Workbook()
        ws = wb.active
        ws.title = "សិស្ស"

        headers = [
            "ល.រ",
            "លេខសម្គាល់សិស្ស",
            "នាមត្រកូល",
            "នាមខ្លួន",
            "ថ្នាក់រៀន",
            "ស្ថានភាព",
            "ថ្ងៃខែឆ្នាំកំណើត",
            "កន្លែងកំណើត",
            "លេខទូរស័ព្ទ",
            "ភេទ",
            "ប្រភេទសិស្ស",
            "កាលបរិច្ឆេទចូលរៀន",
            "ប្រភេទថ្នាក់",
            "ឆ្នាំសិក្សា",
            "ឈ្មោះឪពុក",
            "មុខរបរ ឪពុក",
            "លេខទូរស័ព្ទ ឪពុក",
            "ឈ្មោះម្តាយ",
            "មុខរបរ ម្តាយ",
            "លេខទូរស័ព្ទ ម្តាយ",
        ]

        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")
            ws.column_dimensions[cell.column_letter].width = max(len(header) + 4, 15)

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="សិស្ស_template.xlsx")

    def import_students(self, request):
        if request.method == "POST" and request.FILES.get("excel_file"):
            try:
                df = pd.read_excel(request.FILES["excel_file"], dtype=object)
            except Exception as e:
                self.message_user(request, trans ("មិនអាចបើកឯកសារ Excel: %s") % e, level=messages.ERROR)
                return redirect("..")

            df.rename(columns=lambda c: str(c).strip(), inplace=True)

            for _, row in df.iterrows():
                student_id = safe_str(row.get("លេខសម្គាល់សិស្ស") or row.get("លេខសម្គាល់សិស្ស", "")).strip()
                if not student_id:
                    continue

                family_name = safe_str(row.get("នាមត្រកូល"))
                given_name = safe_str(row.get("នាមខ្លួន"))
                phone_number = safe_str(row.get("លេខទូរស័ព្ទ"))
                place_of_birth = safe_str(row.get("កន្លែងកំណើត"))
                student_type_value = safe_str(row.get("ប្រភេទសិស្ស"))
                gender_value = safe_str(row.get("ភេទ"))

                dob = parse_date(row.get("ថ្ងៃខែឆ្នាំកំណើត"))
                enrollment_date = parse_date(row.get("កាលបរិច្ឆេទចូលរៀន"))

                major_name = safe_str(row.get("ប្រភេទថ្នាក់") or row.get("ជំនាញ") or row.get("ប្រភេទថ្នាក់"))
                major_obj = None
                if major_name:
                    major_obj, _ = Major.objects.get_or_create(name=major_name)

                gender_code = khmer_gender_to_code(gender_value)
                student_type_code = student_type_value
                map_type = {
                    "ពេញម៉ោង": "ពេញម៉ោង",
                    "ក្រៅម៉ោង": "ក្រៅម៉ោង",
                    "Full-Time": "ពេញម៉ោង",
                    "Part-Time": "ក្រៅម៉ោង",
                }
                student_type_code = map_type.get(student_type_value, student_type_value)

                student, created = Student.objects.update_or_create(
                    student_id=student_id,
                    defaults={
                        "family_name": family_name,
                        "given_name": given_name,
                        "gender": gender_code or "",
                        "date_of_birth": dob,
                        "place_of_birth": place_of_birth,
                        "phone_number": phone_number,
                        "student_type": student_type_code,
                        "enrollment_date": enrollment_date,
                        "major": major_obj,
                    },
                )

                class_name = safe_str(row.get("ថ្នាក់រៀន"))
                year_name = safe_str(row.get("ឆ្នាំសិក្សា"))

                school_class_obj = SchoolClass.objects.filter(name=class_name).first() if class_name else None
                academic_year_obj = None
                if year_name:
                    academic_year_obj, _ = AcademicYear.objects.get_or_create(name=year_name)

                status_kh = safe_str(row.get("ស្ថានភាព"))
                status_code = khmer_status_to_code(status_kh)

                if student and school_class_obj and academic_year_obj:
                    Enrollment.objects.update_or_create(
                        student=student,
                        academic_year=academic_year_obj,
                        semester=None,
                        defaults={
                            "school_class": school_class_obj,
                            "status": status_code,
                            "enrolled_date": enrollment_date or (datetime.today().date()),
                        },
                    )

                father_name = safe_str(row.get("ឈ្មោះឪពុក"))
                father_job = safe_str(row.get("មុខរបរ ឪពុក"))
                father_phone = safe_str(row.get("លេខទូរស័ព្ទ ឪពុក"))

                mother_name = safe_str(row.get("ឈ្មោះម្តាយ"))
                mother_job = safe_str(row.get("មុខរបរ ម្តាយ"))
                mother_phone = safe_str(row.get("លេខទូរស័ព្ទ ម្តាយ"))

                if father_name or mother_name:
                    parent, _ = Parent.objects.get_or_create(
                        father_name=father_name or None,
                        mother_name=mother_name or None,
                        defaults={
                            "father_phone": father_phone or None,
                            "mother_phone": mother_phone or None,
                            "father_occupation": father_job or None,
                            "mother_occupation": mother_job or None,
                        },
                    )
                    parent.students.add(student)

            # ✅ fixed here
            self.message_user(request, trans ("✅ អានទិន្នន័យសិស្សរួចរាល់"), level=messages.SUCCESS)
            return redirect("..")

        return render(request, "admin/students/import_students.html", {})

    def export_students(self, request):
        qs = Student.objects.all()
        data = []
        for s in qs:
            enrollments = ", ".join([f"{e.school_class} ({e.academic_year})" for e in s.enrollments.all()])
            parents = ", ".join([f"{p.father_name or ''} / {p.mother_name or ''}" for p in s.parents.all()])
            data.append(
                {
                    "លេខសម្គាល់សិស្ស": s.student_id,
                    "នាមត្រកូល": s.family_name,
                    "នាមខ្លួន": s.given_name,
                    "ភេទ": s.gender,
                    "ថ្ងៃខែឆ្នាំកំណើត": s.date_of_birth,
                    "លេខទូរស័ព្ទ": s.phone_number,
                    "កន្លែងកំណើត": s.place_of_birth,
                    "ប្រភេទសិស្ស": s.student_type,
                    "ជំនាញ": s.major.name if s.major else "",
                    "ការចុះឈ្មោះ": enrollments,
                    "អាណាព្យាបាល": parents,
                }
            )
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="សិស្ស.xlsx")

    def assign_users_to_students(self, request, queryset):
        created_count = 0
        skipped_count = 0
        group_name = "សិស្ស"
        group, _ = Group.objects.get_or_create(name=group_name)
        default_password = "123@Gov.kh"

        for student in queryset:
            if student.user:
                skipped_count += 1
                continue

            username = student.student_id
            email = f"{username}@school.local"
            user = User.objects.create_user(
                username=username,
                password=default_password,
                email=email,
                first_name=student.given_name or "",
                last_name=student.family_name or "",
            )
            user.groups.add(group)
            student.user = user
            student.save()
            created_count += 1

        # ✅ already fixed here
        self.message_user(
            request,
            trans ("✅ បង្កើត %(created)d គណនីថ្មី, ⏭️ %(skipped)d សិស្សមានគណនីរួចហើយ") % {
                "created": created_count,
                "skipped": skipped_count,
            },
            level=messages.SUCCESS,
        )

    assign_users_to_students.short_description = trans ("បង្កើតគណនីសិស្ស")


