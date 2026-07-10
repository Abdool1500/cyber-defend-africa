/**
 * Client-side quiz countdown display. This is UX only — the server is the
 * source of truth for expiry (see apps/quizzes/services/attempts.py
 * is_expired), so a manipulated client clock can't extend an attempt.
 */

function formatDuration(totalSeconds) {
  const clamped = Math.max(0, Math.floor(totalSeconds));
  const hours = Math.floor(clamped / 3600);
  const minutes = Math.floor((clamped % 3600) / 60);
  const seconds = clamped % 60;
  const pad = (n) => String(n).padStart(2, "0");
  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
  }
  return `${pad(minutes)}:${pad(seconds)}`;
}

function secondsRemaining(expiresAtIso, now = new Date()) {
  const expiresAt = new Date(expiresAtIso);
  const diffMs = expiresAt.getTime() - now.getTime();
  return Math.max(0, Math.floor(diffMs / 1000));
}

function isExpired(expiresAtIso, now = new Date()) {
  if (!expiresAtIso) return false;
  return secondsRemaining(expiresAtIso, now) <= 0;
}

class QuizTimer {
  constructor({ expiresAt, onTick, onExpire, intervalMs = 1000 }) {
    this.expiresAt = expiresAt;
    this.onTick = onTick;
    this.onExpire = onExpire;
    this.intervalMs = intervalMs;
    this._timerId = null;
    this._expired = false;
  }

  start() {
    this._tick();
    this._timerId = setInterval(() => this._tick(), this.intervalMs);
    return this;
  }

  stop() {
    if (this._timerId) {
      clearInterval(this._timerId);
      this._timerId = null;
    }
  }

  _tick() {
    if (!this.expiresAt) {
      if (this.onTick) this.onTick(null);
      return;
    }
    const remaining = secondsRemaining(this.expiresAt);
    if (this.onTick) this.onTick(remaining);
    if (remaining <= 0 && !this._expired) {
      this._expired = true;
      this.stop();
      if (this.onExpire) this.onExpire();
    }
  }
}

module.exports = { formatDuration, secondsRemaining, isExpired, QuizTimer };
