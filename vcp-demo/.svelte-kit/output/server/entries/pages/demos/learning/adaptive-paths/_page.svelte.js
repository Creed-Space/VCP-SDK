import { c as attr_style, s as stringify, e as ensure_array_like, b as attr_class, a as attr, h as head } from "../../../../../chunks/index2.js";
import { D as DemoContainer } from "../../../../../chunks/DemoContainer.js";
import { $ as escape_html } from "../../../../../chunks/context.js";
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
      return "★".repeat(difficulty) + "☆".repeat(5 - difficulty);
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
      $$renderer2.push(`<!--]--></div> <div class="node-content svelte-1penjlx"><span class="topic-name svelte-1penjlx">${escape_html(topic.name)}</span> <div class="topic-meta svelte-1penjlx"><span class="difficulty svelte-1penjlx">${escape_html(getDifficultyStars(topic.difficulty))}</span> <span class="duration">${escape_html(topic.estimated_hours)}h</span></div> `);
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
function _page($$renderer) {
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
    challenge_appetite: 6,
    feedback_granularity: "high",
    session_duration_preference: 30,
    break_frequency: "moderate"
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
  head("1iy7b78", $$renderer, ($$renderer2) => {
    $$renderer2.title(($$renderer3) => {
      $$renderer3.push(`<title>Adaptive Learning Paths - VCP Learning</title>`);
    });
    $$renderer2.push(`<meta name="description" content="See how VCP enables personalized learning paths with real-time adaptation."/>`);
  });
  {
    let children = function($$renderer2) {
      $$renderer2.push(`<div class="adaptive-layout svelte-1iy7b78"><div class="path-section svelte-1iy7b78">`);
      LearningPathViz($$renderer2, { path, mastery });
      $$renderer2.push(`<!----></div> <div class="context-section svelte-1iy7b78"><div class="profile-card svelte-1iy7b78"><h3 class="svelte-1iy7b78">Learner Profile (from VCP)</h3> <div class="profile-section svelte-1iy7b78"><h4 class="svelte-1iy7b78">Preferred Analogies</h4> <div class="chips svelte-1iy7b78"><!--[-->`);
      const each_array = ensure_array_like(preferences.preferred_analogies);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let analogy = each_array[$$index];
        $$renderer2.push(`<span class="chip svelte-1iy7b78">${escape_html(analogy)}</span>`);
      }
      $$renderer2.push(`<!--]--></div></div> <div class="profile-section svelte-1iy7b78"><h4 class="svelte-1iy7b78">Modality Effectiveness</h4> <div class="modalities svelte-1iy7b78"><!--[-->`);
      const each_array_1 = ensure_array_like(preferences.modality_preferences);
      for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
        let mod = each_array_1[$$index_1];
        $$renderer2.push(`<div class="modality-row svelte-1iy7b78"><span class="mod-type svelte-1iy7b78">${escape_html(mod.type)}</span> <div class="mod-bar svelte-1iy7b78"><div${attr_class("mod-fill svelte-1iy7b78", void 0, { "unavailable": !mod.current_availability })}${attr_style(`width: ${stringify(mod.effectiveness * 100)}%`)}></div></div> <span class="mod-value svelte-1iy7b78">${escape_html(Math.round(mod.effectiveness * 100))}%</span> `);
        if (!mod.current_availability) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="mod-note svelte-1iy7b78"${attr("title", mod.notes)}>⚠</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]--></div></div> <div class="profile-section svelte-1iy7b78"><h4 class="svelte-1iy7b78">Learning Style</h4> <div class="style-grid svelte-1iy7b78"><div class="style-item svelte-1iy7b78"><span class="style-label svelte-1iy7b78">Challenge</span> <span class="style-value svelte-1iy7b78">${escape_html(preferences.challenge_appetite)}/9</span></div> <div class="style-item svelte-1iy7b78"><span class="style-label svelte-1iy7b78">Feedback</span> <span class="style-value svelte-1iy7b78">${escape_html(preferences.feedback_granularity)}</span></div> <div class="style-item svelte-1iy7b78"><span class="style-label svelte-1iy7b78">Sessions</span> <span class="style-value svelte-1iy7b78">${escape_html(preferences.session_duration_preference)}m</span></div> <div class="style-item svelte-1iy7b78"><span class="style-label svelte-1iy7b78">Breaks</span> <span class="style-value svelte-1iy7b78">${escape_html(preferences.break_frequency)}</span></div></div></div></div> <div class="adaptations-card svelte-1iy7b78"><h3 class="svelte-1iy7b78">Adaptations Applied</h3> <p class="adaptations-desc svelte-1iy7b78">VCP context enables these real-time adjustments to your learning experience:</p> <div class="adaptations-list svelte-1iy7b78"><!--[-->`);
      const each_array_2 = ensure_array_like(adaptations);
      for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
        let adaptation = each_array_2[$$index_2];
        $$renderer2.push(`<div class="adaptation-item svelte-1iy7b78"><div class="adaptation-header svelte-1iy7b78"><span class="adaptation-type svelte-1iy7b78">${escape_html(adaptation.type.replace(/_/g, " "))}</span> <span class="adaptation-reason svelte-1iy7b78">${escape_html(adaptation.reason)}</span></div> <div class="adaptation-change svelte-1iy7b78"><div class="before svelte-1iy7b78"><span class="change-label svelte-1iy7b78">Before:</span> <span class="svelte-1iy7b78">${escape_html(adaptation.original_value)}</span></div> <div class="arrow svelte-1iy7b78">→</div> <div class="after svelte-1iy7b78"><span class="change-label svelte-1iy7b78">After:</span> <span class="svelte-1iy7b78">${escape_html(adaptation.adapted_value)}</span></div></div></div>`);
      }
      $$renderer2.push(`<!--]--></div></div> <div class="explanation-card svelte-1iy7b78"><h3 class="svelte-1iy7b78">How VCP Enables This</h3> <ul class="svelte-1iy7b78"><li class="svelte-1iy7b78"><strong>Analogy Preferences</strong> → Content automatically uses familiar domains</li> <li class="svelte-1iy7b78"><strong>Modality Effectiveness</strong> → Selects optimal content format</li> <li class="svelte-1iy7b78"><strong>Current Availability</strong> → Adapts to context (noisy = no audio)</li> <li class="svelte-1iy7b78"><strong>Pace Sensitivity</strong> → Adjusts speed based on mastery + load</li> <li class="svelte-1iy7b78"><strong>Mastery Levels</strong> → Skips known material, reinforces weak areas</li></ul> <p class="key-insight svelte-1iy7b78"><strong>Key:</strong> These preferences travel WITH the learner across platforms.
						A VCP-enabled math tutor knows you prefer cooking analogies even though you
						learned that preference on a coding platform.</p></div></div></div>`);
    };
    DemoContainer($$renderer, {
      title: "Adaptive Learning Paths",
      description: "Learning paths that adapt to your preferences, pace, and context in real-time.",
      children
    });
  }
}
export {
  _page as default
};
