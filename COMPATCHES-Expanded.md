# RICE Expanded compatibility patches — 1.20 beta

Updated 2026-10-07 against the maintainer's **modified local RICE**, installed Culture Expanded (CE, descriptor 1.19.0.6), and installed Ethnicities and Portraits Expanded (EPE, descriptor 1.20.0.3). The RICE base mod is unchanged by this update. These patches do not constitute a full CE migration to CK3 1.20.

## Comparison and changes

- Installed RICE+EPE (Workshop 2553043828) and master at `0a19a061` have identical `.txt` script tokens. There are 225 byte-different files from line-ending normalization and a descriptor version difference. No installed RICE+CE patch was found, so the CE patch was compared against the repository's existing patch and the local base mods. Full initial comparison: [baseline report](reports/compatch-baseline.json).
- Rebase six EPE culture gameplay differences on local RICE: Krivich traditions, Khasi hill dwellers, Ngaju map color, Malagasy parent `ngaju` (instead of `dayak`), Tolaki equitable tradition, and Bungku hill dwellers. Retain all original EPE appearance fields.
- CE supplies the 19 cultures it shares with RICE; filename overrides remove competing RICE/EPE definitions while preserving other cultures in those files. CE cultural choices and appearance remain intact, including CE name lists and CCU metadata.
- Remove overlapping RICE pillar definitions where CE supplies them; also resolve five duplicate languages inside CE's `xRICE_language.txt` in favor of its dedicated language files, preserving the remaining CE file content and metadata.
- Restore 50 suppressed RICE pillars, including American, Australian and Papuan languages/heritages and future-save placeholders. Restore local RICE culture assignments, traditions and the corresponding innovation eligibility. This also preserves equal military custom for Samoan culture.
- Remove the legacy `is_RICE_CE_temp_compatch_loaded = yes` override: RICE's default `no` now permits its normal Australian/American startup innovation grants, which the old temporary patch suppressed because it removed their pillars.
- Use portable `mod/...` paths and remove official Workshop publishing IDs. Display names explicitly identify these as Expanded beta patches. The CE folder retains its legacy `RICE+CE Compatch for 1.19` name so existing paths stay usable.

## Install and load order

Extract the patch ZIP(s) into your CK3 user `mod` directory. Each ZIP contains a mod folder and its matching `.mod` file. Remove the previous local copy of the same patch folder first; stale files include the removed legacy startup gate. Enable only one version of each patch, and disable the official RICE+EPE Workshop patch when using this Expanded EPE patch.

For RICE and EPE, load in this order:

1. Your modified RICE **or** RICE Expanded (one base RICE only)
2. Ethnicities and Portraits Expanded
3. RICE Expanded + EPE Compatibility (1.20 Beta)

For CE, load:

1. Your modified RICE **or** RICE Expanded
2. Ethnicities and Portraits Expanded
3. Culture Expanded
4. RICE Expanded + EPE Compatibility (1.20 Beta)
5. RICE Expanded + CE Compatibility (1.20 Beta)

CE requires EPE; see [CE's Workshop description](https://steamcommunity.com/sharedfiles/filedetails/?id=2829397295). **The CE patch must be last**, so the EPE patch cannot reinstate the duplicate shared cultures. Other map/culture overhauls require separate compatibility work. The current launcher playset, Workshop installations and saves were not modified.

## Script validation

No game process was started for this update. [Validation report](reports/compatch-validation.json) covers four configurations: modified local RICE or repository Expanded, each with EPE alone or EPE+CE and their patches. Each configuration has zero reported errors: 214 effective patched cultures for EPE, 195 for CE+EPE, plus the 19 shared cultures supplied by CE. Checks include:

- File overlays before registry analysis; RICE culture/pillar presence and uniqueness.
- Patched culture pillar, name-list, tradition, parent-culture and ethnicity references.
- Innovation pillar references and the Oceania startup gate.
- Local RICE gameplay preservation in patch-owned cultures, EPE appearance preservation, and CE shared definitions/CCU metadata preservation.
- Script assignment/bracket structure, including adjacent `key=value` syntax.

Source script/localization fingerprints in the report identify the exact local inputs without redistributing the base mods. The existing RICE validator also passes with zero errors and its unchanged 13 optional-mod/debug faith-reference warnings.

These checks do **not** validate rendering, DNA gene compatibility, all engine scopes, event execution, old saves or long campaigns. CE still declares 1.19 support; unrelated CE/vanilla conflicts are outside this focused compatibility patch. The release remains a prerelease.

Reproduce with Python 3.9+ (no third-party packages):

```sh
python3 tools/validate_compatches.py \
  --game /path/to/CK3/game \
  --rice /path/to/modified/RICE \
  --ce /path/to/CultureExpanded \
  --epe /path/to/EPE \
  --local-epe-patch /path/to/installed/RICE-EPE-patch
```

Optional `--local-ce-patch` compares an installed CE patch. `--output` selects the report path.
