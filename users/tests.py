import json
import boto3

from django.test import TestCase
from django.test import Client

from users.models import *

class UserTest(TestCase):

    def setUp(self):
        c = Client()

        test = {"user_email":"test1", "user_nickname":"testnick1", "user_password":"1234"}
        c.post("/user", json.dumps(test), content_type="application/json")

        test = {"user_email":"test12", "user_nickname":"testnick12", "user_password":"1234"}
        c.post("/user", json.dumps(test), content_type="application/json")

    def test_user_signup_check(self):
        c = Client()

        test     = {"user_email":"test2", "user_nickname":"testnick2", "user_password":"1234"}
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
    
    def test_google_user_login_error(self):
        c = Client()

        test = {"social_id":123123}
        response = c.get("/user/googleauth", test, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message" : "회원 정보가 존재하지 않습니다."})

    def test_google_user_login(self):
        c = Client()

        test = {"user_email":"test2", "user_nickname":"testnick2", "social_id":"123123"}
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

        test = {"user_email":"test2", "user_nickname":"testnick2", "social_id":"123123"}
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
                    "community"      : None,
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
        blocked_list = list(BlockedUser.objects.filter(user_id = user.id).values("blocked__user_nickname"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"block_user_check" : True, "blocked_list" : blocked_list})
    
    def test_user_blocked_list(self):
        c = Client()
        
        user         = User.objects.get(user_email ="test1")
        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")
        access_token = response.json()["access_token"]

        response     = c.get("/user/block", **{"HTTP_AUTHORIZATION":access_token, "content_type":"application/json"})
        blocked_list = list(BlockedUser.objects.filter(user_id = user.id).values("blocked__user_nickname"))

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

    def tearDown(self):
        User.objects.filter(user_email="test1").delete()
        User.objects.filter(user_email="test12").delete()
