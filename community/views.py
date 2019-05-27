import json

from django.views import View
from django.db.models import Q
from django.http import JsonResponse, HttpResponse

from .models import *
from users.utils import login_check

class CommunityView(View):
    
    @login_check
    def get(self, request):
        community = Community.objects.all()

        user   = request.user
        search = request.GET.get("search", "")

        if search:
            result = community.filter(Q(zip_code = search) | Q(commu_name__icontains=search)) \
                    .values('id', 'commu_name', 'zip_code', 'location1', 'location2', 'location3')
            return JsonResponse({"Community_list" : list(result)})
        else:
            return JsonResponse({"message" : "검색어를 입력해주세요."}, status=400)
    
    @login_check
    def post(self, request):
        user      = request.user
        community = json.loads(request.body)
        community = Community.objects.get(id = community['id'])

        user.user_community = community
        user.save()
        
        return JsonResponse({"message" : "커뮤니티가 정상적으로 등록되었습니다."})
