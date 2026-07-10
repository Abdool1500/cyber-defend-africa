/**
 * Pure helper mirroring the server-side validation in
 * apps/core/context_processors.py — used by any client-side code that
 * needs to decide whether the waitlist button should be enabled.
 */
function resolveWaitlistUrl(rawUrl) {
  if (!rawUrl || typeof rawUrl !== "string") {
    return { enabled: false, url: null };
  }
  if (!rawUrl.startsWith("https://")) {
    return { enabled: false, url: null };
  }
  return { enabled: true, url: rawUrl };
}

module.exports = { resolveWaitlistUrl };
