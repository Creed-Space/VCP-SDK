import { d as derived, w as writable, g as get } from "./index.js";
const AUDIT_STORAGE_KEY = "vcp_audit_trail";
function isBrowser$1() {
  return typeof window !== "undefined" && typeof localStorage !== "undefined";
}
function loadAuditFromStorage() {
  if (!isBrowser$1()) return [];
  try {
    const stored = localStorage.getItem(AUDIT_STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}
function saveAuditToStorage(entries) {
  if (!isBrowser$1()) return;
  try {
    const trimmed = entries.slice(-100);
    localStorage.setItem(AUDIT_STORAGE_KEY, JSON.stringify(trimmed));
  } catch {
    console.warn("Failed to save audit trail to localStorage");
  }
}
function createAuditStore() {
  const initial = loadAuditFromStorage();
  const { subscribe, set, update } = writable(initial);
  return {
    subscribe,
    set: (entries) => {
      set(entries);
      saveAuditToStorage(entries);
    },
    update,
    clear: () => {
      set([]);
      saveAuditToStorage([]);
    },
    getByPlatform: (platformId) => {
      const entries = get({ subscribe });
      return entries.filter((e) => e.platform_id === platformId);
    },
    getByEventType: (eventType) => {
      const entries = get({ subscribe });
      return entries.filter((e) => e.event_type === eventType);
    },
    getToday: () => {
      const entries = get({ subscribe });
      const today = (/* @__PURE__ */ new Date()).toISOString().split("T")[0];
      return entries.filter((e) => e.timestamp.startsWith(today));
    }
  };
}
const auditTrail = createAuditStore();
function logAuditEntry(entry) {
  auditTrail.update((entries) => {
    const updated = [...entries, entry];
    saveAuditToStorage(updated);
    return updated;
  });
}
const todayAudit = derived(auditTrail, ($entries) => {
  const today = (/* @__PURE__ */ new Date()).toISOString().split("T")[0];
  return $entries.filter((e) => e.timestamp.startsWith(today));
});
derived(auditTrail, ($entries) => {
  const platforms = new Set($entries.map((e) => e.platform_id).filter(Boolean));
  return Array.from(platforms);
});
function getStakeholderView(entries, stakeholderType) {
  return entries.map((entry) => {
    const stakeholderEntry = {
      timestamp: entry.timestamp,
      event_type: entry.event_type,
      private_context_used: (entry.private_fields_influenced ?? 0) > 0,
      private_context_exposed: false
      // Always false by design
    };
    switch (stakeholderType) {
      case "hr":
        stakeholderEntry.compliance_status = {
          policy_followed: true,
          budget_compliant: entry.details?.budget_compliant ?? true,
          mandatory_addressed: entry.details?.mandatory_addressed ?? true
        };
        break;
      case "manager":
        stakeholderEntry.compliance_status = {
          policy_followed: true,
          budget_compliant: entry.details?.budget_compliant ?? true
        };
        break;
      case "community":
        stakeholderEntry.progress_summary = entry.details?.progress_summary;
        break;
      case "coach":
        stakeholderEntry.progress_summary = entry.details?.progress_summary;
        break;
    }
    return stakeholderEntry;
  });
}
function getAuditSummary(entries) {
  const eventsByType = {};
  const platforms = /* @__PURE__ */ new Set();
  let fieldsShared = 0;
  let fieldsWithheld = 0;
  let privateInfluenced = 0;
  let privateExposed = 0;
  for (const entry of entries) {
    eventsByType[entry.event_type] = (eventsByType[entry.event_type] || 0) + 1;
    if (entry.platform_id) {
      platforms.add(entry.platform_id);
    }
    fieldsShared += entry.data_shared?.length || 0;
    fieldsWithheld += entry.data_withheld?.length || 0;
    privateInfluenced += entry.private_fields_influenced || 0;
    privateExposed += entry.private_fields_exposed || 0;
  }
  return {
    totalEvents: entries.length,
    eventsByType,
    platformsAccessed: Array.from(platforms),
    fieldsSharedCount: fieldsShared,
    fieldsWithheldCount: fieldsWithheld,
    privateInfluencedCount: privateInfluenced,
    privateExposedCount: privateExposed
    // Should always be 0
  };
}
const CONTEXT_STORAGE_KEY = "vcp_context";
const CONSENT_STORAGE_KEY = "vcp_consents";
function isBrowser() {
  return typeof window !== "undefined" && typeof localStorage !== "undefined";
}
function loadFromStorage(key) {
  if (!isBrowser()) return null;
  try {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : null;
  } catch {
    console.warn(`Failed to load ${key} from localStorage`);
    return null;
  }
}
function saveToStorage(key, value) {
  if (!isBrowser()) return;
  try {
    if (value) {
      localStorage.setItem(key, JSON.stringify(value));
    } else {
      localStorage.removeItem(key);
    }
  } catch {
    console.warn(`Failed to save ${key} to localStorage`);
  }
}
function createContextStore() {
  const initial = loadFromStorage(CONTEXT_STORAGE_KEY);
  const { subscribe, set, update } = writable(initial);
  return {
    subscribe,
    set: (ctx) => {
      set(ctx);
      saveToStorage(CONTEXT_STORAGE_KEY, ctx);
    },
    update: (fn) => {
      update((current) => {
        const newValue = fn(current);
        saveToStorage(CONTEXT_STORAGE_KEY, newValue);
        return newValue;
      });
    },
    clear: () => {
      set(null);
      saveToStorage(CONTEXT_STORAGE_KEY, null);
    },
    updateField: (key, value) => {
      update((current) => {
        if (!current) return current;
        const updated = { ...current, [key]: value, updated: (/* @__PURE__ */ new Date()).toISOString() };
        saveToStorage(CONTEXT_STORAGE_KEY, updated);
        return updated;
      });
    }
  };
}
const vcpContext = createContextStore();
derived(vcpContext, ($ctx) => {
  if (!$ctx) return null;
  return {
    display_name: $ctx.public_profile?.display_name,
    goal: $ctx.public_profile?.goal,
    experience: $ctx.public_profile?.experience,
    learning_style: $ctx.public_profile?.learning_style,
    pace: $ctx.public_profile?.pace,
    motivation: $ctx.public_profile?.motivation,
    role: $ctx.public_profile?.role,
    team: $ctx.public_profile?.team,
    career_goal: $ctx.public_profile?.career_goal
  };
});
derived(vcpContext, ($ctx) => {
  if (!$ctx) return null;
  const private_ctx = $ctx.private_context || {};
  const constraints = $ctx.constraints || {};
  return {
    time_limited: constraints.time_limited ?? !!private_ctx.schedule_irregular,
    budget_limited: constraints.budget_limited ?? !!private_ctx.financial_constraint,
    noise_restricted: constraints.noise_restricted ?? !!private_ctx.noise_sensitive,
    energy_variable: constraints.energy_variable ?? !!private_ctx.energy_variable,
    schedule_irregular: constraints.schedule_irregular ?? !!private_ctx.schedule_irregular,
    mobility_limited: constraints.mobility_limited ?? !!private_ctx.mobility_limited,
    health_considerations: constraints.health_considerations ?? !!private_ctx.health_conditions
  };
});
function createConsentStore() {
  const initial = loadFromStorage(CONSENT_STORAGE_KEY) || {};
  const { subscribe, set, update } = writable(initial);
  return {
    subscribe,
    set,
    update,
    grantConsent: (platformId, requiredFields, optionalFields) => {
      const consent = {
        platform_id: platformId,
        granted_at: (/* @__PURE__ */ new Date()).toISOString(),
        required_fields: requiredFields,
        optional_fields: optionalFields
      };
      update((consents) => {
        const updated = { ...consents, [platformId]: consent };
        saveToStorage(CONSENT_STORAGE_KEY, updated);
        return updated;
      });
      logAuditEntry({
        id: `consent-${Date.now()}`,
        timestamp: (/* @__PURE__ */ new Date()).toISOString(),
        event_type: "consent_granted",
        platform_id: platformId,
        data_shared: [...requiredFields, ...optionalFields],
        data_withheld: [],
        private_fields_influenced: 0,
        private_fields_exposed: 0
      });
      return consent;
    },
    revokeConsent: (platformId) => {
      update((consents) => {
        const { [platformId]: _, ...rest } = consents;
        saveToStorage(CONSENT_STORAGE_KEY, rest);
        return rest;
      });
      logAuditEntry({
        id: `consent-revoke-${Date.now()}`,
        timestamp: (/* @__PURE__ */ new Date()).toISOString(),
        event_type: "consent_revoked",
        platform_id: platformId,
        data_shared: [],
        data_withheld: [],
        private_fields_influenced: 0,
        private_fields_exposed: 0
      });
    },
    hasConsent: (platformId) => {
      const consents = get({ subscribe });
      return !!consents[platformId];
    },
    getConsent: (platformId) => {
      const consents = get({ subscribe });
      return consents[platformId] || null;
    }
  };
}
createConsentStore();
export {
  getAuditSummary as a,
  getStakeholderView as g,
  todayAudit as t,
  vcpContext as v
};
