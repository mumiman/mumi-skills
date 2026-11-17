# Usage examples

## A natural user request

“ช่วยทำคู่มือภาษาไทยสำหรับสร้างรายงานฉบับร่างจากหน้าเว็บนี้ ขอ Word และ preview”

Inspect the supplied URL/source/screenshots using permitted tools. Propose “เปิดแบบฟอร์ม → กรอกชื่อ → บันทึก → ตรวจข้อความยืนยัน” only when supported. Use the user's source evidence for titles/selectors; ask no per-step questions if the controls are unambiguous. Display the outline before generating. Do not claim the save is persistent without evidence.

## Runnable source-only example

`examples/app.html` is a deliberately synthetic fixture, not the user's application. Its Save draft handler only reveals a confirmation message; it does not persist data. `examples/steps-v2.json` grounds targets/actions in the source and leaves the outcome unverified at runtime.

```bash
python3 scripts/inspect_html.py --html examples/app.html --output /path/inventory.json
python3 scripts/validate_spec.py --spec examples/steps-v2.json --report /path/qa.json --strict
python3 scripts/build_docx.py --spec examples/steps-v2.json --output /path/tutorial-th.docx
python3 scripts/build_preview.py --spec examples/steps-v2.json --output /path/preview-th.html
python3 scripts/build_overlay.py --spec examples/steps-v2.json --output /path/tour.html --external
```

Without screenshots, Word and preview are explicitly text-only. A screenshot must be supplied/captured before claiming an annotated walkthrough. The fixture tests generate raster test images inside temporary directories; they are not app evidence.

## Screenshot-only request

“ทำคู่มือจากภาพหน้าจอทั้งสามนี้ ไม่ทราบ selectors”

Inspect screenshots, propose the visible task sequence, save original dimensions and pixel regions. Create `screenshot` objects with `path`, `width`, `height`, `highlight`, `alt` and privacy-reviewed/redaction fields. Set evidence kind `screenshot` and supports `target` only unless other evidence establishes actions/outcomes. Generate Word/storyboard; do not invent selectors to force a live overlay. Ask once if two visually identical controls make the target ambiguous.

## Legacy input

```bash
python3 scripts/migrate_spec.py --spec examples/steps-legacy.json --output examples/steps-migrated.json
python3 scripts/build_overlay.py --spec examples/steps-legacy.json --output /path/legacy-tour.html
```

Inspect migration warnings. Legacy evidence is unverified and cannot pass strict release validation until checked. Array order determines numbered actions. Use an approved `--asset-root` for legacy images outside the spec folder.

## Different app and tutorial languages

Keep English UI labels such as “New report” exactly as displayed. Write Thai action text around the label. Set `language:"th"` and `app_language:"en"`; no selector changes are required. For two deliverable languages, translate content into `locales`/`i18n`, then generate once per language. Translate title/intro/prerequisites in the selected spec as these are plain content fields, not automatic translation keys.
