(function () {
  var items = Array.prototype.slice.call(document.querySelectorAll('.pg-item'));
  var buttons = Array.prototype.slice.call(document.querySelectorAll('.pg-filter'));
  if (!items.length) return;

  // ---- tag filter (the selected tag is kept in the URL hash, e.g. /photography/#birds)
  function applyFilter(tag) {
    var known = buttons.some(function (b) { return b.dataset.tag === tag; });
    if (!known) tag = 'all';
    buttons.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.tag === tag ? 'true' : 'false'); });
    items.forEach(function (it) {
      it.hidden = !(tag === 'all' || it.dataset.tags.split(',').indexOf(tag) !== -1);
    });
    return tag;
  }
  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      var t = applyFilter(b.dataset.tag);
      history.replaceState(null, '', t === 'all' ? location.pathname : '#' + encodeURIComponent(t));
    });
  });
  applyFilter(decodeURIComponent(location.hash.slice(1)) || 'all');

  // ---- lightbox: shows the thumbnail instantly, swaps in the full-size photo when it has loaded
  var lb = document.createElement('div');
  lb.className = 'pg-lightbox';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Photo viewer');
  lb.innerHTML =
    '<div class="pg-lb-stage">' +
      '<img alt="">' +
      '<div class="pg-lb-bar" aria-hidden="true"></div>' +
      '<button class="pg-lb-btn pg-lb-close" aria-label="Close">&times;</button>' +
      '<button class="pg-lb-btn pg-lb-prev" aria-label="Previous photo">&#8249;</button>' +
      '<button class="pg-lb-btn pg-lb-next" aria-label="Next photo">&#8250;</button>' +
    '</div>' +
    '<div class="pg-lb-info"><div class="pg-lb-title"></div><div class="pg-lb-meta"></div>' +
      '<a class="pg-lb-dl" download>Download original</a></div>';
  document.body.appendChild(lb);
  var stage = lb.querySelector('.pg-lb-stage'), img = stage.querySelector('img');
  var titleEl = lb.querySelector('.pg-lb-title'), metaEl = lb.querySelector('.pg-lb-meta');
  var dlEl = lb.querySelector('.pg-lb-dl');
  var current = null, opener = null, token = 0;

  function visible() { return items.filter(function (i) { return !i.hidden; }); }

  function show(item) {
    current = item;
    var mine = ++token;
    var thumb = item.querySelector('img');
    img.alt = item.dataset.title;
    img.src = thumb.currentSrc || thumb.src;          // already cached: appears immediately
    lb.classList.add('loading');
    var full = new Image();
    full.onload = function () {
      if (mine !== token) return;                      // user already moved on
      img.src = full.src;
      lb.classList.remove('loading');
    };
    full.onerror = function () { if (mine === token) lb.classList.remove('loading'); };
    full.src = item.dataset.full;

    dlEl.href = item.dataset.original;
    var v = visible();
    titleEl.textContent = item.dataset.title;
    metaEl.textContent = item.dataset.tags.split(',').join(' · ') + '   —   ' + (v.indexOf(item) + 1) + ' / ' + v.length;
    lb.classList.toggle('single', v.length < 2);
  }
  function step(d) {
    var v = visible();
    if (v.length < 2) return;
    show(v[(v.indexOf(current) + d + v.length) % v.length]);
  }
  function open(item, byKeyboard) {
    opener = byKeyboard ? item : null;
    show(item);
    lb.classList.add('open');
    document.documentElement.classList.add('pg-lb-lock');
    lb.querySelector('.pg-lb-close').focus({ preventScroll: true });
  }
  function close() {
    token++;
    lb.classList.remove('open', 'loading');
    document.documentElement.classList.remove('pg-lb-lock');
    img.removeAttribute('src');
    // Only hand focus back for keyboard users; after a mouse click it would show a focus ring.
    if (opener) opener.focus({ preventScroll: true });
    if (document.activeElement && document.activeElement !== document.body && !opener) document.activeElement.blur();
  }

  items.forEach(function (it) {
    it.addEventListener('click', function (e) { e.preventDefault(); open(it, e.detail === 0); });
  });
  lb.querySelector('.pg-lb-close').addEventListener('click', close);
  lb.querySelector('.pg-lb-prev').addEventListener('click', function () { step(-1); });
  lb.querySelector('.pg-lb-next').addEventListener('click', function () { step(1); });
  stage.addEventListener('click', function (e) { if (e.target === stage) close(); });   // click on the empty backdrop
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') step(-1);
    else if (e.key === 'ArrowRight') step(1);
  });

  // swipe left/right on touch screens
  var x0 = null;
  lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 50) step(dx < 0 ? 1 : -1);
  }, { passive: true });
})();
