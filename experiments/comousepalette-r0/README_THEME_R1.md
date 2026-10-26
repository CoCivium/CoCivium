# CoMousePalette+ Green R1 | optional presentation theme

**State:** review candidate. **Not installed on X2; physical thumb mapping untested.**

The same bounded CoCopy UI now has three intentionally separate presentation styles:

| Theme | Backgrounds | Text | Purpose |
| --- | --- | --- | --- |
| `Forest` (default on this branch) | Forest `#11271F`, header `#184332`, bottom panel `#18362B` | `#F0F7F0` | Gentle green context framing and quiet black-green editor |
| `Sage` | Pale sage `#E3F1E3`, header `#C6E5CC` | `#163523` | Bright daytime workspace |
| `Classic` | Original Windows system controls | Windows-controlled | Accessibility/system-theme fallback |

The documented foreground/background combinations have WCAG contrast ratios above 7:1 under the static formula. Live physical display, scaling, forced-color behavior, and assistive-tech compatibility remain untested.

## Run the file after the verified R1 media helper is installed

```powershell
pwsh -NoLogo -NoProfile -STA -File .\CoMousePalette_R0.ps1 -Theme Forest
pwsh -NoLogo -NoProfile -STA -File .\CoMousePalette_R0.ps1 -Theme Sage
pwsh -NoLogo -NoProfile -STA -File .\CoMousePalette_R0.ps1 -Theme Classic
```

Windows High Contrast automatically selects Classic despite a requested Forest/Sage theme. Close the window to stop. Nothing is changed globally, no registry or mouse button is remapped, no clipboard is read except via an explicit button, and no automatic paste or outbound request is performed.

**Important:** The existing [pinned X2 R1 installer](START_ON_X2_R1.md) is intentionally unchanged. It still downloads the previously verified R1 source. A separately version-pinned Green candidate can be tried without replacing that stable script.

## Test limits

- `python -m unittest discover -s tests -p 'test_theme.py' -v`: color contrast, explicit privacy hold, Classic fallback, forbidden global hooks.
- Windows PowerShell 7 selftest: `pwsh -NoProfile -STA -File CoMousePalette_R0.ps1 -SelfTest -Theme Forest` (repeat for Sage and Classic).
- These are source and no-window STA tests, not a screenshot, mouse-driver, or physical-X2 proof.
- Never infer that a green category implies permission to view data or send anything.

`PRESENTATION_NE_AUTHORITY | THEME_NE_OS_WALLPAPER | SOURCE_NE_X2_ADOPTION`
