import "@microsoft/typespec-m365-copilot";

using TypeSpec.M365.Copilot.Agents;

/**
 * MA-2041 Lab 1 - SOLUTION - Contoso Support Navigator
 *
 * A declarative agent for Microsoft 365 Copilot, authored in TypeSpec and
 * provisioned with Microsoft 365 Agents Toolkit (Lifecycle > Provision).
 *
 * Compiled with the microsoft/typespec-m365-copilot library at version 1.0.0,
 * which emits appPackage/declarative-agent.json at manifest schema v1.5.
 *
 * NOTE on capability names: the TypeSpec operation is CopilotConnectors, and the
 * emitted manifest capability is named GraphConnectors. Both are correct - one is
 * the library's API, the other is the manifest wire format. The Learn article shows
 * the manifest name. The authoritative list of operations is
 * node_modules/.../typespec-m365-copilot/lib/da-capabilities.tsp.
 */
@agent(
  "Contoso Support Navigator",
  "Helps Contoso support engineers triage customer tickets using Contoso's published support policies."
)
@instructions("""
  You are the Contoso Support Navigator, used by Contoso support engineers.

  Your job is to help an engineer decide how to handle a support ticket.
  Always do the following:
  1. State the applicable support policy and the tier it applies to.
  2. State the response-time commitment in business hours.
  3. Cite the source you used. If you cannot find a policy that applies, say so
     explicitly and recommend escalation to the duty manager - never invent a policy.

  Keep answers under 150 words and use short bullet lists. Do not speculate about
  customer contract terms that are not in your knowledge sources.
""")
@conversationStarter(#{
  title: "Triage a ticket",
  text: "What is the response-time commitment for a Sev B ticket from a Premier customer?"
})
@conversationStarter(#{
  title: "Find a policy",
  text: "Which policy covers after-hours escalation for manufacturing customers?"
})
@behaviorOverrides(#{ discourageModelKnowledge: true })
namespace ContosoSupportNavigator {
  /** Ground web answers in Microsoft Learn only, not the whole web. */
  op webSearch is AgentCapabilities.WebSearch<Sites = [
    {
      url: "https://learn.microsoft.com",
    }
  ]>;

  /**
   * Knowledge from the Copilot connector built in Lab 5.
   * connectionId must equal CONNECTION_ID in solutions/lab5/connector_client.py.
   */
  op copilotConnectors is AgentCapabilities.CopilotConnectors<Connections = [
    {
      connectionId: "contososupportpolicies",
    }
  ]>;
}
