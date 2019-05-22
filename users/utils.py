import jwt
import json

from django.http import JsonResponse, HttpResponse
from enum import Enum

from .models import User
from lunch_button.settings import lunch_secret

class Gender(Enum):
    MALE = 'M'
    FEMALE = 'F'

    @classmethod
    def choices(cls):
        return [(tag, tag.value) for tag in Gender]

def login_check(f):
    def wrapper(self, request, *args, **kwargs):
        access_token = request.headers.get('Authorization', None)
        
        if access_token == None:
            return JsonResponse({"message" : "로그인이 필요한 서비스입니다."}, status=401)
        else:
            decode = jwt.decode(access_token, lunch_secret,  algorithms=['HS256'])
            user_id = decode["user_id"]
            user = User.objects.get(id=user_id)
            request.user = user

            return f(self, request, *args, **kwargs)

    return wrapper
