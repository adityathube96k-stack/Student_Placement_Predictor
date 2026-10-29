/* Dependency-free SVG charts. Usage: <div class="chart" data-chart='{"type":"line",...}'></div> */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";

  function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  function palette() { var p = []; for (var i = 1; i <= 6; i++) p.push(css("--chart-" + i)); return p; }
  function el(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function txt(parent, x, y, s, attrs) { var t = el("text", Object.assign({ x: x, y: y }, attrs || {}), parent); t.textContent = s; return t; }
  function fmt(v, suffix) { var n = Math.round(v * 10) / 10; return n + (suffix || ""); }
  function niceMax(v) { if (v <= 0) return 10; var p = Math.pow(10, Math.floor(Math.log10(v))); var f = v / p; return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * p; }

  function tooltip(host) {
    var tip = host.querySelector(".chart-tip");
    if (!tip) { tip = document.createElement("div"); tip.className = "chart-tip"; host.appendChild(tip); }
    return {
      show: function (evt, text) {
        var r = host.getBoundingClientRect();
        tip.textContent = text; tip.style.left = (evt.clientX - r.left) + "px"; tip.style.top = (evt.clientY - r.top) + "px"; tip.classList.add("is-on");
      },
      hide: function () { tip.classList.remove("is-on"); }
    };
  }
  function attachTip(node, tip, text) {
    node.addEventListener("mousemove", function (e) { tip.show(e, text); });
    node.addEventListener("mouseleave", tip.hide);
    node.addEventListener("focus", function () { var b = node.getBoundingClientRect(), h = node.ownerSVGElement.parentNode.getBoundingClientRect(); tip.show({ clientX: b.left + b.width / 2, clientY: b.top }, text); });
    node.addEventListener("blur", tip.hide);
  }
  function legend(host, items, colors) {
    if (items.length < 2) return;
    var d = document.createElement("div"); d.className = "legend";
    items.forEach(function (name, i) { var s = document.createElement("span"); s.innerHTML = '<i style="background:' + colors[i % colors.length] + '"></i>'; s.appendChild(document.createTextNode(name)); d.appendChild(s); });
    host.appendChild(d);
  }
  function empty(host, msg) { host.innerHTML = '<div class="chart-empty">' + (msg || "Not enough data yet.") + "</div>"; }

  /* ---- Cartesian (line / area / bar) ---- */
  function cartesian(host, spec) {
    var W = host.clientWidth || 600, H = spec.height || 260, m = { t: 14, r: 12, b: 28, l: 38 };
    var series = spec.series || [], labels = spec.labels || [], colors = palette();
    if (!labels.length || !series.length) return empty(host, spec.empty);
    var stacked = spec.stacked, all = [];
    series.forEach(function (s) { s.data.forEach(function (v) { all.push(v); }); });
    var maxV = spec.max || niceMax(stacked ? Math.max.apply(null, labels.map(function (_, i) { return series.reduce(function (a, s) { return a + (s.data[i] || 0); }, 0); })) : Math.max.apply(null, all));
    var minV = spec.min !== undefined ? spec.min : 0;
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": spec.title || "Chart" });
    var iw = W - m.l - m.r, ih = H - m.t - m.b;
    var y = function (v) { return m.t + ih - (v - minV) / (maxV - minV) * ih; };
    for (var g = 0; g <= 4; g++) {
      var gv = minV + (maxV - minV) * g / 4, gy = y(gv);
      el("line", { class: "grid-line", x1: m.l, x2: W - m.r, y1: gy, y2: gy }, svg);
      txt(svg, m.l - 8, gy + 4, fmt(gv, ""), { "text-anchor": "end" });
    }
    var n = labels.length, step = iw / n, tip = tooltip(host);
    var every = Math.ceil(n / Math.max(Math.floor(iw / 56), 1));
    labels.forEach(function (l, i) { if (i % every === 0) txt(svg, m.l + step * i + step / 2, H - 8, l, { "text-anchor": "middle" }); });

    if (spec.type === "bar") {
      var gap = Math.min(step * 0.28, 14), groupW = step - gap * 2;
      var bw = stacked ? groupW : groupW / series.length;
      labels.forEach(function (_, i) {
        var base = 0;
        series.forEach(function (s, si) {
          var v = s.data[i] || 0, h = (v - minV) / (maxV - minV) * ih;
          var x = m.l + step * i + gap + (stacked ? 0 : bw * si), by = stacked ? y(base + v) : y(v);
          var rect = el("rect", { class: "bar", x: x, y: by, width: Math.max(bw - (stacked ? 0 : 3), 2), height: Math.max(h, 0), rx: 3, fill: s.color || colors[si % colors.length], tabindex: 0 }, svg);
          attachTip(rect, tip, (s.name ? s.name + ": " : "") + labels[i] + " " + fmt(v, spec.suffix));
          base += v;
        });
      });
    } else {
      series.forEach(function (s, si) {
        var color = s.color || colors[si % colors.length], pts = s.data.map(function (v, i) { return [m.l + step * i + step / 2, y(v)]; });
        if (!pts.length) return;
        var d = pts.map(function (p, i) { return (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1); }).join(" ");
        if (spec.area !== false && si === 0 || spec.area === true) {
          var id = "g" + Math.random().toString(36).slice(2, 7);
          var defs = el("defs", {}, svg), lg = el("linearGradient", { id: id, x1: 0, x2: 0, y1: 0, y2: 1 }, defs);
          el("stop", { offset: "0%", "stop-color": color, "stop-opacity": 0.22 }, lg); el("stop", { offset: "100%", "stop-color": color, "stop-opacity": 0 }, lg);
          el("path", { d: d + " L" + pts[pts.length - 1][0] + " " + (m.t + ih) + " L" + pts[0][0] + " " + (m.t + ih) + " Z", fill: "url(#" + id + ")" }, svg);
        }
        var path = el("path", { d: d, fill: "none", stroke: color, "stroke-width": 2.5, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
        var len = path.getTotalLength ? path.getTotalLength() : 0;
        if (len && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) { path.style.strokeDasharray = len; path.style.strokeDashoffset = len; path.getBoundingClientRect(); path.style.transition = "stroke-dashoffset 1s cubic-bezier(.22,.7,.2,1)"; path.style.strokeDashoffset = 0; }
        pts.forEach(function (p, i) {
          var c = el("circle", { class: "dot", cx: p[0], cy: p[1], r: 4, fill: css("--surface"), stroke: color, "stroke-width": 2.5, tabindex: 0 }, svg);
          attachTip(c, tip, (s.name ? s.name + ": " : "") + labels[i] + " " + fmt(s.data[i], spec.suffix));
        });
      });
    }
    el("line", { class: "axis-line", x1: m.l, x2: W - m.r, y1: m.t + ih, y2: m.t + ih }, svg);
    host.insertBefore(svg, host.firstChild);
    legend(host, series.map(function (s) { return s.name; }).filter(Boolean), colors);
  }

  /* ---- Horizontal bars ---- */
  function hbar(host, spec) {
    var items = spec.items || []; if (!items.length) return empty(host, spec.empty);
    var colors = palette(), W = host.clientWidth || 500, row = 34, labelW = Math.min(150, W * 0.34), H = items.length * row + 8;
    var max = spec.max || niceMax(Math.max.apply(null, items.map(function (i) { return i.value; })));
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": spec.title || "Chart" });
    var iw = W - labelW - 56;
    items.forEach(function (it, i) {
      var cy = i * row + 4, w = Math.max(it.value / max * iw, 2);
      var label = it.label.length > 22 ? it.label.slice(0, 21) + "…" : it.label;
      txt(svg, 0, cy + 19, label, { "font-size": 12 });
      el("rect", { x: labelW, y: cy + 8, width: iw, height: 12, rx: 6, fill: css("--surface-3") }, svg);
      var r = el("rect", { class: "bar", x: labelW, y: cy + 8, width: w, height: 12, rx: 6, fill: it.color || spec.color || colors[0] }, svg);
      if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) { r.setAttribute("width", 0); requestAnimationFrame(function () { r.style.transition = "width .9s cubic-bezier(.22,.7,.2,1)"; r.setAttribute("width", w); }); }
      txt(svg, labelW + iw + 10, cy + 19, fmt(it.value, spec.suffix), { "font-weight": 700, "font-size": 12, style: "fill:" + css("--ink") });
    });
    host.appendChild(svg);
  }

  /* ---- Donut ---- */
  function donut(host, spec) {
    var items = (spec.items || []).filter(function (i) { return i.value > 0; });
    var total = items.reduce(function (a, i) { return a + i.value; }, 0); if (!total) return empty(host, spec.empty);
    var colors = palette(), S = 200, r = 70, c = 2 * Math.PI * r, off = 0;
    var svg = el("svg", { viewBox: "0 0 " + S + " " + S, role: "img", "aria-label": spec.title || "Chart", style: "max-width:15rem;margin:0 auto" });
    var tip = tooltip(host);
    el("circle", { cx: 100, cy: 100, r: r, fill: "none", stroke: css("--surface-3"), "stroke-width": 24 }, svg);
    items.forEach(function (it, i) {
      var len = it.value / total * c, color = it.color || colors[i % colors.length];
      var seg = el("circle", { class: "bar", cx: 100, cy: 100, r: r, fill: "none", stroke: color, "stroke-width": 24, "stroke-dasharray": Math.max(len - 2, 0.5) + " " + (c - len + 2), "stroke-dashoffset": -off, transform: "rotate(-90 100 100)", tabindex: 0 }, svg);
      attachTip(seg, tip, it.label + ": " + it.value + " (" + Math.round(it.value / total * 100) + "%)");
      off += len;
    });
    var cv = spec.center && spec.center.value !== undefined ? spec.center.value : total;
    txt(svg, 100, 104, String(cv), { "text-anchor": "middle", "font-size": 30, "font-weight": 700, style: "fill:" + css("--ink") + ";font-family:" + css("--font-serif") });
    txt(svg, 100, 124, (spec.center && spec.center.label) || "total", { "text-anchor": "middle", "font-size": 11 });
    host.insertBefore(svg, host.firstChild);
    legend(host, items.map(function (i) { return i.label + " (" + i.value + ")"; }), items.map(function (it, i) { return it.color || colors[i % colors.length]; }));
    host.querySelector(".legend") && (host.querySelector(".legend").style.justifyContent = "center");
  }

  /* ---- Radar ---- */
  function radar(host, spec) {
    var labels = spec.labels || [], series = spec.series || []; if (labels.length < 3) return empty(host, spec.empty);
    var colors = palette(), S = 300, cx = S / 2, cy = S / 2 + 4, R = 100, max = spec.max || 100, n = labels.length;
    var svg = el("svg", { viewBox: "0 0 " + S + " " + (S + 8), role: "img", "aria-label": spec.title || "Chart", style: "max-width:22rem;margin:0 auto" });
    var pt = function (i, v) { var a = -Math.PI / 2 + i * 2 * Math.PI / n, rr = R * v / max; return [cx + rr * Math.cos(a), cy + rr * Math.sin(a)]; };
    for (var g = 1; g <= 4; g++) { var ring = []; for (var i = 0; i < n; i++) ring.push(pt(i, max * g / 4).join(",")); el("polygon", { points: ring.join(" "), fill: "none", stroke: css("--chart-grid") }, svg); }
    labels.forEach(function (l, i) {
      var p = pt(i, max), q = pt(i, max * 1.2);
      el("line", { x1: cx, y1: cy, x2: p[0], y2: p[1], stroke: css("--chart-grid") }, svg);
      txt(svg, q[0], q[1] + 4, l, { "text-anchor": q[0] < cx - 4 ? "end" : q[0] > cx + 4 ? "start" : "middle", "font-size": 12 });
    });
    var tip = tooltip(host);
    series.forEach(function (s, si) {
      var color = s.color || colors[si % colors.length], pts = s.data.map(function (v, i) { return pt(i, v); });
      var poly = el("polygon", { points: pts.map(function (p) { return p.join(","); }).join(" "), fill: color, "fill-opacity": s.dashed ? 0.02 : 0.16, stroke: color, "stroke-width": 2.2, "stroke-dasharray": s.dashed ? "5 4" : null }, svg);
      pts.forEach(function (p, i) { var d = el("circle", { class: "dot", cx: p[0], cy: p[1], r: 3.5, fill: color, tabindex: 0 }, svg); attachTip(d, tip, s.name + " · " + labels[i] + ": " + fmt(s.data[i], "")); });
    });
    host.insertBefore(svg, host.firstChild);
    legend(host, series.map(function (s) { return s.name; }), series.map(function (s, i) { return s.color || colors[i % colors.length]; }));
    host.querySelector(".legend") && (host.querySelector(".legend").style.justifyContent = "center");
  }

  var RENDER = { line: cartesian, area: cartesian, bar: cartesian, hbar: hbar, donut: donut, radar: radar };
  function render(host) {
    var spec; try { spec = JSON.parse(host.getAttribute("data-chart")); } catch (e) { return; }
    var fn = RENDER[spec.type]; if (!fn) return;
    host.innerHTML = ""; fn(host, spec);
  }
  function renderAll() { document.querySelectorAll("[data-chart]").forEach(render); }

  var width = {}, timer;
  function observe() {
    if (!("ResizeObserver" in window)) return;
    var ro = new ResizeObserver(function (entries) {
      entries.forEach(function (e) {
        var id = e.target; if (width.get && width.get(id) === Math.round(e.contentRect.width)) return;
        width.set && width.set(id, Math.round(e.contentRect.width));
        clearTimeout(timer); timer = setTimeout(function () { render(id); }, 120);
      });
    });
    width = new WeakMap();
    document.querySelectorAll("[data-chart]").forEach(function (h) { ro.observe(h); });
  }
  document.addEventListener("themechange", renderAll);
  function start() { renderAll(); observe(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
  window.Charts = { render: render, renderAll: renderAll };
})();
