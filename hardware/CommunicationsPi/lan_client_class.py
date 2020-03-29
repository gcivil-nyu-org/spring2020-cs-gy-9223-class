import os
import time
import json
import requests
from requests.exceptions import HTTPError
from utils import get_logger

class LANClient:
	
	#Class variables
	logging = get_logger("LAN_CLIENT_LOG_FILE")
	url = os.environ["LAN_SERVER"]

	#Function to ping the server
	def ping_lan_server(self):

		LANClient.logging.info("Pinging")

		while True:
			try:
				payload = {"key1": "value1", "key2": "value2"}
				LANClient.logging.info("data: " + json.dumps(payload))
				response = requests.post(LANClient.url, data=payload)
				response.raise_for_status()

			except HTTPError as http_err:
				LANClient.logging.error("HTTP error occurred: {}".format(str(http_err)))

			except Exception as err:
				LANClient.logging.error("error occurred: {}".format(str(err)))

			else:
				time.sleep(1)
 