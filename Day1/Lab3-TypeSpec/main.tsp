import "@typespec/http";
import "@typespec/openapi3";
import "@microsoft/typespec-m365-copilot";

using TypeSpec.M365.Copilot.Agents;

@agent("ZavaTripCoach", "A Seattle arrival coach for fictional Zava new hires.")
// LAB: Replace this starter instruction with the instructions in the guide.
@instructions("Help Zava new hires plan their arrival in Seattle. Do not invent company policies.")
// LAB: Add two @conversationStarter decorators here.
namespace ZavaTripCoach {
  // LAB: Add the source-constrained WebSearch operation here.
}
