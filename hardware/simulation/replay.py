"""Replay saved serial JSON. Retry the same file/ID after transport failure."""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("event_file", type=Path)
    args = parser.parse_args()
    try:
        key = os.environ.get("DEVICE_KEY")
        if not key:
            raise ValueError("Set DEVICE_KEY to the server's local demo device key")
        event = json.loads(args.event_file.read_text(encoding="utf-8-sig"))
        request = urllib.request.Request(
            os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/") + "/api/device/events",
            data=json.dumps(event).encode(),
            headers={"Content-Type": "application/json", "X-Device-Key": key}, method="POST")
        with urllib.request.urlopen(request, timeout=5) as response:
            print(response.status, response.read().decode())
        return 0
    except urllib.error.HTTPError as error:
        print(f"Replay failed: HTTP {error.code}. {error.read().decode(errors='replace')}", file=sys.stderr)
        if error.code in (401,409):
            print("Stop and correct the credential or conflicting event payload; do not retry automatically.", file=sys.stderr)
    except (OSError, ValueError) as error:
        print(f"Replay failed: {error}. Preserve the same event ID when retrying.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
