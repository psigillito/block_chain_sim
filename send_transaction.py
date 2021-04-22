import time
import requests
import schedule
import random
import string


# will send a transaction to every node in the network every second


def send_request(port_number):

    letters = string.ascii_lowercase

    response = {
        "trans_id": random.randint(1, 100000000),
        "sender": ''.join(random.choice(string.ascii_lowercase) for i in range(10)),
        "recipient": ''.join(random.choice(string.ascii_lowercase) for i in range(10)),
        "amount": random.randint(1, 1000)
    }
    r = requests.post(f"http://localhost:{port_number}/transactions/new", json = response)

port_list = [5001, 5002, 5003, 5004, 5005]
for port in port_list:
    schedule.every(1).seconds.do(send_request, port)

while True:
    schedule.run_pending()
    time.sleep(1)


