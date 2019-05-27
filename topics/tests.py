import json

from django.test import TestCase
from django.test import Client 

from users.models import *
from topics.models import *

class TopicTest(TestCase):

    def setUp(self):
        c = Client()

        test = {"user_email":"test1", "user_nickname":"testnick1", "user_password":"1234"}
        c.post("/user", json.dumps(test), content_type="application/json")
        
        Topic.objects.create(topic_name = "트와이스")
        Topic.objects.create(topic_name = "어벤져스")

    def test_topic_search(self):
        c = Client()

        user         = User.objects.get(user_email ="test1")
        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")
        access_token = response.json()["access_token"]

        test = {"search":"스"}
        response = c.get(
            "/topics",
            test,
            **{'HTTP_AUTHORIZATION':access_token, 'content_type':"application/json"}
        )

        self.assertEqual = (response.status_code, 200)
        self.assertEqual = (
            response.json(),
                {
                    "topic_list": [
                        {
                            "topic_id"   : "1",
                            "commu_name" : "트와이스"
                        },
                        {
                            "topic_id"   : "2",
                            "commu_name" : "어벤져스"
                        }
                    ]
                }
        )

    def test_topic_check(self):
        c = Client()
        
        user         = User.objects.get(user_email ="test1")
        test         = {"user_email":"test1", "user_password":"1234"}
        response     = c.post("/user/auth", json.dumps(test), content_type="application/json")
        access_token = response.json()["access_token"]

        test_topic = Topic.objects.get(topic_name="트와이스")
        test = {"topic" : test_topic.id}
        response = c.post(
            "/topics",
            json.dumps(test),
            **{'HTTP_AUTHORIZATION':access_token, 'content_type':"application/json"}
        )

        self.assertEqual = (response.status_code, 200)
        self.assertEqual = (
            response.json(),
                { 
                    "favorite_topic"      : True,
                    "favorite_topic_list" : {
                        "topic_id": test_topic.id,
                        "topic_name": "트와이스"
                    }
                }
        )
    def tearDown(self):
        User.objects.filter(user_email="test1").delete()
        Topic.objects.filter(topic_name = "트와이스").delete()
        Topic.objects.filter(topic_name = "어벤져스").delete()
