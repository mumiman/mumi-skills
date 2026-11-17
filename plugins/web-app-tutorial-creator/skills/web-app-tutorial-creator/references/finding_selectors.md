# Ground selectors in evidence

Prefer a verified, unique `data-tour`, `data-testid`, or stable ID. Generated React IDs and CSS hashes are not stable merely because they are IDs/classes. Check `querySelectorAll(selector).length === 1` in the required route/state when a browser tool permits this operation.

Use fallbacks only when every alternative was observed and refers to the same control. Repeated class names and `nth-child` paths require a stronger stable attribute or an explicit, fragile legacy index. Invalid/ambiguous selectors are recoverable runtime states, never a reason to highlight the first result silently.

For nontechnical users, inspect available HTML/browser evidence yourself. Ask for a sanitized relevant component or a screenshot only when needed. Offer DevTools guidance as a fallback: inspect the control, look for stable IDs/data attributes, send only that element's markup. Do not request the whole body when it may contain private information. “View page source” may omit dynamically rendered elements.
