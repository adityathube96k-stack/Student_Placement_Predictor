/* Mock interview: timer, word counts and progress. */
(function () {
  "use strict";
  var form = document.getElementById("interview-form");
  var start = document.getElementById("start-form");
  if (start) {
    var cats = start.querySelectorAll(".category");
    start.addEventListener("change", function () {
      cats.forEach(function (c) { c.classList.toggle("is-selected", c.querySelector("input").checked); });
    });
  }
  if (!form) return;
  var timer = document.getElementById("timer"), answered = document.getElementById("answered"), bar = document.getElementById("progress");
  var areas = Array.prototype.slice.call(form.querySelectorAll("[data-answer]"));
  var t0 = Date.now();
  setInterval(function () {
    var s = Math.floor((Date.now() - t0) / 1000), m = Math.floor(s / 60);
    timer.textContent = (m < 10 ? "0" : "") + m + ":" + (s % 60 < 10 ? "0" : "") + (s % 60);
  }, 1000);
  function refresh() {
    var done = 0;
    areas.forEach(function (a) {
      var words = a.value.trim() ? a.value.trim().split(/\s+/).length : 0;
      a.parentNode.querySelector("[data-words]").textContent = words;
      if (words >= 5) done++;
    });
    answered.textContent = done;
    bar.style.setProperty("--v", Math.round(done / areas.length * 100));
  }
  form.addEventListener("input", refresh);
  refresh();
  window.addEventListener("beforeunload", function (e) {
    if (areas.some(function (a) { return a.value.trim(); }) && !form.dataset.confirmed) { e.preventDefault(); e.returnValue = ""; }
  });
})();
