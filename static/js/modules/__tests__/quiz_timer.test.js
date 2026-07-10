const { formatDuration, secondsRemaining, isExpired, QuizTimer } = require("../quiz_timer");

describe("formatDuration", () => {
  test("formats seconds under a minute", () => {
    expect(formatDuration(45)).toBe("00:45");
  });

  test("formats minutes and seconds", () => {
    expect(formatDuration(125)).toBe("02:05");
  });

  test("formats hours when present", () => {
    expect(formatDuration(3661)).toBe("01:01:01");
  });

  test("clamps negative durations to zero", () => {
    expect(formatDuration(-10)).toBe("00:00");
  });
});

describe("secondsRemaining / isExpired", () => {
  test("computes remaining seconds relative to now", () => {
    const now = new Date("2026-01-01T00:00:00Z");
    const expiresAt = "2026-01-01T00:05:00Z";
    expect(secondsRemaining(expiresAt, now)).toBe(300);
  });

  test("returns zero once past expiry, never negative", () => {
    const now = new Date("2026-01-01T00:10:00Z");
    const expiresAt = "2026-01-01T00:05:00Z";
    expect(secondsRemaining(expiresAt, now)).toBe(0);
  });

  test("isExpired is false when no expiry is set (untimed quiz)", () => {
    expect(isExpired(null)).toBe(false);
  });

  test("isExpired is true once time has passed", () => {
    const now = new Date("2026-01-01T00:10:00Z");
    expect(isExpired("2026-01-01T00:05:00Z", now)).toBe(true);
  });
});

describe("QuizTimer", () => {
  beforeEach(() => jest.useFakeTimers().setSystemTime(new Date("2026-01-01T00:00:00Z")));
  afterEach(() => jest.useRealTimers());

  test("ticks down and calls onExpire exactly once at zero", () => {
    const onTick = jest.fn();
    const onExpire = jest.fn();
    const timer = new QuizTimer({
      expiresAt: "2026-01-01T00:00:03Z",
      onTick,
      onExpire,
      intervalMs: 1000,
    });
    timer.start();

    jest.advanceTimersByTime(1000);
    jest.advanceTimersByTime(1000);
    jest.advanceTimersByTime(1000);
    jest.advanceTimersByTime(1000);

    expect(onExpire).toHaveBeenCalledTimes(1);
    expect(onTick).toHaveBeenCalled();
  });

  test("stop() prevents further ticks", () => {
    const onTick = jest.fn();
    const timer = new QuizTimer({ expiresAt: "2026-01-01T00:01:00Z", onTick, intervalMs: 1000 });
    timer.start();
    timer.stop();
    const callsAfterStop = onTick.mock.calls.length;
    jest.advanceTimersByTime(5000);
    expect(onTick.mock.calls.length).toBe(callsAfterStop);
  });
});
