/* Runs before first paint so the saved theme never flashes. */
(function () {
  try {
    var saved = localStorage.getItem("spp-theme");
    if (!saved && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) saved = "dark";
    if (saved) document.documentElement.setAttribute("data-theme", saved);
  } catch (e) { /* storage unavailable */ }
})();
