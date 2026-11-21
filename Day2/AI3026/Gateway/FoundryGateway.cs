using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
namespace Day2;

// AIA adaptation: modern Foundry REST boundary, not PersistentAgentsClient.
public static class FoundryGateway
{
    public static string BuildBody(string name, string version, string input)
    {
        if (string.IsNullOrWhiteSpace(name) || name.StartsWith("asst_", StringComparison.Ordinal) || !Regex.IsMatch(name, @"^[A-Za-z0-9_-]+$"))
            throw new ArgumentException("Use the modern Foundry agent NAME, not a classic asst_ ID.");
        if (string.IsNullOrWhiteSpace(version) || !Regex.IsMatch(version, @"^[A-Za-z0-9._-]+$"))
            throw new ArgumentException("Copy the saved agent version from Foundry.");
        if (string.IsNullOrWhiteSpace(input) || input.Length > 4000)
            throw new ArgumentException("Send a question of 1–4000 characters.");
        return JsonSerializer.Serialize(new { input, store = false, stream = false,
            agent_reference = new { type = "agent_reference", name, version } });
    }

    public static Uri ResponseEndpoint(string endpoint)
    {
        if (!Uri.TryCreate(endpoint, UriKind.Absolute, out var uri) || uri.Scheme != "https" ||
            !uri.Host.EndsWith(".services.ai.azure.com", StringComparison.OrdinalIgnoreCase) ||
            !Regex.IsMatch(uri.AbsolutePath, @"^/api/projects/[A-Za-z0-9_-]+/?$") ||
            uri.Query.Length != 0 || uri.Fragment.Length != 0 || uri.UserInfo.Length != 0 || !uri.IsDefaultPort)
            throw new ArgumentException("Use an Azure public-cloud Foundry PROJECT endpoint, not a model/classic endpoint.");
        return new Uri(endpoint.TrimEnd('/') + "/openai/v1/responses");
    }

    public static string ReadAnswer(string json)
    {
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;
        if (!root.TryGetProperty("status", out var status) || status.GetString() != "completed")
            throw new InvalidOperationException("Foundry did not complete the response; inspect the run in Foundry.");
        var text = new List<string>();
        var sources = new SortedSet<string>(StringComparer.Ordinal);
        foreach (var item in root.GetProperty("output").EnumerateArray())
        {
            if (item.GetProperty("type").GetString() == "function_call")
                throw new InvalidOperationException("Client-side function calls are not implemented in this lab. Remove that tool, not the grounding tool.");
            if (item.GetProperty("type").GetString() != "message") continue;
            foreach (var part in item.GetProperty("content").EnumerateArray())
            {
                if (part.GetProperty("type").GetString() == "refusal")
                    text.Add(part.GetProperty("refusal").GetString() ?? "Request refused.");
                if (part.GetProperty("type").GetString() != "output_text") continue;
                text.Add(part.GetProperty("text").GetString() ?? "");
                if (!part.TryGetProperty("annotations", out var annotations)) continue;
                foreach (var citation in annotations.EnumerateArray())
                    if (citation.TryGetProperty("type", out var type) && type.GetString() == "file_citation" && citation.TryGetProperty("filename", out var file))
                        sources.Add(file.GetString() ?? "Unnamed file");
            }
        }
        if (text.Count == 0) throw new InvalidOperationException("No text answer returned. This lab does not render generated images or attachments.");
        return string.Join("\n", text) + (sources.Count == 0 ? "" : "\n\nSource files: " + string.Join(", ", sources));
    }

    public static async Task<string> AskAsync(HttpClient client, Func<CancellationToken, Task<string>> getToken,
        string endpoint, string name, string version, string input, CancellationToken ct = default)
    {
        var uri = ResponseEndpoint(endpoint);
        var body = BuildBody(name, version, input); // Validate before requesting any credentials.
        using var request = new HttpRequestMessage(HttpMethod.Post, uri);
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", await getToken(ct));
        request.Content = new StringContent(body, Encoding.UTF8, "application/json");
        using var response = await client.SendAsync(request, ct);
        if (!response.IsSuccessStatusCode)
            throw new HttpRequestException($"Foundry HTTP {(int)response.StatusCode}. Check identity, role, endpoint, agent name and saved version.", null, response.StatusCode);
        return ReadAnswer(await response.Content.ReadAsStringAsync(ct));
    }
}
