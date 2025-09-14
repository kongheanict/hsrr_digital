# backend/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

# Import app-specific admin classes
from apps.quizzes.admin import (
    QuizCategory, QuizCategoryAdmin,
    Quiz, QuizAdmin,
    Question,
    AnswerOption,
)

from apps.teachers.admin import (
    Specialty, SpecialtyAdmin,
    Teacher, TeacherAdmin,
    Position, PositionAdmin,
)

from apps.students.models import Student, Enrollment, Parent
from apps.students.admin import StudentAdmin
from apps.classes.models import ClassLevel, SchoolClass
from apps.classes.admin import ClassLevelAdmin, SchoolClassAdmin
from apps.core.models import AcademicYear, Semester, Major
from apps.core.admin import AcademicYearAdmin, SemesterAdmin, MajorAdmin


# -----------------------
# Custom Admin Site
# -----------------------
class MyAdminSite(AdminSite):
    site_header = "School Quiz Admin"
    site_title = "School Quiz Portal"
    index_title = "Welcome to Quiz Management"

    class Media:
        css = {
            'all': ('admin_custom.css',)
        }

    def get_app_list(self, request):
        """Customize sidebar order and app labels."""
        app_list = super().get_app_list(request)

        classes_app = None
        teachers_app = None
        students_app = None
        quizzes_app = None
        auth_app = None
        others = []

        for app in app_list:
            if app["app_label"] == "classes":
                app["name"] = "Classes"
                order = ["ClassLevel", "SchoolClass"]
                app["models"].sort(key=lambda m: order.index(m["object_name"]) if m["object_name"] in order else 999)
                classes_app = app

            elif app["app_label"] == "teachers":
                app["name"] = "Teachers"
                order = ["Teacher", "Specialty", "Position"]
                app["models"].sort(key=lambda m: order.index(m["object_name"]) if m["object_name"] in order else 999)
                teachers_app = app

            elif app["app_label"] == "students":
                app["name"] = "Students"
                order = ["Student", "Enrollment", "Parent"]
                app["models"].sort(key=lambda m: order.index(m["object_name"]) if m["object_name"] in order else 999)
                students_app = app

            elif app["app_label"] == "quizzes":
                app["name"] = "Quizzes"
                order = ["QuizCategory", "Quiz", "Question", "AnswerOption"]
                app["models"].sort(key=lambda m: order.index(m["object_name"]) if m["object_name"] in order else 999)
                quizzes_app = app

            elif app["app_label"] == "auth":
                app["name"] = "Accounts"
                auth_app = app

            else:
                others.append(app)

        # Final app order: Classes → Teachers → Students → Quizzes → Accounts → Others
        result = []
        if classes_app:
            result.append(classes_app)
        if teachers_app:
            result.append(teachers_app)
        if students_app:
            result.append(students_app)
        if quizzes_app:
            result.append(quizzes_app)
        if auth_app:
            result.append(auth_app)
        result.extend(others)

        return result


# -----------------------
# Instantiate & Register
# -----------------------
custom_admin_site = MyAdminSite(name="custom_admin")

# Register Quizzes
custom_admin_site.register(QuizCategory, QuizCategoryAdmin)
custom_admin_site.register(Quiz, QuizAdmin)
custom_admin_site.register(Question)
custom_admin_site.register(AnswerOption)

# Register Teachers
custom_admin_site.register(Teacher, TeacherAdmin)
custom_admin_site.register(Specialty, SpecialtyAdmin)
custom_admin_site.register(Position, PositionAdmin)

# Register Students
custom_admin_site.register(Student, StudentAdmin)
custom_admin_site.register(Enrollment)
custom_admin_site.register(Parent)

# Register Classes
custom_admin_site.register(ClassLevel, ClassLevelAdmin)
custom_admin_site.register(SchoolClass, SchoolClassAdmin)

# Register Core
custom_admin_site.register(AcademicYear, AcademicYearAdmin)
custom_admin_site.register(Semester, SemesterAdmin)
custom_admin_site.register(Major, MajorAdmin)

# Register Users and Groups under "Accounts"
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)
