// usage: node frun.js <script.py> [readOnly]   -> runs a Python script in Fusion through the local connector and prints its output
const fs = require('fs');
const URL_ = 'http://127.0.0.1:27182/mcp';
const H = { 'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream' };
(async () => {
  const init = await fetch(URL_, { method: 'POST', headers: H, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-03-26', capabilities: {}, clientInfo: { name: 'claude-code', version: '1' } } }) });
  const sid = init.headers.get('mcp-session-id'); await init.text();
  const HS = Object.assign({ 'Mcp-Session-Id': sid }, H);
  await fetch(URL_, { method: 'POST', headers: HS, body: JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) }).then(r => r.text());
  const args = { featureType: 'script', object: { script: fs.readFileSync(process.argv[2], 'utf8') } };
  if (process.argv[3] === 'readOnly') args.object.readOnly = true;
  const r = await fetch(URL_, { method: 'POST', headers: HS, body: JSON.stringify({ jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: 'fusion_mcp_execute', arguments: args } }) });
  const j = JSON.parse(await r.text());
  const c = (j.result && j.result.content) || [];
  if (!c.length) console.log(JSON.stringify(j).slice(0, 3000));
  for (const x of c) console.log(x.text !== undefined ? x.text : JSON.stringify(x).slice(0, 500));
})();
