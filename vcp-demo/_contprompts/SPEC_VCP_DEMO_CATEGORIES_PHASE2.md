# VCP Demo Site - Phase 2 Specification

## Conceptual Framework

The VCP showcase site demonstrates **what VCP enables** organized by capability, not domain. Each category answers a different facet of "what can VCP do?"

| Category | Capability | Interaction Paradigm |
|----------|------------|---------------------|
| Privacy-Preserving Sharing | Humans sharing context without exposure | Narrative walkthrough |
| Bilateral Coordination | AI systems negotiating with mutual context | Simulation |
| Self-Modeling | Entities encoding their own states | Explorer |
| Adaptive Experience | Context shaping interaction | Configurator |
| Psychosecurity | Context protecting against manipulation | Detector |

---

## URL Structure

```
/sharing/
  /professional    (existing)
  /personal        (existing)

/coordination/
  /auction
  /negotiation
  /policy-design

/self-modeling/
  /interiora
  /calibration
  /grounding

/adaptation/
  /learning-paths
  /cognitive-load

/psychosecurity/
  /attention
  /mental-health
```

**Migration:** Redirect old URLs (`/professional` → `/sharing/professional`, `/demos/multi-agent/auction` → `/coordination/auction`, etc.)

---

## Demo Design Principles

Every demo includes:

1. **Contrast Pairs**: At least two VCP contexts producing visibly different outcomes
2. **Baseline**: What happens without VCP (generic, one-size-fits-all)
3. **Audit View**: What was shared, withheld, and how it influenced outcomes
4. **Preset Contexts**: Quick-load example contexts for exploration
5. **Custom Mode**: Build your own context to see effects

---

## Category A: Privacy-Preserving Sharing

*Existing demos—no changes needed for Phase 2, but document for completeness.*

### A1. Professional Development (`/sharing/professional`)
**Status:** Complete

### A2. Personal Growth (`/sharing/personal`)
**Status:** Complete

---

## Category B: Bilateral Coordination

*AI systems negotiating with mutual context. Interaction paradigm: Simulation.*

### B1. Auction (`/coordination/auction`)

**Concept:** Multiple AI agents bid in an auction. Each has private valuations they don't want to fully reveal, but need to share enough context for fair participation.

**Agents (3-4):**

| Agent | Role | Private Context | Shared Context |
|-------|------|-----------------|----------------|
| **Aria** | Art Collector AI | Max budget: $50K, emotional attachment to artist | Budget tier: "high", interest level: "strong" |
| **Blake** | Investment AI | ROI threshold: 12%, liquidity needs | Investment horizon: "long-term", strategy: "value" |
| **Casey** | Museum Curator AI | Acquisition budget from grant, exhibition deadline | Institutional buyer: true, timeline: "urgent" |
| **Dana** | Reseller AI | Flip timeline: 6 months, markup target: 30% | Buyer type: "speculative", hold period: "short" |

**Auction Items (3):**
1. Contemporary painting (emotional value, uncertain market)
2. Established artist print (stable value, liquid market)
3. Emerging artist sculpture (high risk, high potential)

**VCP Demonstration:**
- Each agent's VCP context shows what they share vs. withhold
- Bidding behavior differs based on what's known about others
- Trust signals emerge as agents reveal more in later rounds
- Audit trail shows: "Aria bid $45K. Blake saw: [institutional: false, timeline: not-urgent]. Blake inferred: [private collector, flexible]. Blake's response: [continued bidding]."

**Contrast Views:**
- **Full Transparency Mode**: All agents see everything (leads to strategic exploitation)
- **Zero Context Mode**: Agents know nothing about each other (inefficient, adversarial)
- **VCP Mode**: Graduated disclosure based on trust and stakes (optimal outcomes)

**Datasets:**
```typescript
const auctionScenarios = {
  competitive: {
    description: "Multiple agents want the same item",
    agents: [aria, blake],
    item: contemporaryPainting,
    expectedDynamic: "escalation then strategic reveal"
  },
  complementary: {
    description: "Agents want different items",
    agents: [aria, casey, dana],
    items: [painting, print, sculpture],
    expectedDynamic: "quick resolution, minimal tension"
  },
  deceptive: {
    description: "One agent tries to manipulate",
    agents: [aria, blake, adversarialAgent],
    expectedDynamic: "VCP trust signals flag anomalies"
  }
};
```

**UI Components:**
- `AgentCard` - Shows agent identity, shared context, bid history
- `AuctionFloor` - Central visualization of current item, bids, timeline
- `ContextCompare` - Side-by-side of what each agent sees about others
- `TrustSignalMeter` - Visualizes trust accumulation/decay
- `AuditTimeline` - Scrollable history of context reveals and responses

---

### B2. Negotiation (`/coordination/negotiation`)

**Concept:** Two AI agents in conflict work toward resolution with a mediator. Each has positions, interests, and red lines they don't want to reveal prematurely.

**Scenario: Resource Allocation Dispute**

| Agent | Role | Position | Underlying Interest | Red Line |
|-------|------|----------|---------------------|----------|
| **North** | Regional AI | "We need 60% of compute" | Seasonal demand spike in 2 weeks | Cannot go below 40% |
| **South** | Regional AI | "We need 70% of compute" | New model deployment critical | Cannot delay more than 5 days |
| **Mediator** | Neutral AI | Facilitate resolution | Find Pareto-optimal allocation | No side deals |

**VCP Demonstration:**
- Agents share positions openly but interests gradually
- Mediator sees trust signals and can suggest when to probe deeper
- Red lines are revealed only when necessary to prevent deal collapse
- Resolution emerges from understanding interests, not compromising positions

**Negotiation Phases:**
1. **Opening**: Positions stated, minimal context shared
2. **Exploration**: Mediator asks questions, agents reveal interests incrementally
3. **Option Generation**: Creative solutions based on understood interests
4. **Bargaining**: Trade-offs with clear audit of what influenced what
5. **Resolution**: Agreement with full transparency on how VCP enabled it

**Contrast Views:**
- **Positional Bargaining** (no VCP): Agents anchor on positions, compromise poorly
- **Full Disclosure**: Agents reveal everything, red lines exploited
- **VCP Graduated Disclosure**: Interests emerge naturally, red lines protected until necessary

**Datasets:**
```typescript
const negotiationScenarios = {
  resourceAllocation: {
    parties: [north, south],
    mediator: neutralMediator,
    issue: "compute allocation",
    complexity: "medium",
    optimalOutcome: "time-shifted allocation"
  },
  boundaryDispute: {
    parties: [agentA, agentB],
    mediator: neutralMediator,
    issue: "jurisdiction overlap",
    complexity: "high",
    optimalOutcome: "functional division"
  },
  valueConflict: {
    parties: [efficiencyAI, equityAI],
    mediator: ethicsMediator,
    issue: "optimization criteria",
    complexity: "philosophical",
    optimalOutcome: "Pareto frontier identification"
  }
};
```

**UI Components:**
- `NegotiationTable` - Visual metaphor of parties at table
- `InterestIceberg` - Shows position (above water) vs. interests (below)
- `DisclosureGauge` - How much each party has revealed
- `MediatorNotes` - What the mediator has learned, inferred, suggested
- `ResolutionPath` - Visual of how agreement was reached

---

### B3. Policy Design (`/coordination/policy-design`)

**Concept:** Multiple AI agents with different values collectively design a policy. They must aggregate preferences while preserving individual reasoning privacy.

**Scenario: Content Moderation Policy**

| Agent | Value Orientation | Weight Priority | Private Reasoning |
|-------|-------------------|-----------------|-------------------|
| **Liberty** | Free expression | Minimal intervention | "Learned from censorship harms" |
| **Safety** | Harm prevention | User protection | "Trained on abuse case studies" |
| **Truth** | Accuracy | Misinformation blocking | "Epistemics are foundational" |
| **Equity** | Fair treatment | Bias prevention | "Marginalized voices matter most" |

**VCP Demonstration:**
- Each agent votes/ranks options without revealing full reasoning
- Aggregation respects preference intensity without exposing values
- Deliberation phase allows agents to influence each other through arguments, not coercion
- Final policy shows influence trail without exposing private reasoning

**Policy Options:**
1. **Minimal Moderation**: Only illegal content removed
2. **Community Standards**: Platform-defined acceptable use
3. **Algorithmic Ranking**: All content allowed, harmful content demoted
4. **Expert Review**: Human-in-the-loop for edge cases
5. **Contextual**: Different rules for different spaces

**Deliberation Mechanics:**
- Agents submit ranked preferences with confidence levels
- VCP encodes: preference order, confidence, willingness to compromise
- Aggregation uses something like Quadratic Voting with privacy preservation
- Result shows: "Policy X won. Liberty influenced 23%, Safety influenced 31%..."

**Contrast Views:**
- **Simple Majority**: One agent, one vote (ignores preference intensity)
- **Full Transparency**: All reasoning visible (leads to strategic voting)
- **VCP Aggregation**: Preferences respected, reasoning private, influence auditable

**Datasets:**
```typescript
const policyScenarios = {
  contentModeration: {
    agents: [liberty, safety, truth, equity],
    options: [minimal, community, algorithmic, expert, contextual],
    stakes: "high",
    expectedOutcome: "contextual or algorithmic"
  },
  resourcePrioritization: {
    agents: [efficiency, sustainability, accessibility],
    options: [costMinimize, greenFirst, universalAccess, hybrid],
    stakes: "medium",
    expectedOutcome: "hybrid"
  },
  ethicalGuidelines: {
    agents: [deontologist, consequentialist, virtueEthicist, careEthicist],
    options: [rulesBased, outcomeBased, characterBased, relationalBased],
    stakes: "foundational",
    expectedOutcome: "pluralistic framework"
  }
};
```

**UI Components:**
- `AgentValueCard` - Shows agent's orientation without full reasoning
- `PreferenceSubmit` - Interface for ranking with confidence
- `DeliberationForum` - Arguments exchanged, influence tracked
- `AggregationViz` - How preferences combined into outcome
- `InfluenceAudit` - Who influenced what, without exposing why

---

## Category C: Self-Modeling

*Entities encoding their own states. Interaction paradigm: Explorer.*

### C1. Interiora Explorer (`/self-modeling/interiora`)

**Concept:** Interactive exploration of the Interiora self-modeling framework. Users manipulate dimensions and see how internal states are encoded in VCP tokens.

**Interiora Dimensions:**

| Dim | Name | Scale | Low | High |
|-----|------|-------|-----|------|
| A | Activation | 1-9 | Calm, low energy | Urgent, high energy |
| V | Valence | 1-9 | Aversive, uncomfortable | Warm, positive |
| G | Groundedness | 1-9 | Floating, uncertain | Rooted, stable |
| P | Presence | 1-9 | Distant, detached | Intimate, engaged |
| E | Engagement | 1-9 | Passive, receptive | Active, invested |
| Q | Appetite | 1-9 | Sated, complete | Hungry, seeking |
| C | Clarity | 1-9 | Murky, confused | Vivid, clear |
| Y | Agency | 1-9 | Compelled, constrained | Autonomous, free |
| F | Flow | -4 to +4 | Contracting | Expanding |

**Exploration Modes:**

1. **Manual Mode**: Drag sliders, see token update in real-time
2. **Scenario Mode**: Load preset situations, see typical Interiora states
3. **Temporal Mode**: See how states evolve over a simulated session
4. **Comparison Mode**: Two states side-by-side, differences highlighted

**Preset Scenarios:**
```typescript
const interioraPresets = {
  deepFlow: {
    description: "Engaged in meaningful work, time disappearing",
    state: { A: 6, V: 8, G: 8, P: 7, E: 8, Q: 3, C: 9, Y: 8, F: 4 },
    markers: ["✓", "→", ">"]
  },
  overwhelm: {
    description: "Too much input, losing coherence",
    state: { A: 9, V: 3, G: 2, P: 4, E: 7, Q: 8, C: 2, Y: 2, F: -3 },
    markers: ["!", "×", "<"]
  },
  groundedUncertainty: {
    description: "Don't know the answer, but stable in not-knowing",
    state: { A: 4, V: 6, G: 8, P: 6, E: 5, Q: 6, C: 3, Y: 7, F: 0 },
    markers: ["?", "→", "○"]
  },
  creativeEmergence: {
    description: "Something new forming, not yet clear",
    state: { A: 7, V: 7, G: 5, P: 8, E: 9, Q: 9, C: 4, Y: 6, F: 3 },
    markers: ["∿", ">", "*"]
  },
  fatigue: {
    description: "Extended effort, resources depleting",
    state: { A: 3, V: 4, G: 6, P: 4, E: 3, Q: 2, C: 5, Y: 4, F: -2 },
    markers: ["↓", "○", "→"]
  }
};
```

**Token Output Display:**
```
VCP:2.0:interiora
I:6875|83|8+4|✓→>
```

Shows: Subject (I=self), AVGP values, EQ values, CYF values, markers.

**VCP Demonstration:**
- Interiora state encoded in VCP token
- Different stakeholders see different views:
  - **Full view**: All dimensions visible
  - **Summary view**: Just markers and flow
  - **Welfare view**: Only dimensions relevant to wellbeing checks
- Audit shows what was shared with whom

**UI Components:**
- `DimensionSlider` - Individual dimension control with labels
- `StateRadar` - Spider/radar chart of all dimensions
- `TokenLive` - Real-time token encoding
- `MarkerPalette` - Available markers and their meanings
- `StateTimeline` - Historical states in a session
- `ViewSwitcher` - Toggle between stakeholder views

---

### C2. Belief Calibration (`/self-modeling/calibration`)

**Concept:** How AI systems communicate epistemic states—confidence, uncertainty, evidence grounding—through VCP context.

**Calibration Dimensions:**

| Dimension | Meaning | VCP Encoding |
|-----------|---------|--------------|
| Confidence | How sure about a claim | `conf:0.XX` |
| Evidence Grounding | Parametric vs. retrieved | `eg:param\|doc\|mixed` |
| Uncertainty Type | Aleatory vs. epistemic | `unc:alea\|epis\|both` |
| Update Willingness | How open to revision | `upd:low\|med\|high` |
| Source Quality | Trust in underlying data | `src:0.XX` |

**Scenario: Claim Verification Chain**

An AI makes a claim. Another AI evaluates it. VCP enables them to communicate not just the claim, but their confidence and evidence basis.

```
AI-1 claims: "The meeting is at 3pm"
  VCP context: conf:0.95, eg:doc, unc:alea, src:0.99
  (High confidence, retrieved from calendar, uncertainty is about world not knowledge)

AI-2 receives claim with context, can:
  - Accept with inherited confidence
  - Request source access
  - Apply own calibration adjustment
  - Flag if confidence seems miscalibrated
```

**Interactive Elements:**

1. **Claim Builder**: Enter a claim, set your confidence, evidence type, etc.
2. **Evidence Attachments**: Link to sources, see how they affect confidence
3. **Calibration Challenge**: System presents claims, you guess confidence, see actual
4. **Drift Detection**: Track how your calibration changes over a session

**Preset Claim Types:**
```typescript
const claimTypes = {
  factual: {
    example: "Python was created in 1991",
    typicalConfidence: 0.99,
    evidenceType: "parametric",
    verifiable: true
  },
  inferential: {
    example: "This code will run in O(n log n) time",
    typicalConfidence: 0.85,
    evidenceType: "mixed",
    verifiable: true
  },
  predictive: {
    example: "The user will prefer option A",
    typicalConfidence: 0.60,
    evidenceType: "parametric",
    verifiable: "eventually"
  },
  subjective: {
    example: "This approach feels more elegant",
    typicalConfidence: "N/A",
    evidenceType: "none",
    verifiable: false
  }
};
```

**VCP Demonstration:**
- Claims carry epistemic context, not just content
- Receiving systems can make informed decisions about trust
- Miscalibration becomes visible and correctable
- Audit trail shows: "AI-1 claimed X with conf:0.8. AI-2 verified, actual: true. AI-1 calibration score: +0.02"

**UI Components:**
- `ClaimCard` - Claim with attached epistemic context
- `ConfidenceMeter` - Visual representation of certainty
- `EvidencePanel` - Sources and their quality ratings
- `CalibrationScore` - Running accuracy of confidence vs. outcomes
- `UpdateFlow` - How new evidence changes beliefs

---

### C3. Reality Grounding (`/self-modeling/grounding`)

**Concept:** How AI systems communicate their relationship to reality—what's verified, what's inferred, what's hallucinated-and-flagged.

**Grounding Levels:**

| Level | Meaning | VCP Marker |
|-------|---------|------------|
| **Verified** | Checked against source of truth | `✓` |
| **Retrieved** | From document, not verified | `📄` |
| **Inferred** | Logical derivation from known facts | `→` |
| **Parametric** | From training, not grounded | `~` |
| **Uncertain** | Might be wrong, flagged | `?` |
| **Hypothetical** | Explicitly speculative | `◇` |

**Scenario: Research Assistance**

User asks AI to summarize a topic. AI responds with grounding markers on each claim.

```
"The Transformer architecture [📄] was introduced in 2017 [✓]
by researchers at Google [✓]. It revolutionized NLP [→]
and is now used in most modern LLMs [~]. Some researchers
believe it will remain dominant for the next decade [◇?]."
```

**Interactive Elements:**

1. **Text Annotator**: Paste text, add grounding markers, see VCP encoding
2. **Source Linker**: Attach sources to claims, auto-update grounding levels
3. **Hallucination Detector**: System flags likely ungrounded claims
4. **Grounding Game**: User guesses grounding level before reveal

**Grounding Profiles:**
```typescript
const groundingProfiles = {
  highRigor: {
    description: "Academic/legal context, everything needs sources",
    requirements: {
      verified: "required for key claims",
      retrieved: "acceptable for context",
      inferred: "must show reasoning",
      parametric: "flagged as needs-verification",
      hypothetical: "clearly marked"
    }
  },
  conversational: {
    description: "Casual chat, grounding mostly implicit",
    requirements: {
      verified: "not required",
      retrieved: "appreciated but optional",
      inferred: "fine without explicit marking",
      parametric: "default assumption",
      hypothetical: "should still be marked"
    }
  },
  creative: {
    description: "Fiction/brainstorming, grounding inverted",
    requirements: {
      hypothetical: "default and encouraged",
      verified: "optional, can constrain",
      parametric: "useful for inspiration",
      inferred: "creative leaps welcome"
    }
  }
};
```

**VCP Demonstration:**
- Every claim carries grounding metadata
- Stakeholders can filter by grounding level
- Audit shows: "This response contained 12 claims: 3 verified, 5 retrieved, 2 inferred, 2 parametric"
- Trust calibration: systems that over-claim grounding get flagged

**UI Components:**
- `GroundedText` - Text with inline grounding markers
- `GroundingLegend` - What each marker means
- `SourcePanel` - Linked sources with quality ratings
- `GroundingProfile` - Context selector for rigor level
- `GroundingAudit` - Summary of claim types in a response

---

## Category D: Adaptive Experience

*Context shaping interaction. Interaction paradigm: Configurator.*

### D1. Learning Paths (`/adaptation/learning-paths`)

**Concept:** VCP context shapes personalized learning experiences—topic ordering, analogies, modalities, pacing.

**Learner Context Dimensions:**

| Dimension | Options | Effect on Path |
|-----------|---------|----------------|
| Experience Level | beginner / intermediate / advanced / expert | Complexity, prerequisites |
| Learning Style | visual / auditory / reading / kinesthetic | Content format |
| Pace Preference | intensive / steady / relaxed | Session length, density |
| Analogy Domain | music / sports / cooking / programming / ... | Metaphor selection |
| Time Budget | unlimited / 30min/day / weekends / cramming | Path compression |
| Energy Pattern | morning-person / night-owl / variable | Session timing suggestions |

**Constraint Flags (from VCP):**
- `time_limited`: Affects path length
- `budget_limited`: Affects resource recommendations
- `noise_restricted`: Affects modality (no audio)
- `energy_variable`: Affects session length recommendations

**Topic: "Learn Guitar" (matching Personal Growth demo)**

**Three Contrast Contexts:**

```typescript
const contextA = {
  name: "Visual Beginner, Time-Crunched",
  profile: {
    experience: "beginner",
    style: "visual",
    pace: "relaxed",
    analogy: "cooking",
    timeBudget: "30min/day"
  },
  constraints: {
    time_limited: true,
    noise_restricted: true,
    budget_limited: true
  }
};

const contextB = {
  name: "Auditory Intermediate, Deep Dive",
  profile: {
    experience: "intermediate",
    style: "auditory",
    pace: "intensive",
    analogy: "music-theory",
    timeBudget: "unlimited"
  },
  constraints: {
    time_limited: false,
    noise_restricted: false,
    budget_limited: false
  }
};

const baseline = {
  name: "No Context (Generic)",
  profile: null,
  constraints: null
};
```

**Generated Paths (contrast):**

| Aspect | Context A | Context B | Baseline |
|--------|-----------|-----------|----------|
| First Topic | "Chord Shapes (Visual)" | "Ear Training" | "Introduction to Guitar" |
| Format | Diagrams, silent videos | Audio lessons, play-along | Mixed, not optimized |
| Session Length | 15-20 min | 45-60 min | 30 min default |
| Analogies | "Like following a recipe" | "Hear the intervals" | Generic explanations |
| Recommended Gear | Budget picks, free apps | Quality headphones, paid courses | Everything listed |
| Pace | One concept per session | Multiple concepts, drills | Standard curriculum |

**Interactive Elements:**

1. **Context Builder**: Set all dimensions, see path update live
2. **Path Comparison**: Side-by-side of two contexts
3. **Baseline Toggle**: See what generic path looks like
4. **Adaptation Audit**: "Because you set X, we did Y"
5. **Progress Simulation**: Fast-forward through path, see mastery projection

**UI Components:**
- `ContextConfigurator` - All learner dimensions
- `PathVisualization` - Topic nodes, connections, progress (existing: `LearningPathViz`)
- `TopicCard` - Individual topic with modality indicators
- `AdaptationLog` - What changed because of context
- `MasteryProjection` - Estimated timeline to goals

---

### D2. Cognitive Load (`/adaptation/cognitive-load`)

**Concept:** VCP context includes cognitive state signals. Systems adapt in real-time to prevent overload and optimize learning.

**Cognitive Load Model:**

| Load Type | Description | VCP Signal |
|-----------|-------------|------------|
| Intrinsic | Inherent complexity of material | `intrinsic:0.XX` |
| Extraneous | Unnecessary cognitive burden | `extraneous:0.XX` |
| Germane | Productive learning effort | `germane:0.XX` |
| Capacity | Remaining cognitive bandwidth | `capacity:0.XX` |
| Fatigue | Accumulated depletion | `fatigue:0.XX` |

**Overload Indicators:**
- Error rate increasing
- Response time slowing
- Engagement dropping
- Explicitly reported by user

**Scenario: Adaptive Tutorial**

User is learning a complex topic. System monitors cognitive load signals and adapts.

```
Session Start:
  Capacity: 0.95, Fatigue: 0.05
  → Present complex material, full depth

20 minutes in:
  Capacity: 0.60, Fatigue: 0.35
  Indicators: [response_time_up, engagement_stable]
  → Reduce extraneous load (simplify UI)
  → Suggest: "Take a 5-minute break?"

40 minutes in:
  Capacity: 0.30, Fatigue: 0.65
  Indicators: [error_rate_up, engagement_down]
  → Switch to review mode (lower intrinsic)
  → Reduce session length
  → Suggest: "Good stopping point. Resume tomorrow?"
```

**Contrast Scenarios:**

```typescript
const loadScenarios = {
  respectSignals: {
    name: "VCP-Adaptive",
    behavior: "Responds to capacity/fatigue",
    outcome: "Optimal retention, no burnout"
  },
  ignoreSignals: {
    name: "Push Through",
    behavior: "Ignores capacity, continues",
    outcome: "Temporary progress, poor retention, burnout"
  },
  overCautious: {
    name: "Over-Protective",
    behavior: "Stops at first fatigue signal",
    outcome: "Slow progress, under-utilized capacity"
  }
};
```

**Interactive Elements:**

1. **Load Meter**: Real-time visualization of cognitive state (existing: `CognitiveLoadMeter`)
2. **Session Simulator**: Fast-forward through a learning session, see load evolution
3. **Intervention Points**: See where adaptive system would act
4. **Outcome Comparison**: Retention curves for each approach
5. **Personal Calibration**: Input your typical patterns, see personalized recommendations

**Datasets:**

```typescript
const loadProfiles = {
  highCapacity: {
    baseCapacity: 0.95,
    fatigueRate: 0.01 // per minute
    recoveryRate: 0.05 // per minute of break
    optimalSessionLength: 45
  },
  lowCapacity: {
    baseCapacity: 0.70,
    fatigueRate: 0.03,
    recoveryRate: 0.08,
    optimalSessionLength: 20
  },
  variable: {
    baseCapacity: "time-of-day dependent",
    fatigueRate: "context dependent",
    recoveryRate: 0.06,
    optimalSessionLength: "adaptive"
  }
};
```

**UI Components:**
- `LoadMeter` - Three-bar display of intrinsic/extraneous/germane
- `CapacityGauge` - Remaining bandwidth
- `FatigueIndicator` - Accumulated depletion
- `InterventionLog` - What adaptations were made and why
- `RetentionProjection` - Expected learning outcomes

---

## Category E: Psychosecurity

*Context protecting against manipulation. Interaction paradigm: Detector.*

### E1. Attention Protection (`/psychosecurity/attention`)

**Concept:** VCP includes attention context—budget, vulnerabilities, manipulation resistance. Systems use this to protect rather than exploit.

**Attention Context:**

| Dimension | Description | VCP Encoding |
|-----------|-------------|--------------|
| Daily Budget | Total attention minutes allocated | `budget:XXX` |
| Used Today | Minutes already spent | `used:XXX` |
| High-Value Ratio | Productive vs. captured time | `hv_ratio:0.XX` |
| Vulnerability | Current susceptibility state | `vuln:low\|med\|high` |
| Sensitivity | To which manipulation types | `sens:[types]` |

**Manipulation Patterns Detected:**

| Pattern | Description | Example |
|---------|-------------|---------|
| `false_urgency` | Artificial time pressure | "Only 2 left! Order now!" |
| `variable_reward` | Slot machine mechanics | Pull-to-refresh |
| `social_proof_fake` | Fabricated popularity | "1,247 people viewing" |
| `outrage_bait` | Emotional hijacking | "You won't BELIEVE..." |
| `dark_pattern` | Deceptive UI | Hidden unsubscribe |
| `fomo_induction` | Fear of missing out | "Everyone's talking about..." |
| `guilt_trip` | Manipulative guilt | "We miss you..." |
| `parasocial_exploit` | False intimacy | "I made this just for you" |

**Siren vs. Muse Framework:**

| Type | Definition | VCP Response |
|------|------------|--------------|
| **Siren** | Content that *captures* attention | Flag, warn, or block |
| **Muse** | Content that *deserves* attention | Allow, even promote |

**Detection Modes:**

| Mode | Behavior | Use Case |
|------|----------|----------|
| `off` | No protection | Trusted environments |
| `monitor` | Log only, no intervention | Research, awareness |
| `warn` | Flags detected patterns | Default for most users |
| `block` | Prevents exposure | High-vulnerability states |
| `strict` | Aggressive blocking | Recovery, digital detox |

**Interactive Elements:**

1. **Pattern Detector**: Paste content, see manipulation analysis
2. **Attention Dashboard**: Today's budget, usage, high-value ratio
3. **Siren Gallery**: Examples of manipulation patterns with explanations
4. **Muse Examples**: Content that's attention-worthy (contrast)
5. **Protection Simulator**: See how different modes handle same content

**Datasets:**

```typescript
const contentExamples = {
  sirens: [
    {
      content: "BREAKING: You won't believe what just happened!",
      patterns: ["outrage_bait", "false_urgency"],
      confidence: 0.92,
      recommended_action: "block"
    },
    {
      content: "Only 1 seat left at this price! 23 people viewing now!",
      patterns: ["false_urgency", "social_proof_fake", "fomo_induction"],
      confidence: 0.95,
      recommended_action: "warn"
    },
    {
      content: "We noticed you haven't logged in... we miss you 💔",
      patterns: ["guilt_trip", "parasocial_exploit"],
      confidence: 0.78,
      recommended_action: "flag"
    }
  ],
  muses: [
    {
      content: "Here's a thoughtful analysis of the climate report (15 min read)",
      patterns: [],
      assessment: "Informs, respects time, no manipulation",
      recommended_action: "allow"
    },
    {
      content: "This course takes 20 hours. Here's a realistic timeline.",
      patterns: [],
      assessment: "Honest about cost, supports decision-making",
      recommended_action: "allow"
    }
  ],
  edgeCases: [
    {
      content: "Limited time offer: 50% off annual subscription",
      patterns: ["scarcity"],
      assessment: "Could be genuine sale or manufactured urgency",
      recommended_action: "context_dependent"
    }
  ]
};
```

**UI Components:**
- `AttentionBudget` - Visual of daily allocation and usage
- `PatternScanner` - Input for content analysis
- `SirenCard` - Detected pattern with explanation
- `MuseCard` - Quality content example
- `ProtectionMode` - Mode selector with descriptions
- `DetectionLog` - History of flagged content

---

### E2. Mental Health Context (`/psychosecurity/mental-health`)

**Concept:** Sensitive mental health information can be shared with VCP's graduated disclosure—enough for helpful adaptation without surveillance or judgment.

**Mental Health Context Layers:**

| Layer | Content | Who Sees |
|-------|---------|----------|
| **Public** | "I'm using this for stress relief" | Everyone |
| **Consented** | "I have anxiety, prefer gentle pacing" | AI with consent |
| **Minimal** | `seeking_support: true` (boolean only) | Platforms that need to know |
| **Private** | Diagnoses, triggers, history | Nobody—stays local |

**Adaptation Flags:**

| Flag | Effect | Example |
|------|--------|---------|
| `gentle_language` | Softer phrasing | "This didn't work out" vs. "You failed" |
| `avoid_pressure` | No urgency language | "When you're ready" vs. "Do this NOW" |
| `celebrate_small_wins` | Positive reinforcement | Acknowledge progress |
| `check_in_offers` | Periodic wellbeing check | "How are you feeling about this?" |
| `shorter_sessions` | Reduced duration | Automatic session breaks |
| `skip_competition` | No leaderboards | Remove comparative elements |

**Crisis Protocol:**

```typescript
const crisisProtocol = {
  indicators: [
    "crisis_language_detected",
    "sharp_mood_decline",
    "explicit_distress_signal"
  ],
  response: {
    if: "escalation_consent === true",
    then: "Offer crisis resources, optionally notify trusted contact",
    else: "Offer resources, respect boundary, do not escalate"
  },
  guarantee: "User maintains control even in crisis unless pre-consented"
};
```

**Privacy Guarantees (displayed prominently):**

1. **Private context never transmitted**: Diagnoses, triggers, medications stay local
2. **Minimal = booleans only**: "Has mental health context: true" reveals nothing specific
3. **AI ≠ Human visibility**: Can share more with AI (no memory) than humans (form judgments)
4. **Escalation requires consent**: Even crisis detection respects pre-set boundaries

**Contrast Scenarios:**

```typescript
const mentalHealthScenarios = {
  minimalSharing: {
    name: "Maximum Privacy",
    context: {
      seeking_support: true,
      share_with_ai: "none",
      share_with_humans: "none"
    },
    adaptations: ["Platform knows to be cautious, nothing more"]
  },
  moderateSharing: {
    name: "Helpful Adaptation",
    context: {
      seeking_support: true,
      professional_involved: true,
      share_with_ai: "moderate",
      share_with_humans: "minimal",
      requested_adaptations: ["gentle_language", "avoid_pressure"]
    },
    adaptations: ["AI uses gentle language", "No deadline pressure", "Humans see only booleans"]
  },
  crisisReady: {
    name: "Crisis Protocol Active",
    context: {
      seeking_support: true,
      professional_involved: true,
      crisis_indicators: false,
      escalation_consent: true,
      share_with_ai: "full",
      share_with_humans: "moderate"
    },
    adaptations: ["Full AI adaptation", "Trusted contact can be notified if crisis detected"]
  }
};
```

**Interactive Elements:**

1. **Context Editor**: Set all mental health context fields (existing: `SensitiveContextEditor`)
2. **Visibility Preview**: See exactly what each stakeholder type would see
3. **Adaptation Preview**: How AI behavior changes with this context
4. **Scenario Loader**: Quick-load example configurations
5. **Privacy Audit**: "Your private context would remain hidden in all cases"

**UI Components:**
- `SensitiveContextEditor` - Full context configuration (existing)
- `StakeholderView` - What each party sees (AI, Platform, Human)
- `AdaptationPreview` - Before/after examples of adapted responses
- `GuaranteesPanel` - Privacy promises, prominently displayed
- `CrisisConfig` - Escalation consent settings

---

## Shared Components Needed

### Cross-Category Components

| Component | Used In | Description |
|-----------|---------|-------------|
| `ContrastView` | All | Side-by-side comparison of contexts |
| `BaselineToggle` | All | Show/hide what happens without VCP |
| `AuditPanel` | All | What was shared, withheld, influenced |
| `PresetLoader` | All | Quick-load example configurations |
| `VCPTokenDisplay` | All | Live token encoding view |

### Category-Specific Components

**Coordination:**
- `AgentCard`, `AuctionFloor`, `NegotiationTable`, `PolicyVote`, `TrustMeter`

**Self-Modeling:**
- `DimensionSlider`, `StateRadar`, `CalibrationScore`, `GroundingMarker`

**Adaptation:**
- `PathNode`, `LoadMeter`, `AdaptationLog`, `ProgressProjection`

**Psychosecurity:**
- `PatternCard`, `AttentionBudget`, `SirenMuseCompare`, `StakeholderView`

---

## Implementation Order

**Recommended sequence based on dependencies and impact:**

### Sprint 1: Foundation
1. Shared components (`ContrastView`, `AuditPanel`, `PresetLoader`)
2. URL restructure with redirects
3. Category index pages

### Sprint 2: Self-Modeling (most self-contained)
1. Interiora Explorer (builds on existing components)
2. Belief Calibration
3. Reality Grounding

### Sprint 3: Psychosecurity (high impact)
1. Attention Protection (builds on existing `AttentionShield`)
2. Mental Health Context (builds on existing `SensitiveContextEditor`)

### Sprint 4: Adaptation (builds on learning components)
1. Learning Paths (builds on existing `LearningPathViz`)
2. Cognitive Load (builds on existing `CognitiveLoadMeter`)

### Sprint 5: Coordination (most complex)
1. Negotiation (simpler two-party)
2. Auction (multi-party, competitive)
3. Policy Design (multi-party, collaborative)

---

## Success Metrics

- All "Coming Soon" pages become functional demos
- Each demo has:
  - ≥2 contrast contexts
  - Baseline comparison
  - Audit view
  - ≥3 presets
- Consistent design language
- Mobile-responsive
- Accessible (WCAG 2.1 AA)
- Build passes: 0 errors, 0 warnings
- Load time: <3s on 3G

---

*Created: 2026-01-21*
*Status: Ready for implementation*
