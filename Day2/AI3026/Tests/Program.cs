using Day2;
using System.Net;
using System.Text.Json;
var tests = new List<(string, Func<Task>)>();
void Check(string name, Action test) => tests.Add((name, () => { test(); return Task.CompletedTask; }));
void Equal<T>(T expected, T actual) { if (!Equals(expected, actual)) throw new Exception($"Expected {expected}; got {actual}"); }
void Throws<T>(Action test) where T : Exception { try { test(); } catch(T) { return; } throw new Exception($"Expected {typeof(T).Name}"); }
const string endpoint = "https://example.services.ai.azure.com/api/projects/training";
// Synthetic fixtures ONLY: these are not Azure outputs or proof of live grounding.
const string fixture = """{"status":"completed","output":[{"type":"file_search_call"},{"type":"message","content":[{"type":"output_text","text":"Fixture answer","annotations":[{"type":"file_citation","filename":"IT_Policy.txt"}]}]}]}""";
Check("same agent name and pinned version", () => {
 using var doc = JsonDocument.Parse(FoundryGateway.BuildBody("it-support-agent", "3", "Question"));
 var body = doc.RootElement;
 Equal("it-support-agent",body.GetProperty("agent_reference").GetProperty("name").GetString());
 Equal("3",body.GetProperty("agent_reference").GetProperty("version").GetString());
 Equal("agent_reference",body.GetProperty("agent_reference").GetProperty("type").GetString());
 Equal(false,body.GetProperty("store").GetBoolean());
 Equal(false,body.TryGetProperty("model",out _)); // Never silently replace with a bare model.
});
Check("classic ID rejected", () => Throws<ArgumentException>(() => FoundryGateway.BuildBody("asst_123","1","q")));
Check("empty version rejected", () => Throws<ArgumentException>(() => FoundryGateway.BuildBody("agent","","q")));
Check("blank input rejected", () => Throws<ArgumentException>(() => FoundryGateway.BuildBody("agent","1"," ")));
Check("4000 character boundary accepted", () => FoundryGateway.BuildBody("agent","1",new string('x',4000)));
Check("4001 characters rejected", () => Throws<ArgumentException>(() => FoundryGateway.BuildBody("agent","1",new string('x',4001))));
Check("project URL preserved", () => Equal(endpoint+"/openai/v1/responses", FoundryGateway.ResponseEndpoint(endpoint+"/").ToString()));
Check("insecure HTTP rejected", () => Throws<ArgumentException>(() => FoundryGateway.ResponseEndpoint(endpoint.Replace("https:","http:"))));
Check("non-Azure host rejected", () => Throws<ArgumentException>(() => FoundryGateway.ResponseEndpoint("https://attacker.invalid/api/projects/x")));
Check("model endpoint rejected", () => Throws<ArgumentException>(() => FoundryGateway.ResponseEndpoint("https://example.services.ai.azure.com/models")));
Check("query rejected", () => Throws<ArgumentException>(() => FoundryGateway.ResponseEndpoint(endpoint+"?x=1")));
Check("citation filename preserved", () => Equal("Fixture answer\n\nSource files: IT_Policy.txt", FoundryGateway.ReadAnswer(fixture)));
Check("incomplete response rejected", () => Throws<InvalidOperationException>(() => FoundryGateway.ReadAnswer("""{"status":"incomplete","output":[]}""")));
Check("empty answer rejected", () => Throws<InvalidOperationException>(() => FoundryGateway.ReadAnswer("""{"status":"completed","output":[]}""")));
Check("unsupported function is explicit", () => Throws<InvalidOperationException>(() => FoundryGateway.ReadAnswer("""{"status":"completed","output":[{"type":"function_call"}]}""")));
tests.Add(("HTTP contract uses REST response and bearer token",async () => {
 using var http = new HttpClient(new FixtureHandler(async request => {
   Equal(HttpMethod.Post,request.Method);
   Equal(endpoint+"/openai/v1/responses",request.RequestUri!.ToString());
   Equal("Bearer fixture-not-a-real-token",request.Headers.Authorization!.ToString());
   using var body=JsonDocument.Parse(await request.Content!.ReadAsStringAsync());
   Equal("3",body.RootElement.GetProperty("agent_reference").GetProperty("version").GetString());
   return new HttpResponseMessage(HttpStatusCode.OK){Content=new StringContent(fixture)};
 }));
 var answer=await FoundryGateway.AskAsync(http,_=>Task.FromResult("fixture-not-a-real-token"),endpoint,"it-support-agent","3","q");
 Equal(true,answer.Contains("IT_Policy.txt"));
}));
tests.Add(("HTTP failure is not an answer or leaked service body", async () => {
 using var http=new HttpClient(new FixtureHandler(_=>Task.FromResult(new HttpResponseMessage(HttpStatusCode.Forbidden){Content=new StringContent("private-service-body")})));
 try { await FoundryGateway.AskAsync(http,_=>Task.FromResult("fixture"),endpoint,"agent","1","q"); throw new Exception("Expected failure"); }
 catch(HttpRequestException ex) { Equal(HttpStatusCode.Forbidden,ex.StatusCode); Equal(false,ex.Message.Contains("private-service-body")); }
}));
tests.Add(("bad identity rejected before token acquisition",async () => {
 bool tokenRequested=false;
 using var http=new HttpClient(new FixtureHandler(_=>throw new Exception("Unexpected HTTP")));
 try { await FoundryGateway.AskAsync(http,_=> {tokenRequested=true;return Task.FromResult("fixture");},endpoint,"asst_123","1","q");throw new Exception("Expected validation"); }
 catch(ArgumentException) { Equal(false,tokenRequested); }
}));
int failed=0;
foreach(var (name,test) in tests) { try {await test();Console.WriteLine("PASS "+name);} catch(Exception ex){failed++;Console.WriteLine("FAIL "+name+": "+ex.Message);} }
Console.WriteLine($"Offline contract tests: {tests.Count-failed}/{tests.Count} passed. No Azure, Teams, or Copilot calls.");
Environment.ExitCode=failed==0?0:1;
sealed class FixtureHandler(Func<HttpRequestMessage,Task<HttpResponseMessage>> respond):HttpMessageHandler
{
 protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken ct) => respond(request);
}
