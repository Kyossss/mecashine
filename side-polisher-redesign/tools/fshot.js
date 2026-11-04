// usage: node fshot.js out.png [direction]  -> screenshot of the Fusion view through the local connector, saved as PNG
const fs = require('fs'); const URL_ = 'http://127.0.0.1:27182/mcp';
const H = { 'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream' };
(async () => {
  const init = await fetch(URL_, { method: 'POST', headers: H, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-03-26', capabilities: {}, clientInfo: { name: 'claude-code', version: '1' } } }) });
  const sid = init.headers.get('mcp-session-id'); await init.text(); const HS = Object.assign({ 'Mcp-Session-Id': sid }, H);
  await fetch(URL_, { method: 'POST', headers: HS, body: JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) }).then(r => r.text());
  const args = { queryType: 'screenshot', width: 1200, height: 800, transparentBackground: false, direction: process.argv[3] || 'current' };
  const r = await fetch(URL_, { method: 'POST', headers: HS, body: JSON.stringify({ jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: 'fusion_mcp_read', arguments: args } }) });
  const j = JSON.parse(await r.text()); const c = (j.result && j.result.content) || [];
  for (const x of c) { if (x.type === 'image') { fs.writeFileSync(process.argv[2], Buffer.from(x.data, 'base64')); console.log('saved', process.argv[2]); return; } }
  console.log(JSON.stringify(j).slice(0, 500));
})();
