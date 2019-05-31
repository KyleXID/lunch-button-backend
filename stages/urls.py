from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path('', StageGroupView.as_view()),
]

