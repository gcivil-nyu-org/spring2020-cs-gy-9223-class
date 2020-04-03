#imported lan server as a module
import lan_server

#Test script to check if the arguments- 1.log file name and 2. port are used correctly
if __name__ == '__main__':
	lan_server.run(log_file_name="TEST_LAN_SERVER_LOG_FILE", port=8080)