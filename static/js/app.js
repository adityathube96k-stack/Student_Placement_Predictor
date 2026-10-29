/* Student Placement Predictor: UI behaviour (no dependencies). */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---- Theme ---- */
  $$("[data-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("spp-theme", next); } catch (e) {}
      document.dispatchEvent(new CustomEvent("themechange"));
    });
  });

  /* ---- Navigation rail (mobile) ---- */
  $$("[data-rail-toggle]").forEach(function (b) { b.addEventListener("click", function () { document.body.classList.toggle("rail-open"); }); });
  $$("[data-rail-close]").forEach(function (b) { b.addEventListener("click", function () { document.body.classList.remove("rail-open"); }); });
  $$("[data-site-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var open = document.body.classList.toggle("site-menu-open");
      b.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  /* ---- Dropdown menus ---- */
  function closeMenus(except) {
    $$("[data-menu].is-open").forEach(function (m) {
      if (m !== except) { m.classList.remove("is-open"); var t = $("[data-menu-trigger]", m); if (t) t.setAttribute("aria-expanded", "false"); }
    });
  }
  $$("[data-menu]").forEach(function (menu) {
    var trigger = $("[data-menu-trigger]", menu);
    trigger.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = !menu.classList.contains("is-open");
      closeMenus(menu);
      menu.classList.toggle("is-open", open);
      trigger.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  document.addEventListener("click", function (e) { if (!e.target.closest("[data-menu]")) closeMenus(); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { closeMenus(); document.body.classList.remove("rail-open"); }
  });

  /* ---- Toasts ---- */
  function dismiss(toast) { toast.classList.add("is-leaving"); setTimeout(function () { toast.remove(); }, 260); }
  $$(".toast").forEach(function (t) {
    var close = $(".toast__close", t);
    if (close) close.addEventListener("click", function () { dismiss(t); });
    setTimeout(function () { if (t.isConnected) dismiss(t); }, t.classList.contains("toast--danger") ? 9000 : 6000);
  });

  /* ---- Confirm dialog for destructive forms ---- */
  var dialog = $("#confirm-dialog");
  var pendingForm = null;
  if (dialog && typeof dialog.showModal === "function") {
    $$("form[data-confirm]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        if (form.dataset.confirmed === "1") return;
        e.preventDefault();
        pendingForm = form;
        $("#confirm-title").textContent = form.dataset.confirmTitle || "Please confirm";
        $("#confirm-message").textContent = form.dataset.confirm;
        $("#confirm-ok").textContent = form.dataset.confirmLabel || "Confirm";
        dialog.showModal();
      });
    });
    $("[data-dialog-cancel]", dialog).addEventListener("click", function () { dialog.close(); pendingForm = null; });
    $("[data-dialog-ok]", dialog).addEventListener("click", function () {
      dialog.close();
      if (pendingForm) { pendingForm.dataset.confirmed = "1"; pendingForm.submit(); }
    });
  }

  /* ---- Loading state on submit ---- */
  $$("form[data-loading]").forEach(function (form) {
    form.addEventListener("submit", function () {
      var btn = $("button[type=submit]", form);
      if (btn && form.checkValidity()) { setTimeout(function () { btn.classList.add("is-loading"); }, 0); }
    });
  });

  /* ---- Sliders synced with number inputs ---- */
  $$("[data-slider]").forEach(function (box) {
    var range = $("input[type=range]", box), num = $("input[type=number]", box);
    function paint() {
      var min = +range.min, max = +range.max, v = Math.min(Math.max(+range.value, min), max);
      range.style.setProperty("--fill", ((v - min) / (max - min) * 100) + "%");
    }
    range.addEventListener("input", function () { num.value = range.value; paint(); num.dispatchEvent(new Event("input", { bubbles: true })); });
    num.addEventListener("input", function () { if (num.value !== "") { range.value = num.value; } paint(); });
    paint();
  });

  /* ---- Password visibility and strength ---- */
  $$("[data-toggle-password]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var input = document.getElementById(btn.dataset.togglePassword);
      var show = input.type === "password";
      input.type = show ? "text" : "password";
      btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
      btn.classList.toggle("is-on", show);
    });
  });
  $$("[data-strength-for]").forEach(function (meter) {
    var input = document.getElementById(meter.dataset.strengthFor);
    var label = meter.nextElementSibling;
    var words = ["Use 8 or more characters", "Weak", "Fair", "Good", "Strong"];
    input.addEventListener("input", function () {
      var v = input.value, score = 0;
      if (v.length >= 8) score++;
      if (/[a-z]/.test(v) && /[A-Z]/.test(v)) score++;
      if (/\d/.test(v)) score++;
      if (/[^A-Za-z0-9]/.test(v) || v.length >= 12) score++;
      if (!v) score = 0;
      meter.dataset.level = score;
      if (label) label.textContent = words[score];
    });
  });
  $$("[data-fill-email]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      $("#email").value = btn.dataset.fillEmail; $("#password").value = btn.dataset.fillPass; $("#password").focus();
    });
  });

  /* ---- Skill chips append to a field ---- */
  $$("[data-chip-target]").forEach(function (chip) {
    chip.addEventListener("click", function () {
      var field = document.getElementById(chip.dataset.chipTarget);
      var list = field.value.split(",").map(function (s) { return s.trim(); }).filter(Boolean);
      if (!list.some(function (s) { return s.toLowerCase() === chip.dataset.chipValue.toLowerCase(); })) list.push(chip.dataset.chipValue);
      field.value = list.join(", ");
      chip.classList.add("chip--ok");
    });
  });

  /* ---- Tabs ---- */
  $$("[data-tabs]").forEach(function (group) {
    var tabs = $$("[data-tab]", group), panels = $$("[data-panel]", group.parentNode);
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function (e) {
        e.preventDefault();
        tabs.forEach(function (t) { t.classList.toggle("is-active", t === tab); });
        panels.forEach(function (p) { p.hidden = p.dataset.panel !== tab.dataset.tab; });
      });
    });
  });

  /* ---- Data tables: search, filter, sort, paginate ---- */
  $$("[data-table]").forEach(function (root) {
    var table = $("table", root), body = $("tbody", table);
    var rows = $$("tr", body);
    var search = $("[data-table-search]", root), filters = $$("[data-table-filter]", root);
    var info = $("[data-table-info]", root), prev = $("[data-prev]", root), next = $("[data-next]", root);
    var size = +(root.dataset.pageSize || 10), page = 1, sortCol = -1, sortDir = 1;
    function cellText(r, i) { var c = r.children[i]; return c ? (c.dataset.sort || c.textContent).trim() : ""; }
    function apply() {
      var q = search ? search.value.trim().toLowerCase() : "";
      var vis = rows.filter(function (r) {
        if (q && r.textContent.toLowerCase().indexOf(q) === -1) return false;
        return filters.every(function (f) { return !f.value || (r.dataset[f.dataset.tableFilter] || "") === f.value; });
      });
      if (sortCol >= 0) {
        vis.sort(function (a, b) {
          var x = cellText(a, sortCol), y = cellText(b, sortCol), nx = parseFloat(x), ny = parseFloat(y);
          var r = (!isNaN(nx) && !isNaN(ny)) ? nx - ny : x.localeCompare(y);
          return r * sortDir;
        });
        vis.forEach(function (r) { body.appendChild(r); });
      }
      var pages = Math.max(1, Math.ceil(vis.length / size));
      page = Math.min(page, pages);
      rows.forEach(function (r) { r.hidden = true; });
      vis.slice((page - 1) * size, page * size).forEach(function (r) { r.hidden = false; });
      if (info) info.textContent = vis.length ? "Showing " + ((page - 1) * size + 1) + "-" + Math.min(page * size, vis.length) + " of " + vis.length : "No matching rows";
      if (prev) prev.disabled = page <= 1;
      if (next) next.disabled = page >= pages;
      var empty = $("[data-table-empty]", root); if (empty) empty.hidden = vis.length > 0;
    }
    if (search) search.addEventListener("input", function () { page = 1; apply(); });
    filters.forEach(function (f) { f.addEventListener("change", function () { page = 1; apply(); }); });
    if (prev) prev.addEventListener("click", function () { page--; apply(); });
    if (next) next.addEventListener("click", function () { page++; apply(); });
    $$("th.sortable", table).forEach(function (th, i) {
      th.addEventListener("click", function () {
        var idx = Array.prototype.indexOf.call(th.parentNode.children, th);
        sortDir = sortCol === idx ? -sortDir : 1; sortCol = idx;
        $$("th", table).forEach(function (h) { h.classList.remove("sorted-asc", "sorted-desc"); });
        th.classList.add(sortDir === 1 ? "sorted-asc" : "sorted-desc");
        apply();
      });
    });
    apply();
  });

  /* ---- Drag and drop file zone ---- */
  $$("[data-dropzone]").forEach(function (zone) {
    var input = $("input[type=file]", zone), name = $("[data-file-name]", zone);
    function show() { if (input.files.length) { name.textContent = input.files[0].name + " (" + Math.round(input.files[0].size / 1024) + " KB)"; var b = zone.closest("form").querySelector("button[type=submit]"); if (b) b.disabled = false; } }
    ["dragenter", "dragover"].forEach(function (ev) { zone.addEventListener(ev, function (e) { e.preventDefault(); zone.classList.add("is-drag"); }); });
    ["dragleave", "drop"].forEach(function (ev) { zone.addEventListener(ev, function (e) { e.preventDefault(); zone.classList.remove("is-drag"); }); });
    zone.addEventListener("drop", function (e) { if (e.dataTransfer.files.length) { input.files = e.dataTransfer.files; show(); } });
    input.addEventListener("change", show);
  });

  /* ---- Segmented filter for card lists ---- */
  $$("[data-filter-cards]").forEach(function (group) {
    var list = document.querySelector("[data-card-list]");
    $$("button", group).forEach(function (btn) {
      btn.addEventListener("click", function () {
        $$("button", group).forEach(function (b) { b.classList.toggle("is-active", b === btn); });
        $$("[data-status]", list).forEach(function (card) { card.hidden = btn.dataset.filter !== "all" && card.dataset.status !== btn.dataset.filter; });
      });
    });
  });

  /* ---- fetch helper with CSRF ---- */
  window.spp = {
    csrf: function () { var el = document.querySelector("meta[name=csrf-token]"); return el ? el.content : ""; },
    post: function (url, data) {
      return fetch(url, { method: "POST", headers: { "Content-Type": "application/json", "X-CSRFToken": window.spp.csrf() }, body: JSON.stringify(data) }).then(function (r) { return r.json(); });
    }
  };
})();
