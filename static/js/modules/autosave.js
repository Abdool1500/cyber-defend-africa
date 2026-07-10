/**
 * Debounced autosave with explicit UI states and a single retry on
 * failure. `saveFn` is injected so this module has no direct dependency
 * on fetch/CSRF wiring and stays trivially unit-testable.
 */
const STATES = {
  IDLE: "idle",
  SAVING: "saving",
  SAVED: "saved",
  FAILED: "failed",
};

class Autosave {
  constructor({ saveFn, delayMs = 800, onStateChange, maxRetries = 1 }) {
    this.saveFn = saveFn;
    this.delayMs = delayMs;
    this.onStateChange = onStateChange || (() => {});
    this.maxRetries = maxRetries;
    this.state = STATES.IDLE;
    this._timer = null;
    this._pendingPayload = null;
  }

  _setState(state) {
    this.state = state;
    this.onStateChange(state);
  }

  schedule(payload) {
    this._pendingPayload = payload;
    if (this._timer) clearTimeout(this._timer);
    this._timer = setTimeout(() => {
      this._run(0).catch(() => {
        // Failure is surfaced via onStateChange(STATES.FAILED); swallow
        // here so an unresolved retry doesn't become an unhandled
        // rejection for callers that only observe state changes.
      });
    }, this.delayMs);
  }

  flush() {
    if (this._timer) {
      clearTimeout(this._timer);
      this._timer = null;
      return this._run(0);
    }
    return Promise.resolve();
  }

  async _run(attempt) {
    const payload = this._pendingPayload;
    this._setState(STATES.SAVING);
    try {
      await this.saveFn(payload);
      this._setState(STATES.SAVED);
    } catch (err) {
      if (attempt < this.maxRetries) {
        return this._run(attempt + 1);
      }
      this._setState(STATES.FAILED);
      throw err;
    }
  }
}

module.exports = { Autosave, STATES };
