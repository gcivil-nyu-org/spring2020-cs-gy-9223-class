#imported lan client as a module
import lan_client

#Test script to check if the arguments- 1.log file name and 2. server url are used correctly
#This script tests client independently and not the server module
if __name__ == '__main__':

	client = lan_client.LANClient("TEST_LAN_CLIENT_LOG_FILE","https://postman-echo.com/post")
	sample_payload = {"Test_Script":"1"}
	client.ping_lan_server(sample_payload)
	