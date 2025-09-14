# teachers/admin.py
from django.contrib import admin, messages
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from datetime import datetime
import pandas as pd
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from .models import Teacher, Position, Specialty
from django.utils.translation import gettext_lazy as trans
from .views import download_teacher_template

# -----------------------
# Shared small textarea
# -----------------------
class SmallTextarea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {}).update({"rows": 2, "style": "width: 90%;"})
        super().__init__(*args, **kwargs)


# -----------------------
# Forms
# -----------------------
class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = "__all__"
        widgets = {
            "place_of_birth": SmallTextarea(),
        }


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = "__all__"


class SpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = "__all__"


# -----------------------
# Inlines & Image Preview
# -----------------------
class TeacherImageWidget(forms.ClearableFileInput):
    template_name = "admin/widgets/teacher_image.html"


# -----------------------
# Specialty Admin
# -----------------------
@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    form = SpecialtyForm
    list_display = ("name",)
    search_fields = ("name",)
    list_per_page = 10
    change_list_template = "admin/teachers/specialties_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-specialties/", self.admin_site.admin_view(self.import_specialties), name="import_specialties")
        ]
        return custom_urls + urls

    def import_specialties(self, request):
        if request.method == "POST" and request.FILES.get("excel_file"):
            df = pd.read_excel(request.FILES["excel_file"])
            for _, row in df.iterrows():
                name = str(row.get("Name")).strip()
                if name:
                    self.model.objects.get_or_create(name=name)

            # ✅ Now works fine
            self.message_user(request, trans("Specialties imported successfully"), level=messages.SUCCESS)
            return redirect("..")

        return render(request, "admin/teachers/import_specialties.html")



# -----------------------
# Position Admin
# -----------------------
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    form = PositionForm
    list_display = ("name", "order")
    search_fields = ("name",)
    ordering = ("order",)


# -----------------------
# Teacher Admin
# -----------------------
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    form = TeacherForm
    list_display = ("tid", "family_name", "given_name","gender", "phone_number", "position", "status", "user_link")
    list_filter = ("position", "status")
    search_fields = ("tid", "family_name", "given_name", "phone_number", "email")
    readonly_fields = ("user", "image_tag")
    list_per_page = 10
    change_list_template = "admin/teachers/teachers_changelist.html"

     # ---------------------
    # Override queryset for ordering
    # ---------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Join Position to order by Position.order
        qs = qs.select_related("position").order_by("position__order", "family_name")
        return qs


    # Show 3x4 image preview
    def image_tag(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="30" height="40" style="object-fit:cover;"/>',
                obj.profile_image.url
            )
        return "-"
    image_tag.short_description = trans("Profile")


    # Link to related user
    def user_link(self, obj):
        if hasattr(obj, "user") and obj.user:
            return obj.user.username
        return "-"
    user_link.short_description = trans("User Account")

    # -------------------
    # Admin URLs
    # -------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-teachers/", self.admin_site.admin_view(self.import_teachers), name="import_teachers"),
            path("export-teachers/", self.admin_site.admin_view(self.export_teachers), name="export_teachers"),
            path("assign-users/<int:teacher_id>/", self.admin_site.admin_view(self.assign_users), name="assign_users"),
            path("download-template/", self.admin_site.admin_view(download_teacher_template), name="download_template_teachers"),
        ]
        return custom_urls + urls

    # -------------------
    # Import Teachers
    # -------------------
    def import_teachers(self, request):
        if request.method == "POST" and request.FILES.get("excel_file"):
            df = pd.read_excel(request.FILES["excel_file"])

            for _, row in df.iterrows():
                # --- Normalize date_of_birth ---
                dob = row.get("Date of birth")
                if pd.notna(dob):
                    try:
                        if isinstance(dob, (int, float)):
                            dob = pd.to_datetime(dob, origin="1899-12-30", unit="D").date()
                        else:
                            dob = pd.to_datetime(str(dob), dayfirst=True, errors="coerce").date()
                    except Exception:
                        dob = None
                else:
                    dob = None

                # --- Get or create Position by name ---
                position_name = row.get("Position", "").strip()
                if position_name:
                    position, _ = Position.objects.get_or_create(name=position_name)
                else:
                    position = None

                # --- Get or create Teacher ---
                teacher, _ = Teacher.objects.get_or_create(
                    tid=row["TID"],
                    defaults={
                        "family_name": row.get("Family name", ""),
                        "given_name": row.get("Given name", ""),
                        "status": row.get("Status", ""),
                        "id_card_number": row.get("ID card number", ""),
                        "date_of_birth": dob,
                        "email": row.get("Email", ""),
                        "gender": row.get("Gender", ""),
                        "phone_number": row.get("Phone number", ""),
                        "place_of_birth": row.get("Place of birth", ""),
                        "enrolled_date": pd.to_datetime(row.get("Enrolled date"), dayfirst=True, errors="coerce").date()
                        if pd.notna(row.get("Enrolled date")) else None,
                        "position": position,
                    },
                )

                # --- Assign specialties by name ---
                specialties = row.get("Specialized division")
                if pd.notna(specialties):
                    teacher.specialties.clear()  # clear previous if updating
                    for s in str(specialties).split(","):
                        spec, _ = Specialty.objects.get_or_create(name=s.strip())
                        teacher.specialties.add(spec)

            self.message_user(request, "Teachers imported successfully", level=messages.SUCCESS)
            return redirect("..")

        return render(request, "admin/teachers/import_teachers.html")
    

    # -------------------
    # Export Teachers
    # -------------------
    def export_teachers(self, request):
        import io
        from django.http import FileResponse
        qs = Teacher.objects.all()
        data = []
        for t in qs:
            data.append({
                "TID": t.tid,
                "Family name": t.family_name,
                "Given name": t.given_name,
                "Status": t.status,
                "ID card number": t.id_card_number,
                "Date of birth": t.date_of_birth,
                "Email": t.email,
                "Gender": t.gender,
                "Phone number": t.phone_number,
                "Place of birth": t.place_of_birth,
                "Specialized division": ", ".join([s.name for s in t.specialties.all()]),
                "Position": t.position.name,
                "Enrolled date": t.enrolled_date,
            })
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="teachers.xlsx")

    # -------------------
    # Assign User Account
    # -------------------
    # -------------------
# Assign User Account
# -------------------
    actions = ["assign_users"]

    def assign_users(self, request, queryset):
        """Bulk assign teachers to user accounts."""
        created_count = 0
        skipped_count = 0

        group_name = "គ្រូបង្រៀន"
        group, _ = Group.objects.get_or_create(name=group_name)

        default_password = "123@Gov.kh"  # 🔑 default password

        for teacher in queryset:
            # Skip if already has a user
            if teacher.user:
                skipped_count += 1
                continue

            username = teacher.phone_number or f"teacher{teacher.id}"
            email = teacher.email or f"{username}@school.local"

            # Create the user
            user = User.objects.create_user(
                username=username,
                password=default_password,
                email=email,
                is_staff=True,
                first_name=teacher.given_name or "",
                last_name=teacher.family_name or "",
            )

            # Assign to group
            user.groups.add(group)

            # Link to teacher
            teacher.user = user
            teacher.save()

            # Polymorphic link (if using custom User with userable fields)
            if hasattr(user, "user_type"):
                user.user_type = "Teacher"
                user.userable_id = teacher.id
                user.userable_type = "teachers.Teacher"
                user.save()

            created_count += 1

        self.message_user(
            request,
            f"✅ {created_count} users created, ⏭️ {skipped_count} teachers already had users.",
            level=messages.SUCCESS,
        )

    assign_users.short_description = "Assign selected teachers to users"

