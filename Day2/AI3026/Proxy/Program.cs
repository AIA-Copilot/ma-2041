// Hosting pattern adapted from Microsoft ProxyAgent-CSharp (MIT).
using AzureAgentToM365ATK;
using Azure.Identity;
using Azure.Core;
using Day2;
using Microsoft.Agents.Builder;
using Microsoft.Agents.Hosting.AspNetCore;
using Microsoft.Agents.Storage;

var builder = WebApplication.CreateBuilder(args);
builder.Configuration.AddUserSecrets<Program>(optional: true);
builder.Services.AddHttpClient("Foundry", c => c.Timeout = TimeSpan.FromSeconds(120));
builder.Services.AddSingleton<TokenCredential>(new AzureCliCredential());
builder.Services.AddCloudAdapter();
builder.Services.AddAgentAspNetAuthentication(builder.Configuration);
builder.AddAgentApplicationOptions();
builder.AddAgent<PolicyAgent>();
builder.Services.AddSingleton<IStorage, MemoryStorage>();
var app = builder.Build();
app.UseAuthentication();
app.UseAuthorization();
app.MapGet("/health", () => Results.Text("Host alive; Foundry and Teams are NOT checked."));
app.MapPost("/api/messages", async (HttpRequest request, HttpResponse response, IAgentHttpAdapter adapter, IAgent agent, CancellationToken ct) =>
    await adapter.ProcessAsync(request, response, agent, ct)).RequireAuthorization();
app.Run();
