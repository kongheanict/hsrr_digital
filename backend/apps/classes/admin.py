
from django import forms
from django.db.models import CharField
from django.db.models.functions import Cast
from django.contrib import admin
from .models import ClassLevel, SchoolClass, HomeroomTeacher
from django.utils.translation import gettext_lazy as _
from apps.core.models import AcademicYear
from django import forms
from django.db.models import Q
from apps.teachers.models import Teacher
try:
    from django_select2.forms import Select2Widget
except ImportError:
    Select2Widget = forms.Select  # Fallback to default Select widget

class YearFilter(admin.SimpleListFilter):
    title = _("ឆ្នាំសិក្សា")
    parameter_name = 'academic_year'

    def lookups(self, request, model_admin):
        return [(year.id, year.name) for year in AcademicYear.objects.filter(status=True)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(academic_year__id=self.value())
        return queryset

# -----------------------
# ClassLevel Admin
# -----------------------
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_per_page = 20
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(name_int=Cast('name', CharField())).order_by('name_int')


# -----------------------
# SchoolClass Admin
# -----------------------

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only for new objects
        if not self.instance.pk:
            # Pre-fill order: next number for all classes
            last_class = SchoolClass.objects.all().order_by("-order").first()
            self.fields["order"].initial = (last_class.order + 1) if last_class and last_class.order else 1

class SchoolClassAdmin(admin.ModelAdmin):
    form = SchoolClassForm
    list_display = ("name", "level", "major", "order")
    list_filter = ("level", "major")
    search_fields = ("name",)
    ordering = ['order']
    autocomplete_fields = ("level", "major")
    list_per_page = 20




class YearFilter(admin.SimpleListFilter):
    title = _("ឆ្នាំសិក្សា")
    parameter_name = 'academic_year'

    def lookups(self, request, model_admin):
        return [(year.id, year.name) for year in AcademicYear.objects.filter(status=True)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(academic_year__id=self.value())
        return queryset

class HomeroomTeacherForm(forms.ModelForm):
    class Meta:
        model = HomeroomTeacher
        fields = '__all__'
        widgets = {
            'teacher': Select2Widget,
            'school_class': Select2Widget,
            'academic_year': Select2Widget,
        }

@admin.register(HomeroomTeacher)
class HomeroomTeacherAdmin(admin.ModelAdmin):
    form = HomeroomTeacherForm
    list_display = ('school_class', 'teacher', 'academic_year')
    list_filter = (YearFilter, 'school_class')
    search_fields = ('teacher__full_name', 'school_class__name', 'academic_year__name')
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('teacher', 'school_class', 'academic_year')

@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'major', 'order')
    list_filter = ('level', 'major')
    search_fields = ('name',)
