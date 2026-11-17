# Live overlay integration

## API and lifecycle

Generate with `build_overlay.py`. The legacy HTML contains `<script id="watc-script">` with the runtime, sanitized config, and CSS passed to `WATC.configure`. To embed, copy this script without its final harness-button listener and connect `WATC.start()` to your app's help button. The former `watc-style` block is replaced by Shadow DOM styles; old instructions to copy both named blocks must be updated.

Prefer `--external`: it emits `NAME.runtime.js`, `NAME.css`, `NAME.init.js` and a harness. Serve assets from the app's origin. The sample initializer expects a button with ID `watc-start`; replace that listener with the host's own integration. Do not inject a second copy on every route render.

```js
const tour = WATC.configure(spec, {styleUrl: '/assets/tutorial.css'});
helpButton.addEventListener('click', () => tour.start());
// On host component unmount:
tour.destroy();
```

`WATC.start()`, `stop()`, `goTo(index)` remain. `destroy()`, `getState()` and `inspect()` are added. `inspect()` checks currently mounted DOM only; it does not activate future routes. Configure with normalized runtime spec (the builder strips screenshots/evidence paths). `create/configure` replaces the prior instance and removes its listeners/root. Start/stop are restartable. Destroy is final for that instance; configure a new instance to start again. Replaced instance handles cannot create stale overlays.

## States and dynamic UI

State is `idle`, `waiting`, `active`, `missing`, `finished` or `destroyed`. Waiting is bounded (default 5 s). A missing target keeps Close, Skip, Back, Retry and Next/Finish available. The observer and 200 ms active-only refresh detect delayed controls, hidden-to-visible changes and route transitions. They never auto-click, submit, navigate or patch the router.

Native `scrollIntoView` runs once per newly resolved target/step, with immediate scrolling to honor reduced motion and avoid smooth-scroll recursion. Scroll/resize adjusts existing marker/tooltip positions. Overflow ancestors clip the highlight. Manual popover puts the isolated Shadow DOM root in the browser top layer when supported; fallback uses z-index. When a native modal opens, the root moves inside the active dialog so its controls are not made inert; it moves back when the dialog closes. This path is logic-tested but still requires native browser validation. Transformed ancestors need host testing.

Use `target.route` and `wait_for` to wait for the user to open a modal/menu or navigate through a SPA. React, Vue and Angular work through their rendered DOM, not framework internals. Native dialog/top-layer, sticky headers, nested clipping and extreme zoom require visual testing. Full-page reload loses tour state; the host must initialize again.

## Accessibility and appearance

The tooltip is a nonmodal dialog: controls are keyboard accessible; focus starts in the tooltip, returns to the launcher on close, and is not trapped away from the app. “Go to target” focuses the control; F6 returns to the tutorial. Escape closes only when focus is in the tour/target so unrelated dialogs keep their keyboard behavior. Custom nonfocusable targets get a temporary tabindex that is restored. Test with the intended screen reader; automated DOM tests are not screen-reader certification.

Configure `render` tokens, but keep high contrast. The primary action remains dark with white text independent of accent color. Thai defaults use Tahoma/Noto Sans Thai/system fonts; none are downloaded. Large targets and tiny viewports may force some tooltip overlap; inspect and crop/split the tutorial step or choose another target. Long text scrolls inside the tooltip.

## CSP and security

No eval, Function, innerHTML, inline event attributes, telemetry or remote fonts. The standalone harness uses an inline script; it needs an appropriate nonce/hash when embedded under a restrictive policy. `--external` uses same-origin external JS/CSS, with the stylesheet loaded into Shadow DOM. For inline style mode the host can pass `{css,nonce}`. Positioning uses DOM style properties; test the exact deployed CSP and any Trusted Types policy. Do not recommend disabling CSP or allowing all unsafe inline content.

One document/root is supported. Cross-origin iframes, closed shadow targets, canvas-only controls and off-DOM virtualized rows require host-specific adapters and are not implemented here.
