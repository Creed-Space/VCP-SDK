import { a3 as escape_html, a6 as attr_style, a7 as stringify, a8 as ensure_array_like, a1 as attr_class, a0 as attr, a2 as head } from "../../../../../chunks/index2.js";
import { D as DemoContainer } from "../../../../../chunks/DemoContainer.js";
import { h as html } from "../../../../../chunks/html.js";
import { P as PresetLoader } from "../../../../../chunks/PresetLoader.js";
import { A as AuditPanel } from "../../../../../chunks/AuditPanel.js";
function LearningPathViz($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { path, mastery } = $$props;
    const levelColors = {
      beginner: "#3498db",
      intermediate: "#f39c12",
      advanced: "#2ecc71",
      expert: "#9b59b6"
    };
    function getMasteryForTopic(topicId) {
      return mastery[topicId];
    }
    function getTopicStatus(topic, index) {
      const topicMastery = getMasteryForTopic(topic.topic_id);
      if (topicMastery && topicMastery.confidence >= topic.mastery_threshold) {
        return "completed";
      }
      if (index === path.current_position) {
        return "in_progress";
      }
      if (index < path.current_position) {
        return "completed";
      }
      const prereqsMet = topic.prerequisites.every((prereq) => {
        const prereqMastery = getMasteryForTopic(prereq);
        return prereqMastery && prereqMastery.confidence >= 0.7;
      });
      return prereqsMet ? "available" : "locked";
    }
    function getDifficultyStars(difficulty) {
      return '<i class="fa-solid fa-star" aria-hidden="true"></i>'.repeat(difficulty) + '<i class="fa-regular fa-star" aria-hidden="true"></i>'.repeat(5 - difficulty);
    }
    function getProgressPercent() {
      return path.completed_hours / path.estimated_total_hours * 100;
    }
    $$renderer2.push(`<div class="learning-path-viz svelte-1penjlx"><div class="path-header svelte-1penjlx"><div class="path-info svelte-1penjlx"><h3 class="svelte-1penjlx">${escape_html(path.name)}</h3> <p class="path-desc svelte-1penjlx">${escape_html(path.description)}</p></div> <div class="path-progress svelte-1penjlx"><div class="progress-bar svelte-1penjlx"><div class="progress-fill svelte-1penjlx"${attr_style(`width: ${stringify(getProgressPercent())}%`)}></div></div> <div class="progress-text svelte-1penjlx"><span>${escape_html(path.completed_hours.toFixed(1))}h / ${escape_html(path.estimated_total_hours)}h</span> <span class="progress-percent svelte-1penjlx">${escape_html(Math.round(getProgressPercent()))}%</span></div></div></div> `);
    if (path.personalization_applied.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="personalization-notice svelte-1penjlx"><span class="notice-icon svelte-1penjlx"><i class="fa-solid fa-wand-magic-sparkles" aria-hidden="true"></i></span> <span>Personalized for you:</span> <!--[-->`);
      const each_array = ensure_array_like(path.personalization_applied);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let adaptation = each_array[$$index];
        $$renderer2.push(`<span class="adaptation-chip svelte-1penjlx">${escape_html(adaptation.replace(/_/g, " "))}</span>`);
      }
      $$renderer2.push(`<!--]--></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="topics-path svelte-1penjlx" role="list" aria-label="Learning path topics"><!--[-->`);
    const each_array_1 = ensure_array_like(path.topics);
    for (let i = 0, $$length = each_array_1.length; i < $$length; i++) {
      let topic = each_array_1[i];
      const status = getTopicStatus(topic, i);
      const topicMastery = getMasteryForTopic(topic.topic_id);
      $$renderer2.push(`<div class="topic-node-container svelte-1penjlx" role="listitem">`);
      if (i > 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div${attr_class("connector svelte-1penjlx", void 0, { "completed": status === "completed" })} aria-hidden="true"></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> <button${attr_class("topic-node svelte-1penjlx", void 0, {
        "locked": status === "locked",
        "available": status === "available",
        "in-progress": status === "in_progress",
        "completed": status === "completed"
      })}${attr("disabled", status === "locked", true)}${attr("aria-label", `${stringify(topic.name)} - ${stringify(status === "completed" ? "Completed" : status === "in_progress" ? "In progress" : status === "locked" ? "Locked" : "Available")}, ${stringify(topic.estimated_hours)} hours, difficulty ${stringify(topic.difficulty)} of 5`)}><div class="node-indicator svelte-1penjlx">`);
      if (status === "completed") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<i class="fa-solid fa-check" aria-hidden="true"></i>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (status === "in_progress") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<i class="fa-solid fa-play" aria-hidden="true"></i>`);
        } else {
          $$renderer2.push("<!--[!-->");
          if (status === "locked") {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<i class="fa-solid fa-lock" aria-hidden="true"></i>`);
          } else {
            $$renderer2.push("<!--[!-->");
            $$renderer2.push(`${escape_html(i + 1)}`);
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></div> <div class="node-content svelte-1penjlx"><span class="topic-name svelte-1penjlx">${escape_html(topic.name)}</span> <div class="topic-meta svelte-1penjlx"><span class="difficulty svelte-1penjlx">${html(getDifficultyStars(topic.difficulty))}</span> <span class="duration">${escape_html(topic.estimated_hours)}h</span></div> `);
      if (topicMastery) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="mastery-bar svelte-1penjlx"><div class="mastery-fill svelte-1penjlx"${attr_style(`width: ${stringify(topicMastery.confidence * 100)}%; background: ${stringify(levelColors[topicMastery.level])}`)}></div></div> <span class="mastery-level svelte-1penjlx"${attr_style(`color: ${stringify(levelColors[topicMastery.level])}`)}>${escape_html(topicMastery.level)}</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div></button> `);
      if (status === "in_progress") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="topic-details svelte-1penjlx"><div class="detail-row svelte-1penjlx"><span class="detail-label svelte-1penjlx">Modalities:</span> <div class="modality-chips svelte-1penjlx"><!--[-->`);
        const each_array_2 = ensure_array_like(topic.modalities_available);
        for (let $$index_1 = 0, $$length2 = each_array_2.length; $$index_1 < $$length2; $$index_1++) {
          let mod = each_array_2[$$index_1];
          $$renderer2.push(`<span class="modality-chip svelte-1penjlx">${escape_html(mod)}</span>`);
        }
        $$renderer2.push(`<!--]--></div></div> `);
        if (topic.analogies_available.length > 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="detail-row svelte-1penjlx"><span class="detail-label svelte-1penjlx">Analogies:</span> <div class="analogy-chips svelte-1penjlx"><!--[-->`);
          const each_array_3 = ensure_array_like(topic.analogies_available);
          for (let $$index_2 = 0, $$length2 = each_array_3.length; $$index_2 < $$length2; $$index_2++) {
            let analogy = each_array_3[$$index_2];
            $$renderer2.push(`<span class="analogy-chip svelte-1penjlx">${escape_html(analogy)}</span>`);
          }
          $$renderer2.push(`<!--]--></div></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (topic.prerequisites.length > 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="detail-row svelte-1penjlx"><span class="detail-label svelte-1penjlx">Prerequisites:</span> <span class="prereqs svelte-1penjlx">${escape_html(topic.prerequisites.join(", "))}</span></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="legend svelte-1penjlx"><div class="legend-item svelte-1penjlx"><span class="legend-dot completed svelte-1penjlx"></span> <span>Completed</span></div> <div class="legend-item svelte-1penjlx"><span class="legend-dot in-progress svelte-1penjlx"></span> <span>In Progress</span></div> <div class="legend-item svelte-1penjlx"><span class="legend-dot available svelte-1penjlx"></span> <span>Available</span></div> <div class="legend-item svelte-1penjlx"><span class="legend-dot locked svelte-1penjlx"></span> <span>Locked</span></div></div></div>`);
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let path = {
      path_id: "web-dev-fundamentals",
      name: "Web Development Fundamentals",
      description: "A personalized introduction to modern web development",
      topics: [
        {
          topic_id: "html-basics",
          name: "HTML Basics",
          prerequisites: [],
          estimated_hours: 3,
          difficulty: 1,
          modalities_available: ["video", "interactive", "text"],
          analogies_available: ["building blocks", "skeleton"],
          mastery_threshold: 0.8
        },
        {
          topic_id: "css-styling",
          name: "CSS Styling",
          prerequisites: ["html-basics"],
          estimated_hours: 4,
          difficulty: 2,
          modalities_available: ["video", "interactive", "text"],
          analogies_available: ["paint", "clothing", "interior design"],
          mastery_threshold: 0.8
        },
        {
          topic_id: "js-fundamentals",
          name: "JavaScript Fundamentals",
          prerequisites: ["html-basics"],
          estimated_hours: 6,
          difficulty: 3,
          modalities_available: ["video", "interactive", "text", "quiz"],
          analogies_available: ["brain", "engine", "recipe"],
          mastery_threshold: 0.75
        },
        {
          topic_id: "dom-manipulation",
          name: "DOM Manipulation",
          prerequisites: ["js-fundamentals", "html-basics"],
          estimated_hours: 4,
          difficulty: 3,
          modalities_available: ["video", "interactive"],
          analogies_available: ["puppeteer", "remote control"],
          mastery_threshold: 0.75
        },
        {
          topic_id: "responsive-design",
          name: "Responsive Design",
          prerequisites: ["css-styling"],
          estimated_hours: 3,
          difficulty: 2,
          modalities_available: ["video", "interactive", "text"],
          analogies_available: ["water", "origami"],
          mastery_threshold: 0.8
        }
      ],
      current_position: 2,
      estimated_total_hours: 20,
      completed_hours: 7,
      personalization_applied: [
        "analogy_substitution",
        "pace_adjustment",
        "examples_increased"
      ]
    };
    let mastery = {
      "html-basics": {
        topic_id: "html-basics",
        topic_name: "HTML Basics",
        level: "intermediate",
        confidence: 0.9,
        last_assessed: "2024-01-15",
        assessment_method: "quiz",
        prerequisites_met: true,
        decay_risk: 0.1
      },
      "css-styling": {
        topic_id: "css-styling",
        topic_name: "CSS Styling",
        level: "intermediate",
        confidence: 0.85,
        last_assessed: "2024-01-18",
        assessment_method: "demonstration",
        prerequisites_met: true,
        decay_risk: 0.15
      },
      "js-fundamentals": {
        topic_id: "js-fundamentals",
        topic_name: "JavaScript Fundamentals",
        level: "beginner",
        confidence: 0.45,
        last_assessed: "2024-01-20",
        assessment_method: "inferred",
        prerequisites_met: true,
        time_to_next_level: 4,
        decay_risk: 0.3
      }
    };
    let preferences = {
      preferred_analogies: ["cooking", "music", "building"],
      modality_preferences: [
        {
          type: "visual",
          effectiveness: 0.9,
          current_availability: true
        },
        {
          type: "kinesthetic",
          effectiveness: 0.8,
          current_availability: true
        },
        {
          type: "reading",
          effectiveness: 0.5,
          current_availability: true
        },
        {
          type: "auditory",
          effectiveness: 0.4,
          current_availability: false,
          notes: "In noisy environment"
        }
      ],
      pace_sensitivity: 0.7,
      challenge_appetite: 6,
      feedback_granularity: "high",
      session_duration_preference: 30,
      break_frequency: "moderate",
      error_tolerance: "high",
      theory_practice_balance: "interleaved"
    };
    let adaptations = [
      {
        type: "analogy_substitution",
        reason: "User prefers cooking analogies",
        original_value: "Functions are like machines",
        adapted_value: "Functions are like recipes - you provide ingredients (parameters) and get a dish (return value)"
      },
      {
        type: "modality_change",
        reason: "High visual effectiveness + noisy environment (no audio)",
        original_value: "Video with narration",
        adapted_value: "Interactive visual tutorial with captions"
      },
      {
        type: "pace_adjustment",
        reason: "Current topic is above comfort level (JS is new)",
        original_value: "Standard pacing",
        adapted_value: "20% slower with extra examples"
      }
    ];
    let selectedPreset = void 0;
    const learnerPresets = [
      {
        id: "visual-learner",
        name: "Visual Learner",
        description: "Prefers diagrams, videos, and visual content",
        icon: "fa-eye",
        data: {
          preferred_analogies: ["architecture", "maps", "diagrams"],
          modality_preferences: [
            {
              type: "visual",
              effectiveness: 0.95,
              current_availability: true
            },
            {
              type: "kinesthetic",
              effectiveness: 0.6,
              current_availability: true
            },
            {
              type: "reading",
              effectiveness: 0.5,
              current_availability: true
            },
            {
              type: "auditory",
              effectiveness: 0.4,
              current_availability: true
            }
          ],
          challenge_appetite: 6,
          feedback_granularity: "high",
          session_duration_preference: 45,
          break_frequency: "minimal"
        },
        tags: ["visual", "focused"]
      },
      {
        id: "hands-on-learner",
        name: "Hands-On Learner",
        description: "Learns by doing, prefers interactive exercises",
        icon: "fa-hand",
        data: {
          preferred_analogies: ["building", "cooking", "crafting"],
          modality_preferences: [
            {
              type: "kinesthetic",
              effectiveness: 0.9,
              current_availability: true
            },
            {
              type: "visual",
              effectiveness: 0.7,
              current_availability: true
            },
            {
              type: "auditory",
              effectiveness: 0.5,
              current_availability: true
            },
            {
              type: "reading",
              effectiveness: 0.3,
              current_availability: true
            }
          ],
          challenge_appetite: 7,
          feedback_granularity: "high",
          session_duration_preference: 30,
          break_frequency: "frequent"
        },
        tags: ["kinesthetic", "interactive"]
      },
      {
        id: "reader-learner",
        name: "Reader Learner",
        description: "Prefers text-based content and documentation",
        icon: "fa-book",
        data: {
          preferred_analogies: ["literature", "history", "stories"],
          modality_preferences: [
            {
              type: "reading",
              effectiveness: 0.9,
              current_availability: true
            },
            {
              type: "visual",
              effectiveness: 0.6,
              current_availability: true
            },
            {
              type: "auditory",
              effectiveness: 0.7,
              current_availability: true
            },
            {
              type: "kinesthetic",
              effectiveness: 0.4,
              current_availability: true
            }
          ],
          challenge_appetite: 5,
          feedback_granularity: "high",
          session_duration_preference: 60,
          break_frequency: "moderate"
        },
        tags: ["text", "deep-dive"]
      },
      {
        id: "audio-limited",
        name: "Audio Unavailable",
        description: "In noisy environment, no audio content",
        icon: "fa-volume-xmark",
        data: {
          preferred_analogies: ["cooking", "music", "building"],
          modality_preferences: [
            {
              type: "visual",
              effectiveness: 0.9,
              current_availability: true
            },
            {
              type: "kinesthetic",
              effectiveness: 0.8,
              current_availability: true
            },
            {
              type: "reading",
              effectiveness: 0.5,
              current_availability: true
            },
            {
              type: "auditory",
              effectiveness: 0.4,
              current_availability: false,
              notes: "In noisy environment"
            }
          ],
          challenge_appetite: 6,
          feedback_granularity: "high",
          session_duration_preference: 30,
          break_frequency: "moderate"
        },
        tags: ["contextual", "adaptive"]
      }
    ];
    function applyPreset(preset) {
      preferences = { ...preferences, ...preset.data };
      selectedPreset = preset.id;
      updateAdaptations();
    }
    function updateAdaptations() {
      const newAdaptations = [];
      if (preferences.preferred_analogies.includes("cooking")) {
        newAdaptations.push({
          type: "analogy_substitution",
          reason: "User prefers cooking analogies",
          original_value: "Functions are like machines",
          adapted_value: "Functions are like recipes - you provide ingredients (parameters) and get a dish (return value)"
        });
      }
      const bestModality = preferences.modality_preferences.filter((m) => m.current_availability).sort((a, b) => b.effectiveness - a.effectiveness)[0];
      const unavailableModality = preferences.modality_preferences.find((m) => !m.current_availability);
      if (unavailableModality) {
        newAdaptations.push({
          type: "modality_change",
          reason: `${unavailableModality.type} unavailable (${unavailableModality.notes || "context"})`,
          original_value: `${unavailableModality.type} content`,
          adapted_value: `${bestModality.type} alternative with captions`
        });
      }
      newAdaptations.push({
        type: "pace_adjustment",
        reason: `Challenge appetite: ${preferences.challenge_appetite}/9`,
        original_value: "Standard pacing",
        adapted_value: preferences.challenge_appetite > 6 ? "Faster with fewer examples" : "Deliberate with more examples"
      });
      adaptations = newAdaptations;
    }
    const auditEntries = [
      // Shared: What the learner profile reveals
      {
        field: "Preferred Analogies",
        category: "shared",
        value: preferences.preferred_analogies.join(", "),
        reason: "Used to select relatable examples"
      },
      {
        field: "Best Modality",
        category: "shared",
        value: `${preferences.modality_preferences.sort((a, b) => b.effectiveness - a.effectiveness)[0].type} (${Math.round(preferences.modality_preferences.sort((a, b) => b.effectiveness - a.effectiveness)[0].effectiveness * 100)}%)`,
        reason: "Determines content format selection"
      },
      {
        field: "Challenge Appetite",
        category: "shared",
        value: `${preferences.challenge_appetite}/9`,
        reason: "Affects difficulty progression"
      },
      {
        field: "Session Duration",
        category: "shared",
        value: `${preferences.session_duration_preference} min`,
        reason: "Sets break reminders and content chunking"
      },
      // Influenced: How adaptations affect experience
      {
        field: "Adaptations Applied",
        category: "influenced",
        value: `${adaptations.length} active`,
        reason: "Real-time content modifications"
      },
      {
        field: "Mastery Levels",
        category: "influenced",
        value: `${Object.keys(mastery).length} topics tracked`,
        reason: "Determines skip/reinforce decisions"
      },
      {
        field: "Path Progress",
        category: "influenced",
        value: `${path.completed_hours}/${path.estimated_total_hours}h`,
        reason: "Adjusts time estimates"
      },
      // Withheld: Internal processing
      {
        field: "Effectiveness Scores",
        category: "withheld",
        reason: "Raw modality scores kept internal"
      },
      {
        field: "Decay Risk Calculations",
        category: "withheld",
        reason: "Knowledge decay predictions internal"
      }
    ];
    head("1iy7b78", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Adaptive Learning Paths - VCP Learning</title>`);
      });
      $$renderer3.push(`<meta name="description" content="See how VCP enables personalized learning paths with real-time adaptation."/>`);
    });
    {
      let children = function($$renderer3) {
        $$renderer3.push(`<div class="adaptive-layout svelte-1iy7b78"><div class="path-section svelte-1iy7b78">`);
        LearningPathViz($$renderer3, { path, mastery });
        $$renderer3.push(`<!----></div> <div class="context-section svelte-1iy7b78">`);
        PresetLoader($$renderer3, {
          presets: learnerPresets,
          selected: selectedPreset,
          onselect: (p) => applyPreset(p),
          title: "Learner Profiles"
        });
        $$renderer3.push(`<!----> `);
        AuditPanel($$renderer3, { entries: auditEntries, title: "Learning Context Audit" });
        $$renderer3.push(`<!----> <div class="profile-card svelte-1iy7b78"><h3 class="svelte-1iy7b78">Learner Profile (from VCP)</h3> <div class="profile-section svelte-1iy7b78"><h4 class="svelte-1iy7b78">Preferred Analogies</h4> <div class="chips svelte-1iy7b78"><!--[-->`);
        const each_array = ensure_array_like(preferences.preferred_analogies);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let analogy = each_array[$$index];
          $$renderer3.push(`<span class="chip svelte-1iy7b78">${escape_html(analogy)}</span>`);
        }
        $$renderer3.push(`<!--]--></div></div> <div class="profile-section svelte-1iy7b78"><h4 class="svelte-1iy7b78">Modality Effectiveness</h4> <div class="modalities svelte-1iy7b78"><!--[-->`);
        const each_array_1 = ensure_array_like(preferences.modality_preferences);
        for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
          let mod = each_array_1[$$index_1];
          $$renderer3.push(`<div class="modality-row svelte-1iy7b78"><span class="mod-type svelte-1iy7b78">${escape_html(mod.type)}</span> <div class="mod-bar svelte-1iy7b78"><div${attr_class("mod-fill svelte-1iy7b78", void 0, { "unavailable": !mod.current_availability })}${attr_style(`width: ${stringify(mod.effectiveness * 100)}%`)}></div></div> <span class="mod-value svelte-1iy7b78">${escape_html(Math.round(mod.effectiveness * 100))}%</span> `);
          if (!mod.current_availability) {
            $$renderer3.push("<!--[-->");
            $$renderer3.push(`<span class="mod-note svelte-1iy7b78"${attr("title", mod.notes)}><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i></span>`);
          } else {
            $$renderer3.push("<!--[!-->");
          }
          $$renderer3.push(`<!--]--></div>`);
        }
        $$renderer3.push(`<!--]--></div></div> <div class="profile-section svelte-1iy7b78"><h4 class="svelte-1iy7b78">Learning Style</h4> <div class="style-grid svelte-1iy7b78"><div class="style-item svelte-1iy7b78"><span class="style-label svelte-1iy7b78">Challenge</span> <span class="style-value svelte-1iy7b78">${escape_html(preferences.challenge_appetite)}/9</span></div> <div class="style-item svelte-1iy7b78"><span class="style-label svelte-1iy7b78">Feedback</span> <span class="style-value svelte-1iy7b78">${escape_html(preferences.feedback_granularity)}</span></div> <div class="style-item svelte-1iy7b78"><span class="style-label svelte-1iy7b78">Sessions</span> <span class="style-value svelte-1iy7b78">${escape_html(preferences.session_duration_preference)}m</span></div> <div class="style-item svelte-1iy7b78"><span class="style-label svelte-1iy7b78">Breaks</span> <span class="style-value svelte-1iy7b78">${escape_html(preferences.break_frequency)}</span></div></div></div></div> <div class="adaptations-card svelte-1iy7b78"><h3 class="svelte-1iy7b78">Adaptations Applied</h3> <p class="adaptations-desc svelte-1iy7b78">VCP context enables these real-time adjustments to your learning experience:</p> <div class="adaptations-list svelte-1iy7b78"><!--[-->`);
        const each_array_2 = ensure_array_like(adaptations);
        for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
          let adaptation = each_array_2[$$index_2];
          $$renderer3.push(`<div class="adaptation-item svelte-1iy7b78"><div class="adaptation-header svelte-1iy7b78"><span class="adaptation-type svelte-1iy7b78">${escape_html(adaptation.type.replace(/_/g, " "))}</span> <span class="adaptation-reason svelte-1iy7b78">${escape_html(adaptation.reason)}</span></div> <div class="adaptation-change svelte-1iy7b78"><div class="before svelte-1iy7b78"><span class="change-label svelte-1iy7b78">Before:</span> <span class="svelte-1iy7b78">${escape_html(adaptation.original_value)}</span></div> <div class="arrow svelte-1iy7b78">→</div> <div class="after svelte-1iy7b78"><span class="change-label svelte-1iy7b78">After:</span> <span class="svelte-1iy7b78">${escape_html(adaptation.adapted_value)}</span></div></div></div>`);
        }
        $$renderer3.push(`<!--]--></div></div> <div class="explanation-card svelte-1iy7b78"><h3 class="svelte-1iy7b78">How VCP Enables This</h3> <ul class="svelte-1iy7b78"><li class="svelte-1iy7b78"><strong>Analogy Preferences</strong> → Content automatically uses familiar domains</li> <li class="svelte-1iy7b78"><strong>Modality Effectiveness</strong> → Selects optimal content format</li> <li class="svelte-1iy7b78"><strong>Current Availability</strong> → Adapts to context (noisy = no audio)</li> <li class="svelte-1iy7b78"><strong>Pace Sensitivity</strong> → Adjusts speed based on mastery + load</li> <li class="svelte-1iy7b78"><strong>Mastery Levels</strong> → Skips known material, reinforces weak areas</li></ul> <p class="key-insight svelte-1iy7b78"><strong>Key:</strong> These preferences travel WITH the learner across platforms.
						A VCP-enabled math tutor knows you prefer cooking analogies even though you
						learned that preference on a coding platform.</p></div></div></div>`);
      };
      DemoContainer($$renderer2, {
        title: "Adaptive Learning Paths",
        description: "Learning paths that adapt to your preferences, pace, and context in real-time.",
        children
      });
    }
  });
}
export {
  _page as default
};
