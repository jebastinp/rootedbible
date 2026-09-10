// This runs before the module graph, so even a failed module import is
// visible. A load failure here is almost always a stale service worker or
// cached asset from a previous deploy serving JS that no longer matches
// the current index.html (different chunk hashes) - the fix is simply to
// drop that old cache and reload, so do it automatically once instead of
// leaving the visitor stuck on a dead page.
(function () {
  var RECOVERY_KEY = 'rooted-startup-recovery-attempted'

  function report(message) {
    var target = document.getElementById('startup-message')
    if (target) target.textContent = message
  }

  function attemptRecovery() {
    var alreadyTried = false
    try {
      alreadyTried = sessionStorage.getItem(RECOVERY_KEY) === '1'
    } catch (e) {}

    if (alreadyTried) {
      report('Rooted could not load. Please reload the page to try again.')
      return
    }

    try {
      sessionStorage.setItem(RECOVERY_KEY, '1')
    } catch (e) {}

    report('Rooted is updating, one moment…')

    var cleanupTasks = []
    if ('serviceWorker' in navigator) {
      cleanupTasks.push(
        navigator.serviceWorker.getRegistrations().then(function (regs) {
          return Promise.all(
            regs.map(function (reg) {
              return reg.unregister()
            })
          )
        })
      )
    }
    if ('caches' in window) {
      cleanupTasks.push(
        caches.keys().then(function (keys) {
          return Promise.all(
            keys.map(function (key) {
              return caches.delete(key)
            })
          )
        })
      )
    }

    Promise.all(cleanupTasks)
      .catch(function () {})
      .then(function () {
        window.location.reload()
      })
  }

  window.addEventListener('error', attemptRecovery)
  window.addEventListener('unhandledrejection', attemptRecovery)

  window.setTimeout(function () {
    var target = document.getElementById('startup-message')
    if (target && target.textContent === 'Loading your reading tracker…') {
      report('Rooted is taking too long to load. Please reload this page. If this continues, share this page address and message with your administrator.')
    }
  }, 10000)
})()
