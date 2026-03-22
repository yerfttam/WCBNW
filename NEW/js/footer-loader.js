/**
 * footer-loader.js
 * Fetches partials/footer.html and injects it into #site-footer-placeholder.
 * Same pattern as nav-loader.js.
 */
(function () {
  const placeholder = document.getElementById('site-footer-placeholder');
  if (!placeholder) return;

  fetch('partials/footer.html')
    .then(r => r.text())
    .then(html => { placeholder.outerHTML = html; })
    .catch(err => console.warn('Footer failed to load:', err));
})();
