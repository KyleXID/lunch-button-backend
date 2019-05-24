from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path('', UserView.as_view()),
    path('/auth', AuthView.as_view()),
    path('/update', UserUpdatelView.as_view()),
    path('/kakaoauth', KakaoAuthView.as_view()),
    path('/kakaouser', KakaoUserView.as_view()),
    path('/googleauth', GoogleAuthView.as_view()),
    path('/googleuser', GoogleUserView.as_view()),
    path('/block', BlockUserView.as_view()),
    path('/summary', SummaryView.as_view()),
]
