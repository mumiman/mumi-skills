# Discovery and planning

Use the least intrusive evidence source that establishes the task. Record which tools were actually available.

| Available evidence | Action | Limitation |
|---|---|---|
| Authorized live browser | Inspect navigation, relevant forms/tabs/dialogs and visible state; collect stable selectors; safely inspect a transition | Do not submit, purchase, delete or change live data without task authorization |
| Static HTML | `python3 scripts/inspect_html.py --html page.html --output inventory.json` | Cannot establish runtime state or dynamic behavior |
| React/Vue/Angular repository | Read route definitions, components, labels and tests with file/search tools | Do not treat source selectors or test claims as observed behavior |
| Screenshots | Inspect image dimensions and labels, annotate known regions | Cannot supply selectors or prove actions/outcomes |
| User description | Draft a proposed journey and label described outcomes | Description is user evidence, not browser verification |
| Existing spec | Normalize and validate, then recheck stale evidence | Old coordinates/routes may no longer match |

When browser DOM evaluation is permitted, `assets/discover.js` returns at most 200 visible controls with candidate selectors, uniqueness counts and CSS-pixel rectangles. It collects no field values, cookies or storage. Check labels/attributes for sensitive text before retaining the inventory. Its sensitivity flag is heuristic, not OCR or a privacy guarantee. `getComputedStyle` checks can miss occlusion; visually inspect the target.

Inspect one relevant user journey, not the whole site. Typical planning questions are: What task is completed? What state must exist before each action? Which transition reveals the next target? What visible evidence establishes success? Do not manufacture Login → Submit if the inputs show neither login nor submission.

Show one concise outline before generation. Ask only about a missing task outcome, genuinely ambiguous target or necessary access. Credentials must be entered by the user using the supported sign-in flow; never request them in a spec or capture them in screenshots. If a source conflicts with another, mark the disputed step unverified and resolve it before live delivery.

Use natural Thai verbs: “เลือกเมนู…”, “กรอก…”, “กด…”, “ตรวจสอบว่า…”. Retain the app's exact visible label in quotes. Keep instructions to one action, usually under 240 characters. Treat expected results as a separate field. Translation dictionaries do not translate automatically; the agent writes and reviews language-specific text.
