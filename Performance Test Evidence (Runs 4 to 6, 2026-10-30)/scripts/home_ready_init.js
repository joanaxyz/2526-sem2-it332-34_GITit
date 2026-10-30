(() => {
  const check = () => {
    if (window.__homeReady) return true;
    const profile = document.querySelector('[aria-label^="Open account menu for"]');
    const map = document.querySelector('[aria-label$="chapter map"] button[aria-label^="Level 1"]');
    if (profile && map) { window.__homeReady = Math.round(performance.now()); return true; }
    return false;
  };
  const start = () => {
    if (check()) return;
    const obs = new MutationObserver(() => { if (check()) obs.disconnect(); });
    obs.observe(document.documentElement, { childList: true, subtree: true, attributes: true });
  };
  if (document.documentElement) start(); else document.addEventListener('DOMContentLoaded', start);
})();
