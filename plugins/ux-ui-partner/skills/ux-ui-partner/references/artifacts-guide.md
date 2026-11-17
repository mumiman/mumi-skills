# UX Artifacts Guide

Formats and templates for specific UX deliverables. Use when the user asks for a particular artifact directly.

## Persona

Use when: the user is defining their target audience or wants to ground decisions in a specific user type.

```markdown
## Persona: [Name — e.g., "Maya, the busy freelance designer"]

**Role:** [Job title / life role]
**Age range:** [20s / 30s / ...]
**Tech literacy:** [Low / Medium / High]
**Context of use:** [Where, when, on what device]

**Goals:**
- [What they're trying to achieve in the product]
- ...

**Frustrations:**
- [Current pain points]
- ...

**Key quote:** "[A sentence that captures their mindset]"

**What success looks like for them:** [One sentence]
```

Keep personas grounded — note whether they're based on actual research or are provisional (assumption-based). Flag assumptions clearly.

---

## User journey map

Use when: showing how a user moves through a process over time, especially to find pain points.

Table format (works well in Markdown):

| Stage | User action | Thinking | Feeling | Pain points | Opportunities |
|-------|-------------|----------|---------|-------------|---------------|
| Awareness | Hears about product | "Is this for me?" | Curious | Not sure what it does | Clearer value prop on landing |
| Signup | Creates account | "Why do they need my phone?" | Hesitant | Too many fields | Progressive profiling |
| First use | Opens dashboard | "Where do I start?" | Overwhelmed | No guidance | Onboarding tour |
| ... | ... | ... | ... | ... | ... |

Use 4-7 stages. Don't make this a 20-stage novel.

---

## User flow

Use when: specifying the sequence of steps and decisions in a task.

Text-based flow:

```
[START]
   ↓
Landing page
   ↓
Click "Get started"
   ↓
Enter email  ─→ (invalid?) → Show inline error, stay on page
   ↓ (valid)
Send verification code
   ↓
Enter code  ─→ (wrong?) → Show error, offer resend (max 3 attempts)
   ↓ (correct)
Set password
   ↓
Dashboard [END — first-time users see onboarding tour]
```

Include:
- Decision points (with branching)
- Error paths
- Entry and exit points
- System actions vs. user actions (can be marked differently)

For complex flows, consider producing a diagram (e.g., Mermaid flowchart) instead of text.

---

## Information architecture

Use when: structuring content, navigation, or how features are grouped.

Tree format:

```
Home
├── Products
│   ├── Category A
│   │   ├── Subcategory 1
│   │   └── Subcategory 2
│   └── Category B
├── Account
│   ├── Profile
│   ├── Orders
│   └── Settings
│       ├── Notifications
│       ├── Privacy
│       └── Billing
└── Help
    ├── FAQ
    └── Contact
```

Principles to apply:
- **Shallow over deep.** Users tolerate more siblings better than more ancestors. Aim for 3 levels max where possible.
- **Mutually exclusive categories.** If a thing could live in two places, the categories are wrong.
- **Match user mental model, not org chart.** Structure by how users think, not how the company is organized.

---

## Wireframe description

Use when: the user wants a low-fidelity layout described before they build/design it.

Describe top-to-bottom, left-to-right:

```markdown
## Wireframe: [Screen name]

**Layout:** [Single column / two column / grid / etc.]
**Max width:** [e.g., "640px for content, full-bleed for hero"]

**Top:**
- Header bar with logo (left), nav (center), avatar menu (right)

**Hero section:**
- H1 headline, left-aligned
- Subtitle below, 60% width
- Primary CTA button below subtitle, left-aligned

**Main content:**
- [Section 1 description]
- [Section 2 description]

**Footer:**
- [Links, social, legal]

**Key interactions:**
- [Hover states, click behaviors, transitions]

**Responsive notes:**
- Mobile: nav collapses to hamburger, hero stacks, ...
```

---

## Usability test script

Use when: the user wants to validate a design with real users.

```markdown
## Usability Test: [What's being tested]

**Goal:** [What question this answers — e.g., "Can new users complete signup without help?"]
**Participants:** [Who — e.g., "5 people who have never used the product, matching our primary persona"]
**Duration:** [Typically 30-45 min]

**Tasks:**
1. "[Realistic scenario + task — e.g., 'You just heard about this product from a friend. Starting from the homepage, create an account and set up your first project.']"
2. ...

**Observe:**
- Where do they hesitate?
- What do they say out loud (think-aloud protocol)?
- Where do they make errors or go down wrong paths?
- Do they complete the task? How long does it take?

**Post-task questions:**
- What was confusing?
- What did you expect to happen that didn't?
- On a scale of 1-7, how easy was this? (SEQ — Single Ease Question)

**Success criteria:**
- [X% of users complete without help]
- [Average SEQ score ≥ Y]
```

---

## Choosing the right artifact

- **Understanding users:** Persona, journey map
- **Defining a problem:** Problem statement, journey map with pain points
- **Designing a solution:** User flow, wireframe, design brief
- **Organizing content:** Information architecture
- **Validating:** Usability test script
