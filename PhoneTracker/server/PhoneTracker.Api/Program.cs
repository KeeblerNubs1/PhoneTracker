using System.Collections.Concurrent;
using System.Security.Cryptography;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

var pairs = new ConcurrentDictionary<string, PairSession>();
var locations = new ConcurrentDictionary<string, LocationRecord>();

app.MapGet("/", () => Results.Ok(new { name = "PhoneTracker API", status = "running" }));

app.MapPost("/api/pair/create", () =>
{
    var code = RandomNumberGenerator.GetInt32(100000, 1000000).ToString();
    var desktopToken = Convert.ToHexString(RandomNumberGenerator.GetBytes(32));
    pairs[code] = new PairSession(code, desktopToken, null, DateTimeOffset.UtcNow.AddMinutes(10), null);
    return Results.Ok(new { code, desktopToken, expiresAt = pairs[code].ExpiresAt });
});

app.MapGet("/api/pair/status", (HttpRequest request) =>
{
    if (!TryBearer(request, out var token)) return Results.Unauthorized();
    var pair = pairs.Values.FirstOrDefault(x => x.DesktopToken == token);
    if (pair is null || pair.ExpiresAt < DateTimeOffset.UtcNow) return Results.NotFound();
    return Results.Ok(new { paired = pair.DeviceToken is not null, deviceName = pair.DeviceName });
});

app.MapPost("/api/pair/complete", (PairRequest input) =>
{
    if (!pairs.TryGetValue(input.Code ?? "", out var pair) || pair.ExpiresAt < DateTimeOffset.UtcNow)
        return Results.BadRequest(new { error = "Pairing code is invalid or expired." });
    var deviceToken = Convert.ToHexString(RandomNumberGenerator.GetBytes(32));
    pairs[input.Code!] = pair with { DeviceToken = deviceToken, DeviceName = input.DeviceName ?? "Android device" };
    return Results.Ok(new { deviceToken });
});

app.MapPost("/api/location", (LocationInput input, HttpRequest request) =>
{
    if (!TryBearer(request, out var token)) return Results.Unauthorized();
    if (input.Latitude is < -90 or > 90 || input.Longitude is < -180 or > 180) return Results.BadRequest();
    locations[token] = new LocationRecord(input.DeviceId, input.Latitude, input.Longitude, input.AccuracyMeters, input.BatteryPercent, DateTimeOffset.UtcNow);
    return Results.Ok();
});

app.MapGet("/api/location", (HttpRequest request) =>
{
    if (!TryBearer(request, out var desktopToken)) return Results.Unauthorized();
    var pair = pairs.Values.FirstOrDefault(x => x.DesktopToken == desktopToken);
    if (pair?.DeviceToken is null) return Results.NotFound(new { error = "No device paired." });
    return locations.TryGetValue(pair.DeviceToken, out var location) ? Results.Ok(location) : Results.NotFound();
});

app.Run("http://0.0.0.0:5080");

static bool TryBearer(HttpRequest request, out string token)
{
    token = "";
    const string prefix = "Bearer ";
    var value = request.Headers.Authorization.ToString();
    if (!value.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)) return false;
    token = value[prefix.Length..].Trim();
    return token.Length > 0;
}

record PairSession(string Code, string DesktopToken, string? DeviceToken, DateTimeOffset ExpiresAt, string? DeviceName);
record PairRequest(string? Code, string? DeviceName);
record LocationInput(string DeviceId, double Latitude, double Longitude, double? AccuracyMeters, int? BatteryPercent);
record LocationRecord(string DeviceId, double Latitude, double Longitude, double? AccuracyMeters, int? BatteryPercent, DateTimeOffset Timestamp);
