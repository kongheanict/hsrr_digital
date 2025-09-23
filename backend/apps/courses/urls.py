from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonViewSet, LessonPartViewSet
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet)
router.register(r'lesson-parts', LessonPartViewSet)

urlpatterns = [
    path('', include(router.urls)),
]