# Caucasus: Passes and Sanctuaries

English Alpha 0.1.0 · CK3 1.20 · RICE regional flavor add-on

## Contents

- Eight Culture Expanded culture definitions: Circassian, Udi, Dagestani, Abkhaz, Laz, Svan, Tat and Alan. Alan replaces its existing definition. CE name lists, required pillars and Armenian Resilience are included.
- CE regional setup for 867, 1066 and 1178: innovation inheritance, county distributions and culture corrections for 23 existing historical characters. The import contains 65 per-start character actions and 59 county actions. A game rule can disable the setup in a new campaign.
- Five original decisions: repair and review the Derbent passage, support scholars in Lori, support Svaneti tower communities, and support learning near Kutaisi from 1106.
- Twenty-two original events: four patronage/policy choices and eighteen annual events about upkeep, caravans, manuscripts and community obligations.
- CE's Establish Transcaucasia decision and confirmation event, giving six decisions and twenty-three events in the standalone profile.
- An original generated Derbent decision banner. Other pictures, event backgrounds and character portraits use installed game/EPE resources.

The English localization includes 686 keys, including imported names and explicit vanilla terminology overrides. No translated gameplay localization is included yet. Future translations should follow the installed vanilla terminology in `research/vanilla-terminology.json`; Derbent is **杰尔宾特** in simplified Chinese.

## Built-in integration

These are authoring sources inside RICE Expanded, not a separately enabled mod. Scripts, localization and the Derbent texture are embedded in `RICE/`. The source CE appearance fields are retained here; Base uses vanilla visual fallbacks, while EPE and CE–EPE installation presets preserve the source appearance fields.

Compatibility overlays are applied by `tools/integrate_caucasus.py` during package construction. Each final package contains only `RICE/` and `RICE.mod`. Select Base, EPE or CE–EPE according to the installed base mods, then load RICE Expanded after those mods. No additional Caucasus or compatibility mod needs enabling. See `CAUCASUS-Expanded.md` at repository root.

The source overlay targets CE 1.19.0.6 (Workshop 2829397295) and EPE 1.20.0.3. Source changes require rebuilding and validating the presets. Start a new campaign to apply culture distributions.

## Gameplay

Regional decisions require direct possession of the named county. Adult rulers must be free and at peace. Lori and Kutaisi learning decisions require a Christian ruler. The annual pool applies to playable county holders; it has a 30% yearly chance and filters events against their current county support and policy.

Repairing Derbent costs 100 gold and grants ten years of restored passage. The ruler chooses one five-year county policy: trade, watch provisions, or maintenance duties. Reviewing the policy costs 25 gold with a three-year cooldown. Policies are county modifiers, and each choice removes the other policies before applying the new one.

Lori and Svaneti grants cost 100 gold for five years. The Kutaisi grant costs 150 gold and becomes available on 1106-01-01. Paid event choices check available gold. Numerical balance is provisional.

RICE's historical-context rule enables brief background tooltips. Events describe authored gameplay situations; specific conversations and disputes are not documented historical incidents.

## Adaptations from CE

- Eight culture records retain CE's original tokens, including names, traditions and appearance references.
- Imported AI-choice values and the standalone Transcaucasia content use a separate namespace.
- The standalone empire's de-jure changes happen when the crown is formed, rather than during initial setup. Its required region follows CE.
- CE's monolithic-culture restrictions are inserted into current vanilla rules. This regional package does not import CE's global CCU acceptance/GUI overhaul or the extra hybridization cost. Standalone labels describe language groups without advertising those absent acceptance bonuses.
- Two broken cultural-history concept links and obvious English prose issues are corrected. Existing vanilla culture and place names retain their vanilla English forms.
- CE has no separate new Caucasus character-history file in the inspected source. Its relevant existing-character culture changes are copied; unrelated fictional Balkan/Pannonia characters are excluded.

## Validation

No CK3 process was started. `research/static-validation.json` records checks of file overlays, duplicate imported definitions, dependency references, English localization, copied cultures and selected gameplay effects. `research/art-validation.json` records DDS decoding, dimensions, compression and mip-level integrity.

This is a statically checked alpha. Engine scope behavior, rendered UI, portrait appearance and campaign balance remain unverified.

Rebuild with `tools/import_ce.py`, then `tools/build_flavor.py`; each accepts or uses the documented installed source directories. Run `tools/validate.py` with explicit game, RICE, EPE and CE paths. See `research/ce-import-manifest.json` for selected source records and fingerprints, and `art/generation.json` for the complete banner prompt.

## Historical references

- [Derbent fortifications](https://whc.unesco.org/en/list/1070)
- [Haghpat and Sanahin](https://whc.unesco.org/en/list/777/)
- [Upper Svaneti](https://whc.unesco.org/en/list/709)
- [Gelati Monastery](https://whc.unesco.org/en/list/710)

See `CREDITS.md` for imported content and artwork attribution.
