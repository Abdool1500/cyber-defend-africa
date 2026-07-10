const { scoreAssessment, TRACKS } = require("../career_assessment");

describe("scoreAssessment", () => {
  test("recommends AI Security Engineering for AI-leaning answers", () => {
    const result = scoreAssessment({
      interest_area: "ai_systems",
      daily_work: "emerging_technology",
    });
    expect(result.recommendedTracks).toEqual([TRACKS.AI_SECURITY]);
    expect(result.isTie).toBe(false);
  });

  test("recommends Ethical Hacking for offensive-leaning answers", () => {
    const result = scoreAssessment({
      interest_area: "offensive_security",
      daily_work: "vulnerability_testing",
    });
    expect(result.recommendedTracks).toEqual([TRACKS.ETHICAL_HACKING]);
  });

  test("recommends SOC Analyst for defensive-leaning answers", () => {
    const result = scoreAssessment({
      interest_area: "defensive_security",
      daily_work: "log_analysis",
    });
    expect(result.recommendedTracks).toEqual([TRACKS.SOC_ANALYST]);
  });

  test("handles a genuine tie by returning every top-scoring track", () => {
    // interest_area -> AI_SECURITY:3, daily_work -> SOC_ANALYST:3 (equal top score)
    const result = scoreAssessment({
      interest_area: "ai_systems",
      daily_work: "log_analysis",
    });
    expect(result.isTie).toBe(true);
    expect(result.recommendedTracks.sort()).toEqual([TRACKS.AI_SECURITY, TRACKS.SOC_ANALYST].sort());
  });

  test("returns no recommendation when nothing is answered", () => {
    const result = scoreAssessment({});
    expect(result.recommendedTracks).toEqual([]);
    expect(result.isTie).toBe(false);
  });

  test("ignores unanswered/unknown question values", () => {
    const result = scoreAssessment({ interest_area: "not_a_real_option" });
    expect(Object.values(result.totals).every((score) => score === 0)).toBe(true);
  });
});
