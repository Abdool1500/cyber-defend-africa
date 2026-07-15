/**
 * Site-wide UI wiring: shows Bootstrap toasts for Django messages, and
 * puts submit buttons into a loading-spinner state so users get feedback
 * and can't double-submit a slow form. DOM-only, no business logic — not
 * unit tested under Jest (unlike static/js/modules/*.js).
 *
 * Assumes forms submit normally (full page navigation) rather than being
 * cancelled by an onsubmit handler — true for every form in this project
 * at the time this was written. A form can opt out with
 * data-no-spinner="true" if that ever changes.
 */
function setThemeIcon(theme) {
  document.querySelectorAll(".theme-toggle-icon").forEach((icon) => {
    icon.classList.toggle("bi-sun-fill", theme === "dark");
    icon.classList.toggle("bi-moon-stars-fill", theme === "light");
  });
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".toast").forEach((el) => {
    new bootstrap.Toast(el).show();
  });

  // The inline script in base.html already set data-bs-theme before
  // first paint (avoids a flash of the wrong theme) — this just syncs
  // the toggle button's icon to whatever that resolved to.
  setThemeIcon(document.documentElement.getAttribute("data-bs-theme") === "light" ? "light" : "dark");

  document.querySelectorAll(".theme-toggle-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const next = document.documentElement.getAttribute("data-bs-theme") === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-bs-theme", next);
      localStorage.setItem("cda-theme", next);
      setThemeIcon(next);
    });
  });

  document.querySelectorAll("form").forEach((form) => {
    if (form.dataset.noSpinner) return;
    form.addEventListener("submit", () => {
      form.querySelectorAll('button[type="submit"]').forEach((button) => {
        if (button.disabled) return;
        button.disabled = true;
        button.innerHTML =
          '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Please wait…';
      });
    });
  });
});
