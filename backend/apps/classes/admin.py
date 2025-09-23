
from django import forms
from django.db.models import CharField
from django.db.models.functions import Cast
from django.contrib import admin
from .models import ClassLevel, SchoolClass
from django.utils.translation import gettext_lazy as _

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
