# Validation and release checks

## Automated checks

Run from the skill directory:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/runtime.test.cjs
node --check assets/overlay.js
node --check assets/discover.js
python3 scripts/validate_spec.py --spec examples/steps-v2.json --report /path/qa.json --strict
```

`test_generators.py` checks legacy migration, malformed schemas, evidence requirements, injection escaping, path/symlink restrictions, raster redaction, geometry, DOCX ZIP/XML/images, numbering, Thai font slots, tall image bounds and text localization. `runtime.test.cjs` checks runtime state and cleanup with a deterministic DOM double. It cannot establish actual CSS/layout, mobile readability, native popover/focus behavior or screen-reader compatibility.

The optional `browser.spec.mjs` requires an installed `@playwright/test` and authorized browser execution. It tests only the bundled synthetic fixture. Do not install/run it when the environment prohibits browser access; record not_run. No fixture result proves the user's live selectors or business behavior.

## Live browser acceptance

Use the tool interfaces actually available. Do not bypass a browser tool restriction with another channel. Record viewport, browser, route, date, app build/version if known, evidence source and result per step.

- On each prerequisite state, resolve primary/fallback selector; require uniqueness unless an explicit legacy index was approved. Check visible label and occlusion visually.
- Try desktop 1280×800 and mobile 390×844; check tooltip/target readability, edge placement, wrapping, browser zoom and viewport resize.
- Exercise Next, Back, Skip, Close, Finish and Retry; verify restart does not duplicate roots/listeners.
- Exercise normal and nested scroll containers; verify no scroll loops and no highlight drift.
- Open actual menu/modal, delay target rendering, change route with pushState/back/forward, hide/remove target, then restore it.
- Check keyboard Tab/Shift+Tab, target-focus button, F6 return, Escape and focus restoration; test the intended screen reader separately.
- Reinitialize/destroy while waiting, and verify no remaining observer/timer/root. Check app controls remain usable.
- Verify the exact deployed CSP, including external stylesheet loading, top-layer behavior and Trusted Types.

## Word and screenshot acceptance

A structurally valid DOCX is not visually validated. Use a supported Word/LibreOffice renderer, then inspect every page: Thai glyphs and marks, fonts, headings/numbering, line wraps, image scaling, annotations, caption associations and overflow. If unavailable, mark `rendered_layout_fonts_annotations:not_run`. Do not claim font substitution will always work.

Inspect the original screenshot before deriving coordinates and the sanitized annotation afterwards. Confirm image dimensions/capture viewport. Review PII manually; the scanner is not OCR. Pixel-based redaction tests establish the specified boxes are opaque, not that every sensitive field was found.

## Reporting

Each builder writes `OUTPUT.qa.json`. Checks use `passed`, `failed`, `not_run`; aggregate is failed if any fail, partial if any are not_run, otherwise passed. `--strict` fails unverified target evidence, selector evidence based only on screenshots/descriptions, missing privacy review, or missing dimensions for highlights. Expected outcomes remain warnings if not supported by evidence.

Retain generated reports, then add actual browser/render review results with evidence. Do not convert a not_run to passed because unit tests passed. Separate generator regression results, fixture integration results and live-app acceptance results. Deliver unresolved warnings and missing checks with the artifact.
