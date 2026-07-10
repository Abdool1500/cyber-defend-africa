/**
 * Small client-side validation helpers for public forms (contact, demo
 * request, etc). These are UX conveniences only — Django forms re-validate
 * everything server-side (see apps/leads/forms.py), so nothing here is a
 * security boundary.
 */
function isValidEmail(value) {
  if (typeof value !== "string") return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

function isNonEmpty(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function validateField(name, value, rules = {}) {
  const errors = [];
  if (rules.required && !isNonEmpty(value)) {
    errors.push(`${name} is required.`);
  }
  if (rules.email && isNonEmpty(value) && !isValidEmail(value)) {
    errors.push(`${name} must be a valid email address.`);
  }
  if (rules.minLength && isNonEmpty(value) && value.trim().length < rules.minLength) {
    errors.push(`${name} must be at least ${rules.minLength} characters.`);
  }
  return errors;
}

function validateForm(values, schema) {
  const errors = {};
  for (const [field, rules] of Object.entries(schema)) {
    const fieldErrors = validateField(field, values[field], rules);
    if (fieldErrors.length > 0) {
      errors[field] = fieldErrors;
    }
  }
  return { isValid: Object.keys(errors).length === 0, errors };
}

module.exports = { isValidEmail, isNonEmpty, validateField, validateForm };
