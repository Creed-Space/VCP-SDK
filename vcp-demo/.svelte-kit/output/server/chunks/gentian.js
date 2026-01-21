const gentianChallengeProgress = {
  total_days: 30,
  days_completed: 18,
  days_adjusted: 3,
  current_streak: 4,
  best_streak: 7,
  badges: ["week_warrior", "chord_master_basic", "consistent_learner"]
};
const challengeLeaderboard = [
  {
    rank: 1,
    display_name: "MelodyMaster",
    days_completed: 21,
    days_adjusted: 0,
    total_days: 21,
    is_current_user: false
  },
  {
    rank: 2,
    display_name: "ChordCrusher",
    days_completed: 20,
    days_adjusted: 1,
    total_days: 21,
    is_current_user: false
  },
  {
    rank: 3,
    display_name: "Gentian",
    days_completed: 18,
    days_adjusted: 3,
    total_days: 21,
    is_current_user: true
  },
  {
    rank: 4,
    display_name: "StringNewbie",
    days_completed: 17,
    days_adjusted: 2,
    total_days: 21,
    is_current_user: false
  },
  {
    rank: 5,
    display_name: "GuitarDreamer",
    days_completed: 15,
    days_adjusted: 4,
    total_days: 21,
    is_current_user: false
  }
];
function getSkipDayContext() {
  return {
    detected: {
      trigger: "post_night_shift",
      energy_state: "low",
      last_practice: "2026-01-20",
      current_streak: 4
    },
    recommendation: {
      action: "skip_today",
      reasoning: "You just finished a night shift rotation. Rest is important for both recovery and learning retention.",
      what_happens: {
        streak: "Current streak (4) becomes adjusted streak",
        leaderboard: "Shows 18/21 (4 adjusted) - no penalty in adjusted view",
        private_reason: "Stored locally only, never shared with community"
      }
    },
    alternatives: [
      "Practice anyway (short session)",
      "Skip today (count as adjusted)",
      "Listen-only session (no manual practice)"
    ]
  };
}
export {
  getSkipDayContext as a,
  challengeLeaderboard as c,
  gentianChallengeProgress as g
};
