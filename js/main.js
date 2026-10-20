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
})();
