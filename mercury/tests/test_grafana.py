from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from mercury.models import EventCodeAccess, GFConfig
from ag_data.models import AGSensor, AGSensorType, AGEvent, AGVenue, AGActiveEvent
from mercury.grafanaAPI.grafana_api import Grafana
import requests
import os
import datetime


# grafana host with basic auth
HOST = "http://admin:admin@localhost:3000"

# db credentials
DB = settings.DATABASES
DB_HOSTNAME = DB["default"]["HOST"] + ":" + str(DB["default"]["PORT"])
DB_NAME = DB["default"]["NAME"]
DB_USERNAME = DB["default"]["USER"]
DB_PASSWORD = DB["default"]["PASSWORD"]


# This test needs to have access to a test deployment of grafana, otherwise
# we will need to wipe out the sensors each time it runs it runs
class TestGrafana(TestCase):
    TESTCODE = "testcode"

    title = "Bar"

    test_sensor_name = "Wind Sensor"
    test_sensor_name_update = "Another Name"
    test_sensor_type = "Dual wind"
    test_sensor_format = {
        "left_gust": {"unit": "km/h", "format": "float"},
        "right_gust": {"unit": "km/h", "format": "float"},
    }

    field_name_1 = "test-field-1"
    field_name_2 = "test-field-2"
    data_type_1 = "test-data-type-1"
    data_type_2 = "test-data-type-2"
    unit_1 = "test-unit-1"
    unit_2 = "test-unit-2"

    test_sensor = {
        "name": test_sensor_name,
        "processing formula": 0,
        "field-names": [field_name_1, field_name_2],
        "data-types": [data_type_1, data_type_2],
        "units": [unit_1, unit_2],
    }

    test_sensor_format_update = {
        "fuel reading": {"unit": "m", "format": "float"},
    }

    test_event_data = {
        "name": "Sunny Day Test Drive",
        "date": datetime.datetime(2020, 2, 2, 20, 21, 22),
        "description": "A very progressive test run at \
                    Sunnyside Daycare's Butterfly Room.",
        "location": "New York, NY",
    }

    test_event_data_update = {
        "name": "Another Day Test Drive",
        "date": datetime.datetime(2020, 3, 3, 20, 21, 22),
        "description": "A very modern test run at \
                        my backyard.",
        "location": "Buffalo, NY",
    }

    test_venue_data = {
        "name": "Venue 1",
        "description": "foo",
        "latitude": 100,
        "longitude": 200,
    }

    def create_gfconfig(self):
        config = GFConfig.objects.create(
            gf_host=HOST,
            gf_token=self.ADMIN,
            gf_db_host=DB_HOSTNAME,
            gf_db_name=DB_NAME,
            gf_db_username=DB_USERNAME,
            gf_db_pw=DB_PASSWORD,
            gf_current=True,
        )
        config.save()
        return config

    # Returns event
    def create_venue_and_event(self, event_name):
        venue = AGVenue.objects.create(
            name=self.test_venue_data["name"],
            description=self.test_venue_data["description"],
            latitude=self.test_venue_data["latitude"],
            longitude=self.test_venue_data["longitude"],
        )
        venue.save()

        event = AGEvent.objects.create(
            name=event_name,
            date=self.test_event_data["date"],
            description=self.test_event_data["description"],
            venue_uuid=venue,
        )
        event.save()

        return event

    def setUp(self):
        # api keys with admin and viewer level permissions
        self.ADMIN = Grafana.create_api_key(HOST, "admin", "Admin")
        self.VIEWER = Grafana.create_api_key(HOST, "viewer", "Viewer")

        self.login_url = "mercury:EventAccess"
        self.sensor_url = "mercury:sensor"
        self.event_url = "mercury:events"
        self.event_delete_url = "mercury:delete_event"
        self.event_update_url = "mercury:update_event"
        self.update_sensor_url = "mercury:update_sensor"
        self.delete_sensor_url = "mercury:delete_sensor"
        self.update_sensor_type_url = "mercury:update_type"
        test_code = EventCodeAccess(event_code="testcode", enabled=True)
        test_code.save()
        # Login
        self._get_with_event_code(self.sensor_url, self.TESTCODE)

        # Create fresh grafana object
        self.config = self.create_gfconfig()
        self.grafana = Grafana(self.config)

        # Create random name to be used for event and datasource
        self.event_name = self.grafana.generate_random_string(10)
        self.updated_event_name = self.event_name + " Day Two"
        self.datasource_name = self.grafana.generate_random_string(10)

        # Clear existing dashboard and datasource
        self.grafana.delete_dashboard_by_name(self.event_name)
        self.grafana.delete_dashboard_by_name(self.updated_event_name)
        self.grafana.delete_datasource_by_name(self.datasource_name)

    def tearDown(self):
        # Create fresh grafana instance (in case test invalidated any tokens, etc.)
        self.grafana = Grafana(self.config)

        # Clear all of the created dashboards
        self.grafana.delete_dashboard_by_name(self.event_name)
        self.grafana.delete_datasource_by_name(self.datasource_name)

    def _get_with_event_code(self, url, event_code):
        self.client.get(reverse(self.login_url))
        self.client.post(reverse(self.login_url), data={"eventcode": event_code})
        response = self.client.get(reverse(url))
        session = self.client.session
        return response, session

    def test_get_dashboard_with_uid_success(self):
        # Should return True if create_dashboard was successful
        dashboard = self.grafana.create_dashboard(self.event_name)
        self.assertTrue(dashboard)

        # Query new dashboard
        uid = dashboard["uid"]
        fetched_dashboard = self.grafana.get_dashboard_with_uid(uid)

        # Confirm params of new dashboard (slug, uid, title)
        self.assertTrue(fetched_dashboard)
        self.assertTrue(fetched_dashboard["meta"])
        self.assertTrue(fetched_dashboard["meta"]["slug"], self.event_name.lower())
        self.assertTrue(fetched_dashboard["dashboard"])
        self.assertTrue(fetched_dashboard["dashboard"]["uid"], uid)
        self.assertTrue(fetched_dashboard["dashboard"]["title"], self.event_name)

    def test_get_dashboard_url_success(self):
        self.grafana.create_dashboard(self.event_name)
        self.assertTrue(self.grafana.get_dashboard_url_by_name(self.event_name))

    def test_get_dashboard_url_none(self):
        self.assertIsNone(
            self.grafana.get_dashboard_url_by_name(self.event_name + "foo")
        )

    def test_get_dashboard_with_uid_fail(self):
        # Create a random UID to search for
        uid = self.grafana.generate_random_string(10)

        # Try and fetch random UID (should return None)
        fetched_dashboard = self.grafana.get_dashboard_with_uid(uid)
        self.assertFalse(fetched_dashboard)

    def test_create_grafana_dashboard_success(self):
        # Should return an object with dashboard credentials
        dashboard = self.grafana.create_dashboard(self.event_name)
        self.assertTrue(dashboard)

    def test_create_grafana_dashboard_verify_new_dashboard_contents(self):
        # Should return an object with dashboard credentials
        dashboard = self.grafana.create_dashboard(self.event_name)

        # Confirm that an object was returned
        self.assertTrue(dashboard)
        # Check for success status message
        self.assertEquals(dashboard["status"], "success")
        # Check that dashboard has correct name
        self.assertEquals(dashboard["slug"], self.event_name.lower())

        # Retrieve UID for new dashboard, use to query new dashboard
        uid = dashboard["uid"]

        # Confirm new dashboard can be queried from the API
        endpoint = os.path.join(self.grafana.endpoints["dashboard_uid"], uid)
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            url=endpoint, headers=headers, auth=("api_key", self.grafana.api_token)
        )

        # Confirm uid and title are as expected
        self.assertEquals(response.json()["dashboard"]["uid"], uid)
        self.assertEquals(response.json()["dashboard"]["title"], self.event_name)

    def test_create_grafana_dashboard_fail_authorization(self):
        self.grafana.api_token = "abcde"  # invalid API token

        expected_message = "Invalid API key"
        with self.assertRaisesMessage(ValueError, expected_message):
            self.grafana.create_dashboard(self.event_name)

    def test_create_grafana_dashboard_fail_permissions(self):
        self.grafana.api_token = self.VIEWER  # API token with viewer permissions

        expected_message = "Access denied - check API permissions"
        with self.assertRaisesMessage(ValueError, expected_message):
            self.grafana.create_dashboard(self.event_name)

    def test_create_grafana_dashboard_fail_empty_title(self):
        expected_message = "Dashboard title cannot be empty"
        with self.assertRaisesMessage(ValueError, expected_message):
            self.grafana.create_dashboard("")

    def test_validate_credentials_success(self):
        # should return True if credentials are valid
        self.assertTrue(self.grafana.validate_credentials())

    def test_update_dashboard_title_success(self):
        event = self.create_venue_and_event(self.event_name)
        self.grafana.create_dashboard(self.event_name)
        new_name = event.name + " foo"
        self.assertTrue(self.grafana.update_dashboard_title(event, new_name))

    def test_update_dashboard_title_fail_same_name(self):
        event = self.create_venue_and_event(self.event_name)
        self.grafana.create_dashboard(self.event_name)
        self.assertFalse(self.grafana.update_dashboard_title(event, event.name))

    def test_update_dashboard_title_fail_no_dashboard(self):
        event = self.create_venue_and_event(self.event_name)
        self.assertFalse(self.grafana.update_dashboard_title(event, event.name))

    def test_validate_credentials_fail_authorization(self):
        self.grafana.api_token = "abcde"  # invalid API token

        expected_message = "Grafana API validation failed: Invalid API key"
        with self.assertRaisesMessage(ValueError, expected_message):
            self.grafana.validate_credentials()

    def test_validate_credentials_fail_permissions(self):
        self.grafana.api_token = self.VIEWER  # API token with viewer permissions

        expected_message = (
            "Grafana API validation failed: Access denied - " "check API permissions"
        )
        with self.assertRaisesMessage(ValueError, expected_message):
            self.grafana.validate_credentials()

    def test_create_grafana_dashboard_fail_duplicate_title(self):
        # Should return a JSON object with a message that the dashboard already exists
        dashboard = self.grafana.create_dashboard(self.event_name)
        self.assertTrue(dashboard)

        expected_message = "Dashboard with the same name already exists"
        with self.assertRaisesMessage(ValueError, expected_message):
            self.grafana.create_dashboard(self.event_name)

    def test_delete_grafana_dashboard(self):
        # Create a dashboard
        dashboard = self.grafana.create_dashboard(self.event_name)
        self.assertTrue(dashboard)

        # Delete the dashboard, should return True if deleted
        deleted_dashboard = self.grafana.delete_dashboard(dashboard["uid"])
        self.assertTrue(deleted_dashboard)

        # Confirm that dashboard was deleted by querying it
        endpoint = os.path.join(
            self.grafana.endpoints["dashboard_uid"], dashboard["uid"]
        )
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            url=endpoint, headers=headers, auth=("api_key", self.grafana.api_token)
        )
        self.assertTrue(response.json()["message"])
        self.assertEquals(response.json()["message"], "Dashboard not found")

    def test_delete_grafana_dashboard_fail(self):
        # Generate a random uid
        uid = self.grafana.generate_random_string(10)

        # Attempt to delete dashboard that doesn't exist, should return False
        deleted_dashboard = self.grafana.delete_dashboard(uid)
        self.assertFalse(deleted_dashboard)

    def test_add_panel(self):
        # Create a dashboard, confirm it was created and retrieve its UID
        dashboard = self.grafana.create_dashboard(self.event_name)
        self.assertTrue(dashboard)
        uid = dashboard["uid"]

        # Create an event and venue
        event = self.create_venue_and_event(self.event_name)

        # Create a sensor type and sensor
        sensor_type = AGSensorType.objects.create(
            name=self.test_sensor_type,
            processing_formula=0,
            format=self.test_sensor_format,
        )
        sensor_type.save()
        sensor = AGSensor.objects.create(
            name=self.test_sensor_name, type_id=sensor_type
        )
        sensor.save()

        # Add a panel to the dashboard
        self.grafana.add_panel(sensor, event)

        # Retrieve the current dashboard
        dashboard_info = self.grafana.get_dashboard_with_uid(uid)

        # Confirm that a panel was added to the dashboard with the expected title
        self.assertTrue(dashboard_info)
        self.assertTrue(dashboard_info["dashboard"])
        self.assertTrue(dashboard_info["dashboard"]["panels"])
        self.assertTrue(len(dashboard_info["dashboard"]["panels"]) == 1)
        self.assertTrue(
            dashboard_info["dashboard"]["panels"][0]["title"] == sensor.name
        )

    def test_add_multiple_panels(self):
        # Create a dashboard, confirm it was created and retrieve its UID
        dashboard = self.grafana.create_dashboard(self.event_name)
        self.assertTrue(dashboard)
        uid = dashboard["uid"]

        # Create an event and venue
        event = self.create_venue_and_event(self.event_name)

        # Create a sensor type
        sensor_type = AGSensorType.objects.create(
            name=self.test_sensor_type,
            processing_formula=0,
            format=self.test_sensor_format,
        )
        sensor_type.save()

        # Create 10 sensors, invoking add_panel for each new sensor
        for i in range(10):
            sensor = AGSensor.objects.create(
                name="".join([self.test_sensor_name, str(i)]), type_id=sensor_type
            )
            sensor.save()

            self.grafana.add_panel(sensor, event)

        # Query dashboard to confirm 10 panels were added
        dashboard_info = self.grafana.get_dashboard_with_uid(uid)
        self.assertTrue(dashboard_info)
        self.assertTrue(dashboard_info["dashboard"])
        self.assertTrue(dashboard_info["dashboard"]["panels"])
        self.assertTrue(len(dashboard_info["dashboard"]["panels"]) == 10)

        # Confirm correct title for each panel
        for i in range(10):
            name = "".join([self.test_sensor_name, str(i)])
            self.assertTrue(dashboard_info["dashboard"]["panels"][i]["title"] == name)

    def test_add_sensor_creates_panel_in_dashboard(self):
        # Create a dashboard, confirm it was created and retrieve its UID
        dashboard = self.grafana.create_dashboard(self.event_name)
        self.assertTrue(dashboard)

        # Create an event
        event = self.create_venue_and_event(self.event_name)

        # Make the event the active event
        AGActiveEvent.objects.create(agevent=event).save()

        # Create a sensor through the UI
        self.client.post(
            reverse(self.sensor_url),
            data={
                "submit_new_sensor": "",
                "sensor-name": self.test_sensor["name"],
                "field-names": self.test_sensor["field-names"],
                "data-types": self.test_sensor["data-types"],
                "units": self.test_sensor["units"],
            },
        )

        self.assertEquals(AGSensor.objects.count(), 1)

        # Fetch the dashboard again
        dashboard = self.grafana.get_dashboard_by_name(self.event_name)
        self.assertTrue(dashboard)

        # Confirm that a panel was added to the dashboard with the expected title
        self.assertTrue(dashboard)
        self.assertTrue(dashboard["dashboard"])
        self.assertTrue(dashboard["dashboard"]["panels"])
        self.assertTrue(len(dashboard["dashboard"]["panels"]) == 1)

        # Note: converting test_sensor_name to lowercase because currently
        # sensor names are automatically capitalized when they are created
        self.assertEquals(
            dashboard["dashboard"]["panels"][0]["title"],
            self.test_sensor["name"].lower(),
        )

    def test_update_sensor_name_updates_panel_title(self):
        # Create a dashboard
        dashboard = self.grafana.create_dashboard(self.event_name)
        self.assertTrue(dashboard)

        # Create an event, create a sensor
        event = self.create_venue_and_event(self.event_name)

        # Create AGSensorType object for foreign key reference
        sensor_type = AGSensorType.objects.create(
            name=self.test_sensor["name"].lower(),
            processing_formula=0,
            format={
                self.field_name_1: {"data_type": self.data_type_1, "unit": self.unit_1},
                self.field_name_2: {"data_type": self.data_type_2, "unit": self.unit_2},
            },
        )
        sensor_type.save()

        # Create AG Sensor Object
        sensor = AGSensor.objects.create(
            name=self.test_sensor["name"].lower(), type_id=sensor_type
        )
        sensor.save()

        # Add the sensor panel to the dashboard
        self.grafana.add_panel(sensor, event)

        updated_test_sensor_name = "foo"

        # Post Edited Name
        self.client.post(
            reverse(self.sensor_url),
            data={
                "edit_sensor": "",
                "sensor-name": self.test_sensor["name"].lower(),
                "sensor-name-updated": updated_test_sensor_name,
                "field-names": self.test_sensor["field-names"],
                "data-types": self.test_sensor["data-types"],
                "units": self.test_sensor["units"],
            },
        )

        # Check that AGSensor object has new name
        sensor = AGSensor.objects.all()[0]
        self.assertEqual(sensor.name, updated_test_sensor_name)

        # Check that sensor name was updated
        sensor = AGSensor.objects.all()[0]
        self.assertEquals(sensor.name, updated_test_sensor_name)

        # Confirm that Grafana panel title was updated
        # Confirm that a panel was added to the dashboard with the expected title
        dashboard = self.grafana.get_dashboard_by_name(self.event_name)

        self.assertTrue(dashboard)
        self.assertTrue(dashboard["dashboard"])
        self.assertTrue(dashboard["dashboard"]["panels"])
        self.assertTrue(len(dashboard["dashboard"]["panels"]) == 1)

        self.assertEquals(
            dashboard["dashboard"]["panels"][0]["title"], updated_test_sensor_name,
        )

    def test_update_sensor_type_updates_panel_query(self):
        # Create a dashboard, confirm it was created
        dashboard = self.grafana.create_dashboard(self.event_name)
        self.assertTrue(dashboard)

        # Create an event
        event = self.create_venue_and_event(self.event_name)

        # Create sensor and sensor type
        sensor_type = AGSensorType.objects.create(
            name=self.test_sensor_name.lower(),
            processing_formula=0,
            format=self.test_sensor_format,
        )
        sensor_type.save()

        sensor = AGSensor.objects.create(
            name=self.test_sensor_name.lower(), type_id=sensor_type
        )
        sensor.save()

        # Create grafana sensor panel
        self.grafana.add_panel(sensor, event)

        # New fields
        field_names_updated = ["foo"]
        data_types_updated = ["float"]
        units_updated = ["km/h"]

        # Post edited sensor type
        self.client.post(
            reverse(self.sensor_url),
            data={
                "edit_sensor": "",
                "sensor-name": self.test_sensor["name"].lower(),
                "sensor-name-updated": self.test_sensor["name"].lower(),
                "field-names": field_names_updated,
                "data-types": data_types_updated,
                "units": units_updated,
            },
        )

        # Confirm that a new Grafana panel was created with a query containing all of
        # the current field names (not checking the full syntax of the query, just that
        # the new field name is in the query)
        dashboard = self.grafana.get_dashboard_by_name(self.event_name)

        self.assertIn(
            field_names_updated[0],
            dashboard["dashboard"]["panels"][0]["targets"][0]["rawSql"],
        )

    def test_update_sensor_name_and_type_updates_panel_title_and_query(self):
        # Create a dashboard, confirm it was created
        dashboard = self.grafana.create_dashboard(self.event_name)
        self.assertTrue(dashboard)

        # Create an event
        event = self.create_venue_and_event(self.event_name)

        # Create sensor and sensor type
        sensor_type = AGSensorType.objects.create(
            name=self.test_sensor_name.lower(),
            processing_formula=0,
            format=self.test_sensor_format,
        )
        sensor_type.save()

        sensor = AGSensor.objects.create(
            name=self.test_sensor_name.lower(), type_id=sensor_type
        )
        sensor.save()

        # Create grafana sensor panel
        self.grafana.add_panel(sensor, event)

        # New fields
        updated_sensor_name = "bar"
        field_names_updated = ["foo"]
        data_types_updated = ["float"]
        units_updated = ["km/h"]

        # Post edited sensor type
        self.client.post(
            reverse(self.sensor_url),
            data={
                "edit_sensor": "",
                "sensor-name": self.test_sensor["name"].lower(),
                "sensor-name-updated": updated_sensor_name,
                "field-names": field_names_updated,
                "data-types": data_types_updated,
                "units": units_updated,
            },
        )

        dashboard = self.grafana.get_dashboard_by_name(self.event_name)

        # Confirm title and query
        self.assertEquals(
            dashboard["dashboard"]["panels"][0]["title"], updated_sensor_name,
        )
        self.assertIn(
            field_names_updated[0],
            dashboard["dashboard"]["panels"][0]["targets"][0]["rawSql"],
        )

    def test_delete_sensor_deletes_panel_in_dashboard(self):
        # Create a dashboard, confirm it was created
        dashboard = self.grafana.create_dashboard(self.event_name)
        self.assertTrue(dashboard)

        # Create an event
        event = self.create_venue_and_event(self.event_name)

        sensor_type = AGSensorType.objects.create(
            name=self.test_sensor_name,
            processing_formula=0,
            format=self.test_sensor_format,
        )
        sensor_type.save()

        sensor = AGSensor.objects.create(
            name=self.test_sensor_name, type_id=sensor_type
        )
        sensor.save()

        self.grafana.add_panel(sensor, event)

        # Delete sensor
        self.client.post(
            reverse(self.delete_sensor_url, kwargs={"sensor_name": sensor.name}),
            follow=True,
        )

        # Confirm sensor was deleted
        self.assertEquals(AGSensor.objects.count(), 0)

        # Confirm that sensor was deleted from Grafana
        # Fetch the dashboard again
        dashboard = self.grafana.get_dashboard_by_name(dashboard["slug"])
        self.assertTrue(dashboard)

        # Confirm that a panel was added to the dashboard with the expected title
        self.assertTrue(dashboard)
        self.assertTrue(dashboard["dashboard"])
        self.assertEquals(len(dashboard["dashboard"]["panels"]), 0)

    def test_add_panel_fail_no_dashboard_exists_for_event(self):
        # Create an event
        event = self.create_venue_and_event(self.event_name)

        # Create a sensor type and sensor
        sensor_type = AGSensorType.objects.create(
            name=self.test_sensor_type,
            processing_formula=0,
            format=self.test_sensor_format,
        )
        sensor_type.save()
        sensor = AGSensor.objects.create(
            name=self.test_sensor_name, type_id=sensor_type
        )
        sensor.save()

        # Check for expected ValueError and message
        expected_message = "Dashboard not found for this event."
        with self.assertRaisesMessage(ValueError, expected_message):
            self.grafana.add_panel(sensor, event)

    def test_create_postgres_datasource(self):
        # Create datasource
        self.grafana.create_postgres_datasource(self.datasource_name)

        # Query new datasource
        endpoint = os.path.join(
            self.grafana.endpoints["datasource_name"], self.datasource_name
        )
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            url=endpoint, headers=headers, auth=("api_key", self.grafana.api_token)
        )

        # Confirm datasource exists with expected name
        self.assertEquals(response.json()["name"], self.datasource_name)

    def test_create_datasource_fail_authorization(self):
        self.grafana.api_token = "abcde"  # invalid API token

        expected_message = "Invalid API key"
        with self.assertRaisesMessage(ValueError, expected_message):
            self.grafana.create_postgres_datasource(self.datasource_name)

    def test_create_datasource_fail_permissions(self):
        self.grafana.api_token = self.VIEWER  # API token with viewer permissions

        expected_message = "Access denied - check API permissions"
        with self.assertRaisesMessage(ValueError, expected_message):
            self.grafana.create_postgres_datasource(self.datasource_name)

    def test_delete_postgres_datasource(self):
        # create the datasource
        self.grafana.create_postgres_datasource(self.datasource_name)

        # deleted should be True if delete_datasource_by_name returns true
        deleted = self.grafana.delete_datasource_by_name(self.datasource_name)
        self.assertTrue(deleted)

        # confirm that the datasource was actually deleted by querying it
        endpoint = os.path.join(
            self.grafana.endpoints["datasource_name"], self.datasource_name
        )
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            url=endpoint, headers=headers, auth=("api_key", self.grafana.api_token)
        )

        self.assertTrue(response.json()["message"])
        self.assertEquals(response.json()["message"], "Data source not found")

    def test_create_event_creates_dashboard_no_panels(self):
        self.grafana.create_postgres_datasource(self.datasource_name)

        # Create a venue
        venue = AGVenue.objects.create(
            name=self.event_name,
            description=self.test_venue_data["description"],
            latitude=self.test_venue_data["latitude"],
            longitude=self.test_venue_data["longitude"],
        )
        venue.save()

        # Send a request to create an event (should trigger the creation of a
        # grafana dashboard of the same name)
        self.client.post(
            reverse(self.event_url),
            data={
                "submit-event": "",
                "name": self.event_name,
                "date": self.test_event_data["date"],
                "description": self.test_event_data["description"],
                "venue_uuid": venue.uuid,
            },
        )

        # If there are spaces in the name, the GF API will replace them with dashes
        # to generate the "slug". A slug can be used to query the API.
        endpoint = os.path.join(
            self.grafana.hostname,
            "api/dashboards/db",
            self.event_name.lower().replace(" ", "-"),
        )

        response = requests.get(url=endpoint, auth=("api_key", self.grafana.api_token))

        # Confirm that a dashboard was created with the expected name
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()["dashboard"]["title"], self.event_name)

    def test_create_event_creates_dashboard_with_panel(self):
        self.grafana.create_postgres_datasource(self.datasource_name)

        # Create a venue
        venue = AGVenue.objects.create(
            name=self.test_venue_data["name"],
            description=self.test_venue_data["description"],
            latitude=self.test_venue_data["latitude"],
            longitude=self.test_venue_data["longitude"],
        )
        venue.save()

        sensor_type = AGSensorType.objects.create(
            name=self.test_sensor_type,
            processing_formula=0,
            format=self.test_sensor_format,
        )
        sensor_type.save()
        sensor = AGSensor.objects.create(
            name=self.test_sensor_name, type_id=sensor_type
        )
        sensor.save()

        # Send a request to create an event (should trigger the creation of a
        # grafana dashboard of the same name)
        self.client.post(
            reverse(self.event_url),
            data={
                "submit-event": "",
                "name": self.event_name,
                "date": self.test_event_data["date"],
                "description": self.test_event_data["description"],
                "venue_uuid": venue.uuid,
            },
        )

        # If there are spaces in the name, the GF API will replace them with dashes
        # to generate the "slug". A slug can be used to query the API.
        endpoint = os.path.join(
            self.grafana.hostname,
            "api/dashboards/db",
            self.event_name.lower().replace(" ", "-"),
        )

        response = requests.get(url=endpoint, auth=("api_key", self.grafana.api_token))

        # Confirm that a dashboard was created with the expected name
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()["dashboard"]["title"], self.event_name)

        # Confirm that a the new dashboard can be queried and has panel with expected
        # title
        dashboard_info = self.grafana.get_dashboard_with_uid(
            response.json()["dashboard"]["uid"]
        )
        self.assertTrue(dashboard_info)
        self.assertTrue(dashboard_info["dashboard"])
        self.assertTrue(dashboard_info["dashboard"]["panels"])
        self.assertTrue(len(dashboard_info["dashboard"]["panels"]) == 1)
        self.assertTrue(
            dashboard_info["dashboard"]["panels"][0]["title"] == sensor.name
        )

    def test_delete_event_deletes_grafana_dashboard(self):
        self.grafana.create_postgres_datasource(self.datasource_name)

        # Create a venue
        venue = AGVenue.objects.create(
            name=self.event_name,
            description=self.test_venue_data["description"],
            latitude=self.test_venue_data["latitude"],
            longitude=self.test_venue_data["longitude"],
        )
        venue.save()

        # Send a request to create an event (should trigger the creation of a
        # grafana dashboard of the same name)
        self.client.post(
            reverse(self.event_url),
            data={
                "submit-event": "",
                "name": self.event_name,
                "date": self.test_event_data["date"],
                "description": self.test_event_data["description"],
                "venue_uuid": venue.uuid,
            },
        )

        dashboard = self.grafana.get_dashboard_by_name(self.event_name)
        self.assertTrue(dashboard)

        # Retrieve event object
        event = AGEvent.objects.all().first()

        # Delete the event by posting to the delete view
        self.client.post(
            reverse(self.event_delete_url, kwargs={"event_uuid": event.uuid})
        )
        # Try and retrieve the dashboard
        dashboard = self.grafana.get_dashboard_by_name(self.event_name)

        self.assertFalse(dashboard)

    def test_update_event_name_updates_grafana_dashboard_name(self):
        self.grafana.create_postgres_datasource(self.datasource_name)

        event = self.create_venue_and_event(self.event_name)

        updated_event_name = self.updated_event_name

        venue = AGVenue.objects.first()

        # Send a request to create an event (should trigger the creation of a
        # grafana dashboard of the same name)
        self.client.post(
            reverse(self.event_url),
            data={
                "submit-event": "",
                "name": self.event_name,
                "date": self.test_event_data["date"],
                "description": self.test_event_data["description"],
                "venue_uuid": venue.uuid,
            },
        )

        dashboard = self.grafana.get_dashboard_by_name(self.event_name)
        self.assertTrue(dashboard)

        # Update the event name
        self.client.post(
            reverse(self.event_update_url, kwargs={"event_uuid": event.uuid}),
            data={
                "name": updated_event_name,
                "description": self.test_event_data["description"],
                "venue_uuid": venue.uuid,
            },
        )

        # Confirm that a dashboard exists with the new event name
        dashboard = self.grafana.get_dashboard_by_name(updated_event_name)
        self.assertTrue(dashboard)
        self.assertEquals(dashboard["dashboard"]["title"], updated_event_name)
