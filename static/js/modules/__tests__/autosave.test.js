const { Autosave, STATES } = require("../autosave");

describe("Autosave", () => {
  beforeEach(() => jest.useFakeTimers());
  afterEach(() => jest.useRealTimers());

  test("debounces multiple schedule() calls into a single save", async () => {
    const saveFn = jest.fn().mockResolvedValue(undefined);
    const autosave = new Autosave({ saveFn, delayMs: 500 });

    autosave.schedule({ value: 1 });
    jest.advanceTimersByTime(100);
    autosave.schedule({ value: 2 });
    jest.advanceTimersByTime(100);
    autosave.schedule({ value: 3 });

    await jest.advanceTimersByTimeAsync(500);

    expect(saveFn).toHaveBeenCalledTimes(1);
    expect(saveFn).toHaveBeenCalledWith({ value: 3 });
  });

  test("transitions through saving -> saved on success", async () => {
    const saveFn = jest.fn().mockResolvedValue(undefined);
    const states = [];
    const autosave = new Autosave({ saveFn, delayMs: 200, onStateChange: (s) => states.push(s) });

    autosave.schedule({ value: 1 });
    await jest.advanceTimersByTimeAsync(200);

    expect(states).toEqual([STATES.SAVING, STATES.SAVED]);
  });

  test("retries once on failure before marking failed", async () => {
    const saveFn = jest
      .fn()
      .mockRejectedValueOnce(new Error("network error"))
      .mockResolvedValueOnce(undefined);
    const states = [];
    const autosave = new Autosave({ saveFn, delayMs: 100, maxRetries: 1, onStateChange: (s) => states.push(s) });

    autosave.schedule({ value: 1 });
    await jest.advanceTimersByTimeAsync(100);

    expect(saveFn).toHaveBeenCalledTimes(2);
    expect(states).toEqual([STATES.SAVING, STATES.SAVING, STATES.SAVED]);
  });

  test("marks failed after exhausting retries", async () => {
    const saveFn = jest.fn().mockRejectedValue(new Error("network error"));
    const states = [];
    const autosave = new Autosave({ saveFn, delayMs: 100, maxRetries: 1, onStateChange: (s) => states.push(s) });

    autosave.schedule({ value: 1 });
    await expect(jest.advanceTimersByTimeAsync(100)).resolves.toBeUndefined();

    expect(saveFn).toHaveBeenCalledTimes(2);
    expect(states).toEqual([STATES.SAVING, STATES.SAVING, STATES.FAILED]);
  });

  test("flush() saves immediately without waiting for the debounce delay", async () => {
    const saveFn = jest.fn().mockResolvedValue(undefined);
    const autosave = new Autosave({ saveFn, delayMs: 5000 });

    autosave.schedule({ value: "final" });
    await autosave.flush();

    expect(saveFn).toHaveBeenCalledWith({ value: "final" });
  });
});
