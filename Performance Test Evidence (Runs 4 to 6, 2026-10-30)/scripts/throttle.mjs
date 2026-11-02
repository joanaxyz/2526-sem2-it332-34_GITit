// Hold a 10 Mbps connection on the agent-browser page until this process is killed (NFR-PERF-03/06).
// Usage: node throttle.mjs <cdp-url from `agent-browser get cdp-url`> [mbps] [latency ms] [clear]
// Network emulation lives on the CDP session, so the process must stay alive while timing.
// "clear" empties the browser's HTTP cache first, for a learner's first visit.
const [cdpUrl, mbps = '10', latency = '40', clear = ''] = process.argv.slice(2)
const http = cdpUrl.replace(/^ws/, 'http').replace(/\/devtools\/browser\/.*$/, '')
const targets = await (await fetch(`${http}/json`)).json()
const page = targets.find((t) => t.type === 'page' && t.url.startsWith('https://git-it-34.vercel.app'))
if (!page) throw new Error('no git-it page target')
const ws = new WebSocket(page.webSocketDebuggerUrl)
let id = 0
const send = (method, params = {}) => ws.send(JSON.stringify({ id: ++id, method, params }))
ws.onopen = () => {
  send('Network.enable')
  if (clear === 'clear') send('Network.clearBrowserCache')
  const bytesPerSecond = (Number(mbps) * 1e6) / 8
  send('Network.emulateNetworkConditions', {
    offline: false,
    latency: Number(latency),
    downloadThroughput: bytesPerSecond,
    uploadThroughput: bytesPerSecond / 2,
  })
  console.log(`throttling ${page.url} to ${mbps} Mbps, ${latency} ms`)
}
ws.onmessage = (event) => {
  const message = JSON.parse(event.data)
  if (message.error) console.error(message.error)
}
setInterval(() => {}, 1 << 30)
