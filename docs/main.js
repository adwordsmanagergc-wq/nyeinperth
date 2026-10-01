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

// ---------- Floating WhatsApp + email contact, and email/WhatsApp choice on the listing form ----------
(function () {
  var WA = "61488898835";
  var ENDPOINT = "https://formsubmit.co/ajax/aj@metatapdigital.com";
  var EMAIL = "aj@metatapdigital.com";
  var logo = document.querySelector(".logo");
  var SITE = logo ? logo.textContent.replace(/\s+/g, " ").trim() : document.title;
  var waLink = function (text) { return "https://wa.me/" + WA + "?text=" + encodeURIComponent(text); };
  var WA_ICON = '<svg viewBox="0 0 32 32" width="26" height="26" aria-hidden="true"><path fill="currentColor" d="M16 3C9 3 3.3 8.6 3.3 15.6c0 2.4.7 4.7 1.9 6.6L3 29l7-2.2c1.8 1 3.9 1.6 6 1.6 7 0 12.7-5.6 12.7-12.6S23 3 16 3zm0 23.1c-1.9 0-3.8-.5-5.4-1.5l-.4-.2-4.1 1.3 1.3-4-.3-.4c-1.1-1.7-1.7-3.6-1.7-5.6C5.4 9.9 10.1 5.3 16 5.3s10.6 4.6 10.6 10.4S21.9 26.1 16 26.1zm5.8-7.8c-.3-.2-1.9-.9-2.2-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-1 1.2-.2.2-.4.2-.7.1-.3-.2-1.3-.5-2.6-1.6-1-.9-1.6-1.9-1.8-2.2-.2-.3 0-.5.1-.7l.5-.6c.2-.2.2-.4.3-.6.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.7s1.2 3.1 1.4 3.4c.2.2 2.4 3.6 5.7 5 .8.3 1.4.5 1.9.7.8.3 1.5.2 2.1.1.6-.1 1.9-.8 2.2-1.5.3-.7.3-1.4.2-1.5-.1-.2-.3-.3-.6-.4z"/></svg>';
  var MAIL_ICON = '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path fill="currentColor" d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm1 2.4V17h16V7.4l-8 5.3-8-5.3zM5.4 7l6.6 4.4L18.6 7H5.4z"/></svg>';

  // Floating buttons
  var box = document.createElement("div");
  box.className = "cf";
  box.innerHTML =
    '<div class="cf-panel" id="cf-panel" role="dialog" aria-modal="false" aria-labelledby="cf-title" hidden>' +
      '<button type="button" class="cf-close" aria-label="Close">×</button>' +
      '<h3 id="cf-title">Send us a message</h3>' +
      '<p class="muted">Questions about an event or listing on ' + SITE + '? We reply within one business day.</p>' +
      '<form class="cf-form">' +
        '<label for="cf-name">Name *</label><input id="cf-name" name="name" required autocomplete="name">' +
        '<label for="cf-email">Email *</label><input id="cf-email" name="email" type="email" required autocomplete="email">' +
        '<label for="cf-phone">Phone</label><input id="cf-phone" name="phone" type="tel" autocomplete="tel">' +
        '<label for="cf-msg">Message *</label><textarea id="cf-msg" name="message" required rows="4"></textarea>' +
        '<input type="hidden" name="_subject" value="New enquiry from ' + SITE + '">' +
        '<input type="hidden" name="_template" value="table">' +
        '<input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">' +
        '<button class="btn btn-primary" type="submit">Send message</button>' +
        '<p class="cf-status muted" aria-live="polite"></p>' +
      '</form>' +
    '</div>' +
    '<button type="button" class="cf-btn cf-mail" aria-label="Email us" aria-controls="cf-panel" aria-expanded="false">' + MAIL_ICON + '</button>' +
    '<a class="cf-btn cf-wa" aria-label="Chat on WhatsApp" target="_blank" rel="noopener" href="' + waLink("Hi, I'm getting in touch from " + SITE + ".") + '">' + WA_ICON + '</a>';
  document.body.appendChild(box);

  var panel = box.querySelector(".cf-panel"), mailBtn = box.querySelector(".cf-mail");
  var toggle = function (open) {
    panel.hidden = !open; mailBtn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) { var f = panel.querySelector("input"); if (f) f.focus(); }
  };
  mailBtn.addEventListener("click", function () { toggle(panel.hidden); });
  box.querySelector(".cf-close").addEventListener("click", function () { toggle(false); mailBtn.focus(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) { toggle(false); mailBtn.focus(); } });

  var cform = box.querySelector(".cf-form");
  cform.addEventListener("submit", function (e) {
    e.preventDefault();
    var st = cform.querySelector(".cf-status"), b = cform.querySelector("button[type=submit]");
    b.disabled = true; st.textContent = "Sending…";
    fetch(ENDPOINT, { method: "POST", body: new FormData(cform), headers: { Accept: "application/json" } })
      .then(function (r) { if (!r.ok) throw new Error(); cform.reset(); st.textContent = "Thanks, your message has been sent. We'll be in touch soon."; b.disabled = false; })
      .catch(function () { st.innerHTML = 'Something went wrong. Please email <a href="mailto:' + EMAIL + '">' + EMAIL + '</a> or message us on WhatsApp.'; b.disabled = false; });
  });

  // Listing form: let buyers choose email or WhatsApp
  var lf = document.querySelector("form.listing");
  if (lf) {
    var sub = lf.querySelector("button[type=submit]");
    if (sub) {
      var paid = /payment/i.test(sub.textContent);
      sub.innerHTML = MAIL_ICON + "<span>" + (paid ? "Email &amp; pay by card" : "Send by email") + "</span>";
      var wa = document.createElement("button");
      wa.type = "button"; wa.className = "btn btn-wa";
      wa.innerHTML = WA_ICON + "<span>Send by WhatsApp</span>";
      var row = document.createElement("div"); row.className = "send-choice";
      var hint = document.createElement("p"); hint.className = "muted send-hint";
      hint.textContent = "Choose how to send your listing: email, or WhatsApp us on +61 488 898 835.";
      sub.parentNode.insertBefore(hint, sub);
      sub.parentNode.insertBefore(row, sub);
      row.appendChild(sub); row.appendChild(wa);
      wa.addEventListener("click", function () {
        if (!lf.reportValidity()) return;
        var skip = { _subject: 1, _template: 1, _honey: 1 };
        var lines = ["Hi, I'd like to list my event on " + SITE + ".", ""];
        Array.from(new FormData(lf).entries()).forEach(function (p) {
          if (skip[p[0]] || !String(p[1]).trim()) return;
          var k = p[0].replace(/_/g, " "); lines.push(k.charAt(0).toUpperCase() + k.slice(1) + ": " + p[1]);
        });
        window.open(waLink(lines.join("\n")), "_blank", "noopener");
        var st = lf.querySelector(".form-status");
        if (st) st.textContent = "WhatsApp should open with your details filled in. Press send and we'll reply with your invoice.";
      });
    }
  }
})();
