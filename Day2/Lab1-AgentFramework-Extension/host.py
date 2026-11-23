"""Authenticated Microsoft 365 Agents SDK host; no anonymous mode."""
import os
from pathlib import Path
from uuid import UUID
from aiohttp import web
from dotenv import load_dotenv
from microsoft_agents.hosting.core import AgentApplication, AgentAuthConfiguration, MemoryStorage
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.aiohttp import CloudAdapter, jwt_authorization_middleware, start_agent_process
from expense_agent import process_expenses_data, ABOUT

ROOT = Path(__file__).parent

async def handle_message(context, *, invoke=process_expenses_data):
    text = (context.activity.text or "").strip()
    if text.lower() in ("/help", "/about") or not text:
        await context.send_activity(ABOUT + " Send: Submit an expense claim. Uses the Lab07 data.txt; each turn is independent.")
        return
    if len(text) > 4000:
        await context.send_activity("Use a request shorter than 4000 characters.")
        return
    try:
        reply = await invoke(text, (ROOT / "data.txt").read_text(encoding="utf-8"))
    except Exception:
        await context.send_activity("Expense agent unavailable. No real submission occurred. Ask the instructor to check model access and configuration.")
        return
    # Keep channel messages bounded without dropping the simulated receipt.
    for start in range(0, len(reply), 6000):
        await context.send_activity(reply[start:start + 6000])

def create_app(env=None):
    env = os.environ if env is None else env
    for key in ("BOT_ID", "BOT_TENANT_ID", "BOT_PASSWORD"):
        if not env.get(key) or "${{" in env[key]:
            raise ValueError("Missing channel configuration: " + key)
    for key in ("BOT_ID", "BOT_TENANT_ID"):
        UUID(env[key])
    config = AgentAuthConfiguration(
        client_id=env["BOT_ID"], tenant_id=env["BOT_TENANT_ID"],
        client_secret=env["BOT_PASSWORD"], anonymous_allowed=False,
        validate_issuer=True, scopes=["https://api.botframework.com/.default"],
    )
    connections = MsalConnectionManager(connections_configurations={"SERVICE_CONNECTION": config})
    adapter = CloudAdapter(connection_manager=connections)
    agent = AgentApplication(storage=MemoryStorage(), connection_manager=connections)
    @agent.activity("message")
    async def on_message(context, _state):
        await handle_message(context)
    async def entry(request):
        return await start_agent_process(request, agent, adapter)
    app = web.Application(middlewares=[jwt_authorization_middleware], client_max_size=64 * 1024)
    app["agent_configuration"] = config
    app["agent_app"] = agent
    app["adapter"] = adapter
    app.router.add_post("/api/messages", entry)
    return app

if __name__ == "__main__":
    load_dotenv(ROOT / ".env")
    load_dotenv(ROOT / ".env.channel")
    web.run_app(create_app(), host="127.0.0.1", port=3978, access_log=None)
