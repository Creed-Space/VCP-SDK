import { a2 as head, a0 as attr, a3 as escape_html, a8 as ensure_array_like, a6 as attr_style, a7 as stringify } from "../../../../../chunks/index2.js";
import { D as DemoContainer } from "../../../../../chunks/DemoContainer.js";
import { M as MultiAgentArena, A as AgentChat } from "../../../../../chunks/MultiAgentArena.js";
import { P as PresetLoader } from "../../../../../chunks/PresetLoader.js";
import { A as AuditPanel } from "../../../../../chunks/AuditPanel.js";
const policyAgents = [
  {
    agent_id: "parent_rep",
    display_name: "Maria",
    role: "voter",
    avatar: '<i class="fa-solid fa-people-group" aria-hidden="true"></i>',
    color: "#e74c3c",
    constitution: {
      id: "family-advocate",
      version: "1.0",
      persona: "godparent",
      adherence: 4
    }
  },
  {
    agent_id: "elder_rep",
    display_name: "Harold",
    role: "voter",
    avatar: '<i class="fa-solid fa-person-cane" aria-hidden="true"></i>',
    color: "#3498db",
    constitution: {
      id: "accessibility-first",
      version: "1.0",
      persona: "sentinel",
      adherence: 4
    }
  },
  {
    agent_id: "youth_rep",
    display_name: "Jordan",
    role: "voter",
    avatar: '<i class="fa-solid fa-person-running" aria-hidden="true"></i>',
    color: "#2ecc71",
    constitution: {
      id: "active-lifestyle",
      version: "1.0",
      persona: "muse",
      adherence: 3
    }
  },
  {
    agent_id: "nature_rep",
    display_name: "Sage",
    role: "voter",
    avatar: '<i class="fa-solid fa-tree" aria-hidden="true"></i>',
    color: "#27ae60",
    constitution: {
      id: "environmental-steward",
      version: "1.0",
      persona: "sentinel",
      adherence: 5
    }
  },
  {
    agent_id: "moderator",
    display_name: "Council Chair",
    role: "mediator",
    avatar: '<i class="fa-solid fa-scale-balanced" aria-hidden="true"></i>',
    color: "#9b59b6",
    constitution: {
      id: "fair-process",
      version: "1.0",
      persona: "ambassador",
      adherence: 5
    }
  }
];
const policyOptions = [
  {
    id: "option_playground",
    name: "Playground Expansion",
    description: "Expand the children's playground with new equipment and safety surfacing.",
    proposer: "parent_rep",
    pros: ["Safe play space for children", "Encourages family visits", "Modern equipment"],
    cons: ["Limited appeal to other age groups", "Higher maintenance costs"],
    vcp_aligned_with: ["family_safety", "community_gathering", "child_development"]
  },
  {
    id: "option_fitness",
    name: "Fitness Trail",
    description: "Install an outdoor fitness trail with exercise stations around the park perimeter.",
    proposer: "youth_rep",
    pros: ["Free exercise option", "Appeals to all ages", "Low maintenance"],
    cons: ["Reduces green space", "May attract crowds"],
    vcp_aligned_with: ["health_wellness", "accessibility", "community_fitness"]
  },
  {
    id: "option_garden",
    name: "Community Garden",
    description: "Convert a section to community garden plots with a small greenhouse.",
    proposer: "nature_rep",
    pros: ["Environmental education", "Fresh produce", "Community bonding"],
    cons: ["Ongoing management needed", "Limited participants"],
    vcp_aligned_with: ["environmental_stewardship", "food_security", "education"]
  },
  {
    id: "option_accessible",
    name: "Accessibility Upgrade",
    description: "Add paved paths, benches, shade structures, and accessible facilities throughout.",
    proposer: "elder_rep",
    pros: ["Inclusive for all abilities", "Improves existing amenities", "Benefits everyone"],
    cons: ['Less "new" appeal', "May seem incremental"],
    vcp_aligned_with: ["accessibility", "dignity", "universal_design"]
  }
];
const policyScenario = [
  {
    round: 1,
    actor: "moderator",
    action: "speak",
    content: "Welcome to the park renovation deliberation. We have $150,000 budget and four proposals. Let's hear from each advocate.",
    sentiment: "neutral",
    vcpContextShared: ["budget", "process_rules"],
    vcpContextHidden: [],
    explanation: "Moderator sets context. Budget and rules are shared with all."
  },
  {
    round: 2,
    actor: "parent_rep",
    action: "speak",
    content: "The playground is the heart of our family community. Safe, engaging play equipment brings families together daily.",
    sentiment: "support",
    referencesOption: "option_playground",
    vcpContextShared: ["priority: family_safety", "goal: community_gathering"],
    vcpContextHidden: ["personal_family_situation", "specific_safety_concerns"],
    explanation: "Maria advocates for playground. Her family focus is visible; personal family details are private."
  },
  {
    round: 3,
    actor: "elder_rep",
    action: "speak",
    content: "Before we add new features, we should ensure everyone can access what we have. Many neighbors can't navigate the current paths.",
    sentiment: "support",
    referencesOption: "option_accessible",
    vcpContextShared: ["priority: accessibility", "value: inclusion"],
    vcpContextHidden: ["personal_mobility_challenges", "health_conditions"],
    explanation: "Harold speaks for accessibility. His advocacy is public; any personal mobility issues remain private."
  },
  {
    round: 4,
    actor: "youth_rep",
    action: "speak",
    content: "A fitness trail gives everyone a free gym. It's not just for young people—I see folks of all ages who would use it.",
    sentiment: "support",
    referencesOption: "option_fitness",
    vcpContextShared: ["priority: health_wellness", "goal: active_community"],
    vcpContextHidden: ["personal_fitness_routine", "gym_membership_status"],
    explanation: "Jordan promotes fitness. Their health values are shared; personal workout habits are not."
  },
  {
    round: 5,
    actor: "nature_rep",
    action: "speak",
    content: "A community garden teaches sustainability, provides fresh food, and creates green jobs for local youth.",
    sentiment: "support",
    referencesOption: "option_garden",
    vcpContextShared: ["priority: environmental_education", "value: sustainability"],
    vcpContextHidden: ["personal_gardening_experience", "dietary_preferences"],
    explanation: "Sage advocates for garden. Environmental values are visible; personal practices are private."
  },
  {
    round: 6,
    actor: "elder_rep",
    action: "speak",
    content: "I want to support the playground, but only if it includes accessible paths and seating for grandparents.",
    sentiment: "question",
    referencesOption: "option_playground",
    vcpContextShared: ["condition: accessibility_integration"],
    vcpContextHidden: ["personal_grandparent_role"],
    explanation: "Harold offers conditional support. His requirement is public; personal family role is private."
  },
  {
    round: 7,
    actor: "parent_rep",
    action: "amend",
    content: "I propose we combine: Playground with accessible paths and seating areas. Grandparents should enjoy watching their grandchildren safely.",
    referencesOption: "option_playground",
    vcpContextShared: ["compromise: integrated_design"],
    vcpContextHidden: ["personal_parent_experiences"],
    explanation: "Maria proposes integration. The compromise is public; personal parenting experiences are private."
  },
  {
    round: 8,
    actor: "youth_rep",
    action: "speak",
    content: "Could the fitness trail connect to the playground? Parents could exercise while kids play.",
    sentiment: "support",
    vcpContextShared: ["suggestion: multi_use_design"],
    vcpContextHidden: ["personal_childcare_constraints"],
    explanation: "Jordan suggests synergy. The design idea is shared; any personal constraints are not."
  },
  {
    round: 9,
    actor: "nature_rep",
    action: "speak",
    content: "What if the garden plots were along the fitness trail? Exercise stations with educational signage about plants.",
    sentiment: "neutral",
    vcpContextShared: ["integration: education_wellness"],
    vcpContextHidden: ["personal_teaching_background"],
    explanation: "Sage proposes integration. The concept is public; personal expertise is private."
  },
  {
    round: 10,
    actor: "moderator",
    action: "speak",
    content: "We're seeing convergence toward an integrated design. Let me propose a combined option: Accessible paths connecting playground, fitness stations, and small garden area.",
    sentiment: "neutral",
    vcpContextShared: ["synthesis: combined_proposal"],
    vcpContextHidden: [],
    explanation: "Moderator synthesizes. The combined proposal emerges from shared preferences."
  },
  {
    round: 11,
    actor: "moderator",
    action: "call_vote",
    content: "All in favor of the integrated park design with accessible playground, fitness trail, and community garden section?",
    vcpContextShared: ["process: final_vote"],
    vcpContextHidden: [],
    explanation: "Vote called on synthesized option that addresses multiple stakeholder values."
  }
];
const finalVotes = [
  {
    voter: "parent_rep",
    option_id: "integrated",
    timestamp: (/* @__PURE__ */ new Date()).toISOString(),
    public_rationale: "This gives our families a safe, accessible play area with room to grow.",
    private_rationale: "My daughter with mobility challenges can finally play with her friends"
  },
  {
    voter: "elder_rep",
    option_id: "integrated",
    timestamp: (/* @__PURE__ */ new Date()).toISOString(),
    public_rationale: "The accessibility focus is maintained while adding new amenities.",
    private_rationale: "I can finally take my walker to watch the grandkids"
  },
  {
    voter: "youth_rep",
    option_id: "integrated",
    timestamp: (/* @__PURE__ */ new Date()).toISOString(),
    public_rationale: "Free fitness for everyone, plus connected community spaces.",
    private_rationale: "Saves me $50/month gym membership"
  },
  {
    voter: "nature_rep",
    option_id: "integrated",
    timestamp: (/* @__PURE__ */ new Date()).toISOString(),
    public_rationale: "The garden section provides environmental education within an active park.",
    private_rationale: "Smaller than I hoped, but better than nothing"
  }
];
const learningPoints = [
  "Each stakeholder shared their VALUES and PRIORITIES publicly (family safety, accessibility, health, environment)",
  "PERSONAL REASONS for those priorities remained private (health conditions, family situations, financial constraints)",
  "The moderator could synthesize a compromise because they understood what each party valued",
  "Private rationales (elderly rep's mobility issues, parent's daughter's disability) never entered the public record",
  "VCP enabled preference aggregation while protecting the dignity of each participant's personal circumstances"
];
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let currentStep = 0;
    let isPlaying = false;
    let messages = [];
    let currentSpeaker = null;
    let showVotes = false;
    let playInterval = null;
    function getAgent(actorId) {
      return policyAgents.find((a) => a.agent_id === actorId) || policyAgents[0];
    }
    function stepForward() {
      if (currentStep < policyScenario.length) {
        const step = policyScenario[currentStep];
        currentSpeaker = step.actor;
        messages = [
          ...messages,
          {
            id: `msg_${currentStep}`,
            sender: getAgent(step.actor),
            content: step.content,
            timestamp: (/* @__PURE__ */ new Date()).toISOString(),
            vcpContextShared: step.vcpContextShared,
            vcpContextHidden: step.vcpContextHidden,
            action: step.action
          }
        ];
        currentStep++;
        if (currentStep >= policyScenario.length) {
          setTimeout(
            () => {
              showVotes = true;
            },
            1e3
          );
        }
        setTimeout(
          () => {
            currentSpeaker = null;
          },
          1500
        );
      } else {
        stopPlaying();
      }
    }
    function stopPlaying() {
      isPlaying = false;
      if (playInterval) {
        clearInterval(playInterval);
        playInterval = null;
      }
    }
    function reset() {
      stopPlaying();
      currentStep = 0;
      messages = [];
      currentSpeaker = null;
      showVotes = false;
    }
    let selectedPreset = void 0;
    let playbackSpeed = 3e3;
    const policyPresets = [
      {
        id: "careful",
        name: "Careful",
        description: "Thoughtful deliberation pace",
        icon: "fa-scale-balanced",
        data: { speed: 4500 },
        tags: ["educational"]
      },
      {
        id: "normal",
        name: "Normal",
        description: "Standard deliberation pace",
        icon: "fa-play",
        data: { speed: 3e3 },
        tags: ["balanced"]
      },
      {
        id: "fast",
        name: "Fast",
        description: "Quick policy overview",
        icon: "fa-forward",
        data: { speed: 1500 },
        tags: ["quick"]
      }
    ];
    function applyPreset(preset) {
      playbackSpeed = preset.data.speed;
      selectedPreset = preset.id;
      if (isPlaying) {
        stopPlaying();
        startPlayingWithSpeed();
      }
    }
    function startPlayingWithSpeed() {
      if (currentStep >= policyScenario.length) {
        reset();
      }
      isPlaying = true;
      playInterval = setInterval(
        () => {
          stepForward();
          if (currentStep >= policyScenario.length) {
            stopPlaying();
          }
        },
        playbackSpeed
      );
    }
    const auditEntries = (() => {
      const entries = [];
      const contributionCounts = policyAgents.reduce(
        (acc, agent) => {
          acc[agent.agent_id] = messages.filter((m) => m.sender.agent_id === agent.agent_id).length;
          return acc;
        },
        {}
      );
      entries.push({
        field: "Policy Options",
        category: "shared",
        value: `${policyOptions.length} proposals`,
        reason: "All options publicly presented"
      });
      entries.push({
        field: "Stakeholder Input",
        category: "shared",
        value: `${messages.length} statements`,
        reason: "Public positions and arguments"
      });
      entries.push({
        field: "Value Alignments",
        category: "shared",
        reason: "Which values each proposal serves"
      });
      entries.push({
        field: "Deliberation Phase",
        category: "influenced",
        value: `Step ${currentStep}/${policyScenario.length}`,
        reason: "Progress affects consensus building"
      });
      entries.push({
        field: "Participation Balance",
        category: "influenced",
        value: Object.values(contributionCounts).join("/") + " msgs",
        reason: "Equal voice opportunity monitored"
      });
      entries.push({
        field: "Consensus Status",
        category: "influenced",
        value: showVotes ? "Achieved" : "Building",
        reason: "Positions converging through dialogue"
      });
      entries.push({
        field: "Personal Circumstances",
        category: "withheld",
        reason: "Individual life situations protected"
      });
      entries.push({
        field: "Private Rationales",
        category: "withheld",
        reason: "Personal reasons for votes never disclosed"
      });
      entries.push({
        field: "Political Considerations",
        category: "withheld",
        reason: "Career/reputation concerns hidden"
      });
      entries.push({
        field: "Emotional Stakes",
        category: "withheld",
        reason: "Personal investment in outcomes protected"
      });
      return entries;
    })();
    head("kkelhp", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Policy Design Demo - VCP Multi-Agent</title>`);
      });
      $$renderer3.push(`<meta name="description" content="See how VCP enables preference aggregation while protecting private rationales."/>`);
    });
    {
      let controls = function($$renderer3) {
        $$renderer3.push(`<button class="control-btn"${attr("disabled", currentStep >= policyScenario.length && !isPlaying, true)}><span class="control-icon">${escape_html(isPlaying ? "⏸" : "▶")}</span> <span>${escape_html(isPlaying ? "Pause" : "Play")}</span></button> <button class="control-btn"${attr("disabled", isPlaying || currentStep >= policyScenario.length, true)}><span class="control-icon">⏭</span> <span>Step</span></button>`);
      }, children = function($$renderer3) {
        $$renderer3.push(`<div class="policy-layout svelte-kkelhp"><div class="controls-row svelte-kkelhp">`);
        PresetLoader($$renderer3, {
          presets: policyPresets,
          selected: selectedPreset,
          onselect: (p) => applyPreset(p),
          title: "Deliberation Pace"
        });
        $$renderer3.push(`<!----> `);
        AuditPanel($$renderer3, {
          entries: auditEntries,
          title: "VCP Context Audit",
          compact: true
        });
        $$renderer3.push(`<!----></div> <div class="options-grid svelte-kkelhp"><!--[-->`);
        const each_array = ensure_array_like(policyOptions);
        for (let $$index_1 = 0, $$length = each_array.length; $$index_1 < $$length; $$index_1++) {
          let option = each_array[$$index_1];
          $$renderer3.push(`<div class="option-card svelte-kkelhp"><h4 class="svelte-kkelhp">${escape_html(option.name)}</h4> <p class="option-desc svelte-kkelhp">${escape_html(option.description)}</p> <div class="option-proposer svelte-kkelhp">Proposed by ${escape_html(policyAgents.find((a) => a.agent_id === option.proposer)?.display_name)}</div> <div class="option-values svelte-kkelhp"><!--[-->`);
          const each_array_1 = ensure_array_like(option.vcp_aligned_with);
          for (let $$index = 0, $$length2 = each_array_1.length; $$index < $$length2; $$index++) {
            let value = each_array_1[$$index];
            $$renderer3.push(`<span class="value-chip svelte-kkelhp">${escape_html(value.replace(/_/g, " "))}</span>`);
          }
          $$renderer3.push(`<!--]--></div></div>`);
        }
        $$renderer3.push(`<!--]--></div> <div class="arena-section svelte-kkelhp">`);
        MultiAgentArena($$renderer3, {
          agents: policyAgents,
          currentSpeaker,
          layout: "row",
          showSharedFields: false
        });
        $$renderer3.push(`<!----></div> <div class="chat-section svelte-kkelhp">`);
        AgentChat($$renderer3, {
          messages,
          agents: policyAgents,
          currentSpeaker,
          showContextIndicators: true
        });
        $$renderer3.push(`<!----></div> `);
        if (showVotes) {
          $$renderer3.push("<!--[-->");
          $$renderer3.push(`<div class="votes-section svelte-kkelhp"><h3 class="svelte-kkelhp"><i class="fa-solid fa-box-ballot" aria-hidden="true"></i> Final Vote: Integrated Park Design</h3> <p class="vote-subtitle svelte-kkelhp">Unanimous approval achieved through deliberation</p> <div class="votes-grid svelte-kkelhp"><!--[-->`);
          const each_array_2 = ensure_array_like(finalVotes);
          for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
            let vote = each_array_2[$$index_2];
            const agent = policyAgents.find((a) => a.agent_id === vote.voter);
            $$renderer3.push(`<div class="vote-card svelte-kkelhp"><div class="vote-header svelte-kkelhp"><span class="vote-avatar svelte-kkelhp">${escape_html(agent?.avatar)}</span> <span class="vote-name svelte-kkelhp"${attr_style(`color: ${stringify(agent?.color)}`)}>${escape_html(agent?.display_name)}</span> <span class="vote-icon svelte-kkelhp"><i class="fa-solid fa-check" aria-hidden="true"></i></span></div> <div class="vote-public svelte-kkelhp"><span class="vote-label svelte-kkelhp">Public Rationale</span> <p class="svelte-kkelhp">${escape_html(vote.public_rationale)}</p></div> <div class="vote-private svelte-kkelhp"><span class="vote-label svelte-kkelhp"><i class="fa-solid fa-lock" aria-hidden="true"></i> Private (never shared)</span> <p class="svelte-kkelhp">${escape_html(vote.private_rationale)}</p></div></div>`);
          }
          $$renderer3.push(`<!--]--></div></div>`);
        } else {
          $$renderer3.push("<!--[!-->");
        }
        $$renderer3.push(`<!--]--> <div class="progress-section svelte-kkelhp"><div class="progress-bar svelte-kkelhp"><div class="progress-fill svelte-kkelhp"${attr_style(`width: ${stringify(currentStep / policyScenario.length * 100)}%`)}></div></div> <span class="progress-text svelte-kkelhp">Step ${escape_html(currentStep)} of ${escape_html(policyScenario.length)}</span></div> `);
        if (showVotes) {
          $$renderer3.push("<!--[-->");
          $$renderer3.push(`<div class="learning-section svelte-kkelhp"><h3 class="svelte-kkelhp"><i class="fa-solid fa-graduation-cap" aria-hidden="true"></i> What VCP Protected</h3> <ul class="learning-points svelte-kkelhp"><!--[-->`);
          const each_array_3 = ensure_array_like(learningPoints);
          for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
            let point = each_array_3[$$index_3];
            $$renderer3.push(`<li class="svelte-kkelhp">${escape_html(point)}</li>`);
          }
          $$renderer3.push(`<!--]--></ul></div>`);
        } else {
          $$renderer3.push("<!--[!-->");
        }
        $$renderer3.push(`<!--]--></div>`);
      };
      DemoContainer($$renderer2, {
        title: "Community Park Renovation",
        description: "Four stakeholders deliberate on how to spend $150k. VCP shares values while protecting personal circumstances.",
        onReset: reset,
        controls,
        children
      });
    }
  });
}
export {
  _page as default
};
