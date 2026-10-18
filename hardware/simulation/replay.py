"""Replay one Wokwi serial JSON event; preserve its ID when retrying."""
import json
import os
import sys
import urllib.request
from pathlib import Path

event = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
request = urllib.request.Request(
 os.getenv("API_URL", "http://127.0.0.1:8000") + "/api/device/events",
 data=json.dumps(event).encode(),
 headers={"Content-Type":"application/json", "X-Device-Key":os.environ["DEVICE_KEY"]},
 method="POST")
with urllib.request.urlopen(request,timeout=5) as response:
 print(response.status,response.read().decode())
