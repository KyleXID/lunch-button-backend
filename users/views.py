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

    def post(self, request):
        new_user = json.loads(request.body)

        if User.objects.filter(user_email=new_user["user_email"]).exists():
            return JsonResponse({"message" : "이미 존재하는 이메일입니다."}, status=400)
        elif User.objects.filter(user_nickname=new_user["user_nickname"]).exists():
            return JsonResponse({"message" : "이미 존재하는 닉네임입니다."}, status=400)
        else:
            password = bytes(new_user["user_password"], "utf-8")
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

            new_user = User(
                    user_email     = new_user["user_email"],
                    user_nickname  = new_user["user_nickname"],
                    user_password  = hashed_password.decode("utf-8"),
            )
            new_user.save()

            return JsonResponse({"message" : "회원가입을 축하드립니다."}, status=200)

    @login_check
    def get(self, request):
        return JsonResponse({
            "user_email"    : request.user.user_email,
            "user_nickname" : request.user.user_nickname,
            "user_summary"  : request.user.summary,
            "thumbnail"     : request.user.thumbnail
        })

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
                            "access_token"  : encoded_jwt_id.decode("utf-8"),
                            "user_nickname" : user.user_nickname
                        }
                    )

        else:
            return JsonResponse({"message" : "회원 정보가 존재하지 않습니다."}, status=400)

class KakaoUserView(View):

    def post(self, request):
        url         = "https://kapi.kakao.com/v2/user/me"
        kakao_token = {
            "Authorization" : "Bearer "+request.headers.get("Authorization", None)
        }
        response    = requests.get(url, headers=kakao_token).json()
        
        new_kakao_user = json.loads(request.body)

        if User.objects.filter(social_id = response["id"]).exists():
            return JsonResponse({"message" : "이미 가입한 계정입니다."}, status=400)
        elif User.objects.filter(user_email = new_kakao_user["user_email"]).exists():
            return JsonResponse({"message" : "이미 존재하는 이메일입니다."}, status=400)
        elif User.objects.filter(user_nickname = new_kakao_user["user_nickname"]).exists():
            return JsonResponse({"message" : "이미 존재하는 닉네임입니다."}, status=400)
        else:
            new_user = User(
                    user_email     = new_kakao_user["user_email"],
                    user_nickname  = new_kakao_user["user_nickname"],
                    social_id      = response["id"]
            )
            new_user.save()

            return JsonResponse({"message" : "회원가입을 축하드립니다."}, status=200)

class GoogleAuthView(View):

    def get(self, request):
        google_social_id = request.GET.get("social_id")

        if User.objects.filter(social_id = google_social_id).exists():
            user           = User.objects.get(social_id = google_social_id)
            encoded_jwt_id = jwt.encode({"user_id" : user.id}, lunch_secret, algorithm="HS256")
            
            return JsonResponse(            
                        {
                            "access_token"  : encoded_jwt_id.decode("utf-8"),
                            "user_nickname" : user.user_nickname
                        }
                    )

        else:
            return JsonResponse({"message" : "회원 정보가 존재하지 않습니다."}, status=400)

class GoogleUserView(View):

    def post(self, request):
        google_user = json.loads(request.body)

        if User.objects.filter(social_id = google_user["social_id"]).exists():
            return JsonResponse({"message" : "이미 가입한 계정입니다."}, status=400)
        elif User.objects.filter(user_email = google_user["user_email"]).exists():
            return JsonResponse({"message" : "이미 존재하는 이메일입니다."}, status=400)
        elif User.objects.filter(user_nickname = google_user["user_nickname"]).exists():
            return JsonResponse({"message" : "이미 존재하는 닉네임입니다."}, status=400)
        else:
            new_user = User(
                    user_email     = google_user["user_email"], 
                    user_nickname  = google_user["user_nickname"],
                    social_id      = google_user["social_id"]
            )
            new_user.save()

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

        blocked_list = list(BlockedUser.objects.filter(user_id = user.id).values("blocked__user_nickname"))

        return JsonResponse({"block_user_check" : check, "blocked_list" : blocked_list})
    
    @login_check
    def get(self, request):
        user = request.user
        
        blocked_list = list(BlockedUser.objects.filter(user_id = user.id).values("blocked__user_nickname"))

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
