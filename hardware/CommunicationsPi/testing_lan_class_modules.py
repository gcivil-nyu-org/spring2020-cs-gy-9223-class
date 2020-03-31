import lan_client_class
import os

client = lan_client_class.LANClient()
sample_payload = {"key1": "value1", "key2": "value2"}

print(client.ping_lan_server(sample_payload))