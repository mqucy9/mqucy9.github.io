(() => {
  const AD_SRC =
    "//compassionate-boot.com/brXRVUszd.G_lb0FYpW/co/se/mX9/ucZwU_lUk/PITjYZ5HMyjEMe0/O/D/k/tpNNjwkUyZMyzTQU5HMIwq";

  function injectHeadOnce() {
    if (document.querySelector('script[data-ad-source="main-ad-head"]')) return;
    const s = document.createElement("script");
    s.src = AD_SRC;
    s.async = true;
    s.dataset.adSource = "main-ad-head";
    document.head.appendChild(s);
  }

  function injectSlots() {
    const slots = document.querySelectorAll(
      ".ads-placeholder, .sticky-ad, .bottom-ad, .ad-inline"
    );
    slots.forEach((el, idx) => {
      if (el.dataset.adInjected) return;
      el.innerHTML = el.innerHTML || "Advertisement";
      const s = document.createElement("script");
      s.src = AD_SRC;
      s.async = true;
      s.dataset.adSource = "slot-" + idx;
      el.appendChild(s);
      el.dataset.adInjected = "1";
    });
  }

  function init() {
    injectHeadOnce();
    injectSlots();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
