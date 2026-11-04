// usage: node fcall.js <tool name> '<json arguments>'   -> calls one tool on the local Fusion connector and prints the result
const URL_ = 'http://127.0.0.1:27182/mcp';
const H = { 'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream' };
(async () => {
  const init = await fetch(URL_, { method: 'POST', headers: H, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-03-26', capabilities: {}, clientInfo: { name: 'claude-code', version: '1' } } }) });
  const sid = init.headers.get('mcp-session-id'); await init.text();
  const HS = Object.assign({ 'Mcp-Session-Id': sid }, H);
  await fetch(URL_, { method: 'POST', headers: HS, body: JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) }).then(r => r.text());
  const r = await fetch(URL_, { method: 'POST', headers: HS, body: JSON.stringify({ jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: process.argv[2], arguments: JSON.parse(process.argv[3]) } }) });
  const j = JSON.parse(await r.text());
  const c = (j.result && j.result.content) || [];
  if (!c.length) console.log(JSON.stringify(j).slice(0, 3000));
  for (const x of c) console.log(x.text !== undefined ? x.text.slice(0, 4000) : JSON.stringify(x).slice(0, 300));
})();
