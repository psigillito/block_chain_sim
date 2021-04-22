import time
import requests

#will send a request to start mining to all the nodes


def send_request(port_number):
    r = requests.get(f"http://localhost:{port_number}/mine")


port_list = [5001, 5002, 5003, 5004, 5005]


while True:
    for port in port_list:
        send_request(port)
    time.sleep(1)


