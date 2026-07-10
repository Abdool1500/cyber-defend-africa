const { resolveWaitlistUrl } = require("../waitlist");

describe("resolveWaitlistUrl", () => {
  test("enables the button for a valid https URL", () => {
    const result = resolveWaitlistUrl("https://docs.google.com/forms/d/e/abc/viewform");
    expect(result.enabled).toBe(true);
    expect(result.url).toBe("https://docs.google.com/forms/d/e/abc/viewform");
  });

  test("disables safely when the URL is missing", () => {
    expect(resolveWaitlistUrl("")).toEqual({ enabled: false, url: null });
    expect(resolveWaitlistUrl(undefined)).toEqual({ enabled: false, url: null });
    expect(resolveWaitlistUrl(null)).toEqual({ enabled: false, url: null });
  });

  test("rejects non-https URLs", () => {
    expect(resolveWaitlistUrl("http://insecure.example.com/form")).toEqual({ enabled: false, url: null });
    expect(resolveWaitlistUrl("javascript:alert(1)")).toEqual({ enabled: false, url: null });
  });

  test("never returns the literal '#' as a usable url", () => {
    const result = resolveWaitlistUrl("#");
    expect(result.enabled).toBe(false);
    expect(result.url).toBeNull();
  });
});
