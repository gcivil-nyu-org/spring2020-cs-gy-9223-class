# imported lan client as a module
import lan_client

# Test script to check if the arguments- 1. default log file name and 2. server url are used correctly
# This script tests client independently and not the server module
if __name__ == "__main__":

    client = lan_client.LANClient(None, "https://postman-echo.com/post")
    # client = lan_client.LANClient("TEST_LAN_CLIENT_LOG_FILE","https://postma.com/post")
    sample_payload = {"Test_Script": "4"}
    client.ping_lan_server(sample_payload)
