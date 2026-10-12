/* Local language preference only. No analytics, cookies or third-party scripts. */
(function () {
  'use strict';
  const supported = ['ko', 'ja', 'zh-CN', 'zh-TW', 'en'];
  function normalize(value) {
    const lang = String(value || '').toLowerCase().replace(/_/g, '-');
    if (/^zh-(hant|tw|hk|mo)(-|$)/.test(lang)) return 'zh-TW';
    if (/^zh(-|$)/.test(lang)) return 'zh-CN';
    if (/^ko(-|$)/.test(lang)) return 'ko';
    if (/^ja(-|$)/.test(lang)) return 'ja';
    if (/^en(-|$)/.test(lang)) return 'en';
    return null;
  }
  function destination(locale, page, search, hash) {
    const params = new URLSearchParams(search);
    params.delete('lang');
    const query = params.toString();
    return '/' + locale + '/' + (page ? page + '/' : '') + (query ? '?' + query : '') + hash;
  }
  const root = document.documentElement.dataset;
  const page = ['', 'privacy', 'terms'].includes(root.page) ? root.page : '';
  const explicit = normalize(new URLSearchParams(location.search).get('lang'));
  let saved = null;
  try { saved = normalize(localStorage.getItem('kokoroom.language')); } catch (_) { /* Private mode still supports links. */ }
  if (root.generic === 'true' || explicit) {
    const browser = (navigator.languages || [navigator.language]).map(normalize).find(Boolean);
    const language = explicit || saved || browser || 'en';
    location.replace(destination(language, page, location.search, location.hash));
    return;
  }
  document.querySelectorAll('[data-language]').forEach(function (link) {
    const language = link.dataset.language;
    if (!supported.includes(language)) return;
    // Keep the reader at the same section when switching languages, including without clicking with a mouse.
    function updateHref() { link.href = destination(language, page, location.search, location.hash); }
    updateHref();
    window.addEventListener('hashchange', updateHref);
    link.addEventListener('click', function () {
      try { localStorage.setItem('kokoroom.language', language); } catch (_) { /* Navigation must still work. */ }
    });
  });
}());
