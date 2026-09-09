// This runs before the module graph, so even a failed module import is visible.
(function () {
  function report(message) {
    var target = document.getElementById('startup-message');
    if (target) target.textContent = message;
  }
  window.addEventListener('error', function () {
    report('Rooted could not load. Please reload the page to try again.');
  });
  window.addEventListener('unhandledrejection', function () {
    report('Rooted could not load. Please reload the page to try again.');
  });
  window.setTimeout(function () {
    var target = document.getElementById('startup-message');
    if (target && target.textContent === 'Loading your reading tracker…') {
      report('Rooted is taking too long to load. Please reload this page. If this continues, share this page address and message with your administrator.');
    }
  }, 10000);
})();
