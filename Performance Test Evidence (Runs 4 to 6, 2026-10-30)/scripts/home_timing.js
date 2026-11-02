(() => {
  const nav = performance.getEntriesByType('navigation')[0];
  const res = performance.getEntriesByType('resource');
  const api = res.filter(r => r.name.includes('/api/')).map(r => ({
    path: new URL(r.name).pathname, start: Math.round(r.startTime), end: Math.round(r.responseEnd), ms: Math.round(r.duration)}));
  const bytes = res.reduce((s, r) => s + (r.transferSize || 0), 0) + (nav.transferSize || 0);
  const lcp = performance.getEntriesByType('largest-contentful-paint').slice(-1)[0];
  const ready = window.__homeReady || null;
  return JSON.stringify({dcl: Math.round(nav.domContentLoadedEventEnd), load: Math.round(nav.loadEventEnd),
    apiDone: Math.max(0, ...api.map(a => a.end)), bytes, ready, api});
})()
