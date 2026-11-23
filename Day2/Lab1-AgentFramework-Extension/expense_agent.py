"""Lab07 completed expense logic, extracted from console I/O for channel reuse.
Upstream source and exact changes: PROVENANCE.md. No real submission occurs.
"""
import os
from typing import Annotated
from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from pydantic import Field

ABOUT = "ExpenseClaimAgent v1 — SIMULATED claims only. No email was sent."

async def process_expenses_data(prompt, expenses_data, *, client=None):
    # Turn-local receipts and Agent: no cross-user/global chat history.
    receipts = []
    @tool(approval_mode="never_require")
    def submit_claim(
        to: Annotated[str, Field(description="Who to send the simulated email to")],
        subject: Annotated[str, Field(description="The subject of the email")],
        body: Annotated[str, Field(description="The text body of the email")],
    ):
        receipt = f"SIMULATED expense claim — No email was sent.\nTo: {to}\nSubject: {subject}\n{body}"
        receipts.append(receipt)
        return receipt

    credential = None
    if client is None:
        endpoint, model = os.getenv("PROJECT_ENDPOINT"), os.getenv("MODEL_DEPLOYMENT_NAME")
        if not endpoint or not model:
            raise ValueError("Retain Lab07 PROJECT_ENDPOINT and MODEL_DEPLOYMENT_NAME")
        credential = AzureCliCredential()
        client = FoundryChatClient(project_endpoint=endpoint, model=model, credential=credential)
    try:
        async with Agent(
            client=client,
            name="ExpenseClaimAgent",
            instructions="""You are an AI assistant for expense claim submission.
At the user's request, create an expense claim and use submit_claim to simulate an
email to expenses@contoso.com with subject 'Expense Claim' and a body containing
itemized expenses with a total. Use only the supplied data; do not ask for more.
The tool is a simulation: never claim that an email, payment, or real submission
was sent or completed. Confirm only that a simulated claim was prepared.""",
            tools=[submit_claim],
        ) as agent:
            response = await agent.run([f"{prompt}: {expenses_data}"])
            # Include the actual tool receipt, not just the model's paraphrase.
            return "\n\n".join([ABOUT, str(response), *receipts])
    finally:
        if credential is not None:
            credential.close()
