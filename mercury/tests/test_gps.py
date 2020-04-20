from django.test import TestCase
from django.urls import reverse
from mercury.models import EventCodeAccess
from ag_data.models import AGEvent, AGActiveEvent, AGVenue
import datetime


class TestGPSView(TestCase):
    TESTCODE = "testcode"

    login_url = "mercury:EventAccess"
    gps_url = "mercury:gps"

    def setUp(self):
        self.login_url = "mercury:EventAccess"
        self.gps_url = "mercury:gps"

        test_code = EventCodeAccess(event_code=self.TESTCODE, enabled=True)
        test_code.save()

    def create_venue_and_event(self, event_name):
        venue = AGVenue.objects.create(
            name="test", description="test", latitude="1", longitude="1",
        )
        venue.save()

        event = AGEvent.objects.create(
            name=event_name,
            date=datetime.datetime(2020, 3, 3, 20, 21, 22),
            description="test",
            venue_uuid=venue,
        )
        event.save()

        return event

    def _get_with_event_code(self, url, event_code):
        self.client.get(reverse(self.login_url))
        self.client.post(reverse(self.login_url), data={"eventcode": event_code})
        response = self.client.get(reverse(url))
        session = self.client.session
        return response, session

    def test_get_no_active_event_success(self):
        response, session = self._get_with_event_code(self.gps_url, self.TESTCODE)

        self.assertEqual(200, response.status_code)
        self.assertEqual(True, session["event_code_active"])
        self.assertEqual(True, session["event_code_known"])

    def test_get_with_active_event_success(self):
        event = self.create_venue_and_event("testing_get")

        active_event = AGActiveEvent(agevent=event)
        active_event.save()

        response, session = self._get_with_event_code(self.gps_url, self.TESTCODE)

        self.assertEqual(200, response.status_code)
        self.assertEqual(True, session["event_code_active"])
        self.assertEqual(True, session["event_code_known"])

        self.assertEqual(200, response.status_code)
