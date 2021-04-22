import time
import requests
import schedule

# will keep sending consensus requests for each node every 5 seconds.


def send_request(port_number):
    r = requests.post(f"http://localhost:{port_number}/nodes/resolve")

port_list = [5001, 5002, 5003, 5004, 5005]
for port in port_list:
    schedule.every(5).seconds.do(send_request, port)

while True:
    schedule.run_pending()
    time.sleep(1)


