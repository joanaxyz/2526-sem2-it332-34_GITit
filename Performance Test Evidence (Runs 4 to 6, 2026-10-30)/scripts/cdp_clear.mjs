// One-off: empty the agent-browser page's HTTP cache. Usage: node cdp_clear.mjs <cdp-url>
const http = process.argv[2].replace(/^ws/, 'http').replace(/\/devtools\/browser\/.*$/, '')
const page = (await (await fetch(`${http}/json`)).json()).find((t) => t.type === 'page' && t.url.includes('git-it-34'))
const ws = new WebSocket(page.webSocketDebuggerUrl)
ws.onopen = () => ws.send(JSON.stringify({ id: 1, method: 'Network.clearBrowserCache' }))
ws.onmessage = () => { console.log('cache cleared'); process.exit(0) }
