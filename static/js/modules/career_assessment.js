/**
 * Scoring logic for the public Career Path Assessment. This is guidance,
 * not a guarantee — see the disclaimer rendered alongside the result on
 * /career-path-assessment/.
 */
const TRACKS = {
  AI_SECURITY: "ai_security_engineering",
  ETHICAL_HACKING: "ethical_hacking",
  SOC_ANALYST: "soc_analyst",
};

// Each question maps an answer choice to points for one or more tracks.
const QUESTIONS = [
  {
    id: "interest_area",
    prompt: "Which of these interests you most?",
    options: [
      { value: "offensive_security", scores: { [TRACKS.ETHICAL_HACKING]: 3 } },
      { value: "defensive_security", scores: { [TRACKS.SOC_ANALYST]: 3 } },
      { value: "ai_systems", scores: { [TRACKS.AI_SECURITY]: 3 } },
      { value: "investigation", scores: { [TRACKS.SOC_ANALYST]: 2, [TRACKS.ETHICAL_HACKING]: 1 } },
    ],
  },
  {
    id: "daily_work",
    prompt: "What kind of daily work appeals to you?",
    options: [
      { value: "coding", scores: { [TRACKS.AI_SECURITY]: 2, [TRACKS.ETHICAL_HACKING]: 1 } },
      { value: "vulnerability_testing", scores: { [TRACKS.ETHICAL_HACKING]: 3 } },
      { value: "log_analysis", scores: { [TRACKS.SOC_ANALYST]: 3 } },
      { value: "emerging_technology", scores: { [TRACKS.AI_SECURITY]: 3 } },
    ],
  },
];

const TRACK_LABELS = {
  [TRACKS.AI_SECURITY]: "AI Security Engineering",
  [TRACKS.ETHICAL_HACKING]: "Ethical Hacking & Penetration Testing",
  [TRACKS.SOC_ANALYST]: "SOC Analyst & Blue Team Operations",
};

function scoreAssessment(answers) {
  const totals = {
    [TRACKS.AI_SECURITY]: 0,
    [TRACKS.ETHICAL_HACKING]: 0,
    [TRACKS.SOC_ANALYST]: 0,
  };

  for (const question of QUESTIONS) {
    const chosenValue = answers[question.id];
    const option = question.options.find((o) => o.value === chosenValue);
    if (!option) continue;
    for (const [track, points] of Object.entries(option.scores)) {
      totals[track] += points;
    }
  }

  const maxScore = Math.max(...Object.values(totals));
  const topTracks = Object.entries(totals)
    .filter(([, score]) => score === maxScore && maxScore > 0)
    .map(([track]) => track);

  return {
    totals,
    recommendedTracks: topTracks,
    recommendedLabels: topTracks.map((t) => TRACK_LABELS[t]),
    isTie: topTracks.length > 1,
  };
}

const _exports = { TRACKS, QUESTIONS, TRACK_LABELS, scoreAssessment };
if (typeof module !== "undefined" && module.exports) {
  module.exports = _exports;
} else {
  window.CareerAssessment = _exports;
}
