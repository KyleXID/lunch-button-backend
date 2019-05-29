import json

from django.test import TestCase
from django.test import Client

from users.models import *
from community.models import *

class CommunityTest(TestCase):

    def setUp(self):
        c = Client()
 
        Community.objects.create(
            zip_code = "06168",
            commu_name = "위워크 삼성역점"
        )
        Community.objects.create(
            zip_code = "06210",
            commu_name = "위워크 선릉점"
        )

        test = {
            "user_email":"test1",
            "user_nickname":"testnick1",
            "user_password":"1234",
            "community_id":Community.objects.get(zip_code="06168").id
        }
        c.post("/user", json.dumps(test), content_type="application/json")
    
    def test_commu_name_searching(self):
        c = Client()

        test = {"search":"위워크"}
        response = c.get(
            "/community",
            test,
            content_type="application/json")

        self.assertEqual = (response.status_code, 200)
        self.assertEqual = (
            response.json(),
                {
                    "Community_list": [
                        {   
                            "commu_name": "위워크 삼성역점",
                            "id": 1,
                            "location1": None,
                            "location2": None,
                            "location3": None,
                            "zip_code": "06168"
                        },
                        {       
                            "commu_name": "위워크 선릉점",
                            "id": 2,
                            "location1": None,
                            "location2": None,
                            "location3": None,
                            "zip_code": "06210"
                        }
                    ]
                }   
        )
    
    def test_zip_code_searching(self):
        c = Client()

        test = {"search":"06168"}
        response = c.get(
            "/community",
            test,
            content_type="application/json"
        )

        self.assertEqual = (response.status_code, 200)
        self.assertEqual = (
            response.json(),
                {
                    "Community_list": [
                        {
                            "commu_name": "위워크 삼성역점",
                            "id": Community.objects.get(zip_code="06168").id,
                            "location1": None,
                            "location2": None,
                            "location3": None,
                            "zip_code": "06168"
                        }
                    ]
                }
        )

    def test_select_community(self):
        c = Client()

        user         = User.objects.get(user_email ="test1")
        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")
        access_token = response.json()["access_token"]

        test = {"id":Community.objects.get(zip_code="06168").id}
        response = c.post(
            "/community",
            json.dumps(test),
            **{'HTTP_AUTHORIZATION':access_token, 'content_type':"application/json"}
        )

        self.assertEqual = (response.status_code, 200)
        self.assertEqual = (response.json(), {"message" : "커뮤니티가 정상적으로 등록되었습니다."})
