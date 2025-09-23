from rest_framework import serializers
from .models import Course, Lesson, LessonPart, StudentProgress

class LessonPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonPart
        fields = ['id', 'title', 'content', 'order']

class LessonSerializer(serializers.ModelSerializer):
    parts = LessonPartSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'order', 'parts']

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'cover_image', 'lessons', 'is_completed']

    def get_is_completed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            progress = StudentProgress.objects.filter(user=user, course=obj).first()
            return progress.completed if progress else False
        return False