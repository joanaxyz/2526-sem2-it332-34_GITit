// NFR-PERF-02: time from the real Enter keydown in the terminal to the submitted command's
// line and output being painted in the terminal (browser simulation, before the server
// confirms). The automation presses the keys; this listener timestamps them.
// Samples accumulate in window.__perfSamples (ms).
(() => {
  const input = document.querySelector('[aria-label="Git command"]');
  if (!input) return 'terminal input not found';
  const terminal = input.closest('[role="region"]') || document.body;
  const occurrences = (text, needle) => text.split(needle).length - 1;
  window.__perfSamples = [];
  input.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter') return;
    const command = input.value.trim();
    if (!command) return;
    const t0 = event.timeStamp;
    const before = occurrences(terminal.innerText, command);
    const done = () => requestAnimationFrame(() => {
      window.__perfSamples.push(Math.round((performance.now() - t0) * 10) / 10);
    });
    const obs = new MutationObserver(() => {
      if (occurrences(terminal.innerText, command) > before) { obs.disconnect(); done(); }
    });
    obs.observe(terminal, { childList: true, subtree: true, characterData: true });
    setTimeout(() => obs.disconnect(), 5000);
  }, { capture: true });
  return 'listening';
})()
