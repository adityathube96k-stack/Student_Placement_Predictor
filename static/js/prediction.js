/* Live what-if estimate on the prediction form. */
(function () {
  "use strict";
  var form = document.getElementById("predict-form");
  if (!form) return;
  var dial = form.querySelector(".dial"), band = document.getElementById("live-band"), note = document.getElementById("live-note"), factors = document.getElementById("live-factors");
  var names = ["cgpa", "attendance", "aptitude_score", "coding_score", "communication_score", "technical_score", "projects", "internships", "certifications"];
  var timer, seq = 0;

  function setDial(v) {
    dial.style.setProperty("--v", v);
    dial.querySelector(".dial__value").firstChild.nodeValue = Math.round(v);
    dial.classList.remove("dial--high", "dial--mid", "dial--low");
    dial.classList.add("dial--on-ink");
  }
  function collect() {
    var data = {};
    for (var i = 0; i < names.length; i++) {
      var el = form.elements[names[i]];
      if (!el || el.value === "") return null;
      data[names[i]] = el.value;
    }
    return data;
  }
  function update() {
    var data = collect(); if (!data) return;
    var mine = ++seq;
    window.spp.post(form.dataset.previewUrl, data).then(function (res) {
      if (mine !== seq) return;
      if (!res.ok) { note.textContent = res.error; return; }
      setDial(res.probability);
      band.textContent = res.band + " chance";
      note.textContent = res.result === "Placed" ? "Model expects a placement with these inputs." : "Model expects this profile to need improvement.";
      factors.innerHTML = "";
      res.factors.forEach(function (f) {
        var row = document.createElement("div"); row.className = "live-factor";
        var sign = f.impact > 0 ? "+" : "";
        row.innerHTML = "<span></span><b class='" + (f.impact >= 0 ? "good" : "bad") + "'></b>";
        row.firstChild.textContent = f.label; row.lastChild.textContent = sign + f.impact.toFixed(1);
        factors.appendChild(row);
      });
    }).catch(function () { note.textContent = "Preview unavailable."; });
  }
  form.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(update, 260); });
  update();
})();
