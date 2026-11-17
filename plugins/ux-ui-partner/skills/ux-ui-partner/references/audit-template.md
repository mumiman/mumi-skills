# Heuristic Audit Report Template

Use this template when running a full UX/UI evaluation on an existing screen, flow, or product. Always lead with an executive summary so busy users know the TL;DR before diving in.

## Structure

```markdown
# UX/UI Audit: [Product/Screen Name]

**Evaluated:** [What — e.g., "Login screen + password reset flow, iOS app v2.3"]
**User context:** [Who uses this and what they're trying to accomplish]
**Date:** [Date]

## 📋 Executive summary

[3-5 sentences. Overall state of the UI, the single biggest issue, the single biggest strength, and the bottom-line recommendation. A busy reader should be able to stop here and still know what to do.]

## 🔍 Findings

### 🔴 Critical (blocks users / excludes users / causes errors)

**C1. [Short title of issue]**
- **What:** [Specific element/behavior — e.g., "Submit button has no visible focus state"]
- **Why it matters:** [User impact + heuristic violated — e.g., "Keyboard users cannot tell which element is focused. Violates WCAG 2.4.7 (Focus Visible)."]
- **💡 Recommendation:** [Specific fix — e.g., "Add a 2px outline in brand color on :focus-visible, matching existing input field pattern."]
- **Effort:** S / M / L

[Repeat for each critical finding]

### 🟡 Major (causes friction or confusion)

[Same structure]

### 🟢 Minor (polish / consistency / nice-to-haves)

[Same structure]

## ♿ Accessibility spot-check

- [ ] Color contrast (text ≥4.5:1, large text ≥3:1)
- [ ] Touch targets ≥44×44pt (mobile) / 24×24px (web minimum)
- [ ] Focus states visible on all interactive elements
- [ ] Keyboard navigable (tab order logical, all actions reachable)
- [ ] Form inputs have associated labels
- [ ] Error messages are descriptive, not just "Invalid input"
- [ ] Images have alt text; decorative images marked as such
- [ ] No information conveyed by color alone

## 🎯 Prioritized action list

Top things to fix first, ordered by user impact / effort:

1. **[Finding ID] — [One-line action]** *(Impact: High, Effort: S)*
2. **[Finding ID] — [One-line action]** *(Impact: High, Effort: M)*
3. ...

## ✅ What's working well

[Brief list — don't skip this. Celebrates good patterns and prevents regression.]
- ...
- ...
```

## Guidelines for writing the audit

- **Lead with the summary.** Always. A 5-sentence exec summary is more useful to a busy reader than a 3000-word report they never finish.
- **Be specific.** "Hierarchy is unclear" is not a finding. "The primary CTA and the secondary link use the same weight and size, so users can't tell which action is primary" is a finding.
- **Quote the heuristic.** When you cite Nielsen or WCAG, name the specific principle (e.g., "Nielsen #5: Error Prevention" or "WCAG 1.4.3: Contrast Minimum").
- **Include effort estimates.** S = <1 day, M = 1-3 days, L = >3 days or requires design/backend changes.
- **Don't pad.** If there are 4 findings, there are 4 findings. Don't invent issues to hit a count.
- **Include "what's working."** Teams need to know what to preserve, not just what to fix.
- **Use emoji as section anchors, not decoration.** The templates above use 📋 🔍 ♿ 🎯 ✅ because they help the reader scan — don't sprinkle random emoji in the middle of findings.
