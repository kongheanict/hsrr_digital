# backend/admin.py
# -----------------------
# Imports
# -----------------------
# Django admin and auth
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

# Core app
from apps.core.models import AcademicYear, Semester, Major
from apps.core.admin import AcademicYearAdmin, SemesterAdmin, MajorAdmin

# Classes app
from apps.classes.models import ClassLevel, SchoolClass, HomeroomTeacher
from apps.classes.admin import ClassLevelAdmin, SchoolClassAdmin, HomeroomTeacherAdmin

# Students app
from apps.students.models import Student, Enrollment, Parent
from apps.students.admin import StudentAdmin

# Teachers app
from apps.teachers.admin import Specialty, SpecialtyAdmin, Teacher, TeacherAdmin, Position, PositionAdmin

# Courses app
from apps.courses.admin import Course, CourseAdmin, Lesson, LessonAdmin, LessonPart, LessonPartAdmin

# Quizzes app
from apps.quizzes.admin import QuizCategory, QuizCategoryAdmin, Quiz, QuizAdmin, StudentResponse, StudentResponseAdmin


# -----------------------
# Custom Admin Site
# -----------------------
class MyAdminSite(AdminSite):
    site_header = "ប្រព័ន្ធគ្រប់គ្រងទិន្នន័យ"
    site_title = "គ្រប់គ្រងទិន្នន័យ HSRR Digital"
    index_title = "សូមស្វាគមន៍មកកាន់ប្រព័ន្ធគ្រប់គ្រងទិន្នន័យ"

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
        courses_app = None
        auth_app = None
        others = []

        for app in app_list:
            if app["app_label"] == "classes":
                app["name"] = "ព័ត៌មានថ្នាក់"
                order = ["ClassLevel", "SchoolClass"]
                app["models"].sort(key=lambda m: order.index(m["object_name"]) if m["object_name"] in order else 999)
                classes_app = app
            elif app["app_label"] == "teachers":
                app["name"] = "គ្រប់គ្រងគ្រូបង្រៀន"
                order = ["Teacher", "Specialty", "Position"]
                app["models"].sort(key=lambda m: order.index(m["object_name"]) if m["object_name"] in order else 999)
                teachers_app = app
            elif app["app_label"] == "students":
                app["name"] = "គ្រប់គ្រងសិស្ស"
                order = ["Student", "Enrollment", "Parent"]
                app["models"].sort(key=lambda m: order.index(m["object_name"]) if m["object_name"] in order else 999)
                students_app = app
            elif app["app_label"] == "quizzes":
                app["name"] = "កម្រងតេស្ត"
                order = ["QuizCategory", "Quiz","StudentResponse"]
                app["models"].sort(key=lambda m: order.index(m["object_name"]) if m["object_name"] in order else 999)
                quizzes_app = app
            elif app["app_label"] == "courses":
                app["name"] = "វគ្គសិក្សា"
                order = ["LessonPart", "Courses", "Lesson"]
                app["models"].sort(key=lambda m: order.index(m["object_name"]) if m["object_name"] in order else 999)
                courses_app = app
            elif app["app_label"] == "auth":
                app["name"] = "គណនីអ្នកប្រើ"
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
        if courses_app:
            result.append(courses_app)
        if auth_app:
            result.append(auth_app)
        result.extend(others)

        return result


# -----------------------
# Instantiate Custom Admin Site
# -----------------------
custom_admin_site = MyAdminSite(name="custom_admin")


# -----------------------
# Model Registrations
# -----------------------
# Core
custom_admin_site.register(AcademicYear, AcademicYearAdmin)
custom_admin_site.register(Semester, SemesterAdmin)
custom_admin_site.register(Major, MajorAdmin)

# Classes
custom_admin_site.register(ClassLevel, ClassLevelAdmin)
custom_admin_site.register(SchoolClass, SchoolClassAdmin)
custom_admin_site.register(HomeroomTeacher, HomeroomTeacherAdmin)

# Students
custom_admin_site.register(Student, StudentAdmin)
custom_admin_site.register(Enrollment)
custom_admin_site.register(Parent)

# Teachers
custom_admin_site.register(Teacher, TeacherAdmin)
custom_admin_site.register(Specialty, SpecialtyAdmin)
custom_admin_site.register(Position, PositionAdmin)

# Courses
custom_admin_site.register(Course, CourseAdmin)
custom_admin_site.register(Lesson, LessonAdmin)
custom_admin_site.register(LessonPart, LessonPartAdmin)

# Quizzes
custom_admin_site.register(QuizCategory, QuizCategoryAdmin)
custom_admin_site.register(Quiz, QuizAdmin)
custom_admin_site.register(StudentResponse, StudentResponseAdmin)

# Accounts
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)