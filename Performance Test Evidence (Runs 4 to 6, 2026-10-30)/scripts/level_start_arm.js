// NFR-PERF-06: arm a timer on the Easy tier Start button; stop when the Git command input is enabled.
// Also records when the input first appears (disabled or not) and every resource fetched in between.
(() => {
  window.__lvl = null;
  const button = [...document.querySelectorAll('button')].find((b) => /Easy tier: (Start|Resume|Continue)/.test(b.getAttribute('aria-label') || b.textContent));
  if (!button) return 'no easy button';
  button.addEventListener('click', () => {
    const t0 = performance.now();
    const marks = performance.getEntriesByType('resource').length;
    let appeared = null;
    const poll = () => {
      const input = [...document.querySelectorAll('input, textarea')].find((el) =>
        /command/i.test((el.getAttribute('aria-label') || '') + (el.getAttribute('placeholder') || '') + (el.name || '')) && el.offsetParent);
      if (input && appeared === null) appeared = Math.round(performance.now() - t0);
      if (input && !input.disabled) {
        const res = performance.getEntriesByType('resource').slice(marks)
          .map((r) => ({ url: r.name.replace(location.origin, '').slice(0, 80), start: Math.round(r.startTime - t0), ms: Math.round(r.duration) }));
        window.__lvl = { ms: Math.round(performance.now() - t0), appeared, res };
      } else if (performance.now() - t0 < 30000) requestAnimationFrame(poll);
      else window.__lvl = { timeout: true, appeared };
    };
    requestAnimationFrame(poll);
  }, { capture: true, once: true });
  return 'armed';
})();
