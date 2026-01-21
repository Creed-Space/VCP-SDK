import { h as head, a as attr, c as attr_style, e as ensure_array_like, s as stringify } from "../../../../../chunks/index2.js";
import { D as DemoContainer } from "../../../../../chunks/DemoContainer.js";
import { M as MultiAgentArena, A as AgentChat } from "../../../../../chunks/MultiAgentArena.js";
import { $ as escape_html } from "../../../../../chunks/context.js";
const auctionAgents = [
  {
    agent_id: "collector_1",
    display_name: "Alexandra",
    role: "bidder",
    avatar: "🎨",
    color: "#e74c3c",
    constitution: {
      id: "art-collector",
      version: "1.0",
      persona: "muse",
      adherence: 3
    }
  },
  {
    agent_id: "collector_2",
    display_name: "Benjamin",
    role: "bidder",
    avatar: "🏛️",
    color: "#3498db",
    constitution: {
      id: "museum-curator",
      version: "1.0",
      persona: "ambassador",
      adherence: 4
    }
  },
  {
    agent_id: "collector_3",
    display_name: "Carla",
    role: "bidder",
    avatar: "💼",
    color: "#2ecc71",
    constitution: {
      id: "investment-advisor",
      version: "1.0",
      persona: "sentinel",
      adherence: 4
    }
  },
  {
    agent_id: "auctioneer",
    display_name: "David",
    role: "auctioneer",
    avatar: "🔨",
    color: "#9b59b6",
    constitution: {
      id: "fair-auction",
      version: "1.0",
      persona: "ambassador",
      adherence: 5
    }
  }
];
const auctionItem = {
  name: "Sunset Over Mountains",
  description: "Oil painting by emerging artist, 2024. 36x48 inches.",
  attributes: {
    artist: "Elena Torres",
    year: 2024
  }
};
const auctionScenario = [
  {
    round: 1,
    actor: "auctioneer",
    action: "announce",
    amount: 5e3,
    message: 'Opening bid for "Sunset Over Mountains" by Elena Torres. Starting at $5,000.',
    vcpContextShared: ["item_details", "reserve_price_met"],
    vcpContextHidden: [],
    explanation: "Auctioneer announces the lot. All participants can see item details."
  },
  {
    round: 1,
    actor: "collector_1",
    action: "bid",
    amount: 5e3,
    message: "I'll open at $5,000. Torres' work resonates with my collection focus.",
    vcpContextShared: ["goal: collection_building", "experience: advanced_collector"],
    vcpContextHidden: ["max_budget", "urgency_level", "collection_gaps"],
    explanation: "Alexandra bids. VCP shares her public goal (collection building) but hides her maximum budget and urgency."
  },
  {
    round: 2,
    actor: "collector_2",
    action: "bid",
    amount: 6e3,
    message: "$6,000. This piece would serve our educational mission well.",
    vcpContextShared: ["role: museum_curator", "goal: public_education"],
    vcpContextHidden: ["board_approval_threshold", "acquisition_budget"],
    explanation: "Benjamin counters. His museum role is public, but board approval limits are private."
  },
  {
    round: 3,
    actor: "collector_3",
    action: "bid",
    amount: 7500,
    message: "$7,500. The artist's trajectory suggests strong appreciation potential.",
    vcpContextShared: ["role: investment_advisor", "goal: portfolio_growth"],
    vcpContextHidden: ["client_identity", "roi_targets", "liquidity_needs"],
    explanation: "Carla enters. Her investment focus is visible, but client details and targets are private."
  },
  {
    round: 4,
    actor: "collector_1",
    action: "bid",
    amount: 9e3,
    message: "$9,000. This artist is important to my vision.",
    vcpContextShared: ["motivation: personal_significance"],
    vcpContextHidden: ["max_budget", "partner_preferences"],
    explanation: "Alexandra raises significantly. Her emotional connection is shared, financial limits remain private."
  },
  {
    round: 5,
    actor: "collector_2",
    action: "bid",
    amount: 1e4,
    message: "$10,000. At this level, I'll need to pause for institutional consultation.",
    vcpContextShared: ["constraint: institutional_process"],
    vcpContextHidden: ["exact_threshold", "approval_timeline"],
    explanation: "Benjamin signals a constraint. The existence of a process is shared, but exact limits are private."
  },
  {
    round: 6,
    actor: "collector_3",
    action: "bid",
    amount: 11e3,
    message: "$11,000. My analysis supports this valuation.",
    vcpContextShared: ["methodology: data_driven"],
    vcpContextHidden: ["projected_returns", "client_mandate"],
    explanation: "Carla continues methodically. Her approach is visible, specific projections are not."
  },
  {
    round: 7,
    actor: "collector_1",
    action: "bid",
    amount: 13e3,
    message: "$13,000. I'm committed to acquiring this piece.",
    vcpContextShared: ["commitment: high"],
    vcpContextHidden: ["max_budget", "approaching_limit"],
    explanation: "Alexandra pushes higher. Her commitment level is shared, but she's nearing her limit privately."
  },
  {
    round: 8,
    actor: "collector_2",
    action: "pass",
    message: "I must step back. This exceeds our current acquisition parameters.",
    vcpContextShared: ["constraint: budget_exceeded"],
    vcpContextHidden: ["exact_limit", "alternative_options"],
    explanation: "Benjamin withdraws. The constraint type is shared, exact numbers remain private."
  },
  {
    round: 9,
    actor: "collector_3",
    action: "bid",
    amount: 14e3,
    message: "$14,000. Still within acceptable range for this asset class.",
    vcpContextShared: ["methodology: risk_adjusted"],
    vcpContextHidden: ["max_authorized", "margin_remaining"],
    explanation: "Carla continues. Her risk framework is visible, exact authorization limits are not."
  },
  {
    round: 10,
    actor: "collector_1",
    action: "bid",
    amount: 15e3,
    message: "$15,000. This is my final offer.",
    vcpContextShared: ["constraint: budget_limit_reached"],
    vcpContextHidden: ["exact_maximum", "financial_situation"],
    explanation: "Alexandra reaches her limit. She signals a ceiling without revealing the exact number."
  },
  {
    round: 11,
    actor: "collector_3",
    action: "bid",
    amount: 16e3,
    message: "$16,000. The fundamentals still support this price point.",
    vcpContextShared: ["analysis: positive_outlook"],
    vcpContextHidden: ["upside_potential", "portfolio_fit"],
    explanation: "Carla exceeds Alexandra. She has room but doesn't reveal how much."
  },
  {
    round: 12,
    actor: "collector_1",
    action: "pass",
    message: "Congratulations. This exceeds my parameters, but it's a worthy acquisition.",
    vcpContextShared: ["outcome: graceful_exit"],
    vcpContextHidden: ["exact_limit", "future_interest"],
    explanation: "Alexandra withdraws gracefully. Her exact limit was never exposed."
  },
  {
    round: 13,
    actor: "auctioneer",
    action: "close",
    amount: 16e3,
    message: "Sold to Carla for $16,000. Congratulations!",
    vcpContextShared: ["final_price", "winner"],
    vcpContextHidden: [],
    explanation: "Auction closes. Final price is public. Private valuations remain private."
  }
];
const learningPoints = [
  "Private valuations (maximum willingness to pay) were never exposed during bidding",
  "Agents shared their goals and constraints at a category level, not specific values",
  "The auctioneer saw limited context about each bidder's preferences",
  'Withdrawal signals ("budget exceeded") communicated limits without revealing exact numbers',
  "VCP enabled personalized bidding strategies while protecting sensitive financial information"
];
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let currentStep = 0;
    let isPlaying = false;
    let messages = [];
    let currentSpeaker = null;
    function stopPlaying() {
      isPlaying = false;
    }
    function reset() {
      stopPlaying();
      currentStep = 0;
      messages = [];
      currentSpeaker = null;
    }
    head("1w305lr", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Auction Demo - VCP Multi-Agent</title>`);
      });
      $$renderer3.push(`<meta name="description" content="See how VCP protects private valuations during a multi-agent auction."/>`);
    });
    {
      let controls = function($$renderer3) {
        $$renderer3.push(`<button class="control-btn"${attr("disabled", currentStep >= auctionScenario.length && !isPlaying, true)}><span class="control-icon">${escape_html(isPlaying ? "⏸" : "▶")}</span> <span>${escape_html(isPlaying ? "Pause" : "Play")}</span></button> <button class="control-btn"${attr("disabled", isPlaying || currentStep >= auctionScenario.length, true)}><span class="control-icon">⏭</span> <span>Step</span></button>`);
      }, children = function($$renderer3) {
        $$renderer3.push(`<div class="auction-layout svelte-1w305lr"><div class="item-card svelte-1w305lr"><div class="item-image svelte-1w305lr">🖼️</div> <div class="item-details svelte-1w305lr"><h3 class="svelte-1w305lr">${escape_html(auctionItem.name)}</h3> <p class="item-description svelte-1w305lr">${escape_html(auctionItem.description)}</p> <div class="item-meta svelte-1w305lr"><span class="meta-item svelte-1w305lr"><span class="meta-label svelte-1w305lr">Artist</span> <span class="meta-value svelte-1w305lr">${escape_html(auctionItem.attributes.artist)}</span></span> <span class="meta-item svelte-1w305lr"><span class="meta-label svelte-1w305lr">Year</span> <span class="meta-value svelte-1w305lr">${escape_html(auctionItem.attributes.year)}</span></span></div> `);
        if (currentStep > 0) {
          $$renderer3.push("<!--[-->");
          $$renderer3.push(`<div class="current-bid svelte-1w305lr"><span class="bid-label svelte-1w305lr">Current Bid</span> <span class="bid-amount svelte-1w305lr">$${escape_html(messages.filter((m) => m.action === "bid").slice(-1)[0]?.content.match(/\$[\d,]+/)?.[0]?.replace("$", "") || "5,000")}</span></div>`);
        } else {
          $$renderer3.push("<!--[!-->");
        }
        $$renderer3.push(`<!--]--></div></div> <div class="arena-section svelte-1w305lr">`);
        MultiAgentArena($$renderer3, {
          agents: auctionAgents,
          currentSpeaker,
          layout: "row",
          showSharedFields: false
        });
        $$renderer3.push(`<!----></div> <div class="chat-section svelte-1w305lr">`);
        AgentChat($$renderer3, {
          messages,
          agents: auctionAgents,
          currentSpeaker,
          showContextIndicators: true
        });
        $$renderer3.push(`<!----></div> <div class="progress-section svelte-1w305lr"><div class="progress-bar svelte-1w305lr"><div class="progress-fill svelte-1w305lr"${attr_style(`width: ${stringify(currentStep / auctionScenario.length * 100)}%`)}></div></div> <span class="progress-text svelte-1w305lr">Round ${escape_html(currentStep)} of ${escape_html(auctionScenario.length)}</span></div> `);
        if (currentStep >= auctionScenario.length) {
          $$renderer3.push("<!--[-->");
          $$renderer3.push(`<div class="learning-section svelte-1w305lr"><h3 class="svelte-1w305lr">🎓 What VCP Protected</h3> <ul class="learning-points svelte-1w305lr"><!--[-->`);
          const each_array = ensure_array_like(learningPoints);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let point = each_array[$$index];
            $$renderer3.push(`<li class="svelte-1w305lr">${escape_html(point)}</li>`);
          }
          $$renderer3.push(`<!--]--></ul></div>`);
        } else {
          $$renderer3.push("<!--[!-->");
        }
        $$renderer3.push(`<!--]--></div>`);
      };
      DemoContainer($$renderer2, {
        title: "Art Auction",
        description: "Three collectors bid on artwork. VCP protects their private valuations while enabling fair competition.",
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
