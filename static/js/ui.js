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
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".toast").forEach((el) => {
    new bootstrap.Toast(el).show();
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
