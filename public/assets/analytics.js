/* p.b.q public-site measurement. No names, form values, or LINE identifiers. */
(() => {
  'use strict';
  const script = document.currentScript;
  const id = script?.dataset.measurementId || '';
  const site = script?.dataset.pbqSite || '';
  const domains = ['pbq-fukuoka-20261022.s-taguchi323.chatgpt.site', 'spseishirotaguchi-sudo.github.io'];
  const allowed = domains.includes(location.hostname) &&
    (location.hostname !== domains[1] || location.pathname.startsWith('/pbq-lp/'));
  if (!/^G-[A-Z0-9]+$/.test(id) || !['hp', 'lp'].includes(site) || !allowed || window.__pbqAnalyticsInitialized) return;
  window.__pbqAnalyticsInitialized = true;

  const preferenceKey = 'pbq.analytics.disabled';
  let disabled = navigator.globalPrivacyControl === true;
  try { disabled ||= localStorage.getItem(preferenceKey) === '1'; } catch (_) { /* Storage may be unavailable. */ }
  window['ga-disable-' + id] = disabled;
  let started = false;
  const sentDepths = new Set();
  const marketingKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'utm_id'];
  const safeUrl = (value, keepMarketing = false) => {
    try {
      const url = new URL(value);
      const clean = new URL(url.origin + url.pathname);
      if (keepMarketing) marketingKeys.forEach(key => {
        const value = url.searchParams.get(key);
        if (value && /^[A-Za-z0-9_.~-]{1,120}$/.test(value)) clean.searchParams.set(key, value);
      });
      return clean.href;
    } catch (_) { return ''; }
  };
  const pageLocation = safeUrl(location.href, true);
  const pageReferrer = safeUrl(document.referrer);
  const pageName = location.pathname.replace(/\/index\.html$/, '/');
  const event = (name, parameters = {}) => {
    if (!started || disabled) return;
    window.gtag('event', name, {content_group: site, page_location: pageLocation, page_path: pageName, ...parameters});
  };
  const start = () => {
    if (started || disabled) return;
    started = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied'
    });
    window.gtag('set', 'ads_data_redaction', true);
    window.gtag('set', 'linker', {domains, accept_incoming: true});
    window.gtag('js', new Date());
    window.gtag('config', id, {
      content_group: site,
      page_location: pageLocation,
      page_referrer: pageReferrer,
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      cookie_flags: 'SameSite=Lax;Secure'
    });
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(tag);
  };

  const controls = [...document.querySelectorAll('[data-analytics-toggle]')];
  const renderPreference = () => {
    controls.forEach(button => {
      button.textContent = disabled ? 'アクセス解析を有効にする' : 'アクセス解析を停止する';
      button.setAttribute('aria-pressed', String(disabled));
      button.disabled = navigator.globalPrivacyControl === true;
    });
    document.querySelectorAll('[data-analytics-status]').forEach(status => {
      status.textContent = navigator.globalPrivacyControl === true ? 'ブラウザのプライバシー設定により、アクセス解析は停止しています。' :
        disabled ? 'このブラウザでの今後のアクセス解析は停止しています。' : 'このブラウザではアクセス解析が有効です。';
    });
  };
  controls.forEach(button => button.addEventListener('click', () => {
    disabled = !disabled;
    window['ga-disable-' + id] = disabled;
    try { localStorage.setItem(preferenceKey, disabled ? '1' : '0'); } catch (_) { /* Current page still respects the choice. */ }
    renderPreference();
    if (!disabled) start();
  }));
  renderPreference();
  start();

  const position = anchor => {
    if (anchor.closest('.mobile-cta')) return 'mobile_fixed';
    if (anchor.closest('dialog')) return 'menu';
    if (anchor.closest('header')) return 'header';
    if (anchor.closest('footer')) return 'footer';
    if (anchor.closest('.hero, .hero-sequence, .hero-stage')) return 'hero';
    if (anchor.closest('.final-section, .entry-section')) return 'final';
    if (anchor.closest('.join-section, #process, #join')) return 'join';
    return 'content';
  };
  document.addEventListener('click', e => {
    const anchor = e.target.closest?.('a[href]');
    if (!anchor) return;
    let url;
    try { url = new URL(anchor.href, location.href); } catch (_) { return; }
    const params = {button_position: position(anchor)};
    if (['lin.ee', 'line.me', 'liff.line.me'].includes(url.hostname)) {
      event(/問い合わせ/.test(anchor.textContent || '') ? 'line_contact_click' : 'line_click', params);
    } else if (['instagram.com', 'www.instagram.com'].includes(url.hostname)) {
      event('instagram_click', params);
    }
    // Measurement never delays, cancels, or rewrites the visitor's navigation.
  }, {capture: true});

  let scrollPending = false;
  const measureDepth = () => {
    scrollPending = false;
    const height = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);
    if (height <= innerHeight + 1 || window.scrollY <= 0 || disabled) return;
    const percent = Math.min(100, 100 * (window.scrollY + innerHeight) / height);
    [25, 50, 75, 90].forEach(depth => {
      if (percent >= depth && !sentDepths.has(depth)) {
        sentDepths.add(depth);
        event('content_progress', {percent_scrolled: depth});
      }
    });
  };
  addEventListener('scroll', () => {
    if (!scrollPending) { scrollPending = true; requestAnimationFrame(measureDepth); }
  }, {passive: true});
  const questions = [...document.querySelectorAll('.faq-list details')];
  questions.forEach((question, index) => question.addEventListener('toggle', () => {
    if (question.open) event('faq_open', {faq_index: index + 1});
  }));
})();
