---
name: user-settings-profiles
description: User treats the GUI settings JSON as per-experiment profiles, not a single hidden preferences blob
metadata:
  type: user
---

The user wants to keep multiple named settings files (one per simulation setup) and switch
between them from the GUI, rather than relying only on the auto-loaded
`grasshopper_gui_settings.json`. Requested Open/Save-As on 2026-08-28.

Implication for future work: any new widget added to the form is also a *profile* field —
it must round-trip through `_collect_settings()`/`_apply_settings()` or a user switching
profiles will silently keep a stale value from the previous profile. Prefer clearing/
resetting derived UI state (e.g. the volume tree) in `_apply_settings` so loading a profile
fully replaces the prior one instead of appending to it.
