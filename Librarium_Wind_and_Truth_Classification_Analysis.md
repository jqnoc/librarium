# Wind and Truth Classification Analysis

## Scope and method

This is a read-only analysis of the Librarium database at:

`C:\Users\Joaquín2\Joaquín Dropbox\JqnOC\Apps\LibrariumApp\jqnoc.db`

Snapshot used:

- Database last-write time: `2026-08-08 22:49:53 +02:00`
- SQLite integrity check: `ok`
- Total books: `724`
- Raw book records with at least one populated taxonomy field: `386`
- Effective classified book records after applying current `work_taxonomy` overrides: `410`, including `Wind and Truth`
- Target record: `Wind and Truth` by `Brandon Sanderson`
- Target `work_id`: empty, so its classification is stored directly on the book record rather than inherited from a shared work record

Books with no effective classification were excluded from the comparison. The report compares semicolon-separated values case-insensitively within the same taxonomy field, then applies the Librarium Taxonomy Guidelines manually. Exact reuse counts are evidence of vocabulary reuse, not automatic recommendations to copy a term to every matching book.

No database values were changed.

## Executive conclusion

The classification has a strong and recognizable Stormlight Archive shape. The major Genre, all four Subgenres, the Form, most Themes, and most Subjects are semantically plausible for this novel. It also reuses a substantial amount of established Sanderson vocabulary, especially from `The Way of Kings`, `Oathbringer`, and `Rhythm of War`.

The record should not be accepted unchanged, however. The main issues are:

1. `Settings` and `Historical Periods` are empty even though this is a large-scale secondary-world novel with established library vocabulary for Roshar and the fictional era of the Everstorm.
2. Ten values are duplicated across Themes and Subjects. Most of those values answer the Theme question and should be removed from Subjects; `Mental Health` and `Slavery` are better retained as Subjects; `War` needs one deliberate category decision.
3. `Secondary World Fantasy` duplicates `High Fantasy` and should be removed. `High Fantasy` is the preferred canonical Subgenre.
4. `Prophecies` is a likely wording inconsistency. The library already uses the singular `Prophecy` on comparable fantasy books.
5. `Magic` and `Magic Systems`, `Gods` and `Godhood`, and `Warfare` and `Epic Warfare` are not invalid duplicates, but they overlap enough to require a conscious level-of-specificity decision.
6. A few terms are new to the current vocabulary (`Armor`, `Godhood`, `Kingdoms`, `Military Leadership`, and `Weapons`). New values are acceptable when they describe the work accurately, but they should be retained only if they are useful beyond one isolated record.

My recommended direction is to keep the classification rich, remove category duplication, add the missing setting and period information, change `Prophecies` to `Prophecy`, and leave the genuinely semantic choices for manual confirmation rather than forcing mechanical normalization.

## Current classification

| Field | Current values | Assessment |
| --- | --- | --- |
| Genre | `Fantasy` | Correct and canonical; exactly one major Genre |
| Subgenres | `Epic Fantasy`; `High Fantasy`; `Military Fantasy`; `Secondary World Fantasy` | Three values are appropriate; remove the redundant non-canonical `Secondary World Fantasy` and retain `High Fantasy` |
| Form | `Novel` | Correct controlled Form |
| Themes | 39 values, listed below | Mostly appropriate; several duplicates with Subjects and a few overlapping concepts |
| Settings | *(empty)* | Clear omission for a secondary-world novel |
| Historical Periods | *(empty)* | Reasonable only if fictional chronology is intentionally omitted; `Era of the Everstorm` is an established candidate |
| Subjects | 34 values, listed below | Many are valid; several are abstract Themes duplicated here |
| Audiences | `Adult`; `General Readers` | Established and plausible |
| Tags | `Fantasy` | Separate from taxonomy; redundant with Genre but harmless if Tags are used for freeform discovery |

## Field-by-field review

### Genre

`Fantasy` is exactly the right major Genre. It is the only Genre, it is already used on 28 other effectively classified records, and there is no reason to add `Fiction` or another major Genre alongside it.

**Recommendation:** keep `Fantasy` unchanged.

### Subgenres

The current record has four values, but the canonical cleaned set has three. The following values are established in the library:

- `Epic Fantasy` appears on 13 other classified records.
- `High Fantasy` appears on 7 other classified records.
- `Military Fantasy` appears on 3 other classified records.
They describe different aspects of the same work:

- `Epic Fantasy` describes scale and narrative scope.
- `High Fantasy` describes the conventional secondary-world, mythic fantasy mode.
- `Military Fantasy` describes the sustained military focus.
`High Fantasy` is the canonical term for the secondary-world fantasy meaning represented by the deprecated `Secondary World Fantasy` value. The two labels should not coexist. The fact that both currently appear on records such as `Oathbringer` is legacy data to clean up, not a reason to retain both.

**Recommendation:** keep `Epic Fantasy`, `High Fantasy`, and `Military Fantasy`; remove `Secondary World Fantasy`. Do not replace them with `Adventure Fantasy`: that is a different emphasis and is not necessary merely because the novel contains journeys or battles.

### Form

`Novel` is the controlled singular Form used by 87 other classified records. It correctly describes presentation rather than genre.

**Recommendation:** keep `Novel` unchanged. Do not use `Epic` here; the taxonomy defines `Epic` as a traditional narrative Form, while `Epic Fantasy` is the Subgenre that applies here.

### Themes

The current list contains many defensible Themes: `Ambition`, `Courage`, `Duty`, `Faith`, `Fear`, `Forgiveness`, `Freedom`, `Friendship`, `Grief`, `Guilt`, `Honor`, `Hope`, `Identity`, `Justice`, `Leadership`, `Love`, `Loyalty`, `Memory`, `Mercy`, `Moral Responsibility`, `Oppression`, `Power`, `Purpose`, `Reconciliation`, `Redemption`, `Responsibility`, `Sacrifice`, `Self-Acceptance`, `Survival`, `Trauma`, `Truth`, `Unity`, `Violence`, and `War` all fit the Themes question when they describe the novel's ideas, values, conflicts, or lived experiences.

The library already reuses most of these. For example, `Identity` appears on 101 other classified records, `Hope` on 84, `Responsibility` on 74, `Freedom` on 70, `Courage` on 71, and `Friendship` on 53. Their frequency does not prove that every book deserves them, but it shows that the phrasing is compatible with the existing vocabulary.

The following decisions are more important:

| Theme value | Recommendation | Reason |
| --- | --- | --- |
| `Depression` | Keep in Themes; remove the duplicate Subject value | Depression is a lived psychological experience. `Rhythm of War` uses it as a Theme and reserves `Mental Health` for Subjects. |
| `Mental Health` | Remove from Themes; keep in Subjects | In this database it functions as a concrete psychological topic or domain. It is already a Subject on `The Way of Kings` and `Rhythm of War`. |
| `Family` | Keep in Themes; remove the duplicate Subject value | Family is explicitly treated as a Theme/relationship in the guidelines. |
| `Freedom` | Keep in Themes; remove the duplicate Subject value | Freedom is an abstract value, not a concrete topic in this record. |
| `Leadership` | Keep in Themes; remove the duplicate Subject value unless the book is being catalogued specifically as a study of leadership | The thematic value is already established; `Military Leadership` can remain as a more concrete Subject if it is materially discussed. |
| `Oppression` | Keep in Themes; remove the duplicate Subject value | Oppression is an abstract social conflict and is already used as a Theme on comparable books. |
| `Parenthood` | Keep in Themes; remove the duplicate Subject value | Parenthood is a lived human relationship/experience and is already used as a Theme on `Rhythm of War`. |
| `Slavery` | Prefer Subject; remove the duplicate Theme value | Slavery is a concrete social institution/topic in the local taxonomy. `The Way of Kings` and `The Final Empire` both use it as a Subject. `Oppression`, `Freedom`, and `Justice` can carry the thematic dimension. |
| `Trauma` | Keep in Themes; remove the duplicate Subject value | Trauma is a lived psychological experience. More specific Subjects such as `Psychology` or a named condition can remain when supported. |
| `War` | Keep in one category only | The library uses `War` both as a Theme and as a Subject. My preferred cleanup is to keep Subject `War` as the concrete central topic, remove Theme `War`, and retain Theme `Violence`. A project-wide policy could reasonably choose the reverse, but both copies should not remain. |

`Hatred`, `Mercy`, `Self-Acceptance`, `Unity`, `Violence`, and `War` are not errors merely because they are less common. `Mercy` appears once elsewhere, `Self-Acceptance` twice, `Unity` four times, `Violence` 18 times, and `War` six times as Themes. They are valid reusable concepts if they are genuinely central to this book.

`Fate` and `Free Will` are both defensible, especially because the novel explores their tension. Do not replace those two values mechanically with the hybrid `Fate versus Free Will`. The library has that hybrid on another book, but the current guidelines prefer one concept per value; the two separate terms are cleaner for filtering. The choice between `Fate` and the existing `Destiny` vocabulary should be handled as a project-wide policy, not as an automatic correction to this one book.

`Moral Responsibility` and `Responsibility` can coexist only if both levels are intentional. `Moral Responsibility` is the more specific ethical concept; `Responsibility` is broader. If the list is meant to stay compact, retain `Moral Responsibility` and remove the broader value. If the novel clearly treats ordinary duty/responsibility separately from moral responsibility, keeping both is defensible.

### Settings

The empty Settings field is the clearest missing classification. This is not an Earth-bound historical novel, so there is no need to invent a real-world location. However, the library already uses the following established fictional settings for related books:

- `Roshar` on `Dawnshard` and `Rhythm of War`
- `Urithiru` and `Shadesmar` on `Rhythm of War`
- `Aimia`, `The Reshi Sea`, and the `Sleepless Islands` on `Dawnshard`

`Roshar` should be the minimum setting for `Wind and Truth`. Add `Urithiru`, `Shinovar`, `Shadesmar`, or other named locations only when each is materially used in the novel and the library's existing spelling is retained. Do not add every place mentioned in passing.

**Recommendation:** add at least `Roshar`; manually confirm the more specific locations from the text before adding them.

### Historical Periods

A real-world period such as `20th Century` would be incorrect. The novel has fictional chronology, and the library already uses `Era of the Everstorm` for `Rhythm of War`. Because `Wind and Truth` follows the same ongoing historical phase, `Era of the Everstorm` is a strong candidate for this record if fictional periods are intended to be reusable across the series.

**Recommendation:** add `Era of the Everstorm` if the book's chronology policy includes named fictional eras. Otherwise, leaving Historical Periods empty is defensible; do not substitute `Modern` or `Contemporary`.

### Subjects

Many Subjects are well placed because they are concrete topics or recognized concepts:

`Armor`, `Cosmere`, `Diplomacy`, `Epic Warfare`, `Godhood`, `Gods`, `Immortality`, `Kingdoms`, `Magic`, `Magic Systems`, `Marriage`, `Military Leadership`, `Military Strategy`, `Mythology`, `Oaths`, `Political Alliances`, `Politics`, `Psychology`, `Religion`, `Social Class`, `Stormlight Archive`, `Theology`, `Warfare`, and `Weapons` can all be valid Subjects for this novel when they are materially represented.

The following values need cleanup or a conscious scope decision:

| Subject value | Recommendation | Reason |
| --- | --- | --- |
| `Depression` | Remove from Subjects; keep Theme `Depression` | Category duplication; the library's Sanderson precedent uses Depression as a Theme. |
| `Family` | Remove from Subjects; keep Theme `Family` | Abstract relationship/theme in this record. |
| `Freedom` | Remove from Subjects; keep Theme `Freedom` | Abstract value. |
| `Leadership` | Remove from Subjects unless used as a concrete academic/topic label | Keep `Military Leadership` as the more specific Subject when appropriate and retain Theme `Leadership`. |
| `Mental Health` | Keep as Subject; remove Theme `Mental Health` | Matches `The Way of Kings` and `Rhythm of War`. |
| `Oppression` | Remove from Subjects; keep Theme `Oppression` | Abstract social conflict. |
| `Parenthood` | Remove from Subjects; keep Theme `Parenthood` | Lived human experience/relationship. |
| `Slavery` | Keep as Subject; remove Theme `Slavery` | Concrete social institution/topic. |
| `Trauma` | Remove from Subjects; keep Theme `Trauma` | Lived psychological experience. |
| `War` | Keep or remove according to the single-category policy | If Subject `War` is retained, remove Theme `War`; otherwise keep Theme `War` and remove this Subject. |

#### Subject-level overlap

These are not automatically wrong, but the list is currently broad enough to create redundancy:

- `Magic` and `Magic Systems`: `Magic Systems` is the more specific established Subject. Keep both only if the general phenomenon and the mechanics of the system are separate cataloguing needs.
- `Gods`, `Godhood`, and `Immortality`: these are related but not synonyms. `Gods` names entities, `Godhood` names divine status, and `Immortality` names a condition. Keep only those that the novel treats as distinct subjects.
- `Epic Warfare` and `Warfare`: `Epic Warfare` is the more specific phrase and already appears on `Oathbringer`. If the generic Subject adds no information, remove `Warfare`; if the book contains military activity that is not all epic warfare, keeping the broader term can be justified.
- `Diplomacy`, `Political Alliances`, `Politics`, `Military Leadership`, and `Military Strategy` are related but distinct. They should remain only when each is materially present; do not collapse them merely because they share a political/military domain.
- `Religion`, `Theology`, and `Mythology` can coexist, but only if the book genuinely addresses institutions, theological ideas, and mythic traditions as separate subjects. Otherwise, keep the most specific and useful values.
- `Kingdoms` is a new generic plural label. It is acceptable if multiple kingdoms are a central topic, but use more specific named political entities where possible. The guidelines prefer singular nouns unless a plural is an established collective term.
- `Weapons` is also new as a generic Subject. It is grammatically understandable, but keep it only if weapons are a meaningful topic rather than incidental fantasy equipment. `Armor` is similarly valid when it is materially relevant.

#### Clear wording correction

Change `Prophecies` to `Prophecy` unless the value is deliberately intended to mean a collection of multiple prophecies. The library already uses `Prophecy` on `Oathbringer`, `Mistborn: Secret History`, `The Eye of the World`, `The Final Empire`, and other fantasy records. `Good Omens` uses `Prophecies`, so the database currently contains both forms; the singular is the stronger reusable default under the guideline to prefer singular nouns.

## Wording and vocabulary consistency

### Values already phrased consistently

These target values match established local forms:

- `Epic Fantasy`
- `High Fantasy`
- `Military Fantasy`
- `Novel`
- `Cosmere`
- `Epic Warfare`
- `Magic Systems`
- `Military Strategy`
- `Mythology`
- `Oaths`
- `Politics`
- `Religion`
- `Stormlight Archive`
- `Warfare`
- most of the common Theme vocabulary such as `Moral Responsibility`, `Self-Acceptance`, `Reconciliation`, and `Unity`

### Values requiring normalization or policy decisions

| Target value or relationship | Existing library wording | Assessment |
| --- | --- | --- |
| `Prophecies` | `Prophecy` | Likely normalization to singular `Prophecy`; keep plural only for a deliberately plural collection |
| `Fate` | `Destiny`; `Fate versus Free Will` | Related but not automatically interchangeable; decide whether the catalog distinguishes fate from destiny, and keep the target's separate `Fate` + `Free Will` if one-concept values are preferred |
| `Magic` + `Magic Systems` | Both occur elsewhere | Not a spelling problem; decide whether the broad and specific Subjects are both needed here |
| `Epic Warfare` + `Warfare` | Both occur elsewhere | Not a spelling problem; choose the most informative level rather than retaining both by default |
| `Kingdoms` | `Lost Kingdoms`, `Kingdom of Navarre`, `United Kingdom` | Generic plural is new; use only when multiple kingdoms are truly a central topic |
| `Weapons` | `Nautical Weapons`, `Nuclear Weapons`, `Weapons of Mass Destruction` | Generic plural is new; valid but should earn its place as a reusable Subject |
| `Armor` | `Armored Bears` and other compound values, but no existing generic `Armor` before this record | New generic Subject; retain if armor is materially important |
| `Military Leadership` | No exact existing value | New but semantically clear; keep if leadership in military command is a distinct topic from Theme `Leadership` |
| `Godhood` | No exact existing value | New but distinct from `Gods` and `Immortality`; keep only if divine status is a developed subject |

The target does not need to adopt every wording choice from `Rhythm of War`. In particular, `Rhythm of War` uses `Destiny`, while other books use `Fate`. This is a candidate vocabulary family, not proof that one of the two is wrong. By contrast, `Secondary World Fantasy` is now explicitly non-canonical and should be replaced by `High Fantasy` in Fantasy classifications.

## Existing classified books that may benefit from the target vocabulary

The list below is deliberately conservative. Generic Themes such as `Hope`, `Identity`, `Responsibility`, and `Sacrifice` occur on dozens of books; an exact match alone is not enough to recommend adding them. The recommendations below are based on close genre, series, or subject fit, and books with no classification were skipped.

### The Way of Kings - Brandon Sanderson

This is the strongest existing comparison point. It already uses many target Subjects: `Cosmere`, `Magic`, `Mental Health`, `Military Strategy`, `Mythology`, `Oaths`, `Religion`, `Slavery`, and `War`. Its Themes already cover much of the target's core vocabulary, including `Courage`, `Duty`, `Faith`, `Freedom`, `Friendship`, `Honor`, `Hope`, `Identity`, `Justice`, `Leadership`, `Love`, `Loyalty`, `Power`, `Responsibility`, `Sacrifice`, `Survival`, `Trauma`, and `Truth`.

Recommended review:

- Keep `High Fantasy` as the canonical Subgenre and do not add `Secondary World Fantasy`; the latter is a legacy synonym that should be removed from existing Fantasy records.
- Add `Stormlight Archive` to Subjects. `Oathbringer`, `Dawnshard`, and `Rhythm of War` already use that series label, while `The Way of Kings` currently lacks it.
- Add setting `Roshar`, using the same spelling as the other Stormlight records. The current empty Settings field is a more important omission than any generic Theme.
- Keep `War` and `Slavery` as Subjects if they are retained under the category policy; do not add duplicate Theme copies merely to mirror `Wind and Truth`.
- Do not add `Depression`, `Parenthood`, `Guilt`, or `Mercy` without confirming that each is a defining concern of this specific volume rather than a general series concept.

### Oathbringer - Brandon Sanderson

`Oathbringer` currently has the same four Subgenres as the target and already uses `Epic Warfare`, `Magic Systems`, `Military Strategy`, `Mythology`, `Oaths`, `Religion`, `Stormlight Archive`, and related Cosmere Subjects. Its Themes already include `Family`, `Trauma`, `Moral Responsibility`, `Reconciliation`, `Unity`, and most of the target's central moral vocabulary.

Recommended review:

- Add `Guilt` as a Theme if the classification is intended to capture Dalinar's defining psychological arc; this is a strong content-based candidate, not a mechanical carry-over.
- Remove `Secondary World Fantasy` and retain `High Fantasy` as the canonical Subgenre.
- Add settings `Roshar`, `Urithiru`, and `Shadesmar` where they are materially used. `Rhythm of War` already demonstrates those established setting values.
- Consider adding `Era of the Everstorm` as a Historical Period if the same fictional chronology policy is adopted for `Wind and Truth`.
- Do not add generic `War` or `Warfare` merely because the book contains battles; `Epic Warfare` and `Siege Warfare` already describe its military Subjects more precisely.

### Rhythm of War - Brandon Sanderson

This is the closest vocabulary match. It already has `Depression` as a Theme, `Mental Health` as a Subject, and `Parenthood`, `Moral Responsibility`, `Oppression`, `Purpose`, `Reconciliation`, `Self-Acceptance`, `Trauma`, and `Unity` as Themes. Its Subjects already include `Cosmere`, `Magic Systems`, `Military Strategy`, `Oaths`, `Stormlight Archive`, and `Warfare`.

Recommended review:

- Preserve the current category split when cleaning `Wind and Truth`: `Depression` belongs in Themes and `Mental Health` in Subjects. Do not copy the target's current cross-category duplicates into this book.
- Consider adding `Guilt`, `Slavery`, or `Violence` only after a manual reading-based check. Each could be defensible, but none should be added simply because it appears in the next volume's classification.
- Add settings `Roshar`, `Urithiru`, and `Shadesmar` if the blank Settings field is an omission rather than an intentional policy choice.
- Add or retain `Era of the Everstorm` as its Historical Period; it is already the library's established fictional period for this record.
- Keep `Destiny` unless a later vocabulary decision standardizes the Fate/Destiny family. Do not change it only to match `Wind and Truth`.

### Dawnshard - Brandon Sanderson

`Dawnshard` already shares `Cosmere`, `Stormlight Archive`, and `Magic Systems` with the target and, unlike the larger Stormlight novels, has populated Settings: `Aimia`, `Roshar`, `Sleepless Islands`, and `The Reshi Sea`. Its `Secondary World Fantasy` value should be treated as legacy and replaced by `High Fantasy` if that record is being normalized.

Recommended review:

- Use this record as a model for adding concrete Settings to `Wind and Truth`, while selecting only locations materially used in the target novel.
- No broad Theme propagation is recommended. `Dawnshard` has a different narrative focus, and its existing classification is already internally coherent.

### Mistborn: Secret History - Brandon Sanderson

This record already uses target Subjects `Cosmere`, `Gods`, `Immortality`, `Magic Systems`, `Mythology`, and `Prophecy`. It is direct evidence that the singular `Prophecy` is established and useful.

Recommended review:

- Keep `Prophecy` as the preferred target wording.
- Do not add `Godhood`, `Theology`, or `Stormlight Archive` automatically. `Gods`, `Immortality`, and Cosmere-related metaphysical Subjects already cover the relevant material; the new terms need book-specific justification.

### The Final Empire - Brandon Sanderson

This record already has `Oppression` as a Theme and `Slavery` as a Subject, alongside `Class Conflict`, `Economic Inequality`, and `Social Inequality` as more precise Subjects.

Recommended review:

- Do not replace those precise class-related Subjects with generic `Social Class`. The target's `Social Class` is valid, but `The Final Empire` already has more informative vocabulary for its social structure.
- Keep the existing Theme/Subject split as a useful precedent: abstract oppression in Themes, concrete slavery in Subjects.

### The Eye of the World and El ojo del mundo - Robert Jordan

Both classified editions already use `Fate` as a Theme, `Prophecy` as a Subject, `Magic Systems`, and `Lost Kingdoms`. They are useful comparison records for the target's fate/prophecy/kingdom vocabulary.

Recommended review:

- No immediate addition of target terms is necessary.
- Use singular `Prophecy` for the target unless a deliberate plural policy is adopted.
- Treat `Fate` and `Destiny` as a policy family rather than changing either record mechanically.

### A Storm of Swords and A Feast for Crows - George R.R. Martin

These already contain several target Subjects in the same general domain: `Diplomacy`, `Military Strategy`, `Political Alliances`, `Religion`, and `Warfare`, with `War` represented through more specific Subjects such as `Civil War`, `Medieval Warfare`, `Naval Warfare`, and `Siege Warfare`.

Recommended review:

- Do not add generic `War` or `Warfare` where the existing specific military Subjects are more informative.
- Use these records as support for retaining `Political Alliances`, `Diplomacy`, and `Military Strategy` as separate Subjects when each is materially present.

### Other exact matches

The target's generic Themes are already present on many classified books, but the strongest exact-match evidence includes:

- `Free Will`: `Rashomon e outros relatos`, `Good Omens`, `Legacy of Blood`, `22/11/63`, and `Flowers for Algernon`
- `Mental Health`: `The Way of Kings`, `Rhythm of War`, and several psychological or biographical works as a Subject
- `Parenthood`: `Rhythm of War`, `El clan`, `Las madres`, `Después del terremoto`, and `Los extraños`
- `Reconciliation`: `Rhythm of War`, `A orillas del mar`, and `Tres cantos fúnebres por Kosovo`
- `Self-Acceptance`: `Rhythm of War` and `La muerte de Vivek Oji`
- `Slavery`: `The Way of Kings`, `The Final Empire`, `Roma soy yo`, and `Maldita Roma` as a Subject
- `War`: `The Way of Kings`, `Lord of the Flies`, and `Tres cantos fúnebres por Kosovo` as a Subject

These matches show that the terms are reusable, but they do not by themselves prove that each book should receive them. Content review remains necessary, especially for broad Themes.

## Recommended final target state

A conservative cleaned version would look like this:

- Genre: `Fantasy`
- Subgenres: `Epic Fantasy; High Fantasy; Military Fantasy`
- Form: `Novel`
- Settings: at least `Roshar`; add only materially used named locations such as `Urithiru`, `Shinovar`, or `Shadesmar`
- Historical Periods: `Era of the Everstorm` if fictional eras are part of the catalog policy; otherwise leave empty rather than using a real-world period
- Audiences: `Adult; General Readers`

Themes should retain the valid emotional, ethical, psychological, and conflict vocabulary, including `Depression`, `Family`, `Freedom`, `Mental Health` only if the project explicitly wants it as a lived-experience Theme, `Oppression`, `Parenthood`, `Trauma`, and `Violence`. Under the stricter local precedent, remove Theme `Mental Health` and Theme `Slavery`, and choose one location for `War`.

Subjects should retain concrete world, political, military, religious, and Cosmere topics, including `Cosmere`, `Epic Warfare`, `Magic Systems`, `Military Strategy`, `Oaths`, `Religion`, `Social Class`, `Stormlight Archive`, and possibly `Theology`, `Godhood`, `Weapons`, and `Armor` after checking their importance. Remove the duplicated abstract values from Subjects, change `Prophecies` to `Prophecy`, and decide whether the broad values `Magic` and `Warfare` add information beyond their more specific counterparts.

## Priority order

1. Remove `Secondary World Fantasy` and retain `High Fantasy` as the canonical Subgenre.
2. Add `Roshar` to Settings and decide whether `Era of the Everstorm` belongs in Historical Periods.
3. Remove Theme/Subject duplicates using the recommended category split.
4. Change `Prophecies` to `Prophecy` unless the plural is intentional.
5. Reduce `Magic`/`Magic Systems` and `Epic Warfare`/`Warfare` only if the broader values add no independent filtering value.
6. Confirm the new generic Subjects `Armor`, `Godhood`, `Kingdoms`, `Military Leadership`, and `Weapons` against the novel before retaining them.
7. Review `The Way of Kings`, `Oathbringer`, and `Rhythm of War` using the focused recommendations above; do not propagate the whole target classification to the rest of the library.
8. Re-run the duplicate audit after manual changes so the catalog can distinguish resolved duplicates from intentional category distinctions.
