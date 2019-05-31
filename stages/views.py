import json
import datetime

from django.views import View
from django.http import JsonResponse, HttpResponse

from .models import *
from users.models import *
from topics.models import *
from users.utils import login_check

class StageGroupView(View):

    @login_check
    def post(self, request):
        stage_input_dic = json.loads(request.body)
        
        user  = request.user
        
        topic_id = stage_input_dic["topic"]
        time     = stage_input_dic["time"]
        
        topic = Topic.objects.get(id=topic_id)
        rooms = self.check_if_room_exists(topic, time)

        if len(rooms) > 0:
            for room in rooms:
                print(room.join(user))
                if room.join(user)==False:
                    participants = json.loads(room.participants)
                    if len(participants) <= 3:       
                        return self.enter_room(user, room)
            else:
                return self.create_room(user, topic, time)
        else:
            return self.create_room(user, topic, time)

    def check_if_room_exists(self, topic, time):
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

        return Stage.objects.filter(select_topic = topic, create_time__range = (today_min, today_max), stage_time = time)

    def create_room(self, user, topic, time):
        user = [user.id]
        user = json.dumps(user)

        create_room = Stage(
            stage_time   = time,
            select_topic = topic,
            participants = user
        )
        create_room.save()
        return JsonResponse({"messgae" : "매칭중입니다....."})

    def enter_room(self, user, room):
        participants = json.loads(room.participants)
        
        participants.append(user.id)
        participants = json.dumps(participants)
        
        room.participants = participants
        room.save()

        if len(json.loads(room.participants)) >=3:
            return JsonResponse({"message" : "매칭이 완료되었습니다", "user_list" : json.loads(room.participants)})
        else:
            return JsonResponse({"message" : "매칭중입니다....."})
