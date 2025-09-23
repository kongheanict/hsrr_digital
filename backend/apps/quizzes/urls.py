# quizzes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, StudentResponseViewSet, QuizAttemptViewSet, StartQuizView, SubmitQuizView, QuizReviewView

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'student-responses', StudentResponseViewSet, basename='response')
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')

urlpatterns = [
    path('', include(router.urls)),
    path('quizzes/<int:quiz_id>/start/', StartQuizView.as_view(), name='start-quiz'),
    path('quizzes/<int:quiz_id>/submit/', SubmitQuizView.as_view(), name='submit-quiz'),
    path('quizzes/<int:quiz_id>/review/', QuizReviewView.as_view(), name='quiz-review'),

]
