(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // year
  document.getElementById('year').textContent = new Date().getFullYear();

  // theme toggle
  document.getElementById('theme').addEventListener('click', function () {
    var root = document.documentElement;
    var dark = root.dataset.theme
      ? root.dataset.theme === 'dark'
      : window.matchMedia('(prefers-color-scheme: dark)').matches;
    var next = dark ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) {}
  });

  // language toggle (EN default, DE from js/i18n.js)
  var DE = window.I18N_DE || {};
  var EN = { typed: ['pipelines.', 'dashboards.', 'decisions.', 'clean datasets.', 'answers.'],
             'console.again': '↻ Run again' };
  var lang = 'en';
  function t(key) { return (lang === 'de' && DE[key]) || EN[key]; }

  function applyLang(next) {
    lang = next === 'de' ? 'de' : 'en';
    document.documentElement.lang = lang;
    // [attribute, how to read, how to write]; English originals are cached on first switch
    [['data-i18n', function (n) { return n.innerHTML; }, function (n, v) { n.innerHTML = v; }],
     ['data-i18n-label', function (n) { return n.getAttribute('aria-label'); },
       function (n, v) { n.setAttribute('aria-label', v); n.setAttribute('title', v); }],
     ['data-i18n-alt', function (n) { return n.alt; }, function (n, v) { n.alt = v; }]
    ].forEach(function (a) {
      document.querySelectorAll('[' + a[0] + ']').forEach(function (n) {
        var key = n.getAttribute(a[0]);
        if (!(key in EN)) EN[key] = a[1](n);
        a[2](n, t(key));
      });
    });
    if (run && run.dataset.ran) run.textContent = t('console.again');
    document.querySelectorAll('[data-count][data-done]').forEach(function (n) {
      n.textContent = fmt(parseFloat(n.dataset.count), parseInt(n.dataset.dec || '0', 10)) + (n.dataset.suffix || '');
    });
    restartTyping();
    try { localStorage.setItem('lang', lang); } catch (e) {}
  }

  document.getElementById('lang').addEventListener('click', function () {
    applyLang(lang === 'de' ? 'en' : 'de');
  });

  // typed headline
  var el = document.getElementById('typed');
  var w = 0, c = 0, del = false, timer;
  function restartTyping() {
    clearTimeout(timer);
    w = 0; c = 0; del = false;
    if (reduce) { el.textContent = t('typed')[0]; return; }
    (function tick() {
      var words = t('typed');
      var word = words[w];
      el.textContent = word.slice(0, c);
      var wait = del ? 40 : 90;
      if (!del && c === word.length) { del = true; wait = 1400; }
      else if (del && c === 0) { del = false; w = (w + 1) % words.length; wait = 300; }
      else { c += del ? -1 : 1; }
      timer = setTimeout(tick, wait);
    })();
  }

  // count-up stats
  function fmt(x, dec) {
    var v = x.toFixed(dec);
    return lang === 'de' ? v.replace('.', ',') : v;
  }
  function countUp(node) {
    var target = parseFloat(node.dataset.count);
    var dec = parseInt(node.dataset.dec || '0', 10);
    var suffix = node.dataset.suffix || '';
    node.dataset.done = '1';
    if (reduce) { node.textContent = fmt(target, dec) + suffix; return; }
    var start = performance.now(), dur = 1200;
    (function step(now) {
      var t = Math.min((now - start) / dur, 1);
      var eased = 1 - Math.pow(1 - t, 3);
      node.textContent = fmt(target * eased, dec) + suffix;
      if (t < 1) requestAnimationFrame(step);
    })(start);
  }

  // reveal on scroll
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      e.target.querySelectorAll('[data-count]').forEach(countUp);
      io.unobserve(e.target);
    });
  }, { threshold: 0.15 }) : null;

  document.querySelectorAll('.stats, .stat, .card, .proj, .console, .skills > div').forEach(function (n) {
    n.classList.add('reveal');
    if (io) io.observe(n); else { n.classList.add('in'); n.querySelectorAll('[data-count]').forEach(countUp); }
  });

  // SQL console easter egg
  var run = document.getElementById('run');
  var results = document.getElementById('results');
  var rows = document.getElementById('rows');
  run.addEventListener('click', function () {
    results.hidden = false;
    rows.hidden = false;
    results.querySelectorAll('li').forEach(function (li, i) {
      li.style.animationDelay = reduce ? '0s' : (i * 0.25) + 's';
    });
    run.dataset.ran = '1';
    run.textContent = t('console.again');
    results.innerHTML = results.innerHTML; // restart animation
  });

  var saved = 'en';
  try { saved = localStorage.getItem('lang') || 'en'; } catch (e) {}
  applyLang(saved);

  // project dialogs
  document.querySelectorAll('[data-open]').forEach(function (card) {
    var dlg = document.getElementById(card.dataset.open);
    card.addEventListener('click', function (e) {
      if (e.target.closest('a')) return; // let links (e.g. GitHub) open normally
      dlg.showModal();
      document.body.classList.add('modal-open');
    });
    dlg.addEventListener('close', function () { document.body.classList.remove('modal-open'); });
    dlg.addEventListener('click', function (e) {
      if (e.target === dlg || e.target.closest('[data-close]')) dlg.close();
    });
  });
})();
