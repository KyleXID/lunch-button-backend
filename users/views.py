import jwt
import json
import uuid
import boto3
import bcrypt
import requests
import my_settings

from django.views import View
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from .models import *
from .utils import login_check
from lunch_button import settings
from lunch_button.settings import lunch_secret

class UserView(View):

    def createUserCommunity(self, user_input_dic):
        user      = User.objects.get(user_email=user_input_dic["user_email"])
        community = user_input_dic["community_id"]
        community = Community.objects.get(id = community)

        user.user_community = community
        user.save()

    def createUserTopic(self, user_input_dic):
        user = User.objects.get(user_email=user_input_dic["user_email"])
        
        if "topic" in user_input_dic:
            
            if len(user_input_dic["topic"]) > 3:
                return JsonResponse({"message" : "관심토픽은 3개까지 선택가능합니다."}, status=400)
            elif len(user_input_dic["topic"]) > 0: 
                
                for topic in user_input_dic["topic"]:
                    user.favorite_topics.add(Topic.objects.get(id = topic).id)
                    user.save()

    @login_check
    def get(self, request):

        if MyFavoriteTopic.objects.filter(topic_user_id=request.user.id).exists():
            favorite_topic = MyFavoriteTopic.objects.filter(topic_user_id=request.user.id)\
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

        return JsonResponse({
            "user_email"     : request.user.user_email,
            "user_nickname"  : request.user.user_nickname,
            "user_summary"   : request.user.summary,
            "thumbnail"      : request.user.thumbnail,
            "community"      : request.user.user_community.commu_name if request.user.user_community is not None else None,
            "favorite_topic" : favorite_topic_list
        })

class EmailUserView(View):

    def post(self, request):
        user_input_dic = json.loads(request.body)

        if User.objects.filter(user_email=user_input_dic["user_email"]).exists():
            return JsonResponse({"message" : "이미 존재하는 이메일입니다."}, status=400)
        elif User.objects.filter(user_nickname=user_input_dic["user_nickname"]).exists():
            return JsonResponse({"message" : "이미 존재하는 닉네임입니다."}, status=400)
        else:
            password = bytes(user_input_dic["user_password"], "utf-8")
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

            user_model = User(
                user_email     = user_input_dic["user_email"],
                user_nickname  = user_input_dic["user_nickname"],
                user_password  = hashed_password.decode("utf-8"),
            )
            user_model.save()
            
            UserView.createUserCommunity(self, user_input_dic)
            UserView.createUserTopic(self, user_input_dic)

            return JsonResponse({"message" : "회원가입을 축하드립니다."}, status=200)


class AuthView(View):

    def post(self, request):
        login_user = json.loads(request.body)
        
        try:
            user = User.objects.get(user_email=login_user["user_email"])

            if bcrypt.checkpw(login_user["user_password"].encode("utf-8"), user.user_password.encode("utf-8")):
                encoded_jwt_id = jwt.encode({"user_id" : user.id}, lunch_secret, algorithm="HS256")
                
                return JsonResponse(
                            {
                                "access_token"  : encoded_jwt_id.decode("utf-8"),
                                "user_nickname" : user.user_nickname
                            }
                        )
            else:
                return JsonResponse({"message" : "비밀번호를 다시 확인해주세요,"}, status=400)
        except ObjectDoesNotExist:
            return JsonResponse({"message" : "등록되지 않은 아이디입니다,"}, status=400)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)

class KakaoAuthView(View):
    
    def get(self, request):
        url         = "https://kapi.kakao.com/v2/user/me"
        kakao_token = {
            "Authorization" : "Bearer "+request.headers.get("Authorization", None)
        }
        response    = requests.get(url, headers=kakao_token).json()
        
        if User.objects.filter(social_id = response["id"]).exists():
            user           = User.objects.get(social_id = response["id"])
            encoded_jwt_id = jwt.encode({"user_id" : user.id}, lunch_secret, algorithm="HS256")
            
            return JsonResponse(
                    {   
                            "USER_EXIST"    : True,
                            "access_token"  : encoded_jwt_id.decode("utf-8"),
                            "user_nickname" : user.user_nickname
                        }
                    )

        else:
            return JsonResponse({"USER_EXIST" : False}, status=200)

class KakaoUserView(View):

    def post(self, request):
        url         = "https://kapi.kakao.com/v2/user/me"
        kakao_token = {
            "Authorization" : "Bearer "+request.headers.get("Authorization", None)
        }
        response    = requests.get(url, headers=kakao_token).json()
        
        user_input_dic = json.loads(request.body)

        if User.objects.filter(social_id = response["id"]).exists():
            return JsonResponse({"message" : "이미 가입한 계정입니다."}, status=400)
        elif User.objects.filter(user_email = user_input_dic["user_email"]).exists():
            return JsonResponse({"message" : "이미 존재하는 이메일입니다."}, status=400)
        elif User.objects.filter(user_nickname = user_input_dic["user_nickname"]).exists():
            return JsonResponse({"message" : "이미 존재하는 닉네임입니다."}, status=400)
        else:
            user_model = User(
                    user_email     = user_input_dic["user_email"],
                    user_nickname  = user_input_dic["user_nickname"],
                    social_id      = response["id"]
            )
            user_model.save()
            
            UserView.createUserCommunity(self, user_input_dic)
            UserView.createUserTopic(self, user_input_dic)

            return JsonResponse({"message" : "회원가입을 축하드립니다."}, status=200)

class GoogleAuthView(View):

    def get(self, request):
        google_social_id = request.GET.get("social_id")

        if User.objects.filter(social_id = google_social_id).exists():
            user           = User.objects.get(social_id = google_social_id)
            encoded_jwt_id = jwt.encode({"user_id" : user.id}, lunch_secret, algorithm="HS256")
            
            return JsonResponse(            
                        {
                            "USER_EXIST"    : True,
                            "access_token"  : encoded_jwt_id.decode("utf-8"),
                            "user_nickname" : user.user_nickname
                        }
                    )

        else:
            return JsonResponse({"USER_EXIST" : False}, status=200)

class GoogleUserView(View):

    def post(self, request):
        user_input_dic = json.loads(request.body)

        if User.objects.filter(social_id = user_input_dic["social_id"]).exists():
            return JsonResponse({"message" : "이미 가입한 계정입니다."}, status=400)
        elif User.objects.filter(user_email = user_input_dic["user_email"]).exists():
            return JsonResponse({"message" : "이미 존재하는 이메일입니다."}, status=400)
        elif User.objects.filter(user_nickname = user_input_dic["user_nickname"]).exists():
            return JsonResponse({"message" : "이미 존재하는 닉네임입니다."}, status=400)
        else:
            user_model = User(
                    user_email     = user_input_dic["user_email"], 
                    user_nickname  = user_input_dic["user_nickname"],
                    social_id      = user_input_dic["social_id"],
                    thumbnail      = user_input_dic["user_thumbnail"] if "user_thumbnail" in user_input_dic else None
            )
            user_model.save()
            
            UserView.createUserCommunity(self, user_input_dic)
            UserView.createUserTopic(self, user_input_dic)

            return JsonResponse({"message" : "회원가입을 축하드립니다."}, status=200)

class UserUpdatelView(View):
    
    @login_check
    def post(self, request):
        user        = User.objects.filter(id = request.user.id)
        update_user = json.loads(request.body)
        message     = ""
        
        if "user_nickname" in update_user:
            if User.objects.filter(user_nickname=update_user["user_nickname"]).exists():
                return JsonResponse({"message" : "이미 존재하는 아이디입니다."}, status=400)
            else:
                if "user_password" in update_user:
                    password        = bytes(update_user["user_password"], "utf-8")
                    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
                    
                    user.update(user_nickname = update_user["user_nickname"])
                    user.update(user_password = hashed_password.decode("utf-8"))
                    message = "회원정보를"
                else:
                    user.update(user_nickname = update_user["user_nickname"])
                    message = "닉네임을"

            return JsonResponse({"message" : message+" 성공적으로 변경하였습니다."}, status=200)
        elif 'user_password' in update_user and "user_nickname" not in update_user:
            password = bytes(update_user['user_password'], "utf-8")
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()) 
            user.update(user_password = hashed_password.decode("UTF-8"))

            return JsonResponse({"message" : "비밀번호를 성공적으로 변경하였습니다."}, status=200)
        else:
            return JsonResponse({"message" : "회원정보를 변경하는데 실패하였습니다."}, status=400)


class BlockUserView(View):

    @login_check
    def post(self, request):
        user       = request.user
        block      = json.loads(request.body)
        block_user = User.objects.get(id = block["user_id"])

        if user.block_users.filter(id = block_user.id).exists():
            user.block_users.remove(block_user)
            check = False
        else:
            user.block_users.add(block_user)
            check = True

        blocked_list = list(BlockedUser.objects.filter(user_id = user.id).values("blocked__user_nickname", "blocked__id"))

        return JsonResponse({"block_user_check" : check, "blocked_list" : blocked_list})
    
    @login_check
    def get(self, request):
        user = request.user
        
        blocked_list = list(BlockedUser.objects.filter(user_id = user.id).values("blocked__user_nickname","blocked__id"))

        return JsonResponse({"blocked_list" : blocked_list})

class SummaryView(View):

    @login_check
    def post(self, request):
        user = request.user
        summary = json.loads(request.body)
        
        if user.summary is None :
            user.summary = summary["summary"]
            user.save()
        else:
            user.summary = summary["summary"]
            user.save(update_fields=["summary"])
        return JsonResponse({"message" : "소개문을 성공적으로 변경하였습니다."})

class UserThumbnailView(View):

    s3_client = boto3.client(
        's3',
        aws_access_key_id     = settings.aws_access_key_id,
        aws_secret_access_key = settings.aws_secret_access_key
    )
    
    @login_check
    def post(self, request):

        user      = request.user
        file      = request.FILES["thumbnail"]
        extension = file.name.split('.')[-1]
        file_name = str(user.id)+uuid.uuid4().hex+"."+extension
        
        self.s3_client.upload_fileobj(
            file, 
            "lunchbutton",
            file_name,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )

        thumbnail_url = "https://s3.ap-northeast-2.amazonaws.com/lunchbutton/"+file_name

        user.thumbnail = thumbnail_url
        user.save()

        return JsonResponse(
                    {
                        "message" : "프로필 이미지 업로드 성공",
                        "img_url" : thumbnail_url
                    }
                )
