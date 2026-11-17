# Tutorial specification v2

Validate with `schemas/tutorial.schema.json` after normalization. Keep content separate from `target`, `screenshot`, `overlay` and `render` configuration. All strings are plain text, never executable HTML/JS. Thai and English locale codes are `th` and `en`; legacy `thai`/`english` are accepted.

| Field | Meaning |
|---|---|
| `schema_version` | 2; omitted means legacy v1 |
| `title`, `intro`, `prerequisites` | Purpose and prerequisites |
| `steps[].id` | Stable ID independent of numbering; unique |
| `title`, `goal`, `action`, `instruction`, `expected_result` | Task content; instructions must be nonempty |
| `evidence` | `kind`, `source`, `status`, `supports`; source reference is mandatory when verified |
| `target.selector`, `fallbacks` | Selectors actually observed in source/DOM; do not fabricate fallbacks |
| `target.route` | Exact pathname, optionally query/hash; pathname-only accepts any query/hash. Avoid secrets in routes |
| `target.timeout_ms` | 0–30000, default 5000; controls waiting notice, not permanent lockout |
| `target.wait_for` | `{selector,state}`; state `visible`, `attached`, or `hidden`; no arbitrary expressions |
| `target.visible` | If present must be true; hidden targets cannot be highlighted |
| `target.enabled` | Default true; false permits informational highlighting of a disabled target; target focus stays disabled |
| `target.index` | Legacy opt-in to an indexed match; warns because DOM order is brittle |
| `screenshot` | Local PNG/JPEG/WebP path; optional original `width`, `height`, `highlight:[x,y,w,h]`, `redactions`, `alt`, `privacy_reviewed`, `annotated` |
| `overlay.placement` | `auto`, `top`, `bottom`, `left`, `right`; runtime prioritizes available space |
| `depends_on` | Earlier step IDs; validation/planning metadata, not a branching engine |
| `optional` | Planning metadata; users can skip any step; no automatic branching |
| `locales`, `i18n` | Translation dictionary and step-field keys; missing key falls back to plain text |
| `controls` | Overrides to runtime UI labels; see LABELS in overlay.js |
| `render` | `accent`, `font`, `document_font`, `radius`, `dim`, `border`; no external font fetching |

Evidence status applies only to the listed `supports` values (`target`, `action`, `outcome`, `route`). A screenshot may verify a target's appearance without verifying the result of clicking it. A source-based selector is not browser-tested. These fields are traceability declarations, not proof that the script can authenticate evidence. The agent must inspect the referenced evidence.

Use original image pixels. Browser collector rectangles use viewport CSS pixels: convert using actual screenshot width/height and capture viewport/crop offsets, not an assumed devicePixelRatio. A viewport rectangle must not be reused for a full-page capture without conversion. Redactions are opaque rectangles applied before annotation; metadata is stripped when re-encoding. Re-capture/crop very tall images when text becomes unreadable.

## Migration

`python3 scripts/migrate_spec.py --spec steps.json --output steps-v2.json`

Never overwrite the source. `caption` becomes `instruction`; explicit legacy `description` remains as `overlay.instruction` only when different. `selector`, `selector_index`, and `tooltip_position` move into nested fields. String screenshots become `{path, annotated:true}`. `color` moves to `render.accent`; `logo` remains supported. IDs are generated for legacy steps and numbering follows array order. Paths are rebased when the output moves; using parent-directory assets then requires `--asset-root` explicitly.

Legacy files remain directly accepted by builders. Empty steps, invalid colors, malformed fields and unsupported keys fail instead of silently producing broken files. Missing evidence/privacy is warned in compatibility mode and fails `--strict`; the migration never marks legacy data verified. This is an intentional tightening of previously unsafe inputs, not a promise to accept every malformed legacy object.
