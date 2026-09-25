# PhoneTracker

A self-hosted Android + Windows location tracker for devices you own or are authorized to manage.

## Architecture

Android app (GPS + permission) -> ASP.NET Core API -> Windows dashboard.

The phone number is not used to derive a location. The Android device explicitly provides GPS coordinates after permission is granted.

## Requirements

- Windows 10/11
- .NET 8 SDK
- Visual Studio 2022 or dotnet CLI
- Android Studio + Android SDK

## Run

1. Start the API:
   `cd server/PhoneTracker.Api && dotnet run`
2. Run the Windows project and create a pairing code.
3. Open the Android project in Android Studio, set the API URL to the server's LAN address, enter the code, and pair.
4. Grant location permission and start tracking.

For internet deployment, use HTTPS and production authentication/token management.
