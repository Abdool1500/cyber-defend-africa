const { QuestionNavigator } = require("../question_navigator");

describe("QuestionNavigator", () => {
  test("starts at the first question", () => {
    const nav = new QuestionNavigator(["q1", "q2", "q3"]);
    expect(nav.currentId).toBe("q1");
    expect(nav.total).toBe(3);
  });

  test("next/previous move within bounds", () => {
    const nav = new QuestionNavigator(["q1", "q2", "q3"]);
    nav.next();
    expect(nav.currentId).toBe("q2");
    nav.next();
    expect(nav.currentId).toBe("q3");
    nav.next(); // already at last — should not move past bounds
    expect(nav.currentId).toBe("q3");
    expect(nav.canGoNext()).toBe(false);

    nav.previous();
    nav.previous();
    expect(nav.currentId).toBe("q1");
    nav.previous(); // already at first
    expect(nav.currentId).toBe("q1");
    expect(nav.canGoPrevious()).toBe(false);
  });

  test("goTo ignores out-of-range indexes", () => {
    const nav = new QuestionNavigator(["q1", "q2"]);
    nav.goTo(5);
    expect(nav.currentId).toBe("q1");
    nav.goTo(-1);
    expect(nav.currentId).toBe("q1");
    nav.goTo(1);
    expect(nav.currentId).toBe("q2");
  });

  test("tracks answered state per question", () => {
    const nav = new QuestionNavigator(["q1", "q2", "q3"]);
    expect(nav.isAnswered("q1")).toBe(false);
    nav.markAnswered("q1");
    expect(nav.isAnswered("q1")).toBe(true);
    expect(nav.unansweredCount()).toBe(2);
    nav.unmarkAnswered("q1");
    expect(nav.isAnswered("q1")).toBe(false);
  });

  test("toggleFlag flips flagged state", () => {
    const nav = new QuestionNavigator(["q1"]);
    expect(nav.isFlagged("q1")).toBe(false);
    nav.toggleFlag("q1");
    expect(nav.isFlagged("q1")).toBe(true);
    nav.toggleFlag("q1");
    expect(nav.isFlagged("q1")).toBe(false);
  });
});
