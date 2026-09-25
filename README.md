# PhoneTracker Windows Application 

Windows desktop dashboard for the PhoneTracker API.

## Install

```powershell
py -m pip install requests
```

## Run

```powershell
py phone_tracker.py
```

The Android device must have location permission and actively send GPS
telemetry to the API. A phone number by itself is not used to obtain GPS.

## Theme

Neon cyan / magenta / purple cyberpunk terminal UI with telemetry cards,
pairing controls, status indicators, and a radar-style GPS visualizer.
