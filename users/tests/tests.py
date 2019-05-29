import json
import boto3

from PIL import Image
from django.test import Client
from django.test import TestCase
from django.utils.six import BytesIO
from unittest.mock import patch, MagicMock
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import *
from community.models import *


def create_image(storage, filename, size=(100, 100), image_mode='RGB', image_format='PNG'):
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    
    if not storage:
        return data
        
    image_file = ContentFile(data.read())
        
    return storage.save(filename, image_file)


class UserTest(TestCase):

    def setUp(self):
        c = Client()
        
        Community.objects.create(
            zip_code = "06168",
            commu_name = "위워크 삼성역점"
        )
        
        test = {
            "user_email":"test1",
            "user_nickname":"testnick1",
            "user_password":"1234",
            "community_id":Community.objects.get(zip_code="06168").id
        }
        c.post("/user", json.dumps(test), content_type="application/json")

        test = {
            "user_email":"test12",
            "user_nickname":"testnick12",
            "user_password":"1234",
            "community_id":Community.objects.get(zip_code="06168").id
        }
        c.post("/user", json.dumps(test), content_type="application/json")
    
    def test_user_signup_check(self):
        c = Client()
        
        test = {
            "user_email":"test2",
            "user_nickname":"testnick2",
            "user_password":"1234",
            "community_id":Community.objects.get(zip_code="06168").id
        }
        response = c.post("/user", json.dumps(test), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message" : "회원가입을 축하드립니다."})

    def test_user_signup_id_check(self):
        c = Client()

        test     = {"user_email":"test1", "user_nickname":"testnick2", "user_password":"1234"}
        response = c.post("/user", json.dumps(test), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message" : "이미 존재하는 이메일입니다."})

    def test_user_signup_nickname_check(self):
        c = Client()

        test     = {"user_email":"test2", "user_nickname":"testnick1", "user_password":"1234"}
        response = c.post("/user", json.dumps(test), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message" : "이미 존재하는 닉네임입니다."})
    
    @patch("users.views.requests")
    def test_kakao_user_sign_up(self, mocked_requests):
        c = Client()

        class MockedResponse:
            def json(self):
                return {
                    'id' : '135135'
                }

        mocked_requests.get = MagicMock(
            return_value = MockedResponse()         
        )
        
        test = {
            "user_email"    : "test2",
            "user_nickname" : "kakaonick1",
            "community_id"  : Community.objects.get(zip_code="06168").id
        }
        response = c.post("/user/kakaouser", json.dumps(test), **{"HTTP_AUTHORIZATION":"1234", "content_type":"application/json"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message" : "회원가입을 축하드립니다."})

    def test_google_user_login_error(self):
        c = Client()

        test = {"social_id":123123}
        response = c.get("/user/googleauth", test, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message" : "회원 정보가 존재하지 않습니다."})

    def test_google_user_login(self):
        c = Client()

        test = {"user_email":"test2", "user_nickname":"testnick2", "social_id":"123123", "community_id":Community.objects.get(zip_code="06168").id}
        response = c.post("/user/googleuser", json.dumps(test), content_type="application/json")
  
        test = {"social_id":123123}
        response = c.get("/user/googleauth", test, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), 
                {
                    "access_token"  : response.json()["access_token"],
                    "user_nickname" : response.json()["user_nickname"]
                }
        )

    def test_google_user_signup(self):
        c = Client()

        test = {
            "user_email":"test2",
            "user_nickname":"testnick2", 
            "social_id":"123123",
            "community_id":Community.objects.get(zip_code="06168").id
        }
        response = c.post("/user/googleuser", json.dumps(test), content_type="application/json")
        self.assertEqual(response.json(), {"message" : "회원가입을 축하드립니다."})        

    def test_user_get(self):
        c = Client()

        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")
        access_token = response.json()["access_token"]
        
        user         = User.objects.get(user_email=test["user_email"])
        response     = c.get('/user', **{'HTTP_AUTHORIZATION':access_token, 'content_type':"application/json"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
                {
                    "user_email"     : user.user_email,
                    "user_nickname"  : user.user_nickname,
                    "user_summary"   : None,
                    "thumbnail"      : None,
                    "community"      : "위워크 삼성역점",
                    "favorite_topic" : None
                }
        )

    def test_user_login(self):
        c = Client()

        test         = {"user_email":"test1", "user_password":"1234"}
        user         = User.objects.get(user_email=test["user_email"])
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")
        access_token = response.json()["access_token"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), 
                {
                    "access_token"  : access_token,
                    "user_nickname" : user.user_nickname
                }
        )

    def test_user_nickname_update(self):
        c = Client()

        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")
        access_token = response.json()["access_token"]

        test     = {"user_nickname":"testnick2"}
        response = c.post(
            "/user/update",
            json.dumps(test),
            **{"HTTP_AUTHORIZATION":access_token,"content_type":"application/json"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message" : "닉네임을 성공적으로 변경하였습니다."})

    def test_user_password_update(self):
        c = Client()

        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")
        access_token = response.json()["access_token"]

        test     = {"user_password":"12345"}
        response = c.post(
            "/user/update",
            json.dumps(test),
            **{"HTTP_AUTHORIZATION":access_token, "content_type":"application/json"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message" : "비밀번호를 성공적으로 변경하였습니다."})

    def test_user_all_update(self):
        c = Client()

        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")
        access_token = response.json()["access_token"]

        test     = {"user_nickname":"testnick2", "user_password":"12345"}
        response = c.post(
            "/user/update",
            json.dumps(test),
            **{'HTTP_AUTHORIZATION':access_token, 'content_type':"application/json"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message" : "회원정보를 성공적으로 변경하였습니다."})

    def test_user_blocked_check(self):
        c = Client()
        
        user         = User.objects.get(user_email ="test1")
        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")
        access_token = response.json()["access_token"]
        
        test         = {"user_id":User.objects.get(user_email="test12").id}
        response     = c.post(
            "/user/block",
            json.dumps(test),
            **{"HTTP_AUTHORIZATION":access_token,
                "content_type":"application/json"}
        )
        blocked_list = list(BlockedUser.objects.filter(user_id = user.id).values("blocked__user_nickname","blocked__id"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"block_user_check" : True, "blocked_list" : blocked_list})
    
    def test_user_blocked_list(self):
        c = Client()
        
        user         = User.objects.get(user_email ="test1")
        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")
        access_token = response.json()["access_token"]

        response     = c.get("/user/block", **{"HTTP_AUTHORIZATION":access_token, "content_type":"application/json"})
        blocked_list = list(BlockedUser.objects.filter(user_id = user.id).values("blocked__user_nickname", "blocked__id"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"blocked_list" : blocked_list})

    def test_summary_insert(self):
        c = Client()

        user         = User.objects.get(user_email ="test1")
        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")

        access_token = response.json()["access_token"]

        test         = {"summary":"안녕하세요. 테스트유저입니다."}
        response     = c.post(
            "/user/summary",
            json.dumps(test),
            **{"HTTP_AUTHORIZATION":access_token, "content_type":"application/json"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message" : "소개문을 성공적으로 변경하였습니다."})
    
    @patch("users.views.UserThumbnailView.s3_client")
    def test_thumbnail_upload(self, mocked_boto3):
        c = Client()
                
        user         = User.objects.get(user_email ="test1")
        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")

        access_token = response.json()["access_token"]
        
        thumbnail = create_image(None, 'thumbnail.png')
        thumbnail_file = SimpleUploadedFile('front.png', thumbnail.getvalue())
        form_data = {"thumbnail" : thumbnail_file}
        
        response       = c.post(
            "/user/thumbnail",
            form_data,
            **{"HTTP_AUTHORIZATION":access_token}
        )
        
         
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "https://s3.ap-northeast-2.amazonaws.com/lunchbutton/",
            response.json()["img_url"] 
        )

    def tearDown(self):
        User.objects.filter(user_email="test1").delete()
        User.objects.filter(user_email="test12").delete()
