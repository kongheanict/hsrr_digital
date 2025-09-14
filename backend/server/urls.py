from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

urlpatterns = [
        path('set-language/', set_language, name='set_language'),
    ] + i18n_patterns(
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="vue/index.html")),
    re_path(r"^(?!admin/|api/).*", TemplateView.as_view(template_name="vue/index.html")),
    )

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns += [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
