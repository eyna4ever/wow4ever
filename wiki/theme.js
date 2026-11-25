/* v22: « Style WoW Forever » is the only look (Mathieu, 04/11/2026): no theme switcher any more.
   Loaded as a classic script in <head> (CSP script-src 'self'): keeps data-theme="wow" and clears the old v20/v21 choice
   (localStorage key 'wk-theme'), so everyone gets the WoW Forever theme. No cookie, no server call, no tracking. */
(function () {
  document.documentElement.setAttribute('data-theme', 'wow');
  try { localStorage.removeItem('wk-theme'); } catch (e) {}
})();
