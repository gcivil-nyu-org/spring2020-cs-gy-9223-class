#imported lan client as a module
import lan_client

#Test script to check if default arguments- 1.log file name and 2. server url are used correctly
#This script tests client with the server module.
if __name__ == '__main__':

	client = lan_client.LANClient()
	sample_payload = {"Test_Script":"2"}
	client.ping_lan_server(sample_payload)
	