# Design Brief Template

Use this template when helping a user ideate a new feature or project from scratch.

## Structure

```markdown
# Design Brief: [Feature / Project Name]

## 1. User & context

**Primary user:** [Role, tech literacy, context of use]
**Secondary users (if any):** [Who else interacts with this]
**Device/platform:** [Web / iOS / Android / desktop / multi-platform]

## 2. The job to be done

Using JTBD framing:

> When **[situation]**, I want to **[motivation]**, so I can **[expected outcome]**.

Current workaround or pain point: [How they do this today and why it's painful]

## 3. Problem statement

> How might we help **[user]** accomplish **[job]** without **[current pain]**?

Success looks like: [1-2 sentences describing the outcome]

## 4. Constraints

- **Technical:** [Stack, platform limits, existing systems to integrate with]
- **Timeline:** [If mentioned]
- **Team:** [Size, design resources]
- **Other:** [Compliance, accessibility requirements, brand guidelines]

## 5. Solution directions

Present 2-3 genuinely different approaches, not variants of one idea.

### Option A: [Name — e.g., "Wizard-style guided flow"]
- **Optimizes for:** [e.g., new users, discoverability]
- **Tradeoffs:** [e.g., slower for power users, more screens to build]
- **Sketch:** [1-2 sentence description of the flow]

### Option B: [Name]
- **Optimizes for:** ...
- **Tradeoffs:** ...
- **Sketch:** ...

### Option C: [Name]
- **Optimizes for:** ...
- **Tradeoffs:** ...
- **Sketch:** ...

**Recommendation:** [Which one and why, based on the user and constraints]

## 6. Detailed design — [Recommended option]

### User flow

Step-by-step, including edge cases:

1. [Entry point]
2. [Action]
3. [System response]
4. [Next action]
5. ...

Edge cases to handle:
- Empty state: [what the user sees first time]
- Error state: [what happens when X fails]
- Loading state: [what happens during wait]
- Success state: [confirmation / next step]

### Key screens

**Screen 1: [Name]**
- Purpose: [Why this screen exists]
- Primary action: [The one thing the user should do]
- Layout: [Top-to-bottom description — header, main content area, actions]
- Components: [e.g., "Input field with inline validation, primary CTA, link to help"]
- Microcopy:
  - Title: "[text]"
  - CTA: "[text]"
  - Helper text: "[text]"

[Repeat for each key screen]

### Interaction details

- [Any non-obvious interaction patterns — e.g., "Tapping the avatar opens a bottom sheet (not a new screen) to maintain flow context"]

## 7. Accessibility & inclusivity

- [ ] Works with keyboard only
- [ ] Works with screen reader (labels, landmarks, announcements)
- [ ] Color contrast ≥4.5:1 for text
- [ ] Touch targets ≥44×44pt
- [ ] Works without relying on color alone
- [ ] Content readable at 200% zoom

## 8. Validation plan

How to test this with real users before shipping:

- **Key question to answer:** [e.g., "Can first-time users complete signup without help?"]
- **Method:** [Moderated usability test / unmoderated / prototype test / smoke test]
- **Sample size:** [5-8 users is usually enough for qualitative]
- **Key metric to track post-launch:** [e.g., completion rate, time to first value, support tickets]
```

## Guidelines for writing the brief

- **Don't skip stages 1-3.** Jumping to solutions without naming the user and job produces generic designs.
- **Offer real alternatives.** Three options that optimize for the same thing aren't three options.
- **Write microcopy.** Button labels and error messages are design. Don't leave them as TODO.
- **Address edge cases explicitly.** Empty, error, loading, and success states are not afterthoughts.
- **Make accessibility a checklist, not a vibe.** Actually verify the items.
