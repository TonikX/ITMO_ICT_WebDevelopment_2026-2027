(() => {
  const menu = document.querySelector(".menu-toggle");
  const nav = document.querySelector("#navigation");
  function closeMenu() {
    nav?.classList.remove("is-open");
    menu?.setAttribute("aria-expanded", "false");
  }
  menu?.addEventListener("click", () => {
    const open = menu.getAttribute("aria-expanded") !== "true";
    menu.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("is-open", open);
  });
  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      menu?.getAttribute("aria-expanded") === "true"
    ) {
      closeMenu();
      menu.focus();
    }
  });
  window
    .matchMedia("(min-width: 1001px)")
    .addEventListener("change", closeMenu);
  document.querySelectorAll("[data-dismiss]").forEach((button) => {
    button.addEventListener("click", () =>
      button.closest('[role="status"]').remove(),
    );
  });
  // The content remains visible without JavaScript. Animation respects OS motion preferences.
  if (window.gsap) {
    const media = gsap.matchMedia();
    media.add("(prefers-reduced-motion: no-preference)", () => {
      const hero = document.querySelector(".hero");
      if (hero) {
        gsap
          .timeline({ defaults: { duration: 0.65, ease: "power3.out" } })
          .from(".hero-eyebrow", { y: 9, autoAlpha: 0 })
          .from(".hero h1", { y: 26, autoAlpha: 0 }, "-=0.48")
          .from(".hero-copy", { y: 14, autoAlpha: 0 }, "-=0.42")
          .from(
            ".hero-visual",
            { y: 18, autoAlpha: 0, duration: 0.8 },
            "-=0.55",
          )
          .from(".hero-strip", { autoAlpha: 0 }, "-=0.4");
      } else {
        const heading = document.querySelector(
          "[data-enter] .page-heading, [data-enter] .detail-title-row, [data-enter] .auth-form, [data-enter] .form-page-intro",
        );
        if (heading)
          gsap.from(heading, {
            y: 16,
            autoAlpha: 0,
            duration: 0.6,
            ease: "power3.out",
          });
      }
    });
    window.addEventListener("pagehide", () => media.revert(), { once: true });
  }
})();
