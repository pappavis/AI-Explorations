# Release 1.6.0 — UI review / TDD / limitations
Version: 1.6.0 | Release ChatID: A61E4C92

## User-facing correction
The previous GUI only displayed CLI output in a textbox; it did not show dashboard cards or a searchable per-firmware table. The new GUI displays a real dashboard and reads a structured status JSON exported by the unchanged firmware discovery/diff engine. Status auto-runs on opening. Refresh and update still call the original engine and then automatically re-check status.

## TDD evidence
RED: test_dashboard_contract.py failed with ModuleNotFoundError: firmware_dashboard.
GREEN: 27 tests passed in this environment. Includes offline status JSON integration and unchanged firmware bytes.
GUI smoke: Tkinter instantiated under Xvfb; rendered screenshot from illustrative fixture data.
Syntax: Python compile and sh -n passed.
Live endpoint: curl could not resolve thefirmwarehub.com; no real website, macOS, Logic Pro or plugin acceptance verified.

## Honest gaps
- Counts derive from the existing manifest and site metadata, not independently inspected VIBE FM runtime versions.
- The original core still uses module-level constants and compact one-line statements. The requested full class refactor is not complete; it was deliberately not attempted in this UI-only release.
- No real download/installation occurred during GUI smoke. The existing offline integration suite tests the download/validation path.
- The GUI uses Tkinter; availability on macOS Python installations is not guaranteed.
- The download percentage is package validation progress, not network-byte progress.
- Site version and internal firmware JSON version may differ; not falsely reconciled.
- SMK-37 remains catalog-only.
