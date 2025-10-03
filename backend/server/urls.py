from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from .admin import custom_admin_site
from apps.core.views import ValidateTokenView, ServerTimeView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# -----------------------------
# i18n patterns for admin & language
# -----------------------------
urlpatterns = i18n_patterns(
    path('admin/', custom_admin_site.urls),
    # path('admin/students/student/', include('apps.students.urls')),
    path('set-language/', set_language, name='set_language'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('select2/', include('django_select2.urls')),
)

# -----------------------------
# SPA routes (outside i18n) - Vue app
# -----------------------------
urlpatterns += [
    path("", TemplateView.as_view(template_name="vue/index.html")),
    re_path(r"^(?!admin/|api/).*", TemplateView.as_view(template_name="vue/index.html")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# -----------------------------
# API endpoints (outside i18n)
# -----------------------------
urlpatterns += [
    path('api/teachers/', include('apps.teachers.urls')),
    path('api/', include('apps.courses.urls')),
    path('api/', include('apps.quizzes.urls')),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('api/auth/validate/', ValidateTokenView.as_view(), name='validate-token'),
    path('api/time/', ServerTimeView.as_view(), name='server-time'),
]
