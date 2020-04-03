# imported lan server as a module
import lan_server

# Test script to check if default log file name and port are used correctly
if __name__ == "__main__":
    lan_server.run(port=8080)
