# Architecture

Android GPS + permission -> ASP.NET Core API -> Windows dashboard.

The phone number is not used as a GPS lookup mechanism. The Android device actively supplies its location after the user grants permission.

Before public deployment, add HTTPS, persistent storage, account authentication, token revocation, rate limiting, and audit logging.
