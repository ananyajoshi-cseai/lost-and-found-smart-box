# Hardware and simulation — Anika

Start with handbook pages 6-9. Implement sketch.ino and diagram.json in simulation/: ESP32 GPIO27 INPUT_PULLUP button, GPIO26 LED through 330 ohms, 40 ms debounce. Commit the Wokwi link, circuit and actual ten-press/hold/reset evidence. They are not yet implemented or verified in this repository.

`simulation/replay.py` sends a saved JSON line to local FastAPI using X-Device-Key from the environment. Preserve the event ID on retries. `event.example.json` is explicitly synthetic. Expected statuses: 201 new, 200 duplicate, 409 changed body, 401 missing/bad key. Python standard library only; no external transport package.

Hardware purchases and real Wi-Fi firmware follow the passed simulation gate, not the other way round. The camera belongs on the laptop. LED state does not prove backend receipt.

Replay failures now exit with code 1 and a readable message; 401/409 require correction. Network failures preserve the input file and event ID for a deliberate retry. Actual replay over HTTP is tested with synthetic fixtures; genuine Wokwi acceptance is still pending (docs/b07-walkthrough.md).
