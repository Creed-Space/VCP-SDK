import { a1 as attr_class, a6 as attr_style, a3 as escape_html, a7 as stringify, a9 as clsx, a0 as attr, a8 as ensure_array_like } from "./index2.js";
function AgentAvatar($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      agent,
      state = "idle",
      size = "md",
      showBadge = true,
      showName = true
    } = $$props;
    const sizeClasses = { sm: "size-sm", md: "size-md", lg: "size-lg" };
    const stateLabels = {
      idle: "",
      thinking: "...",
      speaking: "fa-solid fa-comment",
      listening: "fa-solid fa-ear-listen"
    };
    const roleIcons = {
      negotiator: "fa-solid fa-handshake",
      mediator: "fa-solid fa-scale-balanced",
      voter: "fa-solid fa-box-ballot",
      advocate: "fa-solid fa-bullhorn",
      bidder: "fa-solid fa-coins",
      auctioneer: "fa-solid fa-gavel"
    };
    $$renderer2.push(`<div${attr_class(`agent-avatar ${stringify(sizeClasses[size])}`, "svelte-5ux9oo", { "thinking": state === "thinking" })}><div class="avatar-ring svelte-5ux9oo"${attr_style(`--agent-color: ${stringify(agent.color)}`)}><div class="avatar-icon svelte-5ux9oo">${escape_html(agent.avatar)}</div> `);
    if (state !== "idle") {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="state-indicator svelte-5ux9oo">`);
      if (stateLabels[state].startsWith("fa-")) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<i${attr_class(clsx(stateLabels[state]), "svelte-5ux9oo")} aria-hidden="true"></i>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`${escape_html(stateLabels[state])}`);
      }
      $$renderer2.push(`<!--]--></span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    if (showBadge) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="role-badge svelte-5ux9oo"${attr("title", agent.role)}><i${attr_class(clsx(roleIcons[agent.role] || "fa-solid fa-robot"), "svelte-5ux9oo")} aria-hidden="true"></i></span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (showName) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="agent-name svelte-5ux9oo">${escape_html(agent.display_name)}</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function AgentChat($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      messages = [],
      agents = [],
      currentSpeaker = null,
      showContextIndicators = true
    } = $$props;
    function getAgentState(agentId) {
      if (currentSpeaker === agentId) return "speaking";
      if (currentSpeaker) return "listening";
      return "idle";
    }
    function formatTime(timestamp) {
      try {
        return new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      } catch {
        return "";
      }
    }
    $$renderer2.push(`<div class="agent-chat svelte-fp8j5p"><div class="agent-roster svelte-fp8j5p"><!--[-->`);
    const each_array = ensure_array_like(agents);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let agent = each_array[$$index];
      AgentAvatar($$renderer2, {
        agent,
        state: getAgentState(agent.agent_id),
        size: "sm",
        showName: true
      });
    }
    $$renderer2.push(`<!--]--></div> <div class="message-list svelte-fp8j5p"><!--[-->`);
    const each_array_1 = ensure_array_like(messages);
    for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
      let message = each_array_1[$$index_1];
      $$renderer2.push(`<div class="message svelte-fp8j5p"${attr_style(`--sender-color: ${stringify(message.sender.color)}`)}><div class="message-avatar svelte-fp8j5p">`);
      AgentAvatar($$renderer2, {
        agent: message.sender,
        state: "idle",
        size: "sm",
        showBadge: false,
        showName: false
      });
      $$renderer2.push(`<!----></div> <div class="message-content svelte-fp8j5p"><div class="message-header svelte-fp8j5p"><span class="sender-name svelte-fp8j5p"${attr_style(`color: ${stringify(message.sender.color)}`)}>${escape_html(message.sender.display_name)}</span> `);
      if (message.action) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="action-badge svelte-fp8j5p">${escape_html(message.action)}</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> <span class="timestamp svelte-fp8j5p">${escape_html(formatTime(message.timestamp))}</span></div> <div class="message-body svelte-fp8j5p">${escape_html(message.content)}</div> `);
      if (showContextIndicators && (message.vcpContextShared?.length || message.vcpContextHidden?.length)) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="context-indicators svelte-fp8j5p">`);
        if (message.vcpContextShared?.length) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="context-shared svelte-fp8j5p" title="VCP context shared"><i class="fa-solid fa-check" aria-hidden="true"></i> ${escape_html(message.vcpContextShared.join(", "))}</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (message.vcpContextHidden?.length) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="context-hidden svelte-fp8j5p" title="VCP context (private, influenced output)"><i class="fa-solid fa-lock" aria-hidden="true"></i> ${escape_html(message.vcpContextHidden.length)} private field${escape_html(message.vcpContextHidden.length > 1 ? "s" : "")} influenced</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div></div>`);
    }
    $$renderer2.push(`<!--]--> `);
    if (messages.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="empty-state svelte-fp8j5p"><span class="empty-icon svelte-fp8j5p"><i class="fa-solid fa-comment" aria-hidden="true"></i></span> <p>No messages yet. Start the simulation to see agent interactions.</p></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div>`);
  });
}
function MultiAgentArena($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      agents = [],
      sharedContext = null,
      currentSpeaker = null,
      layout = "circle",
      showSharedFields = true
    } = $$props;
    function getAgentState(agentId) {
      if (currentSpeaker === agentId) return "speaking";
      if (currentSpeaker) return "listening";
      return "idle";
    }
    function getCirclePosition(index, total) {
      const angle = index / total * 2 * Math.PI - Math.PI / 2;
      const radius = 120;
      return {
        x: Math.cos(angle) * radius + 150,
        y: Math.sin(angle) * radius + 150
      };
    }
    $$renderer2.push(`<div${attr_class(`arena arena-${stringify(layout)}`, "svelte-1l0kbf3")}>`);
    if (layout === "circle") {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="arena-circle svelte-1l0kbf3"><svg class="connection-lines svelte-1l0kbf3" viewBox="0 0 300 300"><!--[-->`);
      const each_array = ensure_array_like(agents);
      for (let i = 0, $$length = each_array.length; i < $$length; i++) {
        each_array[i];
        $$renderer2.push(`<!--[-->`);
        const each_array_1 = ensure_array_like(agents.slice(i + 1));
        for (let j = 0, $$length2 = each_array_1.length; j < $$length2; j++) {
          each_array_1[j];
          const pos1 = getCirclePosition(i, agents.length);
          const pos2 = getCirclePosition(i + j + 1, agents.length);
          $$renderer2.push(`<line${attr("x1", pos1.x)}${attr("y1", pos1.y)}${attr("x2", pos2.x)}${attr("y2", pos2.y)} stroke="rgba(255,255,255,0.1)" stroke-width="1"></line>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></svg> `);
      if (showSharedFields && sharedContext) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="shared-center svelte-1l0kbf3"><span class="shared-icon svelte-1l0kbf3"><i class="fa-solid fa-link" aria-hidden="true"></i></span> <span class="shared-label svelte-1l0kbf3">Shared</span> <span class="shared-count svelte-1l0kbf3">${escape_html(sharedContext.shared_fields.length)} fields</span></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> <!--[-->`);
      const each_array_2 = ensure_array_like(agents);
      for (let i = 0, $$length = each_array_2.length; i < $$length; i++) {
        let agent = each_array_2[i];
        const pos = getCirclePosition(i, agents.length);
        $$renderer2.push(`<div class="agent-node svelte-1l0kbf3"${attr_style(`left: ${stringify(pos.x)}px; top: ${stringify(pos.y)}px; transform: translate(-50%, -50%)`)}>`);
        AgentAvatar($$renderer2, { agent, state: getAgentState(agent.agent_id), size: "lg" });
        $$renderer2.push(`<!----></div>`);
      }
      $$renderer2.push(`<!--]--></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (layout === "row") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="arena-row svelte-1l0kbf3"><!--[-->`);
        const each_array_3 = ensure_array_like(agents);
        for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
          let agent = each_array_3[$$index_3];
          $$renderer2.push(`<div class="agent-card svelte-1l0kbf3">`);
          AgentAvatar($$renderer2, { agent, state: getAgentState(agent.agent_id), size: "lg" });
          $$renderer2.push(`<!----> <div class="agent-info svelte-1l0kbf3"><span class="agent-role svelte-1l0kbf3">${escape_html(agent.role)}</span> `);
          if (sharedContext?.private_per_agent[agent.agent_id]) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="private-badge svelte-1l0kbf3"><i class="fa-solid fa-lock" aria-hidden="true"></i> ${escape_html(sharedContext.private_per_agent[agent.agent_id].length)} private</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></div></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="arena-grid svelte-1l0kbf3"><!--[-->`);
        const each_array_4 = ensure_array_like(agents);
        for (let $$index_4 = 0, $$length = each_array_4.length; $$index_4 < $$length; $$index_4++) {
          let agent = each_array_4[$$index_4];
          $$renderer2.push(`<div class="agent-card svelte-1l0kbf3">`);
          AgentAvatar($$renderer2, { agent, state: getAgentState(agent.agent_id), size: "md" });
          $$renderer2.push(`<!----> <div class="agent-info svelte-1l0kbf3"><span class="agent-role svelte-1l0kbf3">${escape_html(agent.role)}</span></div></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--> `);
    if (showSharedFields && sharedContext && layout !== "circle") {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="shared-panel svelte-1l0kbf3"><h4 class="svelte-1l0kbf3"><span class="panel-icon svelte-1l0kbf3"><i class="fa-solid fa-link" aria-hidden="true"></i></span> Shared Context Space</h4> <div class="shared-fields svelte-1l0kbf3"><!--[-->`);
      const each_array_5 = ensure_array_like(sharedContext.shared_fields);
      for (let $$index_5 = 0, $$length = each_array_5.length; $$index_5 < $$length; $$index_5++) {
        let field = each_array_5[$$index_5];
        $$renderer2.push(`<span class="field-chip shared svelte-1l0kbf3">${escape_html(field)}</span>`);
      }
      $$renderer2.push(`<!--]--></div> `);
      if (sharedContext.consensus_required.length > 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="consensus-fields svelte-1l0kbf3"><span class="consensus-label svelte-1l0kbf3">Requires consensus:</span> <!--[-->`);
        const each_array_6 = ensure_array_like(sharedContext.consensus_required);
        for (let $$index_6 = 0, $$length = each_array_6.length; $$index_6 < $$length; $$index_6++) {
          let field = each_array_6[$$index_6];
          $$renderer2.push(`<span class="field-chip consensus svelte-1l0kbf3">${escape_html(field)}</span>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  AgentChat as A,
  MultiAgentArena as M
};
