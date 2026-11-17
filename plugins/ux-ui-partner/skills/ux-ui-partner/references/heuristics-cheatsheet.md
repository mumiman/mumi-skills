# UX Heuristics & Principles Cheatsheet

Quick reference for common frameworks. Cite these by name in audits and critiques so recommendations are grounded.

## Nielsen's 10 Usability Heuristics

1. **Visibility of system status** — Always keep users informed about what's happening through feedback.
2. **Match between system and real world** — Use familiar words, concepts, and conventions; not internal jargon.
3. **User control and freedom** — Support undo/redo, easy exits from unwanted states.
4. **Consistency and standards** — Follow platform conventions; same things should look/behave the same.
5. **Error prevention** — Design to avoid errors in the first place; confirm destructive actions.
6. **Recognition rather than recall** — Show options; don't make users remember things from one screen to the next.
7. **Flexibility and efficiency of use** — Accelerators for experts, simple paths for novices.
8. **Aesthetic and minimalist design** — Every extra element competes with relevant ones.
9. **Help users recognize, diagnose, and recover from errors** — Error messages in plain language, pointing to a solution.
10. **Help and documentation** — Searchable, task-focused, concise.

## Cognitive load laws

- **Hick's Law:** Time to decide increases with the number and complexity of choices. → Fewer options, progressive disclosure, smart defaults.
- **Fitts's Law:** Time to acquire a target depends on its size and distance. → Primary actions: big, close to where the user's attention/cursor is.
- **Miller's Law:** People hold ~7 (±2) items in short-term memory. → Chunk information, limit menu items.
- **Jakob's Law:** Users spend most of their time on other sites, so they expect your site to work the same way. → Don't reinvent common patterns without good reason.
- **Law of Proximity (Gestalt):** Things close together are perceived as related. → Group related controls; separate unrelated ones.
- **Peak-end rule:** People judge an experience by its peak (best/worst) and its end. → Nail the first-run experience and the confirmation/completion moments.

## WCAG 2.2 AA essentials

Minimum bar for accessibility. If any of these fail, it's a critical-severity finding.

- **1.4.3 Contrast:** Text ≥4.5:1; large text (18pt+ or 14pt+ bold) ≥3:1
- **1.4.11 Non-text contrast:** UI components and graphics ≥3:1
- **2.1.1 Keyboard:** All functionality available via keyboard
- **2.4.7 Focus visible:** Keyboard focus indicator must be visible
- **2.5.5 Target size:** Touch targets ≥24×24 CSS pixels (44×44 recommended)
- **3.3.1 Error identification:** Errors clearly identified in text
- **3.3.2 Labels:** Form inputs have persistent, visible labels (not just placeholder)
- **1.1.1 Non-text content:** Images have text alternatives (or are marked decorative)
- **1.3.1 Info and relationships:** Semantic structure (headings, landmarks, lists) conveyed programmatically

## Platform conventions

### iOS Human Interface Guidelines — highlights
- Navigation: tab bar (≤5 tabs) for top-level, nav bar with back button for drilldown
- Destructive actions: red, confirmed via action sheet
- Don't reinvent system controls (date pickers, share sheet)
- Safe area insets matter — don't hide content behind notch or home indicator
- Touch targets ≥44×44pt

### Material Design 3 — highlights
- Navigation: bottom nav (3-5) for top-level, nav rail for tablets, nav drawer for >5
- Elevation and shadows communicate hierarchy
- Motion: easing and duration matter; use standard curves
- FAB for single primary action on a screen; don't overuse
- Touch targets ≥48×48dp

### Web conventions
- Logo in top-left, links home
- Primary nav at top or left
- Search prominent if content-heavy
- Underlined blue (or branded) text = link
- Forms: labels above fields (not placeholders-as-labels), inline validation, clear required/optional
- Responsive: mobile-first, test at 320px, 768px, 1024px, 1440px

## Design thinking (backbone framework)

1. **Empathize** — Understand the user through interviews, observation, data. Don't skip this.
2. **Define** — Frame the problem as a crisp "How might we..." statement.
3. **Ideate** — Generate many options before picking one. Quantity before quality.
4. **Prototype** — Make it real enough to test. Low-fi first.
5. **Test** — With real users. Iterate based on what you learn.

Not linear — loops and backtracks are normal.

## Jobs to be Done (JTBD)

> When **[situation]**, I want to **[motivation]**, so I can **[expected outcome]**.

Forces you to frame features around user jobs, not features-for-features-sake. Example:
> When *I'm adding a new expense on the go*, I want to *snap a photo of the receipt instead of typing*, so I can *log it quickly without losing the details*.

## Atomic design

Hierarchy for design systems:
- **Atoms** — Basic building blocks (buttons, inputs, labels)
- **Molecules** — Simple combinations (search bar = input + button)
- **Organisms** — Complex sections (header = logo + nav + search)
- **Templates** — Page-level skeletons
- **Pages** — Real content in templates

Useful when the user is building or evaluating a design system, not every feature.

## Red flags (common anti-patterns)

- Secondary/tertiary buttons with no border and no fill — they read as static text, so users don't know they're clickable (affordance failure). Give ghost/secondary buttons a visible border. Only the one filled primary button per view may be borderless.
- Placeholder text used as the only label
- Carousels/sliders that auto-advance (low click-through, accessibility issues)
- Infinite scroll without alternatives for finding specific items
- Dark patterns (confirmshaming, forced continuity, hidden costs)
- "Click here" link text (use descriptive link text)
- Hover-only interactions on touch devices
- Modals stacked on modals
- Confirmation dialogs for non-destructive actions ("Are you sure you want to save?")
- Error messages that blame the user ("You entered invalid data")
- Forms with no visible progress on multi-step flows
