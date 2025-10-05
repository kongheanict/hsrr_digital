import logging
from rest_framework import serializers
from .models import Quiz, Question, AnswerOption, StudentResponse, QuizAttempt
from apps.classes.models import SchoolClass
from apps.students.models import Student
from django.utils import timezone
import difflib

logger = logging.getLogger(__name__)

# Serializer for SchoolClass
class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = ['id', 'name']

# Serializer for AnswerOption
class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ['id', 'text', 'is_correct']

# Serializer for Question (light version for list, full for detail)
class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'difficulty', 'order', 'points', 'options']

# Light Question Serializer for quiz list (no options to avoid heavy queries)
class LightQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'difficulty', 'points']  # No options for list

# Serializer for StudentResponse (updated for new model structure)
class StudentResponseSerializer(serializers.ModelSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=AnswerOption.objects.all(),
        required=False
    )
    points_earned = serializers.FloatField(read_only=True)
    question = QuestionSerializer(read_only=True)  # Include question details

    class Meta:
        model = StudentResponse
        fields = ['id', 'question', 'selected_options', 'text_answer', 'submitted_at', 'points_earned']
        read_only_fields = ['submitted_at', 'points_earned']

# Serializer for QuizAttempt (updated for new structure)
class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz = serializers.SerializerMethodField()
    student = serializers.StringRelatedField()  # For display
    selected_questions = QuestionSerializer(many=True, read_only=True)  # Fixed: Removed redundant source

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'student', 'score', 'start_time', 'completed_at', 'selected_questions']
    
    def get_quiz(self, obj):
        return QuizSerializer(obj.quiz, context=self.context).data

# Serializer for Quiz (optimized: light questions for list, full for detail)
class QuizSerializer(serializers.ModelSerializer):
    has_attempted = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()  # Dynamic based on context
    category = serializers.StringRelatedField()
    teacher = serializers.StringRelatedField()
    classes = SchoolClassSerializer(many=True, read_only=True)
    time_limit = serializers.DurationField(allow_null=True)
    total_questions_per_attempt = serializers.SerializerMethodField()  # New property

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'category', 'teacher', 'classes',
            'created_at', 'time_limit', 'start_time', 'status', 'questions',
            'allow_check_answer', 'allow_see_score', 'has_attempted',
            'num_easy_questions', 'num_medium_questions', 'num_hard_questions',
            'total_questions_per_attempt'
        ]

    def get_questions(self, obj):
        # For list view (QuizViewSet), use light serializer to avoid N+1 queries/heavy load
        if self.context.get('view') and self.context['view'].action == 'list':
            return LightQuestionSerializer(obj.questions.all(), many=True, context=self.context).data
        # For detail/start/review, use full with options
        return QuestionSerializer(obj.questions.all(), many=True, context=self.context).data

    def get_has_attempted(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        try:
            student = Student.objects.get(user=request.user)
            return QuizAttempt.objects.filter(
                student=student, quiz=obj, completed_at__isnull=False
            ).exists()
        except Student.DoesNotExist:
            return False

    def get_total_questions_per_attempt(self, obj):
        return obj.total_questions_per_attempt

# Serializer for QuizReview (updated for new structure: use attempt.responses)
class QuizReviewSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(source='selected_questions.question', many=True, read_only=True)  # Only selected questions
    student_responses = serializers.SerializerMethodField()
    quiz_info = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = ['id', 'score', 'start_time', 'completed_at', 'questions', 'student_responses', 'quiz_info']

    def get_student_responses(self, obj):
        # Updated: Filter by attempt (new structure)
        responses = StudentResponse.objects.filter(
            attempt=obj
        ).select_related('question').prefetch_related('selected_options')
        return StudentResponseSerializer(responses, many=True, context=self.context).data

    def get_quiz_info(self, obj):
        try:
            return {
                'id': obj.quiz.id,
                'title': obj.quiz.title,
                'allow_check_answer': obj.quiz.allow_check_answer,
                'allow_see_score': obj.quiz.allow_see_score,
                'total_questions': obj.quiz.total_questions_per_attempt,
            }
        except AttributeError as e:
            logger.error(f"Error in get_quiz_info: {str(e)}")
            return {}