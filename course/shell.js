(function(){
  "use strict";
  var WEEKS = {
    "1": {name:"One agent", scale:"1 agent"},
    "2": {name:"Small teams", scale:"3–5 agents"},
    "3": {name:"Systems", scale:"10–25 agents"},
    "4": {name:"Scale", scale:"100 agents"}
  };
  var store = {
    get: function(k){ try { return JSON.parse(localStorage.getItem("o2h:" + k)); } catch (e) { return null; } },
    set: function(k, v){ try { localStorage.setItem("o2h:" + k, JSON.stringify(v)); } catch (e) {} }
  };
  var CHECK = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8.5l3.2 3L13 4.5"/></svg>';
  var CROSS = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 4l8 8M12 4l-8 8"/></svg>';

  var lessons = Array.prototype.slice.call(document.querySelectorAll("section.lesson[id^=\"lesson-\"]"));
  var views = Array.prototype.slice.call(document.querySelectorAll("[data-view]"));
  var labsDone = store.get("labs") || {};

  function pad(n){ return (n < 10 ? "0" : "") + n; }
  function lessonNum(sec){ return parseInt(sec.id.replace("lesson-", ""), 10); }
  function lessonDone(sec){ var lab = sec.querySelector("[data-lab-id]"); return !!(lab && labsDone[lab.getAttribute("data-lab-id")]); }

  var nav = document.getElementById("rail-nav");
  function buildNav(){
    var html = '<ul class="wk__list"><li><a class="navitem navitem--plain" href="#home" data-target="home">Course home</a></li></ul>';
    ["1","2","3","4"].forEach(function(w){
      html += '<div class="wk"><div class="wk__head"><span class="n">Week ' + w + '</span><span class="t">' + WEEKS[w].name + '</span></div><ul class="wk__list">';
      lessons.filter(function(s){ return s.getAttribute("data-week") === w; }).forEach(function(s){
        var n = lessonNum(s);
        html += '<li><a class="navitem' + (lessonDone(s) ? " is-done" : "") + '" href="#' + s.id + '" data-target="' + s.id + '"><span class="num">' + pad(n) + '</span><span class="t">' + s.getAttribute("data-title") + '</span><span class="tick" aria-hidden="true">' + CHECK + '</span></a></li>';
      });
      html += '</ul></div>';
    });
    html += '<div class="wk"><div class="wk__head"><span class="n">After</span><span class="t">Keep handy</span></div><ul class="wk__list"><li><a class="navitem navitem--plain" href="#reference" data-target="reference">Reference sheet</a></li></ul></div>';
    nav.innerHTML = html;
  }
  function buildRoadmap(){
    var grid = document.getElementById("roadmap-grid");
    if (!grid) return;
    var html = "";
    ["1","2","3","4"].forEach(function(w){
      html += '<div class="rm-col"><div class="rm-col__head"><span class="n">Week ' + w + '</span><span class="t">' + WEEKS[w].name + '</span><span class="s">' + WEEKS[w].scale + '</span></div>';
      lessons.filter(function(s){ return s.getAttribute("data-week") === w; }).forEach(function(s){
        html += '<a class="rm-item' + (lessonDone(s) ? " is-done" : "") + '" href="#' + s.id + '"><span class="num">' + pad(lessonNum(s)) + '</span><span class="t">' + s.getAttribute("data-title") + '</span></a>';
      });
      html += '</div>';
    });
    grid.innerHTML = html;
  }
  function buildPagers(){
    lessons.forEach(function(s, i){
      var prev = lessons[i - 1], next = lessons[i + 1];
      var div = document.createElement("div");
      div.className = "pager";
      var h = "";
      h += prev ? '<a class="prev" href="#' + prev.id + '"><span>Previous · ' + pad(lessonNum(prev)) + '</span>' + prev.getAttribute("data-title") + '</a>' : '<a class="prev" href="#home"><span>Back</span>Course home</a>';
      h += next ? '<a class="next" href="#' + next.id + '"><span>Next · ' + pad(lessonNum(next)) + '</span>' + next.getAttribute("data-title") + '</a>' : '<a class="next" href="#reference"><span>After the course</span>Reference sheet</a>';
      div.innerHTML = h;
      s.appendChild(div);
    });
  }

  var countEl = document.getElementById("progress-count");
  var fillEl = document.getElementById("progress-fill");
  var barEl = document.getElementById("progress-bar");
  var scaleEl = document.getElementById("topbar-scale");

  function show(id){
    var target = document.getElementById(id);
    if (!target || !target.hasAttribute("data-view")) { id = "home"; target = document.getElementById("home"); }
    views.forEach(function(v){ v.hidden = v !== target; });
    Array.prototype.forEach.call(nav.querySelectorAll(".navitem"), function(a){
      a.classList.toggle("is-current", a.getAttribute("data-target") === id);
      if (a.getAttribute("data-target") === id) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    if (id.indexOf("lesson-") === 0) {
      var n = lessonNum(target);
      countEl.innerHTML = "Lesson <b>" + n + "</b> of " + lessons.length;
      fillEl.style.width = (n / lessons.length * 100) + "%";
      barEl.setAttribute("aria-valuenow", n);
      var w = WEEKS[target.getAttribute("data-week")];
      scaleEl.textContent = "Week " + target.getAttribute("data-week") + " · " + w.name + " · " + w.scale;
      store.set("last", id);
      document.title = pad(n) + " · " + target.getAttribute("data-title") + " · Scaling Agents";
    } else {
      var done = lessons.filter(lessonDone).length;
      countEl.innerHTML = id === "reference" ? "<b>Reference</b>" : "<b>" + lessons.length + "</b> lessons · " + done + " labs done";
      fillEl.style.width = (done / lessons.length * 100) + "%";
      barEl.setAttribute("aria-valuenow", 0);
      scaleEl.textContent = id === "reference" ? "Flags, settings and patterns" : "1 → 3–5 → 10–25 → 100";
      document.title = "Scaling Agents: From One to One Hundred";
    }
    document.body.classList.remove("nav-open");
    document.getElementById("menu-btn").setAttribute("aria-expanded", "false");
  }
  function route(scroll){
    var id = (location.hash || "#home").slice(1);
    show(id);
    if (scroll !== false) window.scrollTo(0, 0);
  }

  var resume = document.getElementById("resume-link");
  var last = store.get("last");
  if (resume && last && document.getElementById(last)) {
    var ls = document.getElementById(last);
    resume.href = "#" + last;
    resume.innerHTML = "Resume · Lesson " + pad(lessonNum(ls));
    resume.hidden = false;
  }

  document.getElementById("menu-btn").addEventListener("click", function(){
    var open = document.body.classList.toggle("nav-open");
    this.setAttribute("aria-expanded", open ? "true" : "false");
  });
  document.getElementById("scrim").addEventListener("click", function(){ document.body.classList.remove("nav-open"); });

  function each(sel, fn){ Array.prototype.forEach.call(document.querySelectorAll(sel), fn); }

  each('[data-component="predict"]', function(root){
    var btn = root.querySelector("[data-reveal]"), panel = root.querySelector("[data-reveal-panel]");
    if (!btn || !panel) return;
    btn.addEventListener("click", function(){
      var open = panel.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.textContent = open ? "Hide" : "Reveal";
    });
  });

  each('[data-component="mcq"]', function(root){
    var opts = Array.prototype.slice.call(root.querySelectorAll(".opt"));
    var fbs = Array.prototype.slice.call(root.querySelectorAll(".fb"));
    var fbWrap = root.querySelector(".c-mcq__fb");
    if (fbWrap) fbWrap.setAttribute("aria-live", "polite");
    opts.forEach(function(o){
      o.addEventListener("click", function(){
        if (root.classList.contains("is-done")) return;
        root.classList.add("is-done");
        var right = o.getAttribute("data-correct") === "true";
        opts.forEach(function(x){
          var isRight = x.getAttribute("data-correct") === "true";
          if (x === o) { x.classList.add(right ? "is-right" : "is-wrong"); x.querySelector(".mk").innerHTML = right ? CHECK : CROSS; }
          else if (isRight) { x.classList.add("is-right"); x.querySelector(".mk").innerHTML = CHECK; }
          else x.classList.add("is-dim");
          x.setAttribute("aria-disabled", "true");
        });
        var key = o.getAttribute("data-fb");
        fbs.forEach(function(f){ f.classList.toggle("is-shown", f.getAttribute("data-fb") === key); });
        var retry = document.createElement("button");
        retry.className = "btn btn--ghost c-mcq__retry";
        retry.type = "button";
        retry.textContent = "Try again";
        retry.addEventListener("click", function(){
          root.classList.remove("is-done");
          opts.forEach(function(x){ x.classList.remove("is-right","is-wrong","is-dim"); x.querySelector(".mk").innerHTML = ""; x.removeAttribute("aria-disabled"); });
          fbs.forEach(function(f){ f.classList.toggle("is-shown", f.getAttribute("data-fb") === "idle"); });
          retry.remove();
        });
        root.querySelector(".ex__body").appendChild(retry);
      });
    });
  });

  each('[data-component="verdict"]', function(root){
    var answer = root.getAttribute("data-answer");
    var btns = Array.prototype.slice.call(root.querySelectorAll(".vbtn"));
    var panels = Array.prototype.slice.call(root.querySelectorAll(".vfb"));
    var stack = root.querySelector(".stack");
    if (stack) stack.setAttribute("aria-live", "polite");
    btns.forEach(function(b){
      b.addEventListener("click", function(){
        if (root.classList.contains("is-done")) return;
        root.classList.add("is-done");
        var pick = b.getAttribute("data-pick");
        b.classList.add("is-picked", pick === answer ? "is-right" : "is-wrong");
        panels.forEach(function(p){ p.classList.toggle("is-shown", p.getAttribute("data-for") === pick); });
      });
    });
  });

  each('[data-component="code"]', function(root){
    var lines = Array.prototype.slice.call(root.querySelectorAll("button.cl"));
    var notes = Array.prototype.slice.call(root.querySelectorAll(".cnote"));
    lines.forEach(function(l){
      l.setAttribute("type", "button");
      l.addEventListener("click", function(){
        var key = l.getAttribute("data-note");
        lines.forEach(function(x){ x.classList.toggle("is-active", x === l); });
        notes.forEach(function(n){ n.classList.toggle("is-shown", n.getAttribute("data-note") === key); });
      });
    });
  });

  each('[data-component="stepper"]', function(root){
    var frames = Array.prototype.slice.call(root.querySelectorAll(".stepper__frames > li"));
    if (!frames.length) return;
    var body = root.querySelector(".ex__body");
    var ctl = document.createElement("div");
    ctl.className = "stepper__ctl";
    var dots = "";
    frames.forEach(function(){ dots += "<span></span>"; });
    ctl.innerHTML = '<button type="button" class="btn btn--ghost" data-step="-1">Back</button><button type="button" class="btn" data-step="1">Next</button><span class="stepper__count" aria-live="polite"></span><span class="stepper__dots" aria-hidden="true">' + dots + '</span>';
    body.appendChild(ctl);
    var i = 0;
    var count = ctl.querySelector(".stepper__count");
    var dotEls = ctl.querySelectorAll(".stepper__dots span");
    var prevB = ctl.querySelector('[data-step="-1"]'), nextB = ctl.querySelector('[data-step="1"]');
    function list(attr){ return (attr || "").split(",").map(function(s){ return s.trim(); }).filter(Boolean); }
    function render(){
      root.classList.add("is-live");
      var f = frames[i];
      var on = list(f.getAttribute("data-on")), edges = list(f.getAttribute("data-edges"));
      Array.prototype.forEach.call(root.querySelectorAll("[data-node]"), function(n){ n.classList.toggle("is-lit", on.indexOf(n.getAttribute("data-node")) !== -1); });
      Array.prototype.forEach.call(root.querySelectorAll("[data-edge]"), function(e){ e.classList.toggle("is-lit", edges.indexOf(e.getAttribute("data-edge")) !== -1); });
      frames.forEach(function(x, j){ x.classList.toggle("is-shown", j === i); });
      Array.prototype.forEach.call(dotEls, function(d, j){ d.classList.toggle("on", j <= i); });
      count.textContent = "Step " + (i + 1) + " of " + frames.length;
      prevB.disabled = i === 0;
      nextB.textContent = i === frames.length - 1 ? "Start over" : "Next";
    }
    prevB.addEventListener("click", function(){ if (i > 0) { i--; render(); } });
    nextB.addEventListener("click", function(){ i = i === frames.length - 1 ? 0 : i + 1; render(); });
    render();
  });

  function copyText(text, btn){
    function done(ok){ btn.textContent = ok ? "Copied" : "Selected"; setTimeout(function(){ btn.textContent = "Copy"; }, 1600); }
    function fallback(){
      var pre = btn.closest(".cmd").querySelector("pre");
      var r = document.createRange(); r.selectNodeContents(pre);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      done(false);
    }
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function(){ done(true); }, fallback);
      else fallback();
    } catch (e) { fallback(); }
  }
  each(".cmd", function(cmd){
    var pre = cmd.querySelector("pre");
    if (!pre) return;
    var bar = document.createElement("div");
    bar.className = "cmd__bar";
    var file = cmd.getAttribute("data-file"), kind = cmd.getAttribute("data-kind");
    var label = file ? 'File <b></b>' : kind === "prompt" ? "Prompt · type into Claude Code" : "Shell";
    bar.innerHTML = '<span class="cmd__kind">' + label + '</span><button type="button" class="cmd__copy">Copy</button>';
    if (file) bar.querySelector("b").textContent = file;
    cmd.insertBefore(bar, pre);
    bar.querySelector(".cmd__copy").addEventListener("click", function(){ copyText(pre.textContent, this); });
  });

  each('[data-component="lab"]', function(lab){
    var id = lab.getAttribute("data-lab-id");
    var body = lab.querySelector(".lab__body");
    if (!id || !body) return;
    var label = document.createElement("label");
    label.className = "lab__done";
    label.innerHTML = '<input type="checkbox" id="done-' + id + '"> I ran this lab';
    var box = label.querySelector("input");
    box.checked = !!labsDone[id];
    box.addEventListener("change", function(){
      labsDone[id] = box.checked;
      store.set("labs", labsDone);
      buildNav(); buildRoadmap();
      route(false);
    });
    body.appendChild(label);
  });

  var STOPS = [1,2,3,5,8,10,15,20,25,35,50,75,100,150,200];
  var SHARE = [2,2,1,14,3,1,1];
  function simulate(N, M, waves){
    var share = SHARE.slice(0, waves);
    var sumShare = share.reduce(function(a,b){ return a+b; }, 0);
    var counts = share.map(function(s){ return Math.max(1, Math.round(M * s / sumShare)); });
    var T = 6, TOK = 0.25, BRIEF = 0.12, REPORT = 0.03, READ = 0.15;
    var minutes = 0, tokens = 0;
    counts.forEach(function(m){
      var n = Math.min(N, m);
      var team = N > 1;
      var rework = team ? Math.min(0.4, 0.004 * n) : 0;
      var tasks = m * (1 + rework);
      var rounds = Math.ceil(tasks / n);
      minutes += rounds * T + (team ? 1.5 + READ * n : 0);
      tokens += tasks * TOK + (team ? tasks * (BRIEF + REPORT) + REPORT * tasks * Math.min(n, 20) * 0.5 : 0);
    });
    return {minutes: minutes, tokens: tokens};
  }
  function fmtTime(min){ return min >= 120 ? (min / 60).toFixed(1) + " h" : Math.round(min) + " min"; }
  each('[data-component="scale-sim"]', function(root){
    var M = parseInt(root.getAttribute("data-modules") || "240", 10);
    var W = Math.min(7, parseInt(root.getAttribute("data-waves") || "7", 10));
    var start = parseInt(root.getAttribute("data-start") || "5", 10);
    var idx = STOPS.indexOf(start); if (idx < 0) idx = 3;
    var base = simulate(1, M, W);
    var uid = "sim-" + Math.abs(M * 31 + start);
    root.classList.add("sim");
    root.innerHTML =
      '<div class="ex__head"><span class="dot"></span><span class="label">Scale simulator · toy model</span></div>' +
      '<div class="ex__body"><div class="sim__grid"><div class="sim__controls">' +
      '<label for="' + uid + '" class="label">Agents working in parallel</label>' +
      '<div class="sim__n"><output for="' + uid + '"></output><span>agents · ' + M + ' modules · ' + W + ' waves</span></div>' +
      '<input type="range" id="' + uid + '" min="0" max="' + (STOPS.length - 1) + '" step="1" value="' + idx + '">' +
      '<div class="sim__ticks"><span>1</span><span>10</span><span>50</span><span>200</span></div>' +
      '<div class="sim__stats">' +
      '<div class="sim__stat"><span>Wall-clock</span><b data-o="time"></b></div>' +
      '<div class="sim__stat"><span>Speedup vs 1</span><b data-o="speed"></b></div>' +
      '<div class="sim__stat"><span>Tokens (millions)</span><b data-o="tok"></b></div>' +
      '<div class="sim__stat"><span>Token cost vs 1</span><b data-o="mult"></b></div>' +
      '</div></div>' +
      '<div class="sim__chartwrap" style="display:grid;gap:.5rem;min-width:0"><div class="sim__chart"></div>' +
      '<div class="sim__legend"><span><i style="background:var(--accent)"></i>Speedup</span><span><i style="background:var(--ink-3)"></i>Perfect speedup</span><span><i style="background:var(--worker)"></i>Token cost multiple</span></div></div>' +
      '</div><p class="sim__note">Illustrative numbers, not measurements: one agent spends 6 minutes and 0.25M tokens per module. A team adds a fresh briefing for every task, reports the orchestrator has to read, and rework from collisions that grows with team size. The dependency waves cap how much can run at once. Watch where the curve flattens.</p></div>';
    var input = root.querySelector("input"), out = root.querySelector("output");
    var chart = root.querySelector(".sim__chart");
    var Wd = 560, Hd = 230, L = 44, R = 44, Tp = 14, B = 34;
    function x(n){ return L + Math.log(n) / Math.log(200) * (Wd - L - R); }
    var pts = STOPS.map(function(n){ var s = simulate(n, M, W); return {n:n, speed: base.minutes / s.minutes, mult: s.tokens / base.tokens}; });
    var maxS = Math.max.apply(null, pts.map(function(p){ return p.speed; }));
    var yMax = Math.max(10, Math.ceil(maxS / 5) * 5 + 5);
    var maxM = Math.max.apply(null, pts.map(function(p){ return p.mult; }));
    var mMax = Math.max(2, Math.ceil(maxM * 2) / 2);
    function y(v){ return Tp + (1 - Math.min(v, yMax) / yMax) * (Hd - Tp - B); }
    function y2(v){ return Tp + (1 - (v - 1) / (mMax - 1)) * (Hd - Tp - B); }
    function draw(cur){
      var s = '<svg viewBox="0 0 ' + Wd + ' ' + Hd + '" role="img" aria-label="Speedup and token cost by number of agents">';
      [0, yMax / 2, yMax].forEach(function(v){ s += '<line class="sim__grid-line" x1="' + L + '" x2="' + (Wd - R) + '" y1="' + y(v) + '" y2="' + y(v) + '"/><text class="sim__tick" x="' + (L - 8) + '" y="' + (y(v) + 4) + '" text-anchor="end">' + v + '×</text>'; });
      [1, mMax].forEach(function(v){ s += '<text class="sim__tick" x="' + (Wd - R + 8) + '" y="' + (y2(v) + 4) + '" style="fill:var(--worker)">' + v + '×</text>'; });
      [1, 10, 100, 200].forEach(function(n){ s += '<text class="sim__tick" x="' + x(n) + '" y="' + (Hd - 12) + '" text-anchor="middle">' + n + '</text>'; });
      s += '<line class="sim__axis" x1="' + L + '" x2="' + (Wd - R) + '" y1="' + (Hd - B) + '" y2="' + (Hd - B) + '"/>';
      var ideal = "", curve = "", cost = "";
      for (var n = 1; n <= 200; n = Math.ceil(n * 1.15)) { ideal += (ideal ? "L" : "M") + x(n).toFixed(1) + " " + y(n).toFixed(1); if (n >= yMax) break; }
      pts.forEach(function(p, j){ curve += (j ? "L" : "M") + x(p.n).toFixed(1) + " " + y(p.speed).toFixed(1); cost += (j ? "L" : "M") + x(p.n).toFixed(1) + " " + y2(p.mult).toFixed(1); });
      s += '<path class="sim__ideal" d="' + ideal + '"/><path class="sim__cost" d="' + cost + '"/><path class="sim__curve" d="' + curve + '"/>';
      s += '<circle class="sim__dot sim__dot--cost" r="5" cx="' + x(cur.n) + '" cy="' + y2(cur.mult) + '"/><circle class="sim__dot" r="6" cx="' + x(cur.n) + '" cy="' + y(cur.speed) + '"/>';
      s += '</svg>';
      chart.innerHTML = s;
    }
    function update(){
      var n = STOPS[parseInt(input.value, 10)];
      var r = simulate(n, M, W);
      var p = {n:n, speed: base.minutes / r.minutes, mult: r.tokens / base.tokens};
      out.textContent = n;
      input.setAttribute("aria-valuetext", n + " agents");
      root.querySelector('[data-o="time"]').textContent = fmtTime(r.minutes);
      root.querySelector('[data-o="speed"]').textContent = p.speed.toFixed(1) + "×";
      root.querySelector('[data-o="tok"]').textContent = r.tokens.toFixed(0);
      root.querySelector('[data-o="mult"]').textContent = p.mult.toFixed(2) + "×";
      draw(p);
    }
    input.addEventListener("input", update);
    update();
  });

  var dlBtn = document.getElementById("dl-btn"), dlStatus = document.getElementById("dl-status");
  var DL_READY = "kestrel-starter.zip · a git repo with Python source, tests, scripts and an empty TypeScript target.";
  function starterBlob(){
    var b64 = document.getElementById("starter-zip").textContent.replace(/\s+/g, "");
    var bin = atob(b64), bytes = new Uint8Array(bin.length);
    for (var k = 0; k < bin.length; k++) bytes[k] = bin.charCodeAt(k);
    return new Blob([bytes], {type: "application/zip"});
  }
  if (dlBtn && window.claude && typeof window.claude.use === "function") {
    window.claude.use("downloads").then(function(dl){
      if (!dl) { dlStatus.textContent = "Downloading isn't available in this view. Clone the repo with the commands above instead."; dlBtn.disabled = true; return; }
      dlBtn.disabled = false;
      dlStatus.textContent = DL_READY;
      dlBtn.addEventListener("click", function(){
        dlBtn.disabled = true;
        dlStatus.textContent = "Preparing the zip…";
        Promise.resolve().then(function(){
            return dl.save({filename: "kestrel-starter.zip", data: starterBlob()});
          })
          .then(function(){ dlStatus.textContent = "Saved. Unzip it and follow Lab 01."; })
          .catch(function(e){
            var code = e && e.code;
            dlStatus.textContent = code === "declined" ? "Download cancelled. Press the button again whenever you're ready." :
              code === "rate_limited" ? "A save prompt is already open. Finish that one first." :
              "The download didn't start. Reload the page and try again.";
          })
          .then(function(){ dlBtn.disabled = false; });
      });
    });
  } else if (dlBtn) {
    dlBtn.disabled = false;
    dlStatus.textContent = DL_READY;
    dlBtn.addEventListener("click", function(){
      var a = document.createElement("a");
      a.href = URL.createObjectURL(starterBlob());
      a.download = "kestrel-starter.zip";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(function(){ URL.revokeObjectURL(a.href); }, 1000);
      dlStatus.textContent = "Downloading. Unzip it and follow Lab 01.";
    });
  }

  buildNav();
  buildRoadmap();
  buildPagers();
  window.addEventListener("hashchange", function(){ route(true); });
  route(false);
})();
