import os
import json
import requests
from requests.exceptions import HTTPError
from ..Utils.utils import get_logger


class LANClient:
    def __init__(self, log_file_name=None, lan_server_url=None):
        if log_file_name is None:
            self.logging = get_logger("LAN_CLIENT_LOG_FILE")
        else:
            self.logging = get_logger(log_file_name, log_file_name)

        if lan_server_url is None:
            self.url = self.get_server_url_from_env()
        else:
            self.url = lan_server_url

    def get_server_url_from_env(self):
        ip = os.environ["LAN_SERVER_IP"]
        port = os.environ["LAN_PORT"]
        return "http://{}:{}".format(ip, port)

    # Function to ping the LAN server
    # Accepts payload as a python dictionary
    def ping_lan_server(self, payload):
        self.logging.info("Pinging")

        try:
            self.logging.info("data: " + json.dumps(payload))
            response = requests.post(self.url, data=payload)
            response.raise_for_status()
            return response

        except HTTPError as http_err:
            self.logging.error("HTTP error occurred: {}".format(str(http_err)))
            # re-raised so that it can be handled further up the call stack
            raise

        except Exception as err:
            self.logging.error("error occurred: {}".format(str(err)))
            raise
        return
