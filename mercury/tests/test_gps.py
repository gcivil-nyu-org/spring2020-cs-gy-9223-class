from django.test import TestCase
from django.urls import reverse
from mercury.models import EventCodeAccess, GFConfig
from ag_data.models import AGEvent, AGVenue, AGSensor, AGSensorType
from mercury.grafanaAPI.grafana_api import Grafana
import os
import datetime

class TestGPSView(TestCase):
    TESTCODE = "testcode"

    login_url = "mercury:EventAccess"
    gps_url = "mercury:gps"


    def _get_with_event_code(self, url, event_code):
            self.client.get(reverse(self.login_url))
            self.client.post(reverse(self.login_url), data={"eventcode": event_code})
            response = self.client.get(reverse(url))
            session = self.client.session
            return response, session

    def test_get(self):
        response = self._get_with_event_code(self.gps_url, self.TESTCODE)[0]
        
        self.assertEqual(200, response.status_code)