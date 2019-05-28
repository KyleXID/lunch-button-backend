import json

from django.views import View
from django.http import JsonResponse, HttpResponse

from .models import *          
from users.models import *
from users.utils import login_check

class TopicView(View):
    
    @login_check
    def get(self, request):
        topics = Topic.objects.all()

        user   = request.user
        search = request.GET.get("search", "")

        if search:
            result = topics.filter(topic_name__icontains=search).values('id', 'topic_name')
            return JsonResponse({"topic_list" : list(result)})
        else:
            return JsonResponse({"message" : "검색어를 입력해주세요."}, status=400)
    
    @login_check
    def post(self, request):
        topic = json.loads(request.body)
        user  = request.user
        
        topic = Topic.objects.get(id=topic["topic"])

        if user.favorite_topics.filter(select_topic__id = topic.id).exists():
            user.favorite_topics.remove(topic)
            check_topic = False
        else:
            if user.favorite_topics.count() > 3:
                return JsonResponse({"message" : "관심토픽은 3개까지 선택가능합니다."}, status=400)
            else:
                user.favorite_topics.add(topic)
                check_topic = True
        
        if MyFavoriteTopic.objects.filter(topic_user_id=user.id).exists():
            favorite_topic = MyFavoriteTopic.objects.filter(topic_user_id=user.id)\
                .values('id', 'topic_id').order_by('id')
            favorite_topic_list = list(favorite_topic)
            favorite_topic_list = [
                {
                    'topic_id' : topic['topic_id'],
                    'topic_name' : Topic.objects.get(id=topic['topic_id']).topic_name
                } for topic in favorite_topic_list
            ]
        else:
            favorite_topic_list = None

        return JsonResponse(
            {
                "favorite_topic"      : check_topic,
                "favorite_topic_list" : favorite_topic_list
            }
        )
