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

  // typed headline
  var words = ['pipelines.', 'dashboards.', 'decisions.', 'clean datasets.', 'answers.'];
  var el = document.getElementById('typed');
  if (reduce) {
    el.textContent = words[0];
  } else {
    var w = 0, c = 0, del = false;
    (function tick() {
      var word = words[w];
      el.textContent = word.slice(0, c);
      var wait = del ? 40 : 90;
      if (!del && c === word.length) { del = true; wait = 1400; }
      else if (del && c === 0) { del = false; w = (w + 1) % words.length; wait = 300; }
      else { c += del ? -1 : 1; }
      setTimeout(tick, wait);
    })();
  }

  // count-up stats
  function countUp(node) {
    var target = parseFloat(node.dataset.count);
    var dec = parseInt(node.dataset.dec || '0', 10);
    var suffix = node.dataset.suffix || '';
    if (reduce) { node.textContent = target.toFixed(dec) + suffix; return; }
    var start = performance.now(), dur = 1200;
    (function step(now) {
      var t = Math.min((now - start) / dur, 1);
      var eased = 1 - Math.pow(1 - t, 3);
      node.textContent = (target * eased).toFixed(dec) + suffix;
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

  document.querySelectorAll('.stats, .stat, .card, .console, .skills > div').forEach(function (n) {
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
    run.textContent = '↻ Run again';
    results.innerHTML = results.innerHTML; // restart animation
  });

  // projects
  var grid = document.getElementById('grid');
  var filters = document.getElementById('filters');
  var projects = window.PROJECTS || [];
  var active = 'All';

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s == null ? '' : String(s);
    return d.innerHTML;
  }
  function safeUrl(u) { return /^https?:\/\//i.test(u || '') ? u : ''; }

  function render() {
    grid.innerHTML = projects
      .filter(function (p) { return active === 'All' || p.tags.indexOf(active) > -1; })
      .map(function (p) {
        var links = [['code', 'Code ↗'], ['demo', 'Live demo ↗'], ['report', 'Report ↗']]
          .filter(function (l) { return safeUrl((p.links || {})[l[0]]); })
          .map(function (l) {
            return '<a href="' + esc(safeUrl(p.links[l[0]])) + '" target="_blank" rel="noopener">' + l[1] + '</a>';
          }).join('');
        var c = p.colors || ['#1f4e8c', '#4aa3ff'];
        return '<article class="proj">' +
          '<div class="thumb" style="--c1:' + esc(c[0]) + ';--c2:' + esc(c[1]) + '">' + esc(p.emoji) +
          (p.draft ? '<span class="status">draft</span>' : '') + '</div>' +
          '<div class="body"><h3>' + esc(p.title) + '</h3>' +
          '<p>' + esc(p.summary) + '</p>' +
          (p.result ? '<p class="result">' + esc(p.result) + '</p>' : '') +
          (links ? '<div class="links">' + links + '</div>' : '') +
          '<div class="tags">' + p.tags.map(function (t) { return '<span>' + esc(t) + '</span>'; }).join('') + '</div>' +
          '</div></article>';
      }).join('');
  }

  function renderFilters() {
    var tags = ['All'];
    projects.forEach(function (p) { p.tags.forEach(function (t) { if (tags.indexOf(t) < 0) tags.push(t); }); });
    filters.innerHTML = tags.map(function (t) {
      return '<button type="button" aria-pressed="' + (t === active) + '">' + esc(t) + '</button>';
    }).join('');
  }

  filters.addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (!b) return;
    active = b.textContent;
    renderFilters();
    render();
  });

  renderFilters();
  render();
})();
