from django.urls import path

from . import views
from .views import *

urlpatterns = [          
    path('', TopicView.as_view()),
    path('/daily', SelectOrCreateTopicView.as_view()),
]
