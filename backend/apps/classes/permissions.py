from django.contrib.auth.models import User
from .models import HomeroomTeacher, SchoolClass
from apps.core.models import AcademicYear
from apps.teachers.models import Teacher

def is_homeroom_teacher(user: User, school_class: SchoolClass, academic_year: AcademicYear) -> bool:
    """
    Check if the user is a homeroom teacher for the given class and academic year.
    """
    return HomeroomTeacher.objects.filter(
        teacher__user=user,
        school_class=school_class,
        academic_year=academic_year
    ).exists()