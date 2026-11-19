import "@microsoft/typespec-m365-copilot";

using TypeSpec.M365.Copilot.Agents;

/**
 * MA-2041 Lab 1 - Contoso Support Navigator
 *
 * A declarative agent for Microsoft 365 Copilot, authored in TypeSpec and
 * provisioned with the Microsoft 365 Agents Toolkit.
 *
 * EXERCISE 1.3 - replace the instructions below.
 * EXERCISE 1.4 - add the two conversation starters.
 * EXERCISE 1.5 - add the WebSearch capability scoped to learn.microsoft.com.
 */
@agent(
  "Contoso Support Navigator",
  "Helps Contoso support engineers triage customer tickets using Contoso's published support policies."
)
@instructions("""
  You are the Contoso Support Navigator.
  TODO EXERCISE 1.3: replace this placeholder with real behavioural instructions.
""")
namespace ContosoSupportNavigator {
  // TODO EXERCISE 1.5: add the WebSearch capability here.
}
