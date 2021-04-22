import requests
import sys

# shutdown the passed in node server

print(f"Arguments count: {len(sys.argv)}")

URL = f"http://localhost:{sys.argv[1]}/shutdown"
r = requests.get(url=URL)

data = r.json()
result = data['result']
print(f"{result}")
