from django.contrib import admin
from .models import Course, Lesson, LessonPart, StudentCourseAssignment, StudentProgress
from django.utils.translation import gettext_lazy as _

class LessonPartInline(admin.TabularInline):
    model = LessonPart
    extra = 1
    fields = ['title', 'content', 'order']
    ordering = ['order']
    verbose_name = _("lesson part")
    verbose_name_plural = _("lesson parts")

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'order']
    ordering = ['order']
    inlines = [LessonPartInline]
    verbose_name = _("lesson")
    verbose_name_plural = _("lessons")

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title',)
    filter_horizontal = ('classes',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title']
    list_select_related = ['course']
    inlines = [LessonPartInline]

@admin.register(LessonPart)
class LessonPartAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'order', 'created_at']
    list_filter = ['lesson__course', 'lesson']
    search_fields = ['title', 'content']
    list_select_related = ['lesson', 'lesson__course']



@admin.register(StudentCourseAssignment)
class StudentCourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'assigned_at')
    list_filter = ('course',)
    search_fields = ('user__username', 'course__title')

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completed', 'completed_at')
    list_filter = ('completed',)
    search_fields = ('user__username', 'course__title')