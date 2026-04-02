(function loadAdScript() {
  var src = "https://gullible-thanks.com/bv3.Va0CPw3wpCvqb/mVVrJUZ/DL0M2NOLT/ITy/NwDzYdxDLoTuYL5cMMjDIV0-NQj/UC";
  if (document.querySelector('script[data-ad-source="main-ad-script"]')) return;
  var s = document.createElement("script");
  s.src = src;
  s.async = true;
  s.dataset.adSource = "main-ad-script";
  document.head.appendChild(s);
})();

(function fillPlaceholders() {
  var slots = document.querySelectorAll(".ads-placeholder, .sticky-ad, .bottom-ad, .ad-inline");
  slots.forEach(function (el) {
    if (!el.dataset.adInjected) {
      el.innerHTML = el.innerHTML || "Advertisement";
      el.dataset.adInjected = "1";
    }
  });
})();
