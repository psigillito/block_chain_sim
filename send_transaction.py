import time
import requests
import schedule
import random
import string
import sys

# will send a transaction to every node in the network every second
#every so many seconds, send a transaction to a random port in the range
#arg 1 = starting port
#arg 2 = number of ports
#arg 3 = seconds between message sent, can be a float i.e. 0.2
#1 is the genesis block

f = open(f"transaction_log.txt", "w")
f.write(f"ID, SENDER, RECIPIENT, AMOUNT\n")
id_counter = 2


def send_request( counter ):
    random_int = random.randint(0, int(sys.argv[2]))
    port_number = int(sys.argv[1]) + random_int
    print(f"SENT TO PORT {port_number}")

    sender = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    recipient = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    amount = random.randint(1, 1000)

    f.write(f"{counter}, {sender}, {recipient}, {amount}\n")
    response = {
        "trans_id": counter,
        "sender": sender,
        "recipient": recipient,
        "amount": amount
    }
    r = requests.post(f"http://localhost:{port_number}/transactions/new", json=response)
    counter += 1
    return counter

#write out transactions to a log file
while True:
    id_counter = send_request(id_counter)
    time.sleep(float(sys.argv[3]))



