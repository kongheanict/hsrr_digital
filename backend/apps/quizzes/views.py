from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
import difflib
import re

from .models import Quiz, QuizAttempt, StudentResponse, Question, AnswerOption
from .serializers import QuizSerializer, QuizAttemptSerializer, StudentResponseSerializer, QuizReviewSerializer
from apps.students.models import Student
from apps.classes.models import SchoolClass

logger = logging.getLogger(__name__)

class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Quiz.objects.none()
        try:
            student = get_object_or_404(Student, user=user)
            active_classes = SchoolClass.objects.filter(
                enrollment__student=student, enrollment__status='ACTIVE'
            ).distinct()
            quizzes = Quiz.objects.filter(
                classes__in=active_classes, status="PUBLISH"
            ).distinct()
            return quizzes
        except Student.DoesNotExist:
            logger.error("Student not found for user in QuizViewSet")
            return Quiz.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class StartQuizView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, quiz_id):
        try:
            quiz = get_object_or_404(Quiz, id=quiz_id, status="PUBLISH")
            student = get_object_or_404(Student, user=request.user)
            
            # Check for a completed attempt
            completed_attempt = QuizAttempt.objects.filter(
                quiz=quiz, student=student, completed_at__isnull=False
            ).first()
            if completed_attempt:
                serializer = QuizAttemptSerializer(completed_attempt, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Check quiz timing
            now = timezone.now()
            if quiz.start_time and now < quiz.start_time:
                return Response({
                    "error": "This quiz has not yet started.",
                    "status": "not_started"
                }, status=status.HTTP_403_FORBIDDEN)
            
            if quiz.start_time and quiz.time_limit:
                end_time = quiz.start_time + quiz.time_limit
                if now > end_time:
                    return Response({
                        "error": "This quiz has already finished.",
                        "status": "finished"
                    }, status=status.HTTP_403_FORBIDDEN)

            # Get or create an in-progress attempt
            in_progress_attempt, created = QuizAttempt.objects.get_or_create(
                quiz=quiz,
                student=student,
                completed_at__isnull=True,
                defaults={'score': 0, 'start_time': now}
            )

            if created:
                in_progress_attempt.start_time = now
                in_progress_attempt.save()

            # Calculate remaining time
            remaining_time = None
            if quiz.start_time and quiz.time_limit:
                time_elapsed = now - quiz.start_time
                remaining_time = quiz.time_limit.total_seconds() - time_elapsed.total_seconds()
                if remaining_time <= 0:
                    in_progress_attempt.completed_at = now
                    in_progress_attempt.score = 0
                    in_progress_attempt.save()
                    serializer = QuizAttemptSerializer(in_progress_attempt, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
            
            # Fetch saved responses
            responses = StudentResponse.objects.filter(quiz=quiz, student=student)
            answers = {}
            for response in responses:
                if response.question.question_type == 'MCQ_MULTI':
                    answers[str(response.question_id)] = [opt.id for opt in response.selected_options.all()]
                else:
                    answers[str(response.question_id)] = (
                        response.selected_options.first().id 
                        if response.selected_options.first() 
                        else response.text_answer
                    )
            
            quiz_data = QuizSerializer(quiz, context={'request': request}).data
            quiz_data['attempt_id'] = in_progress_attempt.id
            quiz_data['answers'] = answers
            quiz_data['remaining_time'] = remaining_time
            
            return Response(quiz_data)
        
        except (Quiz.DoesNotExist, Student.DoesNotExist) as e:
            logger.error(f"Error in StartQuizView: {str(e)}")
            return Response({"error": f"Quiz or student not found: {str(e)}"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error in StartQuizView: {str(e)}", exc_info=True)
            return Response({"error": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class SubmitQuizView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        try:
            quiz = get_object_or_404(Quiz, id=quiz_id)
            student = get_object_or_404(Student, user=request.user)
            attempt_id = request.data.get('attempt_id')
            answers_data = request.data.get('answers', {})

            if not attempt_id:
                return Response({"error": "Attempt ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            attempt = get_object_or_404(
                QuizAttempt, id=attempt_id, student=student, quiz=quiz, completed_at__isnull=True
            )

            total_score = 0
            questions = Question.objects.filter(quiz=quiz)

            for question in questions:
                user_answer = answers_data.get(str(question.id))
                if user_answer is None:
                    continue  # skip unanswered questions

                # Create or update student response
                response, _ = StudentResponse.objects.get_or_create(
                    quiz=quiz,
                    question=question,
                    student=student,
                    defaults={'text_answer': '' if question.question_type == 'SHORT' else None}
                )

                # Clear previous selections for MCQ
                if question.question_type in ['MCQ_SINGLE', 'MCQ_MULTI']:
                    response.selected_options.clear()

                # Save submitted answers
                if question.question_type in ['MCQ_SINGLE', 'MCQ_MULTI']:
                    try:
                        if isinstance(user_answer, list):
                            for answer_id in user_answer:
                                option = AnswerOption.objects.get(id=answer_id)
                                response.selected_options.add(option)
                        elif user_answer:
                            option = AnswerOption.objects.get(id=user_answer)
                            response.selected_options.add(option)
                        response.save()
                    except AnswerOption.DoesNotExist:
                        logger.error(f"Invalid AnswerOption ID: {user_answer}")
                        continue
                elif question.question_type == 'SHORT':
                    response.text_answer = user_answer if user_answer else ''
                    response.save()

                # ----------------- SCORING -----------------
                points_earned = 0

                # MCQ_SINGLE
                if question.question_type == 'MCQ_SINGLE':
                    correct_option = question.options.filter(is_correct=True).first()
                    if correct_option and response.selected_options.filter(id=correct_option.id).exists():
                        points_earned = question.points

                # MCQ_MULTI (strict partial credit with penalty)
                elif question.question_type == 'MCQ_MULTI':
                    all_options = set(question.options.values_list('id', flat=True))
                    correct_options = set(question.options.filter(is_correct=True).values_list('id', flat=True))
                    wrong_options = all_options - correct_options
                    user_answers = set(response.selected_options.values_list('id', flat=True))

                    num_correct = len(correct_options)
                    num_wrong = len(wrong_options)

                    num_correct_selected = len(user_answers & correct_options)
                    num_wrong_selected = len(user_answers & wrong_options)

                    score_from_correct = (question.points * num_correct_selected / num_correct) if num_correct else 0
                    penalty_from_wrong = (question.points * num_wrong_selected / num_wrong) if num_wrong else 0

                    points_earned = score_from_correct - penalty_from_wrong
                    points_earned = max(0, min(points_earned, question.points))

                # SHORT answer
                elif question.question_type == 'SHORT' and response.text_answer:
                    correct_options = question.options.filter(is_correct=True)
                    student_text = response.text_answer.strip().lower()

                    numeric_match = False
                    for opt in correct_options:
                        numbers = re.findall(r'\d+', student_text)
                        if str(opt.text.strip()) in numbers:
                            numeric_match = True
                            break

                    if numeric_match:
                        points_earned = question.points
                    else:
                        keywords = []
                        for opt in correct_options:
                            keywords.extend(re.findall(r'\w+', opt.text.strip().lower()))
                        if keywords:
                            points_per_keyword = question.points / len(keywords)
                            match_count = sum(1 for kw in keywords if kw in student_text)
                            points_earned = round(points_per_keyword * match_count, 2)
                        else:
                            if correct_options.exists():
                                similarity_scores = [
                                    difflib.SequenceMatcher(None, student_text, opt.text.strip().lower()).ratio()
                                    for opt in correct_options
                                ]
                                points_earned = round(question.points * max(similarity_scores), 2)

                # Save points earned per question
                response.points_earned = points_earned
                response.save(update_fields=['points_earned'])
                total_score += points_earned

            # Save attempt score
            attempt.score = round(total_score, 2)
            attempt.completed_at = timezone.now()
            attempt.save(update_fields=['score', 'completed_at'])

            serializer = QuizAttemptSerializer(attempt, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (Quiz.DoesNotExist, Student.DoesNotExist, QuizAttempt.DoesNotExist) as e:
            # logger.error(f"Invalid data: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class QuizReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, quiz_id):
        try:
            quiz = get_object_or_404(Quiz, id=quiz_id)
            student = get_object_or_404(Student, user=request.user)
            attempt = get_object_or_404(
                QuizAttempt, quiz=quiz, student=student, completed_at__isnull=False
            )
            serializer = QuizReviewSerializer(attempt, context={'request': request})
            # logger.info(f"Quiz review data for quiz_id {quiz_id}: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (Quiz.DoesNotExist, Student.DoesNotExist, QuizAttempt.DoesNotExist) as e:
            # logger.error(f"Not found error in QuizReviewView: {str(e)}")
            return Response(
                {"error": f"Quiz, student, or completed attempt not found: {str(e)}"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # logger.error(f"Unexpected error in QuizReviewView: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StudentResponseViewSet(viewsets.ModelViewSet):
    queryset = StudentResponse.objects.all()
    serializer_class = StudentResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            student = Student.objects.get(user=self.request.user)
            return StudentResponse.objects.filter(student=student)
        except Student.DoesNotExist:
            # logger.error("Student not found in StudentResponseViewSet")
            return StudentResponse.objects.none()

    def perform_create(self, serializer):
        try:
            student = Student.objects.get(user=self.request.user)
            serializer.save(student=student)
        except Student.DoesNotExist:
            # logger.error("Student not found in perform_create")
            raise serializers.ValidationError("Student not found.")

class QuizAttemptViewSet(viewsets.ModelViewSet):
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            student = Student.objects.get(user=self.request.user)
            return QuizAttempt.objects.filter(student=student)
        except Student.DoesNotExist:
            # logger.error("Student not found in QuizAttemptViewSet")
            return QuizAttempt.objects.none()