/* Franks & Buns: analytics consent.
 * Google Analytics is NOT loaded until the player taps "Allow".
 * The choice is saved on this device (fb_consent = granted | denied) and can be
 * changed at any time with fbPrivacyChoices() (the "Privacy choices" links).
 * Used by the website and, bundled as a local file, by the iPhone and Android apps. */
(function () {
  'use strict';
  var GA_ID = 'G-5PVW85JQP6';
  var KEY = 'fb_consent';
  var CID_KEY = 'fb_ga_cid';
  var loaded = false;

  function store(k, v) {
    try { if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) {}
  }
  function read(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  function appPlatform() {
    var C = window.Capacitor;
    try {
      if (C && C.isNativePlatform && C.isNativePlatform()) return (C.getPlatform && C.getPlatform()) || 'app';
    } catch (e) {}
    return null;
  }

  function loadAnalytics() {
    if (loaded) return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied'
    });
    window.gtag('js', new Date());
    var cfg = {};
    var platform = appPlatform();
    if (platform) {
      // In the apps the page is served from inside the app, where cookies are not kept.
      // Keep a random ID on the device instead and label visits as app visits.
      var cid = read(CID_KEY);
      if (!cid) { cid = Math.floor(Math.random() * 2147483647) + '.' + Math.floor(Date.now() / 1000); store(CID_KEY, cid); }
      cfg.client_storage = 'none';
      cfg.client_id = cid;
      cfg.page_location = 'https://franksandbuns.com/app-' + platform + '/';
      cfg.page_title = 'Franks and Buns app (' + platform + ')';
    }
    window.gtag('config', GA_ID, cfg);
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
  }

  function clearAnalyticsCookies() {
    var host = location.hostname, parts = host.split('.');
    var domains = ['', host, '.' + host];
    if (parts.length > 2) domains.push('.' + parts.slice(-2).join('.'));
    document.cookie.split(';').forEach(function (c) {
      var name = c.split('=')[0].trim();
      if (name === '_ga' || name.indexOf('_ga_') === 0 || name === '_gid') {
        domains.forEach(function (d) {
          document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + (d ? '; domain=' + d : '');
        });
      }
    });
  }

  function decide(granted) {
    store(KEY, granted ? 'granted' : 'denied');
    hideBanner();
    if (granted) {
      loadAnalytics();
    } else {
      if (loaded && window.gtag) window.gtag('consent', 'update', { analytics_storage: 'denied' });
      window['ga-disable-' + GA_ID] = true;
      store(CID_KEY, null);
      clearAnalyticsCookies();
    }
  }

  var banner = null;
  function hideBanner() { if (banner && banner.parentNode) banner.parentNode.removeChild(banner); banner = null; }

  function showBanner() {
    if (banner) return;
    var policy = appPlatform() ? 'https://franksandbuns.com/privacy.html' : 'privacy.html';
    banner = document.createElement('div');
    banner.id = 'fb-consent';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', 'Analytics choice');
    banner.innerHTML =
      '<p>Can we count plays with Google Analytics to help improve the game? It stays off unless you allow it. ' +
      '<a href="' + policy + '" target="_blank" rel="noopener">Privacy Policy</a></p>' +
      '<div class="fbc-btns"><button type="button" class="fbc-no">No thanks</button>' +
      '<button type="button" class="fbc-yes">Allow</button></div>';
    var css = document.createElement('style');
    css.textContent =
      '#fb-consent{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(12px + env(safe-area-inset-bottom));' +
      'width:min(560px,calc(100% - 24px));box-sizing:border-box;z-index:2147483000;background:#1d0f02;color:#f3e3c3;' +
      'border:1px solid #ff6600;border-radius:14px;padding:12px 14px;font:14px/1.4 -apple-system,Segoe UI,Roboto,Arial,sans-serif;' +
      'box-shadow:0 6px 24px rgba(0,0,0,.5)}' +
      '#fb-consent p{margin:0 0 10px}#fb-consent a{color:#ffb347}' +
      '#fb-consent .fbc-btns{display:flex;gap:10px;justify-content:flex-end}' +
      '#fb-consent button{font:600 14px/1 inherit;font-family:inherit;border-radius:999px;padding:10px 18px;cursor:pointer;border:1px solid #ff6600}' +
      '#fb-consent .fbc-no{background:transparent;color:#f3e3c3}#fb-consent .fbc-yes{background:#ff6600;color:#fff}';
    banner.appendChild(css);
    ['touchstart', 'touchend', 'mousedown', 'pointerdown'].forEach(function (t) {
      banner.addEventListener(t, function (e) { e.stopPropagation(); }, { passive: true });
    });
    banner.querySelector('.fbc-yes').addEventListener('click', function () { decide(true); });
    banner.querySelector('.fbc-no').addEventListener('click', function () { decide(false); });
    (document.body || document.documentElement).appendChild(banner);
  }

  // "Privacy choices" link: show the choice again (to allow or withdraw).
  window.fbPrivacyChoices = function () { hideBanner(); showBanner(); return false; };

  var choice = read(KEY);
  if (choice === 'granted') loadAnalytics();
  else if (choice !== 'denied') {
    if (document.body) showBanner();
    else document.addEventListener('DOMContentLoaded', showBanner);
  }
})();
