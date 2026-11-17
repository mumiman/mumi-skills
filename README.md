# mumi-skills

Claude skills for field epidemiology, clinical-informatics work, and everyday
LLM workflows. Most skill instructions are written in Thai.

## Skills

| Skill | What it does |
|---|---|
| `brainstorm` | Multi-perspective brainstorming: genuinely different ideas, debate of strengths and weaknesses, then a menu of parts to combine into a solution. |
| `field-epidemiologist` | A calm, causally skeptical senior field epidemiologist who reviews outbreak investigation reports and event risk assessments, and helps think through new events until control measures have an owner, a timeline, and a stop criterion. Not for individual patient care. |
| `handoff-other-llm` | Summarises project and session state into `HANDOFF.md` so another coding agent (Codex, Cursor, Gemini CLI, Antigravity) can continue immediately. Scans for secrets before writing. |
| `presentation-creator` | Builds PowerPoint decks in four house styles with a pre-build menu (style, purpose, audience, tone, palette). Uses the `pptx` skill to produce the file. |
| `real-human-tester` | Role-plays imperfect real users on a web or mobile app, one role at a time, then gives feedback or fixes the app. |

## Install

### Claude Code

```
/plugin marketplace add mumiman/mumi-skills
/plugin install field-epidemiologist@mumi-skills
```

Replace `field-epidemiologist` with any skill name above.

### Claude.ai / Claude Desktop

Download the folder `plugins/<name>/skills/<name>/`, zip it, and upload it under
Settings → Capabilities → Skills.

## Notes

- `presentation-creator` refers to four template files
  (`Template_OutbreakReport.pptx`, `Template_SectionTab.pptx`,
  `Template_NavTabs.pptx`, `Template_Slant.pptx`) that are not included. The
  skill still works from the style specs in `SKILL.md`; attach a template if
  you have one.
- `real-human-tester` creates and submits data in the app under test. Use test
  accounts and obviously fake data, and never point it at a production system.
- These skills give reasoning support, not medical or public-health
  authority. Verify outputs against your own guidelines.

## License

MIT
