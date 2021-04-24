import requests
import sys

addresses = []

start_port = int(sys.argv[1])
count = int(sys.argv[2])+1
for index in range(count):
    URL = f"http://127.0.0.1:{start_port + index}"
    addresses.append(URL)

response = {
    "nodes": addresses
}
for node_addr in addresses:
    r = requests.post(f"{node_addr}/nodes/register", json=response)
