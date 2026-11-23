import asyncio
import importlib.util
from types import SimpleNamespace
import pytest
from aiohttp.test_utils import TestClient, TestServer
from agent_framework import BaseChatClient, ChatResponse, Message, Content, FunctionInvocationLayer


def test_candidate_exists():
    assert importlib.util.find_spec("expense_agent") is not None, "Reusable Lab07 expense module missing"

class MockFoundry(FunctionInvocationLayer, BaseChatClient):
    """Network-free model boundary; the real Agent executes the real tool."""
    def __init__(self, label="synthetic", fail=False):
        super().__init__()
        self.label, self.fail, self.calls = label, fail, []
    async def _inner_get_response(self, *, messages, stream, options, **kwargs):
        self.calls.append(messages)
        if self.fail:
            raise RuntimeError("SECRET must never appear in channel")
        if len(self.calls) == 1:
            return ChatResponse(messages=[Message("assistant", [Content.from_function_call(
                "call1", "submit_claim", arguments={"to": "expenses@contoso.com", "subject": "Expense Claim", "body": self.label})])])
        return ChatResponse(messages=[Message("assistant", ["Draft processed."])])

@pytest.mark.asyncio
async def test_real_agent_tool_and_output():
    from expense_agent import process_expenses_data
    client = MockFoundry()
    reply = await process_expenses_data("Submit an expense claim", "taxi,24.00", client=client)
    assert "SIMULATED" in reply and "No email was sent" in reply and "synthetic" in reply
    assert len(client.calls) == 2
    assert "taxi,24.00" in " ".join(m.text for m in client.calls[0])

@pytest.mark.asyncio
async def test_parallel_turns_do_not_share_tool_output():
    from expense_agent import process_expenses_data
    a,b = await asyncio.gather(process_expenses_data("submit", "a", client=MockFoundry("AAA")), process_expenses_data("submit", "b", client=MockFoundry("BBB")))
    assert "AAA" in a and "BBB" not in a
    assert "BBB" in b and "AAA" not in b

@pytest.mark.asyncio
async def test_handler_commands_input_errors_and_separation():
    from host import handle_message
    seen=[]
    async def invoke(prompt, data):
        seen.append((prompt,data))
        if prompt == "fail": raise RuntimeError("SECRET")
        return "SIMULATED result " + prompt
    class Context:
        def __init__(self,text,cid):
            self.activity=SimpleNamespace(text=text,conversation=SimpleNamespace(id=cid))
            self.sent=[]
        async def send_activity(self,text): self.sent.append(text)
    for text in ["/help", "/about", "", "   "]:
        c=Context(text,"one"); await handle_message(c,invoke=invoke); assert c.sent and not seen
    a,b=Context("first","one"),Context("second","two")
    await asyncio.gather(handle_message(a,invoke=invoke),handle_message(b,invoke=invoke))
    assert a.sent == ["SIMULATED result first"] and b.sent == ["SIMULATED result second"]
    c=Context("fail","one"); await handle_message(c,invoke=invoke)
    assert "SECRET" not in c.sent[0] and "unavailable" in c.sent[0]

CONFIG={"BOT_ID":"11111111-1111-4111-8111-111111111111", "BOT_TENANT_ID":"22222222-2222-4222-8222-222222222222", "BOT_PASSWORD":"synthetic-test-only-not-a-credential"}

def test_missing_configuration_refused():
    from host import create_app
    with pytest.raises(ValueError): create_app({})
    with pytest.raises(ValueError): create_app({**CONFIG,"BOT_ID":"not-a-guid"})

@pytest.mark.asyncio
@pytest.mark.parametrize("header", [None,"Basic abc","Bearer", "Bearer not-a-jwt", "Bearer x y"])
async def test_real_sdk_http_rejects_unauthenticated(header):
    from host import create_app
    async with TestClient(TestServer(create_app(CONFIG))) as client:
        headers={} if header is None else {"Authorization":header}
        r=await client.post("/api/messages",json={"type":"message","text":"/help"},headers=headers)
        assert r.status == 401

@pytest.mark.asyncio
async def test_real_cloud_adapter_routes_to_expense_agent(monkeypatch):
    # Synthetic prevalidated identity + mocked connector, NOT live authentication.
    from unittest.mock import AsyncMock, MagicMock
    from microsoft_agents.activity import Activity, ResourceResponse
    from microsoft_agents.hosting.core import ClaimsIdentity
    import host
    from expense_agent import process_expenses_data
    app=host.create_app(CONFIG)
    adapter=app["adapter"]
    user_client=MagicMock(); user_client.close=AsyncMock()
    connector=MagicMock(); connector.close=AsyncMock()
    factory=adapter._channel_service_client_factory
    monkeypatch.setattr(factory,"create_user_token_client",AsyncMock(return_value=user_client))
    monkeypatch.setattr(factory,"create_connector_client",AsyncMock(return_value=connector))
    sent=[]
    async def send(context, activities):
        sent.extend(a.text for a in activities)
        return [ResourceResponse(id="synthetic") for a in activities]
    monkeypatch.setattr(adapter,"send_activities",send)
    original=host.handle_message
    async def invoke(prompt,data):
        return await process_expenses_data(prompt,data,client=MockFoundry("adapter-receipt"))
    async def routed(context): await original(context,invoke=invoke)
    monkeypatch.setattr(host,"handle_message",routed)
    activity=Activity(type="message",id="test",text="Submit an expense claim",channel_id="msteams",
        service_url="https://example.invalid",conversation={"id":"test-conversation"},
        from_property={"id":"synthetic-user"},recipient={"id":CONFIG["BOT_ID"]})
    identity=ClaimsIdentity({"aud":CONFIG["BOT_ID"],"iss":"https://api.botframework.com"},"synthetic-test")
    await adapter.process_activity(identity,activity,app["agent_app"].on_turn)
    assert any("adapter-receipt" in text and "SIMULATED" in text for text in sent)

@pytest.mark.asyncio
async def test_model_error_propagates_to_handler_boundary():
    from expense_agent import process_expenses_data
    with pytest.raises(RuntimeError):
        await process_expenses_data("submit","synthetic",client=MockFoundry(fail=True))

