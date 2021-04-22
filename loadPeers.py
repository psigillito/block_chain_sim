import requests
import sys

addresses = []

count = int(sys.argv[1])
for x in range(count):
    port = 5000 + x+1
    URL = f"http://127.0.0.1:{port}"
    addresses.append(URL)

response = {
    "nodes": addresses
}
for node_addr in addresses:
    r = requests.post(f"{node_addr}/nodes/register", json = response)
