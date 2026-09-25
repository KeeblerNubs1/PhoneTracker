using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Windows;

namespace PhoneTracker.Desktop;

public partial class MainWindow : Window
{
    private readonly HttpClient http = new();
    private string? desktopToken;
    private System.Windows.Threading.DispatcherTimer? timer;

    public MainWindow() => InitializeComponent();

    private async void CreatePairing_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            var baseUrl = ApiBox.Text.Trim().TrimEnd('/');
            var response = await http.PostAsync($"{baseUrl}/api/pair/create", null);
            response.EnsureSuccessStatusCode();
            using var doc = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
            CodeText.Text = doc.RootElement.GetProperty("code").GetString();
            desktopToken = doc.RootElement.GetProperty("desktopToken").GetString();
            StatusText.Text = "Waiting for Android...";
            timer?.Stop();
            timer = new System.Windows.Threading.DispatcherTimer { Interval = TimeSpan.FromSeconds(3) };
            timer.Tick += async (_, _) => await PollAsync(baseUrl);
            timer.Start();
        }
        catch (Exception ex) { MessageBox.Show(ex.Message, "PhoneTracker"); }
    }

    private async Task PollAsync(string baseUrl)
    {
        if (desktopToken is null) return;
        using var req = new HttpRequestMessage(HttpMethod.Get, $"{baseUrl}/api/pair/status");
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", desktopToken);
        var response = await http.SendAsync(req);
        if (!response.IsSuccessStatusCode) return;
        using var doc = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
        if (!doc.RootElement.GetProperty("paired").GetBoolean()) return;
        StatusText.Text = "Paired";
        DeviceText.Text = doc.RootElement.GetProperty("deviceName").GetString();
        await PollLocationAsync(baseUrl);
    }

    private async Task PollLocationAsync(string baseUrl)
    {
        using var req = new HttpRequestMessage(HttpMethod.Get, $"{baseUrl}/api/location");
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", desktopToken);
        var response = await http.SendAsync(req);
        if (!response.IsSuccessStatusCode) return;
        using var doc = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
        var r = doc.RootElement;
        var lat = r.GetProperty("latitude").GetDouble();
        var lon = r.GetProperty("longitude").GetDouble();
        var ts = r.GetProperty("timestamp").GetDateTimeOffset().ToLocalTime();
        LocationText.Text = $"{lat:F6}, {lon:F6} ({ts:g})";
        MapText.Text = $"Phone location\n\nLatitude: {lat:F6}\nLongitude: {lon:F6}\n\nLast update: {ts:g}";
    }
}
