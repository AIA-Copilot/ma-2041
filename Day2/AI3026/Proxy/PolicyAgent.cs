using Azure.Core;
using Day2;
using Microsoft.Agents.Builder;
using Microsoft.Agents.Builder.App;
using Microsoft.Agents.Builder.State;
using Microsoft.Agents.Core.Models;

public sealed class PolicyAgent : AgentApplication
{
    public const string HelpText = "Ask one self-contained IT policy question. I use the saved Foundry agent and its attached files. I cannot create tickets or remember earlier messages.";
    public PolicyAgent(AgentApplicationOptions options, IConfiguration config, IHttpClientFactory clients,
        TokenCredential credential, ILogger<PolicyAgent> logger) : base(options)
    {
        OnActivity(ActivityTypes.Message, async (ITurnContext turn, ITurnState state, CancellationToken ct) =>
        {
            string text = turn.Activity.Text?.Trim() ?? "";
            if (text.Equals("/help", StringComparison.OrdinalIgnoreCase))
            {
                await turn.SendActivityAsync(HelpText, cancellationToken: ct);
                return;
            }
            try
            {
                string answer = await FoundryGateway.AskAsync(clients.CreateClient("Foundry"),
                    async token => (await credential.GetTokenAsync(new TokenRequestContext(["https://ai.azure.com/.default"]), token)).Token,
                    config["Foundry:ProjectEndpoint"] ?? "", config["Foundry:AgentName"] ?? "",
                    config["Foundry:AgentVersion"] ?? "", text, ct);
                await turn.SendActivityAsync(answer, cancellationToken: ct);
            }
            catch (ArgumentException ex)
            {
                await turn.SendActivityAsync(ex.Message, cancellationToken: ct);
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                // Never echo service bodies, tokens, or exception details into a chat.
                logger.LogWarning("Foundry request failed: {Type}", ex.GetType().Name);
                await turn.SendActivityAsync("The Foundry request failed. Check the local host log and your project configuration; no answer is being substituted.", cancellationToken: ct);
            }
        });
    }
}
