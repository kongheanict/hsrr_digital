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

# Serializer for Question
class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'order', 'points', 'options']

# Serializer for StudentResponse
class StudentResponseSerializer(serializers.ModelSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=AnswerOption.objects.all(),
        required=False
    )
    points_earned = serializers.FloatField(read_only=True)  # <-- new field

    class Meta:
        model = StudentResponse
        fields = ['id', 'question', 'selected_options', 'text_answer', 'submitted_at', 'points_earned']
        read_only_fields = ['submitted_at', 'points_earned']

# Serializer for QuizAttempt
class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'score', 'completed_at', 'answers']
    
    def get_quiz(self, obj):
        return QuizSerializer(obj.quiz, context=self.context).data

    def get_answers(self, obj):
        responses = StudentResponse.objects.filter(student=obj.student, quiz=obj.quiz)
        answers_dict = {}
        for response in responses:
            if response.question.question_type == 'MCQ_MULTI':
                answers_dict[str(response.question_id)] = [opt.id for opt in response.selected_options.all()]
            else:
                answers_dict[str(response.question_id)] = (
                    response.selected_options.first().id 
                    if response.selected_options.first() 
                    else response.text_answer
                )
        return answers_dict

# Serializer for Quiz
class QuizSerializer(serializers.ModelSerializer):
    has_attempted = serializers.SerializerMethodField()
    questions = QuestionSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()
    teacher = serializers.StringRelatedField()
    classes = SchoolClassSerializer(many=True, read_only=True)
    time_limit = serializers.DurationField(allow_null=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'category', 'teacher', 'classes',
            'created_at', 'time_limit', 'start_time', 'status', 'questions',
            'allow_check_answer', 'allow_see_score', 'has_attempted'
        ]

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

# Serializer for QuizReview
class QuizReviewSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(source='quiz.questions', many=True, read_only=True)
    student_responses = serializers.SerializerMethodField()
    quiz_info = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = ['id', 'score', 'completed_at', 'questions', 'student_responses', 'quiz_info']

    def get_student_responses(self, obj):
        responses = StudentResponse.objects.filter(
            quiz=obj.quiz,
            student=obj.student
        ).select_related('question').prefetch_related('selected_options')
        return StudentResponseSerializer(responses, many=True).data

    def get_quiz_info(self, obj):
        try:
            return {
                'id': obj.quiz.id,
                'title': obj.quiz.title,
                'allow_check_answer': getattr(obj.quiz, 'allow_check_answer', False),
                'allow_see_score': getattr(obj.quiz, 'allow_see_score', False),
            }
        except AttributeError as e:
            logger.error(f"Error in get_quiz_info: {str(e)}")
            return {}