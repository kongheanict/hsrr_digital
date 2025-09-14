# core/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import AcademicYear, Semester, Major

# -----------------------
# Academic Year Admin
# -----------------------
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "status","start_date", "end_date")
    search_fields = ("name",)
    list_per_page = 20
    # Khmer labels for filter panel
    list_filter = ("start_date", "end_date")


# -----------------------
# Semester Admin
# -----------------------
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("name", "year", "status","start_date", "end_date")
    search_fields = ("name",)
    autocomplete_fields = ("year",)
    list_per_page = 20
    list_filter = ("year", "start_date", "end_date")


# -----------------------
# Major Admin
# -----------------------
class MajorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_per_page = 20
