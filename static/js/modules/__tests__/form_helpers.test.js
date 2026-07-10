const { isValidEmail, validateField, validateForm } = require("../form_helpers");

describe("isValidEmail", () => {
  test("accepts well-formed emails", () => {
    expect(isValidEmail("person@example.com")).toBe(true);
  });

  test("rejects malformed emails", () => {
    expect(isValidEmail("not-an-email")).toBe(false);
    expect(isValidEmail("missing@domain")).toBe(false);
    expect(isValidEmail("")).toBe(false);
    expect(isValidEmail(null)).toBe(false);
  });
});

describe("validateField", () => {
  test("flags required fields left empty", () => {
    expect(validateField("Full name", "", { required: true })).toContain("Full name is required.");
  });

  test("flags whitespace-only values as empty", () => {
    expect(validateField("Full name", "   ", { required: true }).length).toBe(1);
  });

  test("flags invalid email format", () => {
    const errors = validateField("Email", "bad-email", { required: true, email: true });
    expect(errors).toContain("Email must be a valid email address.");
  });

  test("flags values shorter than minLength", () => {
    const errors = validateField("Message", "hi", { minLength: 10 });
    expect(errors.length).toBe(1);
  });

  test("passes when all rules are satisfied", () => {
    expect(validateField("Email", "person@example.com", { required: true, email: true })).toEqual([]);
  });
});

describe("validateForm", () => {
  test("aggregates errors across fields", () => {
    const { isValid, errors } = validateForm(
      { full_name: "", email: "bad" },
      { full_name: { required: true }, email: { required: true, email: true } }
    );
    expect(isValid).toBe(false);
    expect(Object.keys(errors)).toEqual(["full_name", "email"]);
  });

  test("is valid when every field satisfies its rules", () => {
    const { isValid } = validateForm(
      { full_name: "Jane Doe", email: "jane@example.com" },
      { full_name: { required: true }, email: { required: true, email: true } }
    );
    expect(isValid).toBe(true);
  });
});
