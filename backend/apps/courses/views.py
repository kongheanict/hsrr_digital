from rest_framework import viewsets
from django.db import models
from .models import Course, Lesson, LessonPart,StudentProgress
from .serializers import CourseSerializer, LessonSerializer, LessonPartSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .serializers import CourseSerializer
from apps.students.models import Student
from apps.students.models import Enrollment
from apps.classes.models import SchoolClass

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            print(f"Authenticated user: {user.username}")
            student = Student.objects.filter(user=user).first()
            print(f"Student: {student}")
            if student:
                try:
                    # Get SchoolClass IDs from active enrollments
                    active_classes = SchoolClass.objects.filter(
                        enrollment__student=student,
                        enrollment__status='ACTIVE'
                    ).distinct()
                    print(f"Active classes: {active_classes}")
                    # Filter courses linked to active classes, direct assignments, or completed progress
                    courses = Course.objects.filter(
                        models.Q(classes__in=active_classes) |
                        models.Q(student_assignments__user=user) |
                        models.Q(student_progress__user=user, student_progress__completed=True)
                    ).distinct()
                    print(f"Courses: {courses}")
                    return courses
                except Exception as e:
                    print(f"Error querying courses for student {student}: {e}")
                    return Course.objects.none()
            return Course.objects.filter(
                models.Q(student_assignments__user=user) |
                models.Q(student_progress__user=user, student_progress__completed=True)
            ).distinct()
        return Course.objects.none()

    @action(detail=False, methods=['post'], url_path='complete-course')
    def complete_course(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=401)
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        progress, created = StudentProgress.objects.update_or_create(
            user=user, course=course,
            defaults={'completed': True, 'completed_at': timezone.now()}
        )
        return Response({'completed': progress.completed, 'completed_at': progress.completed_at})

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(course_id=self.request.data.get('course_id'))

class LessonPartViewSet(viewsets.ModelViewSet):
    queryset = LessonPart.objects.all()
    serializer_class = LessonPartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(lesson_id=self.request.data.get('lesson_id'))