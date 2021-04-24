import requests
import sys

# shutdown the passed in node server
URL = f"http://localhost:{sys.argv[1]}/shutdown"
r = requests.get(url=URL)
data = r.json()
