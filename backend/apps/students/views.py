from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.classes.models import HomeroomTeacher, SchoolClass
from apps.core.models import AcademicYear
from apps.teachers.models import Teacher
from apps.students.models import Student, Enrollment

@login_required
def student_list(request):
    # Check if user is staff
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Get the teacher's profile
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return HttpResponseForbidden("No teacher profile associated with this user.")

    # Get the current academic year
    try:
        current_year = AcademicYear.objects.get(status=True)
    except AcademicYear.DoesNotExist:
        return HttpResponseForbidden("No active academic year found.")

    # Get classes where the user is a homeroom teacher
    homeroom_classes = HomeroomTeacher.objects.filter(
        teacher=teacher,
        academic_year=current_year
    ).values_list('school_class__id', flat=True)

    # If no classes assigned, return empty student list
    if not homeroom_classes:
        return render(request, 'admin/students/student_list.html', {
            'students': [],
            'current_year': current_year,
            'title': 'Student List',
        })

    # Get students enrolled in the assigned classes for the current year
    students = Student.objects.filter(
        enrollments__school_class__id__in=homeroom_classes,
        enrollments__academic_year=current_year,
        enrollments__status='ACTIVE'
    ).distinct()

    return render(request, 'admin/students/student_list.html', {
        'students': students,
        'current_year': current_year,
        'title': 'Student List',
    })