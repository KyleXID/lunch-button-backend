import json
                               
from django.test import TestCase
from django.test import Client 

class PingTest(TestCase): 
   
    def test_ping(self):
        c = Client()

        response     = c.get("/ping", content_type="application/json")

        self.assertEqual = (response.status_code, 200)

