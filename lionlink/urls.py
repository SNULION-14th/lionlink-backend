from django.urls import path

from .views import (
    SignupView,
    LoginView,
    MeView,
    PreviewView,
    PreviewDetailView,
)

urlpatterns = [
    path('auth/signup/', SignupView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('users/me/', MeView.as_view()),
    path('previews/', PreviewView.as_view()),
    path('previews/<int:pk>/', PreviewDetailView.as_view()),
]
