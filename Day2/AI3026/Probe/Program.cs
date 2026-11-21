using Azure.Core;
using Azure.Identity;
using Day2;
if (args.Length != 1 || args[0] != "--live")
{
    Console.WriteLine("No network call. Run with --live only after lab permission and configuration checks.");
    return;
}
string Env(string key) => Environment.GetEnvironmentVariable(key) ?? "";
var endpoint = Env("FOUNDRY_PROJECT_ENDPOINT");
var name = Env("FOUNDRY_AGENT_NAME");
var version = Env("FOUNDRY_AGENT_VERSION");
FoundryGateway.ResponseEndpoint(endpoint);
FoundryGateway.BuildBody(name, version, "validate");
Console.WriteLine($"Invoking existing agent {name}, version {version}; no agent is created.");
Console.Write("Self-contained question: ");
var question = Console.ReadLine() ?? "";
using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(120) };
var credential = new AzureCliCredential();
try {
    Console.WriteLine(await FoundryGateway.AskAsync(client,
        async ct => (await credential.GetTokenAsync(new TokenRequestContext(["https://ai.azure.com/.default"]), ct)).Token,
        endpoint, name, version, question));
} catch (Exception ex) { Console.Error.WriteLine(ex is HttpRequestException or ArgumentException or InvalidOperationException ? ex.Message : "Credential or network failure. Check Azure CLI login and connectivity."); Environment.ExitCode = 1; }
