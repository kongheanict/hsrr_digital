from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from .admin import custom_admin_site
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from apps.core.views import ValidateTokenView, ServerTimeView

urlpatterns = [
        path('set-language/', set_language, name='set_language'),
    ] + i18n_patterns(
    path('admin/', custom_admin_site.urls),
    path("", TemplateView.as_view(template_name="vue/index.html")),
    
    re_path(r"^(?!admin/|api/).*", TemplateView.as_view(template_name="vue/index.html")),
    )+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns += [
    path('api/', include('apps.courses.urls')),
    path('api/', include('apps.quizzes.urls')),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    path('api/auth/validate/', ValidateTokenView.as_view(), name='validate-token'),
    path('api/time/', ServerTimeView.as_view(), name='server-time'),
]
