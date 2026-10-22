(() => {
  'use strict';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const mobile = window.matchMedia('(max-width: 700px)');
  const header = document.querySelector('.site-header');
  const sequence = document.querySelector('.hero-sequence');
  const heroVideo = document.querySelector('.hero-video');
  const pause = document.querySelector('.hero-pause');
  let manualPause = false;
  let scrollQueued = false;
  let refreshOrbits = () => {};
  const updateScroll = () => {
    scrollQueued = false;
    if (sequence) {
      const rect = sequence.getBoundingClientRect();
      const progress = reduced.matches ? 0 : Math.max(0, Math.min(1, -rect.top / Math.max(1, rect.height - innerHeight)));
      sequence.style.setProperty('--hero-progress', progress.toFixed(4));
      header?.classList.toggle('is-scrolled', window.scrollY > 130);
      if (heroVideo) {
        const shouldPlay = !manualPause && !reduced.matches && !document.hidden && rect.bottom > 0 && progress < 0.8;
        if (shouldPlay && heroVideo.paused) heroVideo.play().catch(() => {});
        else if (!shouldPlay && !heroVideo.paused) heroVideo.pause();
      }
    }
    refreshOrbits();
  };
  addEventListener('scroll', () => { if (!scrollQueued) { scrollQueued = true; requestAnimationFrame(updateScroll); } }, { passive: true });
  addEventListener('resize', updateScroll, { passive: true });
  document.addEventListener('visibilitychange', updateScroll);
  reduced.addEventListener('change', updateScroll);
  updateScroll();
  pause?.addEventListener('click', () => {
    manualPause = !manualPause;
    pause.textContent = manualPause ? '▶' : 'Ⅱ';
    pause.setAttribute('aria-label', manualPause ? '背景動画を再生' : '背景動画を一時停止');
    updateScroll();
  });

  const menu = document.getElementById('menu-dialog');
  let lastFocus = null;
  const prepareNav = () => document.querySelectorAll('.nav-group').forEach(group => { group.open = !mobile.matches; });
  prepareNav();
  mobile.addEventListener('change', prepareNav);
  document.querySelector('.menu-toggle')?.addEventListener('click', () => {
    lastFocus = document.activeElement;
    menu.showModal();
    menu.querySelector('[data-close]').focus();
  });
  document.querySelectorAll('dialog [data-close]').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
  document.querySelectorAll('dialog').forEach(dialog => {
    dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
    dialog.addEventListener('close', () => { if (lastFocus?.isConnected) lastFocus.focus({ preventScroll: true }); });
  });
  menu?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => menu.close()));

  const valueArticles = [...document.querySelectorAll('[data-value]')];
  if (valueArticles.length) {
    const setOrbit = index => document.querySelectorAll('[data-orbit]').forEach(orbit => {
      const active = orbit.dataset.orbit === index;
      orbit.classList.toggle('is-active', active);
      if (active) orbit.setAttribute('aria-current', 'location'); else orbit.removeAttribute('aria-current');
    });
    refreshOrbits = () => {
      let current = valueArticles[0];
      for (const article of valueArticles) {
        if (article.getBoundingClientRect().top <= innerHeight * 0.5) current = article;
      }
      setOrbit(current.dataset.value);
    };
    refreshOrbits();
  }

  const track = document.getElementById('moment-track');
  document.querySelectorAll('[data-slide]').forEach(button => button.addEventListener('click', () => {
    const item = track?.querySelector('.photo-card');
    if (item) track.scrollBy({ left: (item.getBoundingClientRect().width + 22) * Number(button.dataset.slide), behavior: reduced.matches ? 'instant' : 'smooth' });
  }));

  const setJapaneseText = (element,text,groups) => {
    if(!Array.isArray(groups)||groups.flat().join('')!==text){element.textContent=text;return;}
    element.classList.add('ja-typeset');
    element.replaceChildren(...groups.map(words=>{
      const phrase=document.createElement('pbq-phrase');
      words.forEach((word,i)=>{if(i)phrase.append(document.createElement('wbr'));phrase.append(document.createTextNode(word));});
      return phrase;
    }));
  };
  const photos = JSON.parse(document.getElementById('gallery-data')?.textContent || '[]');
  const photoDialog = document.getElementById('photo-dialog');
  let photoIndex = 0;
  const renderPhoto = index => {
    photoIndex = (index + photos.length) % photos.length;
    const [file, title, caption, width, height, phrases] = photos[photoIndex];
    const img = document.getElementById('lightbox-image');
    img.src = `assets/${file}`; img.alt = title; img.width = width; img.height = height;
    setJapaneseText(document.getElementById('lightbox-title'),title,phrases?.title);
    setJapaneseText(document.getElementById('lightbox-caption'),caption,phrases?.caption);
    document.getElementById('photo-count').textContent = `${String(photoIndex + 1).padStart(2, '0')} / ${String(photos.length).padStart(2, '0')}`;
  };
  document.querySelectorAll('[data-photo]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault(); lastFocus = event.currentTarget; renderPhoto(Number(link.dataset.photo)); photoDialog.showModal(); photoDialog.querySelector('[data-close]').focus();
  }));
  document.getElementById('photo-prev')?.addEventListener('click', () => renderPhoto(photoIndex - 1));
  document.getElementById('photo-next')?.addEventListener('click', () => renderPhoto(photoIndex + 1));
  photoDialog?.addEventListener('keydown', event => { if (event.key === 'ArrowLeft') { event.preventDefault(); renderPhoto(photoIndex - 1); } if (event.key === 'ArrowRight') { event.preventDefault(); renderPhoto(photoIndex + 1); } });
  let touchX = 0;
  photoDialog?.addEventListener('touchstart', event => { touchX = event.changedTouches[0].clientX; }, { passive: true });
  photoDialog?.addEventListener('touchend', event => { const delta = event.changedTouches[0].clientX - touchX; if (Math.abs(delta) > 55) renderPhoto(photoIndex + (delta < 0 ? 1 : -1)); }, { passive: true });

  const feed = document.getElementById('instagram-feed');
  const feedStatus = document.getElementById('instagram-feed-status');
  let lastFeedFetch = 0;
  const loadInstagram = async () => {
    if (!feed || Date.now() - lastFeedFetch < 15 * 60 * 1000) return;
    lastFeedFetch = Date.now();
    try {
      const response = await fetch('/api/instagram', {signal:AbortSignal.timeout(26000)});
      if (!response.ok) throw new Error('unavailable');
      const data = await response.json();
      if (!data.posts?.length) throw new Error('not_connected');
      feed.replaceChildren();
      for (const post of data.posts.slice(0,3)) {
        const link = document.createElement('a');
        link.className = 'instagram-post';
        const url = new URL(post.permalink);
        if (!/^(www\.)?instagram\.com$/.test(url.hostname) || url.protocol !== 'https:') continue;
        link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer';
        link.addEventListener('click', event => {
          if(event.ctrlKey || event.metaKey || event.shiftKey) return;
          event.preventDefault();
          const modal=document.getElementById('instagram-dialog');
          modal.querySelector('iframe').src=url.origin+url.pathname.replace(/\/$/,'')+'/embed/';
          modal.querySelector('.instagram-dialog-link').href=url.href;
          modal.showModal();
        });
        const media = document.createElement('div'); media.className = 'instagram-post-image';
        const img = document.createElement('img'); img.src = post.image; img.alt = (post.caption || 'p.b.qのInstagram投稿').slice(0,100); img.width = 600; img.height = 750; img.loading = 'lazy';
        img.addEventListener('error', () => { img.hidden = true; media.classList.add('has-no-image'); });
        const badge = document.createElement('span'); badge.className = 'instagram-post-type'; badge.textContent = post.type === 'VIDEO' ? 'REEL' : post.type === 'CAROUSEL_ALBUM' ? 'PHOTOS' : 'PHOTO';
        media.append(img,badge);
        if(post.type==='VIDEO') { const play=document.createElement('span'); play.className='instagram-play';play.setAttribute('aria-hidden','true');play.textContent='▶';media.append(play); }
        const details = document.createElement('div'); details.className = 'instagram-post-body';
        const date = document.createElement('time'); date.dateTime = post.timestamp; date.textContent = new Intl.DateTimeFormat('ja-JP',{year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(post.timestamp));
        const caption = document.createElement('p'); caption.className = 'instagram-post-caption'; setJapaneseText(caption,post.caption || 'p.b.qの投稿を見る',post.captionParts);
        const cta = document.createElement('span'); cta.className = 'instagram-post-cta'; cta.textContent = 'Instagramで見る';
        details.append(date,caption,cta); link.append(media,details); feed.append(link);
      }
      feedStatus.textContent = data.status === 'cached' ? 'Instagramの投稿から' : 'Instagramの最新投稿と連携中';
    } catch {
      feed.replaceChildren();
      const fallback = document.createElement('p'); fallback.className = 'instagram-unavailable'; fallback.textContent = 'p.b.qの投稿は、下のボタンからInstagramでご覧いただけます。'; feed.append(fallback);
      feedStatus.textContent = '';
    } finally { feed.setAttribute('aria-busy','false'); }
  };
  if (feed) new IntersectionObserver((entries,observer) => { if (entries.some(e=>e.isIntersecting)) { loadInstagram(); observer.disconnect(); } },{rootMargin:'700px'}).observe(feed);
  document.addEventListener('visibilitychange', () => { if (!document.hidden && feed && lastFeedFetch) loadInstagram(); });

  document.getElementById('instagram-dialog')?.addEventListener('close',event=>event.target.querySelector('iframe').removeAttribute('src'));

})();
