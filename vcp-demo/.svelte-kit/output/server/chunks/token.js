const PRIVATE_MARKER = "🔒";
function encodeContextToCSM1(ctx) {
  const lines = [];
  lines.push(`VCP:${ctx.vcp_version}:${ctx.profile_id}`);
  lines.push(`C:${ctx.constitution.id}@${ctx.constitution.version}`);
  lines.push(`P:${ctx.constitution.persona || "muse"}:${ctx.constitution.adherence || 3}`);
  const goal = ctx.public_profile?.goal || "unset";
  const experience = ctx.public_profile?.experience || "beginner";
  const style = ctx.public_profile?.learning_style || "mixed";
  lines.push(`G:${goal}:${experience}:${style}`);
  lines.push(encodeConstraints(ctx.constraints, ctx.portable_preferences));
  lines.push(encodeActiveFlags(ctx.constraints));
  lines.push(encodePrivateMarkers(ctx.private_context));
  return lines.join("\n");
}
function encodeConstraints(constraints, prefs) {
  const parts = [];
  if (constraints?.noise_restricted) parts.push("🔇");
  if (constraints?.time_limited) parts.push("⏰lim");
  if (constraints?.energy_variable) parts.push("⚡var");
  if (prefs?.noise_mode === "quiet_preferred") parts.push("🔇quiet");
  if (prefs?.noise_mode === "silent_required") parts.push("🔕silent");
  if (prefs?.budget_range === "low") parts.push("💰low");
  if (prefs?.budget_range === "free_only") parts.push("🆓");
  if (prefs?.session_length) parts.push(`⏱️${prefs.session_length.replace("_", "")}`);
  if (parts.length === 0) {
    return "X:none";
  }
  return `X:${parts.join(":")}`;
}
function encodeActiveFlags(constraints) {
  const flags = [];
  if (constraints?.time_limited) flags.push("time_limited");
  if (constraints?.noise_restricted) flags.push("noise_restricted");
  if (constraints?.budget_limited) flags.push("budget_limited");
  if (constraints?.energy_variable) flags.push("energy_variable");
  if (constraints?.schedule_irregular) flags.push("schedule_irregular");
  if (flags.length === 0) {
    return "F:none";
  }
  return `F:${flags.join("|")}`;
}
function encodePrivateMarkers(privateContext) {
  if (!privateContext) {
    return "S:none";
  }
  const markers = [];
  const keys = Object.keys(privateContext).filter(
    (k) => k !== "_note" && k !== "_reasoning"
  );
  const categories = /* @__PURE__ */ new Set();
  for (const key of keys) {
    const category = key.split("_")[0];
    categories.add(category);
  }
  for (const cat of categories) {
    markers.push(`${PRIVATE_MARKER}${cat}`);
  }
  if (markers.length === 0) {
    return "S:none";
  }
  return `S:${markers.join("|")}`;
}
function formatTokenForDisplay(csm1) {
  const lines = csm1.split("\n");
  const maxLen = Math.max(...lines.map((l) => l.length), 40);
  const border = "─".repeat(maxLen + 2);
  const formatted = lines.map((l) => `│ ${l.padEnd(maxLen)} │`).join("\n");
  return `┌${border}┐
${formatted}
└${border}┘`;
}
function getEmojiLegend() {
  return [
    { emoji: "🔇", meaning: "quiet mode" },
    { emoji: "🔕", meaning: "silent required" },
    { emoji: "💰", meaning: "budget tier" },
    { emoji: "🆓", meaning: "free only" },
    { emoji: "⚡", meaning: "energy variable" },
    { emoji: "⏰", meaning: "time limited" },
    { emoji: "⏱️", meaning: "session length" },
    { emoji: "📅", meaning: "irregular schedule" },
    { emoji: "🔒", meaning: "private (hidden value)" },
    { emoji: "✓", meaning: "shared" }
  ];
}
function getTransmissionSummary(ctx) {
  const transmitted = [];
  const withheld = [];
  const influencing = [];
  if (ctx.public_profile) {
    for (const [key, value] of Object.entries(ctx.public_profile)) {
      if (value !== void 0 && value !== null) {
        transmitted.push(key);
      }
    }
  }
  if (ctx.constraints) {
    for (const [key, value] of Object.entries(ctx.constraints)) {
      if (value === true) {
        influencing.push(key);
      }
    }
  }
  if (ctx.private_context) {
    for (const key of Object.keys(ctx.private_context)) {
      if (key !== "_note" && key !== "_reasoning") {
        withheld.push(key);
      }
    }
  }
  return { transmitted, withheld, influencing };
}
export {
  getEmojiLegend as a,
  encodeContextToCSM1 as e,
  formatTokenForDisplay as f,
  getTransmissionSummary as g
};
