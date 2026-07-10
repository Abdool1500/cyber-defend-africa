module.exports = {
  rootDir: "static/js",
  testEnvironment: "jsdom",
  testMatch: ["**/__tests__/**/*.test.js"],
  collectCoverageFrom: ["modules/**/*.js", "!modules/**/__tests__/**"],
};
