(function () {
  "use strict";

  // ---------- Countdown to midnight, 1 January 2027 in Perth (AWST, UTC+8, no daylight saving) ----------
  var TARGET = Date.parse("2027-01-01T00:00:00+08:00"); // = 2026-12-31T16:00:00Z
  var pad = function (n) { return n < 10 ? "0" + n : String(n); };

  function tick() {
    var diff = TARGET - Date.now();
    document.querySelectorAll("[data-countdown]").forEach(function (el) {
      if (diff <= 0) {
        el.innerHTML = '<div class="cd-unit" style="min-width:auto;padding:16px 28px"><div class="cd-num">Happy New Year 2027!</div></div>';
        return;
      }
      var d = Math.floor(diff / 864e5), h = Math.floor(diff / 36e5) % 24,
          m = Math.floor(diff / 6e4) % 60, s = Math.floor(diff / 1e3) % 60;
      var set = function (k, v) { var n = el.querySelector('[data-u="' + k + '"]'); if (n) n.textContent = v; };
      set("d", d); set("h", pad(h)); set("m", pad(m)); set("s", pad(s));
    });
  }
  tick();
  setInterval(tick, 1000);

  // ---------- Mobile menu ----------
  var btn = document.querySelector(".menu-btn"), menu = document.querySelector(".nav ul");
  if (btn && menu) btn.addEventListener("click", function () {
    var open = menu.classList.toggle("open");
    btn.setAttribute("aria-expanded", open);
  });

  // ---------- Fireworks canvas ----------
  var canvas = document.getElementById("fw");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (canvas && canvas.getContext && !reduce) {
    var ctx = canvas.getContext("2d"), W, H, rockets = [], sparks = [];
    var COLORS = ["#ffc94d", "#ff4fa3", "#8b5cff", "#41e3ff", "#ffffff", "#ff7a45"];
    var resize = function () {
      var r = window.devicePixelRatio || 1;
      W = canvas.clientWidth; H = canvas.clientHeight;
      canvas.width = W * r; canvas.height = H * r; ctx.setTransform(r, 0, 0, r, 0, 0);
    };
    resize(); window.addEventListener("resize", resize);

    var launch = function (x) {
      rockets.push({ x: x != null ? x : W * (0.15 + Math.random() * 0.7), y: H, vx: (Math.random() - 0.5) * 1.2,
        vy: -(H / 95 + Math.random() * 3), ty: H * (0.12 + Math.random() * 0.35), c: COLORS[(Math.random() * COLORS.length) | 0] });
    };
    var burst = function (r) {
      var n = 70 + (Math.random() * 50 | 0), ring = Math.random() < 0.3;
      for (var i = 0; i < n; i++) {
        var a = (Math.PI * 2 * i) / n, sp = ring ? 3.2 : Math.random() * 4 + 0.5;
        sparks.push({ x: r.x, y: r.y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, life: 1,
          decay: 0.008 + Math.random() * 0.012, c: Math.random() < 0.2 ? "#fff" : r.c });
      }
    };
    var visible = true;
    document.addEventListener("visibilitychange", function () { visible = !document.hidden; });
    canvas.parentElement.addEventListener("click", function (e) {
      if (e.target.closest("a,button")) return;
      var rect = canvas.getBoundingClientRect(); launch(e.clientX - rect.left);
    });

    var loop = function () {
      requestAnimationFrame(loop);
      if (!visible) return;
      ctx.globalCompositeOperation = "destination-out";
      ctx.fillStyle = "rgba(0,0,0,0.22)"; ctx.fillRect(0, 0, W, H);
      ctx.globalCompositeOperation = "lighter";
      if (Math.random() < 0.035) launch();
      for (var i = rockets.length - 1; i >= 0; i--) {
        var r = rockets[i]; r.x += r.vx; r.y += r.vy; r.vy += 0.05;
        ctx.fillStyle = r.c; ctx.beginPath(); ctx.arc(r.x, r.y, 2, 0, 7); ctx.fill();
        if (r.y <= r.ty || r.vy >= 0) { burst(r); rockets.splice(i, 1); }
      }
      for (var j = sparks.length - 1; j >= 0; j--) {
        var s = sparks[j]; s.x += s.vx; s.y += s.vy; s.vx *= 0.985; s.vy = s.vy * 0.985 + 0.035; s.life -= s.decay;
        if (s.life <= 0) { sparks.splice(j, 1); continue; }
        ctx.globalAlpha = s.life; ctx.fillStyle = s.c;
        ctx.beginPath(); ctx.arc(s.x, s.y, 1.7, 0, 7); ctx.fill();
      }
      ctx.globalAlpha = 1;
    };
    setTimeout(function () { launch(); launch(); }, 300);
    loop();
  }

  // ---------- Directory filters ----------
  var dir = document.querySelector("[data-directory]");
  if (dir) {
    var cards = Array.prototype.slice.call(dir.querySelectorAll(".card"));
    var grid = dir.querySelector(".grid"), q = dir.querySelector("#q"),
        area = dir.querySelector("#area"), sort = dir.querySelector("#sort"),
        countEl = dir.querySelector(".count"), empty = dir.querySelector(".empty");
    var cat = "all";
    var apply = function () {
      var term = (q && q.value || "").trim().toLowerCase(), a = area ? area.value : "all", shown = 0;
      cards.forEach(function (c) {
        var ok = (cat === "all" || c.dataset.cats.split(" ").indexOf(cat) > -1) &&
                 (a === "all" || c.dataset.area === a) &&
                 (!term || c.dataset.search.indexOf(term) > -1);
        c.style.display = ok ? "" : "none"; if (ok) shown++;
      });
      if (sort) {
        var key = sort.value;
        cards.slice().sort(function (x, y) {
          if (key === "featured") return (y.dataset.featured - x.dataset.featured) || (x.dataset.order - y.dataset.order);
          var px = parseFloat(x.dataset.price), py = parseFloat(y.dataset.price);
          if (isNaN(px)) px = 1e9; if (isNaN(py)) py = 1e9;
          return key === "low" ? px - py : (py === 1e9 ? -1 : px === 1e9 ? 1 : py - px);
        }).forEach(function (c) { grid.appendChild(c); });
      }
      if (countEl) countEl.textContent = shown + " event" + (shown === 1 ? "" : "s") + " found";
      if (empty) empty.style.display = shown ? "none" : "block";
    };
    dir.querySelectorAll(".chip").forEach(function (ch) {
      ch.addEventListener("click", function () {
        dir.querySelectorAll(".chip").forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
        ch.setAttribute("aria-pressed", "true"); cat = ch.dataset.cat; apply();
      });
    });
    [q, area, sort].forEach(function (el) { if (el) el.addEventListener("input", apply); });
    var qp = new URLSearchParams(location.search).get("q");
    if (qp && q) q.value = qp;
    var hash = location.hash.replace("#cat-", "");
    if (hash && hash !== location.hash) {
      var pre = dir.querySelector('.chip[data-cat="' + hash + '"]'); if (pre) pre.click();
    }
    apply();
  }

  // ---------- Listing form: save details, then go to payment ----------
  var form = document.querySelector("form.listing");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var endpoint = form.dataset.endpoint, pay = form.dataset.payment, status = form.querySelector(".form-status");
      var submitBtn = form.querySelector("button[type=submit]");
      submitBtn.disabled = true; status.textContent = "Saving your listing…";
      var go = function () {
        status.textContent = "Done. Taking you to secure checkout…";
        var email = encodeURIComponent((form.querySelector("[name=email]") || {}).value || "");
        window.location.href = pay + (pay.indexOf("?") > -1 ? "&" : "?") + "prefilled_email=" + email;
      };
      if (!endpoint || endpoint.indexOf("YOUR_") > -1) {
        // Fallback when no form backend is configured: hand the details to the user's email client.
        var body = Array.prototype.map.call(new FormData(form).entries ? Array.from(new FormData(form).entries()) : [], function (p) { return p[0] + ": " + p[1]; }).join("\n");
        window.location.href = "mailto:" + form.dataset.email + "?subject=" + encodeURIComponent("NYE listing request") + "&body=" + encodeURIComponent(body);
        status.textContent = "Your email app should open. Send the email and we'll reply with a payment link within 24 hours.";
        submitBtn.disabled = false; return;
      }
      fetch(endpoint, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error();
          if (!pay || pay.indexOf("YOUR_") > -1) {
            form.reset();
            status.textContent = "Thanks! Your listing request has been sent. We'll email you within one business day with your invoice and next steps.";
            submitBtn.disabled = false; return;
          }
          go();
        })
        .catch(function () { status.textContent = "Something went wrong. Please email us at " + form.dataset.email; submitBtn.disabled = false; });
    });
  }
})();
