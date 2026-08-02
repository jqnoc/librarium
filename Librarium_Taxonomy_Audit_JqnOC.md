# Librarium Taxonomy Audit - JqnOC

Generated: 2026-08-02 (post-cleanup audit)

## Scope

This is a read-only audit of the current active JqnOC SQLite database at `%APPDATA%/Librarium/jqnoc.db`, generated after the requested cleanup of the 412 sparse legacy records. The database was not modified by this audit. It includes every book with at least one populated value in `genres`, `subgenres`, `forms`, `themes`, `settings`, `historical_periods`, `subjects`, or `audiences`.

- Included books: **33**
- Total books in the database: **719**
- Excluded books with no populated classification: **686**
- Historical sparse legacy records cleared before this audit: **412**
- Books with at least one non-theme classification field: **33**
- Books with an exact cross-category duplicate: **27**
- Exact cross-category duplicate category overlaps: **48**
- Books missing a Form: **3**
- Books missing a Setting: **1**
- Books with exactly one valid major Genre: **33**

## Population

| Field | Books with a value | Tokens | Unique values |
| --- | ---: | ---: | ---: |
| Genres | 33 | 33 | 5 |
| Subgenres | 33 | 199 | 117 |
| Forms | 30 | 32 | 6 |
| Themes | 33 | 600 | 353 |
| Settings | 32 | 123 | 99 |
| Historical Periods | 33 | 103 | 52 |
| Subjects | 33 | 570 | 494 |
| Audiences | 33 | 62 | 3 |

All 33 current classified books have a populated `themes` field. The current data is materially richer than the cleared legacy records, but it is not fully normalized: exact values are duplicated between categories, several Themes values describe concrete subjects, and wording variants prevent Similar Works from recognizing related books.

## Audit Rules

- Keep exactly one major Genre per book: Fantasy, Fiction, Science Fiction, Non-Fiction, or Biography.
- Move literary, academic, critical, and publishing classifications to Subgenres; do not leave them as major Genres.
- Move presentation modes to the controlled singular Form values: Essay, Novel, Novella, Short Story, Memoir, Letters, Dialogue, Interview, Diary, Treatise, or Speech.
- Keep ideas and lived experiences in Themes; move concrete people, places, disciplines, events, works, institutions, and other topics to Subjects.
- Keep geographical values in Settings and chronological values in Historical Periods.
- Remove duplicate values from Themes when the same value already has a clearer target field.
- Use one category for each concept unless duplication has a compelling semantic reason.
- Treat ambiguous values and inferred Forms as manual review items. No uncertain value is silently assigned to a new category.

## Global Findings

- **Genre:** all 33 books have exactly one valid major Genre; no Genre correction is required.
- **Form:** 30 books use only controlled Form values. `A Short History of Dublin`, `Scotland: From Prehistory to the Present`, and `Tiburón` have no Form and require manual confirmation, with `Essay` a plausible candidate for each but not an automatic assignment.
- **Audience:** all values are valid (`Adult` on 33 books, `General Readers` on 27, and `Young Adult` on 2).
- **Exact duplication:** 27 books repeat 48 concepts across categories, most often between Subgenres and Subjects or Settings and Subjects.
- **Category drift:** Themes contain concrete or domain values such as `Architecture`, `Books`, `Diamond Trafficking`, `Religion`, `War`, and `Fear and Cinema`; each requires either movement to Subjects or a deliberate split into independent concepts.
- **Historical-period precision:** `Modern` is often stored alongside a more precise decade or named period; `New Hollywood` is a film movement, not a Historical Period.
- **Similar Works fragmentation:** the same concept is represented by spelling, grammatical, or category-specific variants. The recommended canonical forms are listed below; these are correction candidates, not database writes.

The guide contains one controlled-vocabulary inconsistency: the `Reina del grito` example says `Essays`, while the Form rules require the singular controlled value `Essay`. The live database already uses `Essay`.

## Interchangeable Values Affecting Similar Works

Similar Works compares exact, case-insensitive tokens within the selected category. The following values represent the same concept or a close wording variant that related books will not match reliably:

| Category | Current values | Recommended canonical treatment | Affected records |
| --- | --- | --- | --- |
| Themes | `Anti-Semitism` / `Antisemitism` | Keep `Antisemitism` in American English | `El emblema del traidor`; `Mendel el de los libros` |
| Themes | `Tradition and Modernity` / `Tradition versus Modernity` | Keep `Tradition and Modernity` | `Scotland: From Prehistory to the Present`; `Rhythm of War` |
| Themes | `Class` / `Social Class` / `Class Differences` / `Class Struggle` | Use `Social Class` for the broad concept; retain narrower values only when intended | `Agua negra`; `A Little Trickerie`; `La dama de La Cartuja`; `La leyenda del ladrón` |
| Themes | `Fear` / `Fear and Cinema` / `Feminine Fears` | Split hybrid values and retain distinct concepts only when supported | `Reina del grito`; `Tiburón` |
| Subgenres | `Adventure` / `Adventure Fiction` | Keep `Adventure Fiction` | `Conquista de lo inútil` and other Adventure Fiction records |
| Subgenres | `Coming-of-Age` / `Coming-of-Age Fiction` | Choose one canonical spelling and reuse it | `A Little Trickerie`; `Flowers for Algernon`; `La leyenda del ladrón`; `Rhythm of War` |
| Subgenres | `Tragedy` / `Tragic Fiction` | Choose one classification label; do not fragment by grammar | `Flowers for Algernon`; `Agua negra` |
| Settings | `New York` / `New York City` | Keep `New York City` for the city; reserve `New York` for the state | `Flowers for Algernon`; `Hija de la venganza` |
| Subjects | `Cinema History` / `Film History` / `History of Cinema` | Keep `Film History` | `Conversaciones con Akira Kurosawa`; `Conquista de lo inútil`; `Tiburón` |
| Historical Periods | `Modern` / `Contemporary` / decade-specific values | Do not merge automatically; keep the most specific period supported by the book | Multiple records |
| Historical Periods | `16th Century` / `Early 16th Century` / `Late 16th Century` | These are hierarchical, not interchangeable; use the most specific supported value | `Américo Vespucio`; `Felipe II`; `La leyenda del ladrón` |

The similarity scan also produced false positives such as `World War I` / `World War II`, `Novel` / `Novella`, `Historical Fiction` / `Historical Non-Fiction`, and `Psychological Fiction` / `Psychological Non-Fiction`. These must **not** be merged.

## Book-by-Book Audit

Each current entry preserves the exact populated database values first, followed by required corrections. `Manual review` means the stored data is insufficient to make a defensible automatic decision; it is not a database write.

### Current Classified Books

#### 1. A Little Trickerie - Rosanna Pike

- Database ID: `5ac24f58-59e5-4a23-916d-9784a633d6a6`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `British Literature; Coming-of-Age; Historical Fiction; Picaresque; Satirical Fiction`
  - Forms: `Novel`
  - Themes: `Belonging; Courage; Credulity; Deception; Depression; Faith; Freedom; Grief; Hope; Identity; Justice; Marginalization; Oppression; Perseverance; Poverty; Resilience; Self-Discovery; Social Class; Survival; Womanhood`
  - Settings: `Herefordshire; Leominster; Rural England`
  - Historical Periods: `16th Century; Early Tudor Period`
  - Subjects: `Beggars; Con Artistry; English Countryside; Holy Maid of Leominster; Medieval Christianity; Outcasts and Marginalized Communities; Pilgrimage; Priory Life; Religious Imposture; Religious Institutions; Social Mobility; Tudor Society; Vagrancy; Women in Tudor England`
  - Audiences: `Adult; General Readers`
- Required corrections: Review `Social Class` against the shared class-theme vocabulary; no controlled-field violation is currently evident.
- Verdict: **Mostly compliant; vocabulary normalization review recommended**

#### 2. A Short History of Dublin - Pat Boran

- Database ID: `ebcd262b-0ea8-4d94-9d7a-7c97031531f2`
- Current values:
  - Genres: `Non-Fiction`
  - Subgenres: `Accessible History; History; Local History; Popular History; Religion; Short-form History; Urban History`
  - Forms: *(empty)*
  - Themes: `Affectionate Tone; Architecture; Capital City; City Biography; City Portrait; Culture; Disease; Eras of Glory; Georgian Beauty; Hinterland and Landscape; Housing; Irish Identity; Irish Wit and Culture; National Identity; Population growth; Poverty; Society; Traffic and urban problems; Tragedy and resilience; Urban Development`
  - Settings: `Dublin; Ireland; Leinster`
  - Historical Periods: `Contemporary; Early Modern; Georgian Era; Medieval; Modern; Prehistory; Viking Age`
  - Subjects: `British Colonialism; Capital Cities; Colonial Ireland; Colonialism; Cultural History; Dublin History; Geography; Georgian Architecture; Irish History; Irish Literature; Irish Studies; Medieval Dublin; Politics; Trade; Urban History; Viking Settlement`
  - Audiences: `Adult; General Readers`
- Required corrections: Manually confirm the Form, with `Essay` a plausible candidate. Review concrete Theme values such as `Architecture`, `Housing`, and `Urban Development`; reduce the duplicate `Urban History` in Subgenres and Subjects.
- Verdict: **Non-compliant until Form and category overlaps are reviewed**

#### 3. Agua negra - Joyce Carol Oates

- Database ID: `66423d78-cb4d-412e-93c8-a5d6142e30c5`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `Feminist Fiction; Literary Fiction; Political Fiction; Psychological Fiction; Tragic Fiction`
  - Forms: `Novella`
  - Themes: `Class; Death; Disillusionment; Fear; Feminist Critique; Gender; Hero Worship; Identity; Loneliness; Male Privilege; Manipulation; Memory; Moral Ambiguity; Mortality; Patriarchy; Power; Power Imbalance; Sexual Politics; Silence; Social Class; Survival; Trauma; Vulnerability`
  - Settings: `Chappaquiddick Island; Martha's Vineyard; Massachusetts; United States`
  - Historical Periods: `1960s; Modern`
  - Subjects: `American Literature; American Politics; Car Accidents; Chappaquiddick Incident; Drowning; Feminism; Gender Relations; Non-Linear Narrative; Political Corruption; Political Power; Politics; Psychological Trauma; Stream of Consciousness; Ted Kennedy`
  - Audiences: `Adult`
- Required corrections: Review the coexistence of `Class` and `Social Class`; prefer one canonical broad concept unless the distinction is intentional. Review broad `Modern` beside the specific `1960s`.
- Verdict: **Mostly compliant; minor normalization review required**

#### 4. Américo Vespucio - Stefan Zweig

- Database ID: `e5016574-3b35-4847-91b7-04833efa59e9`
- Current values:
  - Genres: `Biography`
  - Subgenres: `Historical Biography; Historical Essay; History; Intellectual History; Popular History`
  - Forms: `Essay`
  - Themes: `Chance; Discovery; Exploration; Fame; Historical Error; Historical Interpretation; Historical Memory; Identity; Irony of History; Justice; Legacy; Merit; Reputation; Truth`
  - Settings: `Atlantic Ocean; Europe; Florence; Lisbon; Seville; South America`
  - Historical Periods: `Age of Discovery; Early 16th Century; Late 15th Century; Renaissance`
  - Subjects: `Age of Discovery; Amerigo Vespucci; Atlantic Voyages; Austrian Literature; Cartography; Christopher Columbus; Colonial History; Cosmographiae Introductio; European History; European Imperialism; German-Language Literature; History; History of Exploration; History of Geography; Humanism; Italian Explorers; Martin Waldseemüller; Naming of America; New World; South American History; Vespucci Question`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce the exact duplicates `Age of Discovery` across Historical Periods and Subjects and `History` across Subgenres and Subjects; retain each concept in its clearest category.
- Verdict: **Non-compliant until duplicate placements are reduced**

#### 5. Conquista de lo inútil - Werner Herzog

- Database ID: `497239f6-8fb3-4bb7-9375-03d713f45d3c`
- Current values:
  - Genres: `Non-Fiction`
  - Subgenres: `Adventure; Film History; Film Studies; German-Language Literature; Literary Non-Fiction; Memoir; Travel Writing`
  - Forms: `Diary; Essay`
  - Themes: `Ambition; Art and Sacrifice; Artistic Creation; Creativity; Exploration; Failure; Human Will; Isolation; Madness; Man versus Nature; Nature; Nature as Hostile Force; Obsession; Perseverance; Philosophical Reflection; Reality and Illusion; Risk; Survival; The Impossible`
  - Settings: `Amazon Rainforest; Loreto Region; Peru; Ucayali River`
  - Historical Periods: `1980s; Contemporary`
  - Subjects: `Amazon Rainforest; Auteur Cinema; Behind-the-Scenes Filmmaking; Cinema; Creative Process; Enrico Caruso; Extreme Filmmaking; Film History; Film Production; Film Studies; Filmmaking; Fitzcarraldo; German Cinema; German New Cinema; Indigenous Peoples of Peru; Klaus Kinski; Opera; Peru; Production Diaries; Werner Herzog`
  - Audiences: `Adult; General Readers`
- Required corrections: Normalize Subgenre `Adventure` to `Adventure Fiction` if that is the chosen canonical value. Reduce duplicate `Film History`, `Film Studies`, `Amazon Rainforest`, and `Peru` placements; confirm whether `Memoir` is intentional alongside Forms `Diary; Essay`.
- Verdict: **Non-compliant until duplicate and variant values are reviewed**

#### 6. Conversaciones con Akira Kurosawa - Akira Kurosawa

- Database ID: `2ee8b013-0102-4917-84b4-f6fedc168c94`
- Current values:
  - Genres: `Biography`
  - Subgenres: `Cinema History; Film Criticism; Film Studies; Japanese Cinema`
  - Forms: `Interview`
  - Themes: `Art and Silence; Artistic Creation; Artistic Integrity; Artistic Vision; Collaboration; Creativity; Human Nature; Inspiration; Memory; Perfectionism; Silence; Storytelling; Tradition and Modernity`
  - Settings: `Japan; Tokyo`
  - Historical Periods: `1960s; 20th Century; Postwar Japan`
  - Subjects: `20th-Century Japanese Culture; Adaptation; Akira Kurosawa; Auteur Theory; Cinema; Cinema History; Dersu Uzala; Donald Richie; Film Criticism; Film Direction; Film History; Film Production; Film Studies; Filmmaking; Gabriel García Márquez; George Lucas; Hollywood; Humanism; Japanese Cinema; Japanese Culture; Japanese Film Industry; Kagemusha; Kenji Mizoguchi; Nagisa Oshima; Ran; Rashomon; Screenwriting; Seven Samurai; Steven Spielberg; Yasujirō Ozu`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce the exact duplicates `Cinema History`, `Film Criticism`, `Film Studies`, and `Japanese Cinema` across Subgenres and Subjects; retain academic classifications in Subgenres and concrete topics in Subjects.
- Verdict: **Non-compliant until duplicate placements are reduced**

#### 7. Cuando los inviernos eran inviernos - Bernd Brunner

- Database ID: `ce6099f0-77e2-42b9-9feb-e200cea0f0b5`
- Current values:
  - Genres: `Non-Fiction`
  - Subgenres: `Cultural History; Environmental History; History; Nature Writing; Popular History; Popular Science; Science`
  - Forms: `Essay`
  - Themes: `Community; Cultural Memory; Curiosity; Human Adaptation; Imagination; Landscape; Nature; Nostalgia; Resilience; Seasonal Change; Solidarity; Survival; Tradition`
  - Settings: `Alps; Arctic; Europe; North America`
  - Historical Periods: `Contemporary; Early Modern; Ice Age; Little Ice Age; Medieval; Modern`
  - Subjects: `Alpine History; Animal Adaptation; Arctic Exploration; Art History; Climate Change; Climate History; Cryosphere; Cultural History; Environmental History; Folklore; Freezing; History of Science; Ice; Ice Skating; Ice Trade; Literature; Meteorology; Plant Adaptation; Seasons; Snow; Snowflakes; White Christmas; Wilson Bentley; Winter; Winter Mythology; Winter Sports; World Ice Theory; Year Without a Summer`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce duplicate `Cultural History` and `Environmental History` placements between Subgenres and Subjects; review concrete weather and science values for Subject placement.
- Verdict: **Non-compliant until duplicate placements are reduced**

#### 8. Descripción de China - Matteo Ricci

- Database ID: `59ff6882-c024-4b16-b969-069cdfce81dc`
- Current values:
  - Genres: `Non-Fiction`
  - Subgenres: `Asian Studies; Cultural History; Ethnography; Historical Narrative; Historical Non-Fiction; History; Religion; Religious History; Science; Sinology; Travel Writing`
  - Forms: `Essay`
  - Themes: `Civilization; Cross-Cultural Dialogue; Cultural Accommodation; Cultural Understanding; Curiosity; Diplomacy; Education; Evangelization; Exploration; Identity; Inculturation; Knowledge; Tolerance`
  - Settings: `Beijing; China; Macau; Ming China; Nanjing`
  - Historical Periods: `Early 17th Century; Early Modern; Late 16th Century; Late Ming Dynasty`
  - Subjects: `Asian Studies; Buddhism; Cartography; Catholic Church; Catholic Missions; Chinese Culture; Chinese Government; Chinese History; Chinese Philosophy; Christianity in China; Confucianism; Counter-Reformation; Cultural Exchange; Ethnography; Europe's Image of China; Geography; History of China; Imperial Court; Jesuits; Mandarins; Ming Dynasty; Primary Historical Sources; Sinology; Society of Jesus; Taoism; Western Science in China; World Map in Chinese`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce duplicate `Asian Studies`, `Ethnography`, and `Sinology` placements between Subgenres and Subjects. Review `Ming China` as a Setting against its historical-period meaning.
- Verdict: **Non-compliant until duplicate placements are reduced**

#### 9. El círculo de los días - Ken Follett

- Database ID: `18f616de-f369-4441-b2f3-58125da061fb`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `Adventure Fiction; British Literature; Ensemble Cast; Epic Fiction; Historical Fiction; Prehistoric Fiction`
  - Forms: `Novel`
  - Themes: `Ambition; Belonging; Community; Conflict; Cooperation; Division; Faith; Family; Freedom; Hope; Identity; Innovation; Justice; Leadership; Legacy; Love; Patriarchy; Perseverance; Power; Revenge; Sacrifice; Social Hierarchy; Spirituality; Survival; Tradition; Vision`
  - Settings: `Britain; Salisbury Plain; Stonehenge`
  - Historical Periods: `c. 2500 BC; Late Neolithic`
  - Subjects: `Agriculture; Ancient Technology; Astronomy; Craftsmanship; Drought; Engineering; Flint Mining; Gender Roles; Megalithic Architecture; Megaliths; Monument Construction; Neolithic Britain; Religion; Ritual and Ceremony; Social Organization; Solar Alignments; Stonehenge; Trade; Tribal Society; Violence; Women's Subjugation`
  - Audiences: `Adult; General Readers`
- Required corrections: Review the exact `Stonehenge` duplicate between Setting and Subject and retain each occurrence only if the two meanings are deliberately distinct.
- Verdict: **Minor duplicate-placement correction required**

#### 10. El dique de carena de Gamazo - Andrés Ortega Piris; Víctor Manuel Moreno Sáiz

- Database ID: `49cf5d18-a0d2-46fd-b824-0962f17cdb2e`
- Current values:
  - Genres: `Non-Fiction`
  - Subgenres: `Academic Non-Fiction; Architectural History; History; Industrial History; Local History; Maritime History`
  - Forms: `Essay`
  - Themes: `Cultural Heritage; Economic Development; Industrialization; Infrastructure; Maritime Engineering; Restoration; Technological Innovation; Urban Development`
  - Settings: `Bay of Santander; Cantabria; Santander; Spain`
  - Historical Periods: `Contemporary; Early 20th Century; Industrial Revolution; Late 19th Century; Modern; Restoration Spain`
  - Subjects: `Bien de Interés Cultural; Cantabrian History; Civil Engineering; Dique de Gamazo; Dry Docks; Engineering History; Fishing Industry; Heritage Conservation; Hydraulic Engineering; Industrial Archaeology; Industrial Heritage; Junta de Obras del Puerto; Maritime History; Maritime Infrastructure; Merchant Shipping; Naval Engineering; Port Engineering; Port Infrastructure; Port of Santander; Restoration Architecture; Ship Repair; Shipbuilding; Spanish Industrialization; Spanish Naval History`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce the exact `Maritime History` duplicate between Subgenres and Subjects; retain the classification in the category that best describes its use.
- Verdict: **Minor duplicate-placement correction required**

#### 11. El emblema del traidor - Juan Gómez-Jurado

- Database ID: `24224bef-81d5-4689-84b9-312e0b7f2a5c`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `Adventure Fiction; Coming-of-Age; Espionage Fiction; Historical Fiction; Historical Romance; Historical Thriller; Mystery; Political Fiction; Thriller`
  - Forms: `Novel`
  - Themes: `Anti-Semitism; Betrayal; Courage; Family Rivalry; Family Secrets; Forbidden Love; Identity; Justice; Love; Loyalty; Orphan Protagonist; Persecution; Political Intrigue; Pursuit; Revenge; Sacrifice; Search for Truth; Survival; Totalitarianism; Truth and Its Consequences`
  - Settings: `Berlin; Europe; Germany; Munich; Strait of Gibraltar`
  - Historical Periods: `1940s; Interwar Period; Modern; Nazi Germany; World War II`
  - Subjects: `Espionage; Freemasonry; German History; Holocaust; Intelligence Services; Nazism; Political History; Resistance Movements; Secret Societies; Spanish Literature; World War II`
  - Audiences: `Adult; General Readers`
- Required corrections: Normalize Theme `Anti-Semitism` to the chosen canonical spelling `Antisemitism`; review the exact `World War II` duplicate between Historical Periods and Subjects.
- Verdict: **Non-compliant until spelling and duplicate placement are reviewed**

#### 12. El extranjero - Albert Camus

- Database ID: `899ef7ba-5a27-448f-9b7f-09ae22aef19c`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `Absurdist Fiction; Existential Fiction; Literary Fiction; Philosophical Fiction; Psychological Fiction`
  - Forms: `Novel`
  - Themes: `Absurdity; Alienation; Atheism; Authenticity; Death; Emotional Detachment; Freedom; Grief; Guilt; Identity; Indifference; Isolation; Justice; Meaninglessness; Moral Ambiguity; Mortality; Outsider; Responsibility; Social Conformity; The Human Condition`
  - Settings: `Algeria; Algiers; French Algeria; Mediterranean`
  - Historical Periods: `1940s; Interwar Period; Modern`
  - Subjects: `Absurdism; Albert Camus; Capital Punishment; Colonialism; Criminal Justice; Existentialism; First-Person Narration; French Algeria; French Colonialism; French Literature; Murder; Philosophy; The Arab`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce the exact `French Algeria` duplicate between Setting and Subject. Replace ambiguous Subject `The Arab` with a precise label after manual confirmation; review broad `Modern` beside the 1940s and Interwar Period.
- Verdict: **Non-compliant until ambiguous and duplicate values are reviewed**

#### 13. El mito de Sísifo - Albert Camus

- Database ID: `964a7ba5-181d-45ce-a310-1789c7b174f2`
- Current values:
  - Genres: `Non-Fiction`
  - Subgenres: `Existential Philosophy; Philosophical Essay; Philosophy`
  - Forms: `Essay`
  - Themes: `Alienation; Atheism; Authenticity; Death; Despair; Freedom; Hope; Individualism; Meaning of Life; Meaninglessness; Mortality; Passion; Reason versus Irrationality; Revolt; The Absurd; The Human Condition`
  - Settings: *(empty)*
  - Historical Periods: `20th Century`
  - Subjects: `20th-Century Philosophy; Absurdism; Absurdist Philosophy; Consciousness; Ethics; Existentialism; French Literature; French Philosophy; Friedrich Nietzsche; Fyodor Dostoevsky; Greek Mythology; Literature and Philosophy; Philosophy; Sisyphus; Suicide; Søren Kierkegaard`
  - Audiences: `Adult`
- Required corrections: No Setting is required if no geographical subject is intended. Review the exact `Philosophy` duplicate between Subgenres and Subjects.
- Verdict: **Mostly compliant; duplicate placement review required**

#### 14. El palacio del agua - Laura Portas

- Database ID: `af5ddbea-54c5-403f-aa2f-d7137be73b77`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `Costumbrista Fiction; Historical Fiction; Historical Mystery; Historical Romance; Romance; Thriller`
  - Forms: `Novel`
  - Themes: `Ambition; Aristocracy; Betrayal; Corruption; Diamond Trafficking; First Love; Forbidden Love; Identity; Lies; Love; Love Triangle; Loyalty; Origins; Secrets; Serving Class; Social Class; Water Symbolism`
  - Settings: `Balneario de Mondariz; Galicia; Mondariz; Spain`
  - Historical Periods: `1920s; Interwar Period; Modern`
  - Subjects: `Crime; Galician History; Galician Landscape; Social History; Spa Culture; Spanish History; Thermal Baths; Women's Lives`
  - Audiences: `Adult; General Readers`
- Required corrections: Review concrete Theme `Diamond Trafficking` for Subject placement and apply one consistent policy for broad `Modern` alongside the 1920s and Interwar Period.
- Verdict: **Mostly compliant; Theme and period precision review required**

#### 15. Felipe II - Manuel Fernández Álvarez

- Database ID: `7a9b3f7a-9658-4fb9-a7c6-afd3ee20556c`
- Current values:
  - Genres: `Biography`
  - Subgenres: `Historical Biography; History; Political History; Religion; Royal Biography`
  - Forms: `Essay`
  - Themes: `Arts Patronage; Centralization of Power; Court Life; Cultural Transformation; Diplomacy; Duty; Empire; Faith; Kingship; Leadership; Monarchy; Political Strategy; Power; Regional Tensions; Religion; Religious Reform; State Finances; War`
  - Settings: `Americas; El Escorial; Europe; Madrid; Portugal; Spain; Spanish Netherlands`
  - Historical Periods: `16th Century; Early Modern; Renaissance; Spanish Golden Age`
  - Subjects: `Absolute Monarchy; Annexation of Portugal; Atlantic Empire; Battle of Lepanto; Catholic Church; Charles V, Holy Roman Emperor; Colonization of the Americas; Counter-Reformation; Early Modern History; El Escorial; European Diplomacy; European History; Habsburg Dynasty; Mary I of England; Morisco Rebellion; Philip II of Spain; Prince Don Carlos; Spanish Armada; Spanish Empire; Spanish Historiography; Spanish History`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce duplicate `Religion` between Subgenres and Themes and `El Escorial` between Setting and Subject; retain each concept once unless the meanings are deliberately distinct.
- Verdict: **Non-compliant until duplicate placements are reduced**

#### 16. Flowers for Algernon - Daniel Keyes

- Database ID: `dfb985cd-53b8-4c40-bc17-f5fa5612b4f5`
- Current values:
  - Genres: `Science Fiction`
  - Subgenres: `Coming-of-Age; Epistolary Novel; Literary Science Fiction; Philosophical Fiction; Psychological Fiction; Social Commentary; Speculative Fiction; Tragedy`
  - Forms: `Novel`
  - Themes: `Acceptance; Alienation; Cognitive Decline; Discrimination; Empathy; Free Will; Friendship; Happiness; Hope; Hubris; Human Dignity; Human Experimentation; Identity; Intelligence; Isolation; Knowledge; Loneliness; Loss of Innocence; Love; Memory; Mortality; Psychological Transformation; Romantic Relationships; Self-Awareness; The Cost of Progress`
  - Settings: `New York; New York City; United States`
  - Historical Periods: `1960s; Contemporary; Mid-20th Century`
  - Subjects: `American Literature; Cognitive Enhancement; Consciousness; Ethics; Experimental Medicine; Intellectual Disability; Medical Ethics; Mouse Symbolism; Neuroscience; Psychology; Science Fiction; Scientific Ethics`
  - Audiences: `Adult; Young Adult`
- Required corrections: Normalize `New York` and `New York City` to the intended geographic level. Remove or justify Subject `Science Fiction`, which duplicates the Genre; apply one consistent policy to `1960s`, `Mid-20th Century`, and `Contemporary`.
- Verdict: **Non-compliant until duplicate and period values are reviewed**

#### 17. Hija de la venganza - Michael McDowell

- Database ID: `7e147f87-070c-45a4-b53b-f14a7d8229d3`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `Gothic Fiction; Historical Fiction; Historical Thriller; Horror; Penny Dreadful; Psychological Horror; Thriller`
  - Forms: `Novel`
  - Themes: `Cat and Mouse; Family; Female Power; Female Protagonist; Female Villain; Good versus Evil; Gore; Greed; Identity; Inheritance; Justice; Poverty; Psychic Powers; Revenge; Serial Murder; Social Class; Survival`
  - Settings: `New York; New York City; United States`
  - Historical Periods: `1860s; Gilded Age; Modern; Victorian Era`
  - Subjects: `American Literature; Clairvoyance; Family Violence; Gothic Fiction; Murder; New York City; Psychic Phenomena; Serial Killers; Victorian America; Violence`
  - Audiences: `Adult`
- Required corrections: Normalize `New York` and `New York City`; reduce duplicate `Gothic Fiction` between Subgenres and Subjects and `New York City` between Setting and Subject; review broad `Modern` beside the specific periods.
- Verdict: **Non-compliant until duplicate and period values are reviewed**

#### 18. La dama de La Cartuja - Inma Aguilera

- Database ID: `84e7939b-7a1f-40f4-ba39-eaf5a0eddd64`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `Costumbrista Fiction; Family Saga; Historical Fiction; Historical Mystery; Historical Romance; Romance`
  - Forms: `Novel`
  - Themes: `Ambition; Aristocracy; Artisanship; Class Differences; Domestic Abuse; Envy; Family Mystery; Family Secrets; Female Artisans; Female Resilience; Heritage; Identity; Impossible Love; Love; Multi-Generational Saga; Prejudice; Social Class; Three Generations of Women; Women's Work`
  - Settings: `Andalusia; Seville; Spain; Triana`
  - Historical Periods: `19th Century; Belle Époque; Early 20th Century; Modern`
  - Subjects: `Andalusian Culture; Ceramics; Decorative Arts; La Cartuja Porcelain Factory; Pickman Family; Pottery; Sevillian Society; Spanish History; Women's Lives`
  - Audiences: `Adult; General Readers`
- Required corrections: Review broad `Modern` beside the 19th Century, Belle Époque, and Early 20th Century. Review `Female Artisans`, `Three Generations of Women`, and `Women's Work` for the Theme/Subject boundary.
- Verdict: **Mostly compliant; period and Theme/Subject review required**

#### 19. La leyenda del ladrón - Juan Gómez-Jurado

- Database ID: `c88e8286-cdea-4fe0-bf59-3ce595ad06e9`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `Adventure Fiction; Coming-of-Age; Historical Adventure; Historical Fiction; Historical Mystery; Historical Thriller; Picaresque`
  - Forms: `Novel`
  - Themes: `Ambition; Betrayal; Class Struggle; Coming of Age; Courage; Freedom; Friendship; Identity; Inequality; Injustice; Justice; Love; Loyalty; Orphanhood; Passion; Poverty; Redemption; Revenge; Social Class; Survival`
  - Settings: `Andalusia; Seville; Spain`
  - Historical Periods: `16th Century; Early Modern; Renaissance; Spanish Golden Age`
  - Subjects: `Cervantes; Crime; Don Quixote; Galley Slaves; Maritime History; Organized Crime; Philip II of Spain; Plague; Seville; Social History; Spanish Empire; Spanish Golden Age; Spanish History; Spanish Literature; William Shakespeare`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce exact `Seville` duplication between Setting and Subject and `Spanish Golden Age` duplication between Historical Periods and Subjects.
- Verdict: **Non-compliant until duplicate placements are reduced**

#### 20. La mano izquierda de la oscuridad - Ursula K. Le Guin

- Database ID: `57e452b6-973f-4b9d-a253-540b9935600a`
- Current values:
  - Genres: `Science Fiction`
  - Subgenres: `Feminist Science Fiction; Literary Fiction; Philosophical Fiction; Political Fiction; Social Science Fiction; Speculative Fiction`
  - Forms: `Novel`
  - Themes: `Androgyny; Betrayal; Cultural Observation; Duality; Epic Journey; Exile; Friendship; Gender; Identity; Isolation; Loyalty; Nationalism; Non-Binary Identity; Otherness; Outsider Perspective; Political Intrigue; Sexuality; Social Structure`
  - Settings: `Alien World; Fictional Planet; Gethen; Winter`
  - Historical Periods: `Future`
  - Subjects: `Alien Culture; Anthropology; Ethnographic Narrative; First Contact; Gender Studies; Hainish Cycle; Kemmer; Politics; Sociology; Taoism; Telepathy; World-Building`
  - Audiences: `Adult`
- Required corrections: No exact cross-category duplicate or controlled-field violation was found. Apply shared vocabulary normalization only when a canonical list is adopted.
- Verdict: **Mostly compliant**

#### 21. Las aventuras de Simbad el marino - René Khawam

- Database ID: `123569bf-37b4-4fd7-b389-8ba7c7b00c03`
- Current values:
  - Genres: `Fantasy`
  - Subgenres: `Adventure Fiction; Classic Literature; Folklore; Maritime Adventure; Mythological Fiction`
  - Forms: `Novel`
  - Themes: `Courage; Curiosity; Exploration; Fate; Fortune; Greed; Hospitality; Justice; Perseverance; Spirituality; Storytelling; Survival; Wealth; Wisdom; Wonder`
  - Settings: `Abbasid Caliphate; Arabian Sea; Baghdad; China; Exotic Lands; Indian Ocean; Madagascar; Persian Gulf`
  - Historical Periods: `9th Century; Islamic Golden Age; Medieval`
  - Subjects: `Abbasid Caliphate; Arabic Literature; Fantastic Beasts; Folklore; Frame Narrative; Hero's Journey; Maritime History; Medieval Islamic World; Medieval Literature; Merchants and Trade; Middle Eastern Literature; Mythical Creatures; Mythology; Navigation; Oral Tradition; Persian Origins; Seven Voyages; Sinbad the Sailor`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce duplicate `Folklore` between Subgenres and Subjects and `Abbasid Caliphate` between Setting and Subject. Replace or remove imprecise Setting `Exotic Lands` after manual confirmation.
- Verdict: **Non-compliant until duplicate and ambiguous Setting values are reviewed**

#### 22. Mendel el de los libros - Stefan Zweig

- Database ID: `bff84ca7-bcb2-4225-b344-a403e6893b9b`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `Historical Fiction; Literary Fiction; Psychological Fiction; Short Fiction`
  - Forms: `Novella`
  - Themes: `Antisemitism; Bibliophilia; Books; Bureaucracy; Civilization; Cultural Memory; Displacement; Fragility of Culture; Friendship; Genius; Human Dignity; Identity; Injustice; Isolation; Knowledge; Loss; Love of Literature; Memory; Nostalgia; Obsession; Persecution; Reading; War`
  - Settings: `Austria; Austria-Hungary; Café Gluck; Vienna`
  - Historical Periods: `Belle Époque; Early 20th Century; Modern; World War I`
  - Subjects: `Austrian Literature; Austrian Society; Bibliography; Bookselling; Censorship; Coffeehouse Culture; Frame Narrative; German-Language Literature; Intellectual Life; Jewish Culture; Libraries; Viennese Culture; Wartime Internment; World War I`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce exact `World War I` duplication between Historical Periods and Subjects. Review concrete Theme `Books` for Subject placement and broad `Modern` beside the more precise periods.
- Verdict: **Non-compliant until category and period values are reviewed**

#### 23. Nada se opone a la noche - Delphine de Vigan

- Database ID: `e7900e77-c713-4889-a80d-8eaa6759215a`
- Current values:
  - Genres: `Biography`
  - Subgenres: `Family Biography; Family Drama; Memoir; Psychological Non-Fiction`
  - Forms: `Memoir`
  - Themes: `Appearance and Reality; Bipolar Disorder; Child Sexual Abuse; Childhood; Childhood Trauma; Courage; Depression; Family; Family Dysfunction; Family Secrets; Grief; Identity; Incest; Loss; Love; Maternal Love; Memory; Mental Illness; Mother-Daughter Relationship; Motherhood; Mourning; Repression; Resilience; Silence; Trauma; Vulnerability`
  - Settings: `France; Paris`
  - Historical Periods: `1960s; 1970s; Contemporary; Late 20th Century`
  - Subjects: `Biography; Delphine de Vigan; Family History; French Literature; Lucile Poirier; Mental Health; Oral History; Photography; Psychiatry; Psychology; Suicide; Women's Lives; Writing`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce duplicate `Biography` between Genre and Subjects and `Memoir` between Subgenres and Form; retain the Form value and keep Subgenre `Memoir` only if it is intentionally used as a literary classification.
- Verdict: **Non-compliant until duplicate placements are reduced**

#### 24. Reina del grito - Desirée de Fez

- Database ID: `61f11350-ea94-4e29-bf3b-c8ee39ce92a5`
- Current values:
  - Genres: `Non-Fiction`
  - Subgenres: `Autobiographical Essay; Cultural Criticism; Feminist Non-Fiction; Film Criticism; Genre Journalism; Spanish Film Criticism`
  - Forms: `Essay; Memoir`
  - Themes: `Aging; Anxiety; Body Image; Catharsis; Desire; Fear; Fear and Fascination; Feminine Fears; Feminism; Identity; Memory; Motherhood; Patriarchy; Self-Exposure; Sexuality; Social Expectations; Social Pressure; Trauma; Womanhood`
  - Settings: `Spain`
  - Historical Periods: `Contemporary`
  - Subjects: `Adolescence; Adult Life; Cinema; Female Gaze; Film Criticism; Film Studies; Gender Studies; Horror Cinema; Horror Fandom; Popular Culture; Psychology; Violence Against Women; Women in Male-Dominated Spaces; Women's Studies`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce duplicate `Film Criticism` between Subgenres and Subjects. Split hybrid Theme `Fear and Fascination` only if both independent concepts are supported; confirm the combined Form `Essay; Memoir` from the work's actual presentation.
- Verdict: **Non-compliant until duplicate and hybrid values are reviewed**

#### 25. Rendezvous With Rama - Arthur C. Clarke

- Database ID: `0750cbc4-1672-43d6-b771-d65317bee5c4`
- Current values:
  - Genres: `Science Fiction`
  - Subgenres: `Big Dumb Object; First Contact; Hard Science Fiction; Mystery; Space Exploration`
  - Forms: `Novel`
  - Themes: `Cold Rationalism; Cooperation; Curiosity; Discovery; Exploration; Humanity; Humanity's Insignificance; Isolation; Non-Communication; Scientific Inquiry; Sense of Wonder; Survival; The Unknown; Wonder`
  - Settings: `Rama; Solar System; Space`
  - Historical Periods: `Future; Near Future`
  - Subjects: `Alien Spacecraft; Alien Technology; Artificial Worlds; Astronomy; Biots; British Literature; Classic Literature; Cylindrical Worlds; Engineering; Extraterrestrial Intelligence; Interstellar Objects; Physics; Space Exploration; Spacecraft; Zero Gravity`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce exact `Space Exploration` duplication between Subgenres and Subjects.
- Verdict: **Minor duplicate-placement correction required**

#### 26. Rhythm of War - Brandon Sanderson

- Database ID: `e373d4d0-035d-4926-85b8-af68113ce21f`
- Current values:
  - Genres: `Fantasy`
  - Subgenres: `Adventure Fiction; American Literature; Coming-of-Age Fiction; Epic Fantasy; Heroic Fantasy; Military Fantasy; Science Fantasy; Secondary World Fantasy`
  - Forms: `Novel`
  - Themes: `Addiction; Ambition; Betrayal; Compassion; Cooperation; Courage; Depression; Destiny; Discovery; Duty; Duty versus Desire; Faith; Family; Forgiveness; Freedom; Friendship; Grief; Healing; Honor; Hope; Identity; Innovation; Isolation; Justice; Knowledge; Leadership; Love; Loyalty; Moral Responsibility; Oppression; Parenthood; Perseverance; Power; Purpose; Reconciliation; Recovery; Redemption; Resilience; Responsibility; Sacrifice; Self-Acceptance; Survival; Tradition versus Modernity; Trauma; Trust; Unity`
  - Settings: `Roshar; Shadesmar; Urithiru`
  - Historical Periods: `Era of the Everstorm`
  - Subjects: `Adolin Kholin; Alethi; Ancient Civilizations; Bridge Four; Cosmere; Cultivation; Dalinar Kholin; Dissociative Identity Disorder; Engineering; Fabrial Technology; Fused; Honor; Investiture; Kaladin Stormblessed; Knights Radiant; Magic Systems; Mental Health; Military Strategy; Navani Kholin; Oaths; Odium; Parshendi; PTSD; Raboniel; Scientific Research; Shallan Davar; Shards; Singers; Spren; Stormlight Archive; Surgebinding; Urithiru; Venli; Warfare`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce exact `Honor` duplication between Themes and Subjects and `Urithiru` between Setting and Subject. Normalize Theme `Tradition versus Modernity` to the chosen canonical wording `Tradition and Modernity`.
- Verdict: **Non-compliant until duplicate and variant values are reviewed**

#### 27. Scotland: From Prehistory to the Present - Fiona Watson

- Database ID: `e1f6e24e-6aa4-4ec8-a4cb-e8a8bd4cb2b9`
- Current values:
  - Genres: `Non-Fiction`
  - Subgenres: `Cultural History; History; National History; Popular History; Religion; Scottish Studies`
  - Forms: *(empty)*
  - Themes: `Conflict; Cultural Identity; Heritage; Independence; Landscape and Identity; Nation Building; National Identity; Political Change; Power; Social Change; Tradition and Modernity; Union`
  - Settings: `British Isles; Great Britain; Scotland`
  - Historical Periods: `Ancient; Contemporary; Early Modern; Medieval; Modern; Prehistory`
  - Subjects: `20th-Century Scotland; Act of Union 1707; Angles; British History; Celtic Culture; Devolution; Highland Clearances; House of Stuart; Ice Age Britain; Industrial Revolution; Jacobitism; Macbeth; Medieval Scotland; Picts; Prehistoric Britain; Robert the Bruce; Romans in Britain; Scotland; Scots; Scottish Culture; Scottish Enlightenment; Scottish History; Scottish Parliament; Scottish Reformation; United Kingdom; Viking Age; Wars of Scottish Independence; William Wallace`
  - Audiences: `Adult; General Readers`
- Required corrections: Manually confirm the Form, with `Essay` a plausible candidate. Reduce duplicate `Scotland` between Setting and Subject and keep the canonical Theme wording `Tradition and Modernity`.
- Verdict: **Non-compliant until Form and duplicate placement are reviewed**

#### 28. Sintoísmo - Sokyo Ono

- Database ID: `ecb839fa-e7c3-4de9-b7bd-722572950e48`
- Current values:
  - Genres: `Non-Fiction`
  - Subgenres: `Comparative Religion; Introductory Guide; Religion`
  - Forms: `Essay`
  - Themes: `Community; Festivals; Nature; Purity; Ritual; Sacred Places; Spirituality; Tradition`
  - Settings: `Japan`
  - Historical Periods: `Contemporary`
  - Subjects: `Japanese Culture; Japanese Religion; Mythology; Religious Studies; Shinto`
  - Audiences: `Adult; General Readers`
- Required corrections: Confirm whether controlled Form `Essay` accurately describes the work alongside Subgenre `Introductory Guide`; no exact cross-category duplicate was found.
- Verdict: **Mostly compliant; Form semantics require confirmation**

#### 29. Soy un gato - Natsume Sōseki

- Database ID: `c21e0035-6674-4800-95b5-6e8ce57ef982`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `Classic Literature; Comedy of Manners; Humor; Japanese Literature; Literary Fiction; Modernist Literature; Novel-in-Episodes; Philosophical Fiction; Satirical Fiction`
  - Forms: `Novel`
  - Themes: `Alienation; Class; Conformity; Friendship; Human Nature; Identity; Individualism; Intellectualism; Irony; Observation; Social Satire; Tradition and Modernity; Vanity`
  - Settings: `Japan; Tokyo`
  - Historical Periods: `Early 20th Century; Meiji Era`
  - Subjects: `Academic Life; Animal Narrators; Anthropomorphism; Cats; Cats in Literature; Cultural Criticism; Humor; Intellectual Life; Japanese Culture; Japanese Identity; Japanese Literature; Japanese Society; Meiji Japan; Middle Class; Modernization; Philosophy; Social Criticism; Westernization`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce duplicate `Humor` and `Japanese Literature` placements between Subgenres and Subjects; retain literary classification in Subgenres and concrete cultural/literary topics in Subjects.
- Verdict: **Non-compliant until duplicate placements are reduced**

#### 30. Taras Bulba - Nikolai Gogol

- Database ID: `da24f7fb-6d66-48be-a662-b00e7dc12d83`
- Current values:
  - Genres: `Fiction`
  - Subgenres: `Adventure Fiction; Epic Literature; Historical Adventure; Historical Fiction; Literary Fiction; Romantic Nationalism`
  - Forms: `Novella`
  - Themes: `Betrayal; Brotherhood; Courage; Death; Duty; Faith; Family; Father-Son Relationships; Freedom; Glory; Heroism; Honor; Identity; Love; Loyalty; National Identity; Revenge; Sacrifice; Tradition; Tragic Ending; War`
  - Settings: `Dnieper River; Polish-Lithuanian Commonwealth; Ukraine; Ukrainian Steppe; Zaporizhian Sich`
  - Historical Periods: `16th Century; Early Modern; Polish-Lithuanian Commonwealth`
  - Subjects: `Cossacks; Eastern European History; Folk Literature; Frontier Society; Military History; Oral Tradition; Orthodox Christianity; Polish History; Polish-Lithuanian Commonwealth; Russian Literature; Ukrainian History; Ukrainian Literature; Zaporizhian Cossacks`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce the three-way duplicate `Polish-Lithuanian Commonwealth` across Setting, Historical Periods, and Subjects by deciding which occurrence answers Where, When, or What.
- Verdict: **Non-compliant until three-way duplicate placement is reduced**

#### 31. The Granite Kingdom - Tim Hannigan

- Database ID: `756c6eff-2c26-4dcd-b115-dbe6528dcae4`
- Current values:
  - Genres: `Non-Fiction`
  - Subgenres: `Cultural History; Folklore; History; Local History; Nature Writing; Travel Writing`
  - Forms: `Memoir`
  - Themes: `Belonging; Celtic Identity; Childhood Memories; Coastal Life; Home; Landscape; Myth and Reality; Overtourism; Pirates; Regional Identity; Rural Life; Sense of Place; Smugglers; Tourism; Walking`
  - Settings: `Bodmin Moor; Cornwall; England; Penwith Peninsula; Tamar Valley`
  - Historical Periods: `Contemporary`
  - Subjects: `Archaeology; British History; Copper Mining; Cornish History; Cornish Language; Cornwall in Art and Literature; Cultural History; Fishing Communities; Geography; Geology; King Arthur; Literary History; Tin Mining`
  - Audiences: `Adult; General Readers`
- Required corrections: Reduce exact `Cultural History` duplication between Subgenres and Subjects; review `Tourism`, `Walking`, `Coastal Life`, and `Landscape` for concrete Subject versus lived-experience Theme placement.
- Verdict: **Non-compliant until duplicate and boundary values are reviewed**

#### 32. The Talisman - Stephen  King; Peter Straub

- Database ID: `85b77dbe-d454-44a4-b171-1c265988a958`
- Current values:
  - Genres: `Fantasy`
  - Subgenres: `Adventure Fiction; Coming-of-Age; Dark Fantasy; Horror; Portal Fantasy; Supernatural Fiction`
  - Forms: `Novel`
  - Themes: `Coming of Age; Courage; Destiny; Dying Parent; Family; Friendship; Good versus Evil; Grief; Hope; Identity; Loss; Love; Loyalty; Mother-Son Relationship; Parallel Worlds; Power; Quest; Redemption; Sacrifice; Survival`
  - Settings: `Midwestern United States; New Hampshire; New York City; Pacific Coast; The Territories; United States; Western United States`
  - Historical Periods: `1980s; Contemporary`
  - Subjects: `American Literature; Dark Fantasy; Hero's Journey; Hotels; Magic; Magic Objects; Medievalism; Monsters; Multiverse; Parallel Universes; Quest Narrative; Railroads; Religious Fanaticism; Shape-Shifting; Small-Town America; Supernatural Creatures; Werewolves`
  - Audiences: `Adult; Young Adult`
- Required corrections: Reduce exact `Dark Fantasy` duplication between Subgenres and Subjects. Normalize `Coming-of-Age` and `Coming of Age` according to the chosen category vocabulary.
- Verdict: **Non-compliant until duplicate and variant values are reviewed**

#### 33. Tiburón - Quim Casas; Juan Manuel Corral; Juan Andrés Pedrero Santos

- Database ID: `ff0912f1-b6bc-490f-8871-5e40a86c68ad`
- Current values:
  - Genres: `Non-Fiction`
  - Subgenres: `Cinema History; Film Criticism; Film History; Film Studies; Popular Culture; Spanish Film Criticism`
  - Forms: *(empty)*
  - Themes: `Artistic Vision; Collaboration; Cultural Impact; Fear; Fear and Cinema; Innovation; Nature versus Humanity; Storytelling; Suspense`
  - Settings: `Amity Island; Martha's Vineyard; Massachusetts; United States`
  - Historical Periods: `1970s; Contemporary; New Hollywood`
  - Subjects: `Adaptation; American Cinema; Behind-the-Scenes Filmmaking; Blockbuster Cinema; Cinema; Film Criticism; Film History; Film Production; Filmmaking; History of Cinema; Hollywood History; Horror Cinema; Jaws; John Williams; Literary Adaptation; New Hollywood; Novel-to-Film Adaptation; Peter Benchley; Popular Culture; Richard Dreyfuss; Robert Shaw; Roy Scheider; Shark Films; Steven Spielberg; Thriller Films; Universal Pictures`
  - Audiences: `Adult; General Readers`
- Required corrections: Manually confirm the Form, with `Essay` a plausible candidate. Reduce duplicate `Film Criticism`, `Film History`, and `Popular Culture` placements; move `New Hollywood` out of Historical Periods if it is being used as a film movement; split hybrid Theme `Fear and Cinema` only if both concepts are supported.
- Verdict: **Non-compliant until Form, duplicate, period, and hybrid values are reviewed**

### Historical Pre-Clear Audit (Superseded)

The entries below preserve the earlier 412-book sparse-record audit for provenance. Those records were subsequently cleared from all eight classification columns at the user's request and are not part of the current population or findings above.

#### 1. 22 largos - Caroline Wahl

- Database ID: `7272d603-378d-4b73-8de1-e34653e59ae2`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 2. 22/11/63 - Stephen  King

- Database ID: `d1314b0b-3480-4c11-8f65-c9b85a2a99b7`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 3. A Crown of Swords - Robert Jordan

- Database ID: `8e88b842-a8ef-447b-ae1d-2b949fc3b8ca`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 4. A Dance with Dragons - George R.R. Martin

- Database ID: `767a5ddc-9e42-4304-81db-0fef5802718b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 5. A Darkling Plain - Philip Reeve

- Database ID: `cff2ef38-3dac-41de-8660-917e32121fa7`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 6. A Day of Fallen Night - Samantha Shannon

- Database ID: `713da935-aa55-4b5d-a539-680f6596d38f`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 7. A Feast for Crows - George R.R. Martin

- Database ID: `a43bee85-5cc7-42e7-a25f-0beb46e184a0`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 8. A Game of Thrones - George R.R. Martin

- Database ID: `1562c989-7631-49d6-8b65-7b2451950e6c`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 9. A Memory of Light - Robert Jordan; Brandon Sanderson

- Database ID: `1823410d-21f3-410d-a67b-a65cb93a940d`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 10. A orillas del mar - Abdulrazak Gurnah

- Database ID: `293b1559-1136-493b-9298-a0e34a8acefb`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 11. A Passage to India - E.M. Forster

- Database ID: `879444d2-22b8-44df-b554-00c6e31bd76c`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 12. A Storm of Swords - George R.R. Martin

- Database ID: `ac76804e-d77e-4beb-8c48-76f96697540e`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 13. A Tale of Two Cities - Charles Dickens

- Database ID: `05d080df-ffb5-492d-83cf-aa1294dab9c3`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 14. A Web of Air - Philip Reeve

- Database ID: `50232a49-a995-4f4c-a6b7-47f421ce4109`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 15. After Dark - Haruki Murakami

- Database ID: `def40e41-9fc1-4127-9a64-760d3adf1069`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 16. Agents of Chaos I: Hero's Trial - James Luceno

- Database ID: `f333f189-d680-401c-98cc-03d9861a6d84`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 17. Agents of Chaos II: Jedi Eclipse - James Lucerno

- Database ID: `519e2bdb-8095-4461-b488-ba0d108b5eeb`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 18. Agnes Grey - Anne Brontë

- Database ID: `bfc71d12-3fd0-41a8-8022-e14de7c058fa`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 19. Al faro - Virginia Woolf

- Database ID: `25283a80-3790-405b-a808-0bdf9cceff0b`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 20. Al Polo Norte en avión - Roald Amundsen

- Database ID: `d6d6a738-f20b-45b5-be46-55beafe3e402`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 21. Alfonso II el Casto - José M. Andrade Cernadas

- Database ID: `ddc047a8-d9e3-420e-979d-9c039c08c43d`
- Current populated fields:
  - Themes: Biography
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Biography` -> Genres: `Biography`
  - Remove every moved major genre label from Themes after populating Genres

#### 22. Amber and Ashes - Margaret Weis

- Database ID: `daa5ef5d-e05a-4b96-a40a-539be24a6197`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 23. Amber and Blood - Margaret Weis

- Database ID: `1d719849-99dd-40fc-99d7-5acfb3da7a12`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 24. Amber and Iron - Margaret Weis

- Database ID: `c5ca90f1-a5f5-4008-93a8-3fc8d4158457`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 25. An Almond for a Parrot - Wray Delaney

- Database ID: `9aede5a4-075c-4eb2-b771-1ee5b30f8e14`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 26. Araña - Jon Bilbao

- Database ID: `63e272f4-0e74-465b-9d17-25a7d5a7299c`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 27. Ardiente secreto - Stefan Zweig

- Database ID: `a317e5b1-3a43-4274-9782-bfa591b8b297`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 28. Arenas movedizas - Jun'ichirō Tanizaki

- Database ID: `8c039269-1570-4436-b05a-d7a2d195d87e`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 29. Asesinato en Mesopotamia - Agatha Christie

- Database ID: `d3d7bfb0-cf31-48a6-9876-660c7366f10a`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 30. Bailén - Benito Pérez Galdós

- Database ID: `a55207d5-0c1e-42bc-87bc-1fa865d81ee9`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 31. Balance Point - Kathy Tyers

- Database ID: `4d4875d2-2d4f-4a07-97d4-cf247b16a206`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 32. Basilisco - Jon Bilbao

- Database ID: `a5f6fbe4-cd9c-4be2-bffa-d2e3faae6fa7`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 33. Belleza y verdad - Ian Stewart

- Database ID: `fc8e8e42-9119-49a6-9fe5-56fd7d0e140a`
- Current populated fields:
  - Themes: Science
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Science`
  - Move Themes: `Science` -> Subgenres: `Science`

#### 34. Betrayal - Aaron Allston

- Database ID: `9ed24498-c0c6-4e47-b33d-e601839bf53f`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 35. Brevísima relación de la destruición de las Indias - Bartolomé de las Casas

- Database ID: `74383e3d-bac9-4077-8d79-6c296918118a`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 36. Brothers in Arms - Margaret Weis; Don Perrin

- Database ID: `ca1798c3-7ae7-4698-aa0d-9f808305cc11`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 37. Buenas noches, dulces sueños - Jiří Kratochvil

- Database ID: `df46fc3d-0ba1-45dd-96f1-c2a3a4439fa4`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 38. Cada noche a las nueve - Julian Gloag

- Database ID: `5b9c3dce-97e4-476a-a240-4ee4ecd539f2`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 39. Cambios - Mo Yan

- Database ID: `282838e4-6444-458c-b4b2-8607808c478e`
- Current populated fields:
  - Themes: Biography
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Biography` -> Genres: `Biography`
  - Remove every moved major genre label from Themes after populating Genres

#### 40. Campesinos y señores - Theodor Kallifatides

- Database ID: `bba4a7a7-295d-4c37-9688-f292a574e350`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 41. Carta de una desconocida - Stefan Zweig

- Database ID: `56712bb9-a36e-44ca-994d-120dc4a56324`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 42. Chapterhouse: Dune - Frank Herbert

- Database ID: `98c56229-68f0-4d68-bc0b-b399d5c34144`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 43. Children of Dune - Frank Herbert

- Database ID: `2b8a78f1-6b5b-4708-bfe8-356a7ed60443`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 44. Chroniques de Jérusalem - Guy Delisle

- Database ID: `768cd12e-45bd-47f6-8ea0-476423abc4fa`
- Current populated fields:
  - Themes: Graphic Novel; Memoir; Travel Narrative; Non-Fiction; Bande Dessinée; Jerusalem; Israeli-Palestinian conflict; Middle East; Expatriate life; Stranger in a strange land; Outsider perspective; Daily life; Checkpoints and borders; West Bank; Doctors Without Borders (MSF); Stay-at-home parent; Judaism; Islam; Christianity; Three religions; Holy sites; Political tension; Occupation; Humor and irony; Vignette structure; Autobiographical; Quebec author; French-language comics; Award-winning (Angoulême); Contemporary history; Cultural observation; Family abroad; Secular viewpoint; Candid reportage; Urban portrait
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Graphic Novel` -> Subgenres: `Graphic Novel`
  - Move Themes: `Memoir` -> Subgenres: `Memoir`
  - Move Themes: `Non-Fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 45. Cien años de soledad - Gabriel García Márquez

- Database ID: `10e0689e-8c2c-49d8-8e9c-13debc6a76e0`
- Current populated fields:
  - Themes: Magical Realism
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Magical Realism`
  - Move Themes: `Magical Realism` -> Subgenres: `Magical Realism`

#### 46. Cisnes salvajes - Jung Chang

- Database ID: `bab2586d-17c8-45f5-9fb7-3b02616ae9a5`
- Current populated fields:
  - Themes: Biography
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Biography` -> Genres: `Biography`
  - Remove every moved major genre label from Themes after populating Genres

#### 47. Comercios de Tokio - Mateusz Urbanowicz

- Database ID: `2993c551-fb2e-40e8-a5fc-10d7e92cd15a`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 48. Compostela y su ángel - Gonzalo Torrente Ballester

- Database ID: `5f6b3c2f-9461-4e9d-939e-cb96ffb2e8f0`
- Current populated fields:
  - Themes: Travel Literature
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Travel Literature`
  - Move Themes: `Travel Literature` -> Subgenres: `Travel Writing`

#### 49. Contos vellos para rapaces novos - Xosé Neira Vilas

- Database ID: `06ece908-793f-4aff-ad8b-773653e0dba1`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 50. Crepúsculo de los ídolos - Friedrich Nietzsche

- Database ID: `846c767d-d4c6-4cd2-ac17-3d68ad9286e8`
- Current populated fields:
  - Themes: Philosophy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Philosophy`
  - Move Themes: `Philosophy` -> Subgenres: `Philosophy`

#### 51. Crosscurrent - Paul S. Kemp

- Database ID: `d9f6726f-228a-45d1-a841-096549d14ee0`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 52. Crossroads of Twilight - Robert Jordan

- Database ID: `4e159b72-00df-4944-9e08-060f100bdffd`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 53. Cruces - Alex Landragin

- Database ID: `2fb45a1f-23b9-4fb6-acdc-32ac2a87f993`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 54. Crucible - Troy Denning

- Database ID: `d396f487-1c2b-47eb-bb5d-3515fa61e392`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 55. Crónica del pájaro que da cuerda al mundo - Haruki Murakami

- Database ID: `95342650-482f-4d5c-be0d-e873ebe7c7e8`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 56. Cujo - Stephen  King

- Database ID: `bfd05915-f842-4a08-baad-745230965073`
- Current populated fields:
  - Themes: Horror
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Horror`
  - Move Themes: `Horror` -> Subgenres: `Horror`

#### 57. Cultura japonesa - Federico Lanzaco Salafranca

- Database ID: `c5f478e2-0288-46e3-9b9c-5532acf7864c`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 58. Dark Force Rising - Timothy Zahn

- Database ID: `468b0dd3-9f50-4f55-871b-ac00728c4282`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 59. Dark Journey - Elaine Cunningham

- Database ID: `91017196-0538-48ca-8799-6f82c14a2f88`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 60. Dark Tide I: Onslaught - Michael A. Stackpole

- Database ID: `4714e4aa-0953-42d6-8fed-caa948c37090`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 61. Dark Tide II: Ruin - Michael A. Stackpole

- Database ID: `d62a9551-7e72-4b72-92f3-a88efb610107`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 62. Dawnshard - Brandon Sanderson

- Database ID: `9c0f2eb8-a847-40cb-8b08-33a0111abb0c`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 63. De cómo un rey perdió Francia - Maurice Druon

- Database ID: `3fc00f3f-6691-4cb1-b956-51900df3a89d`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 64. De ratones y hombres - John Steinbeck

- Database ID: `d4891106-05ef-4a91-a864-d85de08f44a4`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 65. Después del terremoto - Haruki Murakami

- Database ID: `d1397d9b-6312-408b-b5df-666f0525c9cf`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 66. Destiny's Way - Walter Jon Williams

- Database ID: `a861d7f6-ad89-4f62-90e5-7c14dfa05717`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 67. Dios creó los números - Stephen Hawking

- Database ID: `39ed03ba-192f-4466-ad31-ec5e28612f13`
- Current populated fields:
  - Themes: Science
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Science`
  - Move Themes: `Science` -> Subgenres: `Science`

#### 68. Do Androids Dream of Electric Sheep? - Philip K. Dick

- Database ID: `c7581cda-b6f9-4743-9bff-caf0614b8ee2`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 69. Don Álvaro o la fuerza del sino - Duque de Rivas

- Database ID: `44f29386-21ea-4e19-9564-0db22e65ad29`
- Current populated fields:
  - Themes: Play
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre: `Fiction` from `Play`
  - Review Form: `Play` because Play is not in the current controlled Form vocabulary
- Manual review:
  - Choose an existing controlled Form or explicitly extend the controlled vocabulary for Play

#### 70. Dracula - Bram Stoker

- Database ID: `62736934-79f0-4c16-bbfa-b5fab0e96bb0`
- Current populated fields:
  - Themes: Horror
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Horror`
  - Move Themes: `Horror` -> Subgenres: `Horror`

#### 71. Dragon Wing - Margaret Weis; Tracy Hickman

- Database ID: `6269b77a-d933-426c-923b-13cd8170b704`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 72. Dragons of a Fallen Sun - Margaret Weis; Tracy Hickman

- Database ID: `8073a99f-5312-47a9-854f-d40a4d67d14b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 73. Dragons of a Lost Star - Margaret Weis; Tracy Hickman

- Database ID: `2639a0c2-743b-4b3a-b99a-20298b8a5148`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 74. Dragons of a Vanished Moon - Margaret Weis; Tracy Hickman

- Database ID: `ef5b6983-3fc3-4774-aff3-19089f95976c`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 75. Dragons of Autumn Twilight - Margaret Weis; Tracy Hickman

- Database ID: `cb303fbf-984d-4064-884a-7a61cf9c7513`
- Current populated fields:
  - Themes: Fantasy; High Fantasy; Epic Fantasy; Sword and Sorcery; Adventure; Quest narrative; Good vs. evil; Dragons; Magic and sorcery; Ensemble cast; Fellowship / found family; War and conflict; Political intrigue; Religious themes; False gods; Knights and warriors; Elves; Dwarves; Kender (halflings); Mages and wizards; Clerics and healing magic; Prophecy; World-building; Medieval setting; Friendship and loyalty; Betrayal; Sacrifice; Redemption; Reluctant hero; Classic fantasy tropes; Tabletop RPG origins (Dungeons & Dragons); Shared world; Series opener; 1980s fantasy; Co-authored; Maps and appendices; Krynn setting; Dragonlance universe; Comic relief; Dark lord antagonist
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Move Themes: `Epic Fantasy` -> Subgenres: `Epic Fantasy`
  - Move Themes: `Adventure` -> Subgenres: `Adventure Fiction`
  - Move Themes: `Quest narrative` -> Subjects: `Quest narrative`
  - Move Themes: `Ensemble cast` -> Subgenres: `Ensemble cast`
  - Move Themes: `World-building` -> Subjects: `World-building`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 76. Dragons of Deceit - Margaret Weis; Tracy Hickman

- Database ID: `291abdc7-5269-420e-8e69-8e89eeb240f3`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 77. Dragons of Eternity - Margaret Weis; Tracy Hickman

- Database ID: `f2b928fc-a967-4979-b836-a4c1dad23a43`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 78. Dragons of Fate - Margaret Weis; Tracy Hickman

- Database ID: `db059ca6-dd84-4dbc-9168-e14af1ce969a`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 79. Dragons of Spring Dawning - Margaret Weis; Tracy Hickman

- Database ID: `5364dd8e-8cc1-4c47-866f-e353706f9d24`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 80. Dragons of Summer Flame - Margaret Weis; Tracy Hickman

- Database ID: `40b900e6-d790-4e21-a70d-bb78652cb8dd`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 81. Dragons of the Dwarven Depths - Margaret Weis; Tracy Hickman

- Database ID: `02aee2b1-6c1a-45a9-98da-cc960966fb6b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 82. Dragons of the Highlord Skies - Margaret Weis; Tracy Hickman

- Database ID: `68a2b6f7-644b-4beb-bac2-d2a62e447a7f`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 83. Dragons of the Hourglass Mage - Margaret Weis; Tracy Hickman

- Database ID: `a61112cd-ea24-478b-869f-ff1e279042d8`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 84. Dragons of Winter Night - Margaret Weis; Tracy Hickman

- Database ID: `0b5da02c-f435-411c-87b8-42fe6ebb84aa`
- Current populated fields:
  - Themes: Fantasy; High Fantasy; Epic Fantasy; Sword and Sorcery; Adventure; Quest narrative; Good vs. evil; Dragons; Magic and sorcery; Ensemble cast; Fellowship / found family; War and conflict; Political intrigue; Religious themes; Divine magic restored; Knights and warriors; Elves; Dwarves; Kender (halflings); Mages and wizardry; Clerics and healing magic; Prophecy; World-building; Medieval setting; Friendship and loyalty; Betrayal; Sacrifice; Redemption; Tragic romance; Character death; Loss and grief; Series continuation; Tabletop RPG origins (Dungeons & Dragons); Shared world; 1980s fantasy; Co-authored; Krynn setting; Dragonlance universe; Dark lord antagonist; Escalating stakes
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Move Themes: `Epic Fantasy` -> Subgenres: `Epic Fantasy`
  - Move Themes: `Adventure` -> Subgenres: `Adventure Fiction`
  - Move Themes: `Quest narrative` -> Subjects: `Quest narrative`
  - Move Themes: `Ensemble cast` -> Subgenres: `Ensemble cast`
  - Move Themes: `World-building` -> Subjects: `World-building`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 85. Dubliners - James Joyce

- Database ID: `73ba2728-a378-4404-b586-fc393e084338`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 86. Dune - Frank Herbert

- Database ID: `e1ec0639-9076-4ee8-aa55-55079687ce00`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 87. Dune Messiah - Frank Herbert

- Database ID: `a5d8d15b-edbd-4dd7-b5a4-1ea2efca044b`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 88. Ecce homo - Friedrich Nietzsche

- Database ID: `2342996c-4752-415a-a6fd-7ab2abb40946`
- Current populated fields:
  - Themes: Philosophy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Philosophy`
  - Move Themes: `Philosophy` -> Subgenres: `Philosophy`

#### 89. Edge of Victory I: Conquest - Greg Keyes

- Database ID: `b6e83c3d-1177-452d-942f-baa0a4e4309b`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 90. Edge of Victory II: Rebirth - Greg Keyes

- Database ID: `9bbf2ba9-e01c-448c-9a40-4d51d3db7c6d`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 91. Edgedancer - Brandon Sanderson

- Database ID: `f1635391-c71f-40b5-a003-5abe835e0239`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 92. El 19 de marzo y el 2 de mayo - Benito Pérez Galdós

- Database ID: `c22e9ae5-ecb0-41a6-a8c6-2dbc88fe2159`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 93. El affaire Arnolfini - Jean-Philippe Postel

- Database ID: `2d261678-6b1a-4492-ac16-98d8db959139`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 94. El albatros negro - María Oruña

- Database ID: `f0f571d9-9336-49c6-b35f-d7b74057a3cb`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 95. El asesinato de Rogelio Ackroyd - Agatha Christie

- Database ID: `a55f10fa-8182-42d8-a9c3-4099ba1a6df4`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 96. El año negro - Ismail Kadare

- Database ID: `5d270cda-dcb9-45e6-bed0-649161b1e660`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 97. El barco faro y otros relatos - Siegfried Lenz

- Database ID: `3331edad-2567-4821-8b39-3e6f11ac2f4a`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 98. El bosque de los cuatro vientos - María Oruña

- Database ID: `776fbeb7-5ce0-4da9-8505-5fef078b139a`
- Current populated fields:
  - Themes: Historical Mystery; Historical Fiction; Thriller; Spanish Literature; Adventure; 19th-century Galicia; Dual timeline; Monastery setting; Santo Estevo de Ribas de Sil; Galician landscape; Medieval relics; Lost artifacts; Female protagonist; Women in history; Feminist themes; Medicine and botany; Social conventions; Fall of the Ancien Régime; The Catholic Church; Benedictine monks; Art recovery; Anthropology; Contemporary investigation; Murder mystery; Parallel storylines; Small-town secrets; Legend and reality; Ribeira Sacra; Spanish history; Real historical artifacts; Standalone novel; Nature as setting; Period atmosphere; 19th-century Spain; Galician culture
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Mystery`
  - Move Themes: `Historical Mystery` -> Subgenres: `Historical Mystery`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`
  - Move Themes: `Thriller` -> Subgenres: `Thriller`
  - Move Themes: `Spanish Literature` -> Subjects: `Spanish Literature`
  - Move Themes: `Adventure` -> Subgenres: `Adventure Fiction`
  - Move Themes: `19th-century Galicia` -> Historical Periods: `19th-century Galicia`
  - Move Themes: `Galician landscape` -> Subjects: `Galician landscape`
  - Move Themes: `Anthropology` -> Subjects: `Anthropology`
  - Move Themes: `Spanish history` -> Subjects: `Spanish history`
  - Move Themes: `19th-century Spain` -> Historical Periods: `19th-century Spain`
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 99. El camino a la realidad - Roger Penrose

- Database ID: `207eadf4-8df0-4d43-be41-d0af5109353c`
- Current populated fields:
  - Themes: Science
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Science`
  - Move Themes: `Science` -> Subgenres: `Science`

#### 100. El camino del fuego - María Oruña

- Database ID: `d96116d4-e08d-4aed-998f-3dd5cf295a8d`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 101. El caso de los anónimos - Agatha Christie

- Database ID: `579bcd22-a32a-4cd5-8ca6-e170ceaf8590`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 102. El castillo - Franz Kafka

- Database ID: `654110d5-0c61-40c8-bc2f-55466eac0417`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 103. El clan - Carmen Mola

- Database ID: `fd43a968-e59d-42b7-af28-3a1e6d730035`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 104. El cuenco de laca - Fernando Schwartz

- Database ID: `09026105-4146-42e4-aa86-2b7a62954ef2`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 105. El dique - Michael McDowell

- Database ID: `4853bcdf-ee15-4b23-a82d-5f90ddd55a9b`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 106. El fin del «Homo sovieticus» - Svetlana Aleksiévich

- Database ID: `5ce37404-7e1b-4d4b-9550-5e20c3ccfaa2`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 107. El guardián invisible - Dolores Redondo

- Database ID: `8227dd8f-b312-4a29-81b8-8099e4f9d7e9`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 108. El hospital de la transfiguración - Stanisław Lem

- Database ID: `5b026db0-fc29-42d9-a6df-3481a2d7cdb8`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 109. El invierno del mundo - Ken Follett

- Database ID: `4d41532a-6538-4620-accc-d18ee481950c`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 110. El Levante - Mircea Cărtărescu

- Database ID: `a24a5a05-d6da-411d-b881-66d58f4616b0`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 111. El maestro Mateo - Francisco López Iglesias

- Database ID: `0b516181-1414-4e55-97ea-0eaecc8f915e`
- Current populated fields:
  - Themes: Biography
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Biography` -> Genres: `Biography`
  - Remove every moved major genre label from Themes after populating Genres

#### 112. El misterio de la cripta embrujada - Eduardo Mendoza

- Database ID: `fac4b46b-d9cd-4d1d-9cd7-2badef98bd8d`
- Current populated fields:
  - Themes: Comedy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Comedy`
  - Move Themes: `Comedy` -> Subgenres: `Comedy`

#### 113. El misterio de Sans-Souci - Agatha Christie

- Database ID: `b00477af-0a4c-44ad-97e9-2acee7ba325c`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 114. El misterio del cuarto amarillo - Gaston Leroux

- Database ID: `39d32e1c-eb85-4042-b11b-64f4e7f2a363`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 115. El misterioso caso de Styles - Agatha Christie

- Database ID: `65db99c9-4e55-4573-978c-d3cfaa2e7ffe`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 116. El nudo Windsor - S.J. Bennett

- Database ID: `03a3dab2-c5b7-4436-a720-d47d76792647`
- Current populated fields:
  - Themes: Fiction; Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 117. El ojo del mundo - Robert Jordan

- Database ID: `4efabb7c-7e4d-48c2-b822-45f70b6101c7`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 118. El rey de hierro - Maurice Druon

- Database ID: `e22f25e9-879f-4027-9900-5863f62fae2c`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 119. El románico de Cantabria en sus cinco colegiatas - María Eálo de Sá

- Database ID: `462a8d34-07b2-4f51-a3dd-5eb756120a5a`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 120. El señor de Bembibre - Enrique Gil y Carrasco

- Database ID: `b91dba0d-e059-4b23-80ed-9402cf4dfc91`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 121. El sombrero de tres picos - Pedro Antonio de Alarcón

- Database ID: `bb663b91-fed0-4b43-b6a6-f6a8b9ad2cd1`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 122. El terror de la razón - H.P. Lovecraft

- Database ID: `6e8d7deb-127b-40c4-bad7-6188fd738e92`
- Current populated fields:
  - Themes: Letter Collection
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Letter Collection`
  - Move Themes: `Letter Collection` -> Subgenres: `Letters`

#### 123. El tiempo entre costuras - María Dueñas

- Database ID: `f5124340-4381-499f-bd7c-ac7dfa7fe495`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 124. El umbral de la eternidad - Ken Follett

- Database ID: `df31600a-c634-4b6b-9428-c26147ddc8af`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 125. El umbral de la noche - Stephen  King

- Database ID: `547c321f-288f-4465-9b70-d780f144ebf4`
- Current populated fields:
  - Themes: Horror
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Horror`
  - Move Themes: `Horror` -> Subgenres: `Horror`

#### 126. El árbol de la ciencia - Pío Baroja

- Database ID: `23306431-6a98-4538-8b54-60cf3a940c0c`
- Current populated fields:
  - Themes: Philosophy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Philosophy`
  - Move Themes: `Philosophy` -> Subgenres: `Philosophy`

#### 127. El árbol de la ciencia - Pío Baroja

- Database ID: `3de2d024-b200-4efd-933b-c2e948873246`
- Current populated fields:
  - Themes: Philosophy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Philosophy`
  - Move Themes: `Philosophy` -> Subgenres: `Philosophy`

#### 128. Elantris - Brandon Sanderson

- Database ID: `7f217d74-889c-4dab-b40f-43ec58286cdc`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 129. Elric of Melniboné - Michael Moorcock

- Database ID: `289a5496-38c3-4563-a919-c7bd9c26c90c`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 130. Elven Star - Margaret Weis; Tracy Hickman

- Database ID: `8cfc449a-242e-46d1-8321-ee90bbb58ccf`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 131. Ender's Game - Orson Scott Card

- Database ID: `63ee7574-f081-4a67-9410-01a7669ecaf5`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 132. Enemy Lines I: Rebel Dream - Aaron Allston

- Database ID: `54473ca3-e632-46ed-b061-04ae3ddd2f69`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 133. Enemy Lines II: Rebel Stand - Aaron Allston

- Database ID: `8ef3f249-fa1d-415c-8a27-26dd38d7ceb7`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 134. Escribir contra los hombres - H.P. Lovecraft

- Database ID: `f0f0def5-b18f-4d4e-92c3-76044eb3fe8b`
- Current populated fields:
  - Themes: Letter Collection
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Letter Collection`
  - Move Themes: `Letter Collection` -> Subgenres: `Letters`

#### 135. Exile - R.A. Salvatore

- Database ID: `ccfa5883-d1de-4fab-ae8c-8c585987ac36`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 136. Fate of the Jedi: Abyss - Troy Denning

- Database ID: `218015af-dedd-4c5c-9183-40337a7f9185`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 137. Fate of the Jedi: Allies - Christie Golden

- Database ID: `51707422-d85c-42ee-9bfe-7f6b41df3e96`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 138. Fate of the Jedi: Apocalypse - Troy Denning

- Database ID: `56dbef80-f308-42b0-aed8-d668eba6cad0`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 139. Fate of the Jedi: Ascension - Christie Golden

- Database ID: `ff1e22ad-4e25-489e-aab8-5960337aed77`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 140. Fate of the Jedi: Backlash - Aaron Allston

- Database ID: `006a5959-465d-4fb4-ad58-f7907b7735c4`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 141. Fate of the Jedi: Conviction - Aaron Allston

- Database ID: `2837abb3-36a1-49ae-8ad6-391c7fa20197`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 142. Fate of the Jedi: Omen - Christie Golden

- Database ID: `0bea054f-c558-4a7c-9384-8ad923357519`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 143. Fate of the Jedi: Outcast - Aaron Allston

- Database ID: `e8a722fe-717f-4f5c-b359-08a0b8fa4504`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 144. Fate of the Jedi: Vortex - Troy Denning

- Database ID: `7e359c24-9bd8-465d-9d6a-e971abaa37a9`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 145. Fever Crumb - Philip Reeve

- Database ID: `35ca57d8-bb4c-46a4-9dc4-a5360572b11b`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 146. Fire Sea - Margaret Weis; Tracy Hickman

- Database ID: `c5f3651f-ebba-433c-9f65-3f1ca24b5903`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 147. Force Heretic I: Remnant - Sean Williams; Shane Dix

- Database ID: `3b3bbb7a-76da-4af1-9e9a-7e00ec48ee7c`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 148. Force Heretic II: Refugee - Sean Williams; Shane Dix

- Database ID: `f8e14ef9-19ad-48c0-b5f6-983f3319d4e3`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 149. Force Heretic III: Reunion - Sean Williams; Shane Dix

- Database ID: `322f26d0-6ef5-4224-bf94-9931949f3f21`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 150. Frankenstein - Mary Wollstonecraft Shelley

- Database ID: `63c5d0e7-6f3f-4f00-9140-1c07ea1a3316`
- Current populated fields:
  - Themes: Horror
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Horror`
  - Move Themes: `Horror` -> Subgenres: `Horror`

#### 151. God Emperor of Dune - Frank Herbert

- Database ID: `68562e12-2551-4fdc-97fa-1587d875a64a`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 152. Gods of Jade and Shadow - Silvia Moreno-Garcia

- Database ID: `05e3c9f9-05fc-418b-a909-929a12ef1a90`
- Current populated fields:
  - Themes: Fiction; Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Choose exactly one major Genre from Fiction; Fantasy; the conservative proposal is `Fantasy` based on the most specific current label
  - Move Themes: `Fiction` -> Genres: `Fantasy`
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels
- Manual review:
  - Confirm the proposed major Genre because the legacy Themes value contains multiple genre levels

#### 153. Hacia la tierra del Zar - Teodoro M. Kalaw

- Database ID: `eeb28462-27ba-4851-b10b-936271e1bdd4`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 154. Harry Potter and the Chamber of Secrets - J.K. Rowling

- Database ID: `fa52955c-26ae-40fa-9b98-9eb8840220b4`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 155. Harry Potter and the Deathly Hallows - J.K. Rowling

- Database ID: `89333d78-ed2e-48e0-8624-974c4d3d3e7d`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 156. Harry Potter and the Goblet of Fire - J.K. Rowling

- Database ID: `eb13ebb9-fb12-4dc7-b029-8925a88d643b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 157. Harry Potter and the Half-Blood Prince - J.K. Rowling

- Database ID: `33ca771b-d17c-42c6-8b21-dd90e0384a9b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 158. Harry Potter and the Order of the Phoenix - J.K. Rowling

- Database ID: `5603de5f-39e4-4f6a-9d0a-17f0915a568a`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 159. Harry Potter and the Philosopher's Stone - J.K. Rowling

- Database ID: `b7680791-3f41-4dd3-9b20-99b5f5d26b62`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 160. Harry Potter and the Prisoner of Azkaban - J.K. Rowling

- Database ID: `95dad0e2-c6f8-49c6-a7ee-68d673f6fd72`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 161. Harry Potter y el cáliz de fuego - J.K. Rowling

- Database ID: `cbf60699-74ef-4aad-b045-a6c32fe1fd9a`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 162. Harry Potter y el misterio del príncipe - J.K. Rowling

- Database ID: `ad427047-ae05-4676-a4ff-48729901e6cd`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 163. Harry Potter y el prisionero de Azkaban - J.K. Rowling

- Database ID: `9569e425-26a3-4e4f-9574-79dd7406d78a`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 164. Harry Potter y la cámara secreta - J.K. Rowling

- Database ID: `74baa1d8-8435-4964-9429-bdfc2d90e9b2`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 165. Harry Potter y la Orden del Fénix - J.K. Rowling

- Database ID: `a895069a-4c05-4d3a-a741-72d39e2eec68`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 166. Harry Potter y la piedra filosofal - J.K. Rowling

- Database ID: `4d64a9c3-24a8-4a1d-a4cc-cc6f2701f2c1`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 167. Heike monogatari - Anonymous

- Database ID: `b96f9140-f195-4e45-a164-8eb8c4a35392`
- Current populated fields:
  - Themes: Epic Literature; Historical Fiction; Military Tale (Gunki Monogatari); Japanese Classical Literature; Tragedy; Impermanence (mujō); Buddhist themes; Samurai culture; Bushido; Civil war; Clan rivalry; Taira clan; Minamoto clan; Genpei War; 12th-century Japan; Rise and fall of power; Heroism; Honor and duty; Loyalty; Self-sacrifice; Aristocracy vs. warrior class; Oral tradition; Biwa recitation; Episodic structure; Karma and fate; Enlightenment and monasticism; Love stories; Female characters; Tragic heroes; Political intrigue; Medieval Japan; Court life; Anonymous authorship; Classic of world literature; Influence on Noh and Kabuki theater
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Epic Literature`
  - Move Themes: `Epic Literature` -> Subgenres: `Epic Literature`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`
  - Move Themes: `Tragedy` -> Subgenres: `Tragedy`
  - Move Themes: `12th-century Japan` -> Historical Periods: `12th-century Japan`
  - Move Themes: `Oral tradition` -> Subjects: `Oral tradition`
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 168. Heir to the Empire - Timothy Zahn

- Database ID: `cc5c5a8f-6362-4a08-8852-cfc0424ee921`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 169. Heretics of Dune - Frank Herbert

- Database ID: `ff5d1180-8d5e-41ef-a681-013cb02cb0b8`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 170. Hierba - Keum Suk Gendry-Kim

- Database ID: `0c161764-da49-4c3f-8586-734a8a3dfc51`
- Current populated fields:
  - Themes: Graphic Novel; Non-Fiction; Biographical Memoir; Historical Comics; Korean Literature (Manhwa); Comfort women; Sexual slavery; World War II; Japanese occupation of Korea; Japanese Imperial Army; Korea; Manchuria; Colonial violence; Gendered violence; War crimes; Trauma and survival; Memory and testimony; Oral history; Interview-based narrative; Female protagonist; Child's perspective; Poverty and abandonment; Resilience and strength; Black and white artwork; Ink brushwork; Anti-war; Historical atrocity; Disputed history; Colonial amnesia; Shame and grief; Marginalized voices; Women's rights; Human rights; Award-winning; Harvey Award winner
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Graphic Novel` -> Subgenres: `Graphic Novel`
  - Move Themes: `Non-Fiction` -> Genres: `Non-Fiction`
  - Move Themes: `Biographical Memoir` -> Subgenres: `Memoir`
  - Move Themes: `World War II` -> Historical Periods: `World War II`
  - Move Themes: `Oral history` -> Subjects: `Oral history`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 171. Historias de la palma de la mano - Yasunari Kawabata

- Database ID: `7c0d2c6c-fb79-4ee2-a9d6-d4d542c978fc`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 172. Homeland - R.A. Salvatore

- Database ID: `5dce6fb1-b052-4f29-ac36-b236e865b1f5`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 173. Horizonte de estrellas - Víctor Conde; Guillem Sánchez

- Database ID: `4f0b7bdf-c180-4e94-93b5-5d2f3b4ffcce`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 174. Incompleteness - Rebecca Goldstein

- Database ID: `2e17cfc7-ca0f-4315-8123-2a9c6db21c27`
- Current populated fields:
  - Themes: Science
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Science`
  - Move Themes: `Science` -> Subgenres: `Science`

#### 175. Indigno de ser humano - Osamu Dazai

- Database ID: `6478f935-62c6-4c86-9868-eb06af38186e`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 176. Infernal Devices - Philip Reeve

- Database ID: `8557c676-6415-4da0-9ab2-05b7c1fc624d`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 177. Into the Labyrinth - Margaret Weis; Tracy Hickman

- Database ID: `16c4a059-35a6-47bf-862c-b98191405a80`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 178. Into Thin Air - Jon Krakauer

- Database ID: `7689bd49-6879-4f12-bcf5-367e6d040e31`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 179. It - Stephen  King

- Database ID: `16f47d33-2040-4b92-a405-f847e2039502`
- Current populated fields:
  - Themes: Horror
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Horror`
  - Move Themes: `Horror` -> Subgenres: `Horror`

#### 180. Ivanhoe - Walter Scott

- Database ID: `bb751521-4eed-4ebc-9821-cc8225dcf31a`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 181. Kioto - Yasunari Kawabata

- Database ID: `b55f6256-9af2-4b80-bdcc-81a3cbfb60fb`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 182. Klara and the Sun - Kazuo Ishiguro

- Database ID: `eaf95e02-606b-450e-a644-109813a10d48`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 183. Knife of Dreams - Robert Jordan

- Database ID: `1b49ae96-6fa0-4f1c-84e0-2bf3f448d3ac`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 184. Kokoro - Natsume Sōseki

- Database ID: `14cd453e-f479-48c4-895e-9566c3b9cbe5`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 185. La armadura de la luz - Ken Follett

- Database ID: `6bec71a7-5662-43b7-8bb4-c01f4e8a0f0b`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 186. La bailarina de Izu - Yasunari Kawabata

- Database ID: `abb3a640-c0c5-4816-8af8-55cb4b29744d`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 187. La casa - Michael McDowell

- Database ID: `6ebada20-0e68-4f89-ba61-8e5ff7299d85`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 188. La casa de las bellas durmientes - Yasunari Kawabata

- Database ID: `59fc53f0-1ab9-4d2b-a0e4-e265b40f297d`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 189. La caída de los gigantes - Ken Follett

- Database ID: `e61a8cfd-2fe0-473c-b4e8-e69f7991eb28`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 190. La chica que vive al final del camino - Laird Koenig

- Database ID: `001c463d-cc35-42db-9196-1ae48c768447`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 191. La China que viví y entreví - Marcela de Juan

- Database ID: `8a23a743-453a-459d-9ca2-72bdec907811`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 192. La clase de griego - Han Kang

- Database ID: `a05fd528-2be2-4ff3-af1c-457f1e54335f`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 193. La condición humana - Hannah Arendt

- Database ID: `2853a177-8d42-4268-bbd1-886b25262c97`
- Current populated fields:
  - Themes: Philosophy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Philosophy`
  - Move Themes: `Philosophy` -> Subgenres: `Philosophy`

#### 194. La corte de Carlos IV - Benito Pérez Galdós

- Database ID: `d574c4c3-2c24-4174-b0c0-00ba91dd1ed2`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 195. La felicidad de los pececillos - Simon Leys

- Database ID: `561d6735-2b2a-4b8a-966d-a5dc46206d62`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 196. La filosofía del vino - Béla Hamvas

- Database ID: `54130b27-cbda-4d6f-9fd3-9942d95b94f5`
- Current populated fields:
  - Themes: Philosophy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Philosophy`
  - Move Themes: `Philosophy` -> Subgenres: `Philosophy`

#### 197. La flor de lis y el león - Maurice Druon

- Database ID: `183d8274-8445-44ce-adbe-626ce914c3d5`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 198. La fortuna - Michael McDowell

- Database ID: `11dba24e-6c5c-44e3-bfb3-e010863e01ba`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 199. La gran hambruna en la China de Mao - Frank Dikötter

- Database ID: `ca4988f0-8c2b-4bf0-b6ae-566f09cefcaa`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 200. La guerra - Michael McDowell

- Database ID: `8e46d2db-e6f4-4c36-9fb0-086d6ec24b97`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 201. La isla del tesoro - Robert Louis Stevenson

- Database ID: `0116e723-8345-4f14-b0b1-c317879107a5`
- Current populated fields:
  - Themes: Adventure Fiction; Coming-of-Age; Nautical Fiction; Classic Literature; British Literature; Pirates; Treasure hunt; Buried treasure; Sea voyage; Sailing ships; 18th-century setting; Mutiny; Moral ambiguity; Betrayal; Loyalty; Friendship; Boy protagonist; Male coming-of-age; Eccentric villain; Long John Silver; Hispaniola; Desert island; Maps and navigation; Good vs. evil; Greed; Survival; Swashbuckling; Classic adventure tropes; Atmospheric setting; Tropical island; Tavern life; 19th-century British fiction; Iconic characters; First-person narration; Father figure (surrogate)
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Adventure Fiction`
  - Move Themes: `Adventure Fiction` -> Subgenres: `Adventure Fiction`
  - Move Themes: `Coming-of-Age` -> Subgenres: `Coming-of-Age`
  - Move Themes: `Classic Literature` -> Subgenres: `Classic Literature`
  - Move Themes: `British Literature` -> Subgenres: `British Literature`
  - Move Themes: `18th-century setting` -> Historical Periods: `18th-century setting`
  - Move Themes: `19th-century British fiction` -> Historical Periods: `19th-century British fiction`
  - Move Themes: `First-person narration` -> Subjects: `First-person narration`
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 202. La ley de los varones - Maurice Druon

- Database ID: `0eafebb7-d475-4086-8b1b-072486d20cec`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 203. La librería - Penelope Fitzgerald

- Database ID: `a32a0e87-88a5-4deb-9d38-43ebbfb5240a`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 204. La loba de Francia - Maurice Druon

- Database ID: `6f7e1009-dffb-4120-b84b-00b40b3b2e4f`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 205. La matemática: su contenido, métodos y significado I - A.D. Aleksándrov; A.N. Kolmogórov; M.A. Lavréntiev

- Database ID: `1b46c778-b092-485f-b493-4497273b8ede`
- Current populated fields:
  - Themes: Science
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Science`
  - Move Themes: `Science` -> Subgenres: `Science`

#### 206. La materia oscura y los dinosaurios - Lisa Randall

- Database ID: `03ee7796-dfdc-4713-98fc-6e3228cbdd16`
- Current populated fields:
  - Themes: Popular Science; Cosmology; Physics; Paleontology; Science Writing; Dark matter; Dinosaur extinction; Cretaceous-Paleogene extinction event; Chicxulub impact; Comets and asteroids; Oort Cloud; Milky Way galaxy; Particle physics; Astrophysics; Interconnectedness of the universe; Mass extinctions; Solar System; Origin of life; Big Bang; Cosmic history; Speculative science; Scientific hypothesis; Harvard physicist; Accessible science writing; History of science; Geology; Biology and evolution; Kuiper Belt; Gravitational forces; Dark energy; Scientific method; Harvard University; New York Times bestseller; Women in science; Dissipative dark matter theory
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Popular Science`
  - Move Themes: `Popular Science` -> Subgenres: `Popular Science`
  - Move Themes: `Physics` -> Subjects: `Physics`
  - Move Themes: `Solar System` -> Settings: `Solar System`
  - Move Themes: `History of science` -> Subjects: `History of science`
  - Move Themes: `Geology` -> Subjects: `Geology`
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 207. La morada - R.A. Salvatore; Andrew Dabb; Tim Seeley

- Database ID: `82ff9c28-ebb9-4e9a-91f8-bff4521ca039`
- Current populated fields:
  - Themes: Comic; Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Comic` -> Subgenres: `Comic`
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 208. La muerte de Vivek Oji - Akwaeke Emezi

- Database ID: `2e7bebf3-f160-45c8-bcd5-2681198f5dfb`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 209. La Nena - Carmen Mola

- Database ID: `7932f4c3-8dcc-49a8-bed0-177c1612188f`
- Current populated fields:
  - Themes: Fiction; Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 210. La novia gitana - Carmen Mola

- Database ID: `4ea185cc-1d04-45d0-987a-e864cbf69fb7`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 211. La pandilla de Asakusa - Yasunari Kawabata

- Database ID: `c138b6bf-7ea2-4592-9514-68b007583423`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 212. La península de las casas vacías - David Uclés

- Database ID: `208db65f-115b-4710-a4cb-91afd6e9cb02`
- Current populated fields:
  - Themes: Fiction; Magical Realism
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Move Themes: `Magical Realism` -> Subgenres: `Magical Realism`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 213. La Red Púrpura - Carmen Mola

- Database ID: `9a2f17d0-35bc-4fc5-ac29-be57f9054241`
- Current populated fields:
  - Themes: Fiction; Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 214. La reina estrangulada - Maurice Druon

- Database ID: `f7f32fc8-e88f-4fbb-a38c-ccb5d62b59a4`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 215. La riada - Michael McDowell

- Database ID: `9d3b71e7-d9f7-426d-8955-33e86c8d49fb`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 216. La teoría del todo - Stephen Hawking

- Database ID: `c47d6fee-2ef4-47bb-b87a-0b7cd1ba929c`
- Current populated fields:
  - Themes: Science
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Science`
  - Move Themes: `Science` -> Subgenres: `Science`

#### 217. Las bellas extranjeras - Mircea Cărtărescu

- Database ID: `1ba91a66-9075-4669-8b4a-206f77b49de0`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 218. Las madres - Carmen Mola

- Database ID: `d8b58f49-697f-4bf0-b626-62bc74268798`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 219. Las tinieblas y el alba - Ken Follett

- Database ID: `cdf68aec-a4ff-4f1c-80cf-9dd2e8f1fbb3`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 220. Lección de alemán - Siegfried Lenz

- Database ID: `83c3e6e2-b936-45a9-b9e4-58ec8a4b4954`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 221. Legacy of Blood - Richard A. Knaak

- Database ID: `0e91e797-0f9e-4508-9581-4937802d2a1c`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 222. Legacy of the Force: Bloodlines - Karen Traviss

- Database ID: `334f0b8a-af4f-48f5-8f60-7c8ef2800582`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 223. Legacy of the Force: Exile - Aaron Allston

- Database ID: `c12e5a9d-149f-463e-b530-ef8fd283715d`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 224. Legacy of the Force: Fury - Aaron Allston

- Database ID: `fee607ed-7b27-4595-98d1-653198ab356f`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 225. Legacy of the Force: Inferno - Troy Denning

- Database ID: `ae30295d-d1ad-4d69-89ff-dec12676349b`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 226. Legacy of the Force: Invincible - Troy Denning

- Database ID: `5ebbc3b7-12c3-45b6-bcc9-cc29d3d94675`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 227. Legacy of the Force: Revelation - Karen Traviss

- Database ID: `96f25391-da2a-40b7-aac5-f5e865cec711`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 228. Legacy of the Force: Sacrifice - Karen Traviss

- Database ID: `eb49ce06-a777-4bec-9eae-b84d99a22e3f`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 229. Legacy of the Force: Tempest - Troy Denning

- Database ID: `296515a5-7ab6-4025-989b-f904f36d2ce7`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 230. Legado en los huesos - Dolores Redondo

- Database ID: `588adf19-1933-4b3f-82c1-1c2754993723`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 231. Lluvia - Michael McDowell

- Database ID: `f9c6922b-c0c1-4979-9fd6-86c259b12db4`
- Current populated fields:
  - Themes: Horror
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Horror`
  - Move Themes: `Horror` -> Subgenres: `Horror`

#### 232. Lo bello y lo triste - Yasunari Kawabata

- Database ID: `a46c1e8b-66b5-4bd2-955a-210cf35094cc`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 233. Lord of Chaos - Robert Jordan

- Database ID: `f2f24b39-9255-4ac1-8c5c-96b2dbe90d9a`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 234. Lord of the Flies - William Golding

- Database ID: `5d39743b-2802-45a4-bf98-583ce28d2d55`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 235. Lorenz Saladin - Annemarie Schwarzenbach

- Database ID: `f0367093-190f-45fd-8858-5f5ebb55d2a3`
- Current populated fields:
  - Themes: Biography
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Biography` -> Genres: `Biography`
  - Remove every moved major genre label from Themes after populating Genres

#### 236. Los extraños - Jon Bilbao

- Database ID: `98758617-1e36-4309-a319-efc06d481154`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 237. Los infortunios de Svoboda - János Székely

- Database ID: `64e40833-ee1f-464f-88f0-cfa400e65f94`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 238. Los inocentes - María Oruña

- Database ID: `0c782b35-0f65-46a2-9d87-5fcc567bea92`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 239. Los juegos del hambre - Suzanne Collins

- Database ID: `14d3ddde-c700-4509-a506-b98c1564aabb`
- Current populated fields:
  - Themes: Dystopian Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Science Fiction` from `Dystopian Fiction`
  - Move Themes: `Dystopian Fiction` -> Subgenres: `Dystopian Fiction`

#### 240. Los libros de Terramar - Ursula K. Le Guin

- Database ID: `5ca7530e-e9fd-43cd-9da9-9f274405615e`
- Current populated fields:
  - Themes: Fantasy; High Fantasy; Coming-of-age; Anthology; Feminist Literature; American Literature; Magic and wizardry; Dragons; Archipelago world-building; Quest narrative; Good vs. evil; Identity and self-knowledge; Death and the afterlife; Balance and duality; Gender and power; Female protagonists; Hero's journey; Island setting; Ancient languages and true names; Young adult crossover; Taoism-influenced; Ecological themes; Classic fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Move Themes: `Coming-of-age` -> Subgenres: `Coming-of-age`
  - Move Themes: `American Literature` -> Subgenres: `American Literature`
  - Move Themes: `Quest narrative` -> Subjects: `Quest narrative`
  - Move Themes: `Hero's journey` -> Subjects: `Hero's journey`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 241. Los pilares de la Tierra - Ken Follett

- Database ID: `50e37342-8886-4ead-bf1e-74006137f8af`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 242. Los relojes - Agatha Christie

- Database ID: `90771cae-ae44-4e1b-8c53-7981a8e04f70`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 243. Los tres mundos - Santiago Posteguillo

- Database ID: `caf053dc-4939-4d1a-beac-927f25b8f1a8`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 244. Los venenos de la corona - Maurice Druon

- Database ID: `d7618f2d-4659-4346-9dc9-7eb7e9d0703c`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 245. Malaventura - Fernando Navarro

- Database ID: `0afb29e1-2fba-4a98-b389-1cc02717d904`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 246. Maldita Roma - Santiago Posteguillo

- Database ID: `cdcbe410-594c-4d8c-8510-6e7505f9aedf`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 247. Matamonstruos - Jon Bilbao

- Database ID: `5c16fedf-102d-4fd2-b648-006c258f3b30`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 248. Mi familia y otros animales - Gerald Durrell

- Database ID: `92a2dbe5-794c-4835-a0f5-8891b8876f4d`
- Current populated fields:
  - Themes: Biography
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Biography` -> Genres: `Biography`
  - Remove every moved major genre label from Themes after populating Genres

#### 249. Mientras agonizo - William Faulkner

- Database ID: `6e735e82-56cb-40f6-8a35-9cc524810471`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 250. Mil grullas - Yasunari Kawabata

- Database ID: `a52509ae-1692-4edb-90e0-d29803a84217`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 251. Millennium Falcon - James Luceno

- Database ID: `81366f56-0a41-44a9-a7d1-1ad1bf449f43`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 252. Miradnos bailar - Leïla Slimani

- Database ID: `0cb5bf3e-6af4-4aed-afbc-04e286b5726f`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 253. Misceláneas japonesas - Lafcadio Hearn

- Database ID: `faa246ff-f7f6-4f62-88ed-ad55157161c9`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 254. Mistborn: Secret History - Brandon Sanderson

- Database ID: `2112d606-541c-429b-b01c-d6f5f95cf58f`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 255. Moby Dick - Herman Melville

- Database ID: `499fdaa4-6d9e-41e2-b444-1bed74bc2dae`
- Current populated fields:
  - Themes: Adventure
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Adventure`
  - Move Themes: `Adventure` -> Subgenres: `Adventure Fiction`

#### 256. Monasterio de Samos - Pedro de la Portilla

- Database ID: `43647632-9656-44e9-88ee-aee49cba701b`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 257. Mortal Engines - Philip Reeve

- Database ID: `68c4b6d8-6464-48c1-ad90-0c5cbc2150fe`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 258. Máscara - Stanisław Lem

- Database ID: `81ca6b66-eb22-41e2-a61d-586fd3bea97f`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 259. Napoleón en Chamartín - Benito Pérez Galdós

- Database ID: `d24eddce-a1e3-48d9-bc2a-7fd408337907`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 260. Naruto Remix Vol.1 - Masashi Kishimoto

- Database ID: `36386490-2823-473e-b7c9-13540b58963d`
- Current populated fields:
  - Themes: Shōnen Manga; Manga
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Shōnen Manga`
  - Move Themes: `Shōnen Manga` -> Subgenres: `Shōnen Manga`
  - Move Themes: `Manga` -> Subgenres: `Manga`
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 261. Naruto Remix Vol.2 - Masashi Kishimoto

- Database ID: `ec80703c-7278-4081-9dc7-43713055bc65`
- Current populated fields:
  - Themes: Shōnen Manga; Manga
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Shōnen Manga`
  - Move Themes: `Shōnen Manga` -> Subgenres: `Shōnen Manga`
  - Move Themes: `Manga` -> Subgenres: `Manga`
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 262. New Spring - Robert Jordan

- Database ID: `fec94359-b5aa-4d61-beda-e5508e1b1ae0`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 263. Nineteen Eighty-Four - George Orwell

- Database ID: `6dca1d86-8202-432a-aaa5-21603c48a45b`
- Current populated fields:
  - Themes: Dystopian Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Science Fiction` from `Dystopian Fiction`
  - Move Themes: `Dystopian Fiction` -> Subgenres: `Dystopian Fiction`

#### 264. Norse Mythology - Neil Gaiman

- Database ID: `58c9b0a1-13b7-4c77-becc-73b30493398c`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 265. Northern Lights - Philip Pullman

- Database ID: `5f92be4b-a1d0-4d75-a622-002ccfc99439`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 266. Novela de ajedrez - Stefan Zweig

- Database ID: `aa3055c1-9be4-4ffb-87f3-09b351547b2d`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 267. Novela de xadrez - Stefan Zweig

- Database ID: `328d14e4-dee4-4e50-a188-5c10b6de76df`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 268. Nubes flotantes - Fumiko Hayashi

- Database ID: `702348b7-4440-4a48-b50d-79e766bad254`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 269. Nunca - Ken Follett

- Database ID: `4ea67d30-70bb-4431-bc21-b03f014c90e2`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 270. Oathbringer - Brandon Sanderson

- Database ID: `077eda0f-6a42-4783-9696-52cd6f53710e`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 271. Of Mice and Men - John Steinbeck

- Database ID: `2800322f-e34d-49eb-abfe-5b85e9cd06cc`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 272. Ofrenda a la tormenta - Dolores Redondo

- Database ID: `7c6f27ce-f1ed-4b50-b2bf-83abb969510c`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 273. ONE PIECE 巻百十三 - Eiichiro Oda

- Database ID: `2b8b5827-c57d-4d88-b352-a626f516b64f`
- Current populated fields:
  - Themes: Manga
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Manga`
  - Move Themes: `Manga` -> Subgenres: `Manga`

#### 274. ONE PIECE 巻百十四 - Eiichiro Oda

- Database ID: `3e20d60d-3883-494c-9380-b273a8af8fd2`
- Current populated fields:
  - Themes: Manga
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Manga`
  - Move Themes: `Manga` -> Subgenres: `Manga`

#### 275. Orient-Express - Mauricio Wiesenthal

- Database ID: `71e5d3d2-2eca-4cc2-97f3-190eac75e25a`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 276. Os outros feirantes - Álvaro Cunqueiro

- Database ID: `aa558ba1-ab3b-4251-9331-f70a8d8b66de`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 277. Otaberra - Elisa Victoria

- Database ID: `95c9d4c5-2151-422b-a1ec-636ccc5d9df9`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 278. Pasajero para Fráncfort - Agatha Christie

- Database ID: `11c82fe7-f518-4e6f-91fd-7c435dd57dfb`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 279. Pasión de las santas Perpetua y Felicidad - Alejandra de Riquer

- Database ID: `8d044d1c-9a19-46af-9d02-c9fc242b5dde`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 280. Passage to Dawn - R.A. Salvatore

- Database ID: `f422151f-b059-4132-85eb-c6a34f20b57b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 281. País de nieve - Yasunari Kawabata

- Database ID: `e187ebf2-a3e6-4077-ba1d-752a01ba07e9`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 282. Peregrinatio - Matilde Asensi

- Database ID: `09adbfaf-f396-498b-a63a-ee2f7173e2d4`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 283. Poirot investiga - Agatha Christie

- Database ID: `817f06d4-bd4e-47df-bf7a-38e4fc0dfe6a`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 284. Predator's Gold - Philip Reeve

- Database ID: `5ffa4dee-0953-4477-a74b-7b957256d503`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 285. Pride and Prejudice - Jane Austen

- Database ID: `571ea060-dfa3-4bd8-940a-f51111ec8b62`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 286. Provocación - Stanisław Lem

- Database ID: `e587982c-d558-41e6-8906-303d9900109a`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 287. Pygmalion - George Bernard Shaw

- Database ID: `e124e90a-7710-4238-9921-18938d2a9d71`
- Current populated fields:
  - Themes: Play
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre: `Fiction` from `Play`
  - Review Form: `Play` because Play is not in the current controlled Form vocabulary
- Manual review:
  - Choose an existing controlled Form or explicitly extend the controlled vocabulary for Play

#### 288. Quidditch Through the Ages - Kennilworthy Whisp

- Database ID: `1c77009f-3f3c-4f2b-b21c-e26c47d1d2db`
- Current populated fields:
  - Themes: Miscellanea, Sports, Fantasy, History, Quidditch
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Split comma-packed Themes value `Miscellanea, Sports, Fantasy, History, Quidditch` into: Miscellanea; Sports; Fantasy; History; Quidditch
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Move Themes: `History` -> Subgenres: `History`
  - Manually place comma-packed components: Miscellanea; Sports; Quidditch
- Manual review:
  - Classify comma-packed components from `Miscellanea, Sports, Fantasy, History, Quidditch`

#### 289. Quédate conmigo - Elizabeth Strout

- Database ID: `893926c8-09ef-45d1-b924-0649c4bb1c73`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 290. Rashōmon e outros relatos - Ryūnosuke Akutagawa

- Database ID: `f0049cf8-9274-42cc-bda9-95c7d2c0553c`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 291. Recuerdos de un jardinero inglés - Reginald Arkell

- Database ID: `ad0ceee3-037e-470f-9373-2042db52980f`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 292. Riptide - Paul S. Kemp

- Database ID: `2883a24f-c29d-41b8-ad6d-c8aeddb080cd`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 293. Rob Roy - Walter Scott

- Database ID: `778126e1-1661-48f3-ae4b-1569a9f01562`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 294. Roma soy yo - Santiago Posteguillo

- Database ID: `5bb71fe9-e6eb-4464-a260-254a85232940`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 295. Roncesvalles - María Antonia del Burgo

- Database ID: `d34b775e-5192-4e03-be3f-26db45cdc173`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 296. Sauce ciego, mujer dormida - Haruki Murakami

- Database ID: `f433c0b4-c2c0-4569-831e-541e0c0b1bc9`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 297. Scrivener's Moon - Philip Reeve

- Database ID: `9d8aabc8-61a4-44fc-955e-84215a9c4497`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 298. Sea of Swords - R.A. Salvatore

- Database ID: `9f7afe5f-1129-4a94-abfa-80ec8870aa57`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 299. Sepulcros estruscos - Nicanor Gómez Villegas

- Database ID: `0a42211d-b1e5-43d2-817d-abcfce3abe92`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 300. Serpent Mage - Margaret Weis; Tracy Hickman

- Database ID: `a508c205-2a71-4ef3-b731-c3655424fb05`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 301. Shadows of Self - Brandon Sanderson

- Database ID: `8d3dd262-277a-4212-aa4d-96c5a1f92e30`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 302. Shadows of the Empire - Steve Perry

- Database ID: `4e5b786d-1d2b-4c27-9180-c8cc10460ca1`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 303. Siddhartha - Hermann Hesse

- Database ID: `7e61b8f7-8d89-4182-ae72-a71e46f94431`
- Current populated fields:
  - Themes: Philosophy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Philosophy`
  - Move Themes: `Philosophy` -> Subgenres: `Philosophy`

#### 304. Siege of Darkness - R.A. Salvatore

- Database ID: `cf8db287-48df-4e94-9ef0-324da981bf2b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 305. Silence - Shūsaku Endō

- Database ID: `334d3b73-64a5-4f6a-88bc-32fe239d9ea3`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 306. Sobre la muerte de un perro - Jean Grenier

- Database ID: `4367b709-5d70-47a4-be8e-dfbbbeb4f2e2`
- Current populated fields:
  - Themes: Philosophy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Philosophy`
  - Move Themes: `Philosophy` -> Subgenres: `Philosophy`

#### 307. Sojourn - R.A. Salvatore

- Database ID: `4901527b-402a-47da-b674-59753e575919`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 308. Solaris - Stanisław Lem

- Database ID: `115072fd-3ba5-4732-976e-6902bbb508b8`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 309. Sorgo rojo - Mo Yan

- Database ID: `6d1883e8-d7eb-4959-b71b-2e9a16309062`
- Current populated fields:
  - Themes: Magical Realism; Historical Fiction; Literary Fiction; Chinese Literature; War Fiction; Second Sino-Japanese War; Japanese occupation of China; Shandong province; Rural China; Multi-generational family saga; Resistance fighters; Guerrilla warfare; Non-linear narrative; Flashbacks; First-person narration; Folk tale elements; Myth and legend; Sorghum as symbol; Banditry; Arranged marriage; Love and desire; Violence and brutality; Survival; Memory and the past; Ancestral veneration; Anti-war; Peasant life; Oral tradition; Color symbolism; The Cultural Revolution; Nobel Prize in literature; Film adaptation (Zhang Yimou); Lyrical prose; Postmodern structure; Chinese identity and heritage
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Magical Realism`
  - Move Themes: `Magical Realism` -> Subgenres: `Magical Realism`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`
  - Move Themes: `Literary Fiction` -> Subgenres: `Literary Fiction`
  - Move Themes: `Non-linear narrative` -> Subjects: `Non-linear narrative`
  - Move Themes: `First-person narration` -> Subjects: `First-person narration`
  - Move Themes: `Oral tradition` -> Subjects: `Oral tradition`
  - Move Themes: `The Cultural Revolution` -> Historical Periods: `The Cultural Revolution`
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 310. Splinter of the Mind's Eye - Alan Dean Foster

- Database ID: `6910930c-4764-4bb1-a270-9cc1cb4c09fe`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 311. Star by Star - Troy Denning

- Database ID: `c29880b1-7af6-4a01-a2b4-f25c073db385`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 312. Starless Night - R.A. Salvatore

- Database ID: `22dac786-c402-442a-9c04-7d41d8bff47b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 313. Streams of Silver - R.A. Salvatore

- Database ID: `339f7e6f-89b9-4eae-b6c7-6a1ba0d20ada`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 314. Tales of the Dying Earth - Jack Vance

- Database ID: `a8fdce76-7d8c-46cd-b059-1aa2184c3c7c`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 315. Tau Zero - Poul Anderson

- Database ID: `4969997c-48d1-4d18-aa6c-fd40731950e8`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 316. Teatro Manga 1 - Akira Toriyama

- Database ID: `347984ab-7108-4c1a-a2a7-72ddbf219fae`
- Current populated fields:
  - Themes: Manga
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Manga`
  - Move Themes: `Manga` -> Subgenres: `Manga`

#### 317. Termush - Sven Holm

- Database ID: `7c49604d-072f-4cf2-9a61-3f7ec010f70d`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 318. Test of the Twins - Margaret Weis; Tracy Hickman

- Database ID: `92322d3a-de6d-465a-9ca5-7c4b9e8be668`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 319. The Alloy of Law - Brandon Sanderson

- Database ID: `02567313-95a6-4dff-a1ad-489a9c131f99`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 320. The Amber Spyglass - Philip Pullman

- Database ID: `b48ba634-39d9-4a1b-ac8c-b5933763416e`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 321. The Bands of Mourning - Brandon Sanderson

- Database ID: `f4a9fac6-d07c-42fd-b893-128585d8366b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 322. The Black Road - Mel Odom

- Database ID: `7fac1ccb-51f5-495f-bf78-9c3e43b724da`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 323. The Call of Cthulhu and Other Weird Stories - H.P. Lovecraft

- Database ID: `4e88c174-e33f-4d42-adce-72385f8a2ee2`
- Current populated fields:
  - Themes: Horror
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Horror`
  - Move Themes: `Horror` -> Subgenres: `Horror`

#### 324. The Casual Vacancy - J.K. Rowling

- Database ID: `494f807b-d19a-4476-8337-f6733d346af9`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 325. The Communist Manifesto - Karl Marx; Friedrich Engels

- Database ID: `66695c04-5a58-407b-baa8-88dab79768bf`
- Current populated fields:
  - Themes: 1911 Revolution
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `1911 Revolution` -> Historical Periods: `1911 Revolution`
  - Assign exactly one major Genre; the current Themes values do not provide a sufficiently certain controlled value
- Manual review:
  - Determine the major Genre from the book itself before moving any ambiguous values

#### 326. The Complete Fiction of H.P. Lovecraft - H.P. Lovecraft

- Database ID: `07371a42-44ab-49d8-a150-2e5f9771f0e3`
- Current populated fields:
  - Themes: Horror; Weird Fiction; Gothic Fiction; Science Fiction; American Literature; Short Fiction / Anthology; Cosmic Horror; Cosmic horror; Existential dread; The unknown; Ancient gods; Cthulhu Mythos; Forbidden knowledge; Madness and sanity; Unreliable narrator; New England setting; Arkham; Miskatonic University; Necronomicon; Elder Gods; Occult; Tentacled monsters; Dreams and nightmares; Isolation; Academia and scholars; Antiquarianism; Racial anxiety; Early 20th-century America; Atmospheric prose; Epistolary elements; Pseudo-scholarship; Human insignificance; Non-Euclidean geometry; Deep sea horror; Body horror; Ancestral secrets; Decaying small towns; Complete works / Omnibus
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Horror` -> Subgenres: `Horror`
  - Move Themes: `Gothic Fiction` -> Subgenres: `Gothic Fiction`
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Move Themes: `American Literature` -> Subgenres: `American Literature`
  - Move Themes: `Early 20th-century America` -> Historical Periods: `Early 20th-century America`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 327. The Courtship of Princess Leia - Dave Wolverton

- Database ID: `edc2a4dd-31b9-4cc9-a777-60ac18787ad5`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 328. The Crystal Shard - R.A. Salvatore

- Database ID: `1282bf89-fbae-478e-9111-a1dd14c9bc82`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 329. The Dragon Reborn - Robert Jordan

- Database ID: `24fca4aa-25c1-4442-9f86-ca9edc6798ad`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 330. The Essex Serpent - Sarah Perry

- Database ID: `6cba87f6-0b99-44c7-a429-a84364e249d7`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 331. The Eye of the World - Robert Jordan

- Database ID: `6b2adc8d-03d2-403c-b6d8-5a953e118a87`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 332. The Fellowship of the Ring - J.R.R. Tolkien

- Database ID: `b52a2b74-0584-4346-b715-a72500c2d6e2`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 333. The Final Empire - Brandon Sanderson

- Database ID: `380c6c48-6690-46b0-b1e2-bc197a8998d8`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 334. The Final Prophecy - Greg Keyes

- Database ID: `f54d689f-e7fb-4f87-b4b8-7cf97c60cc31`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 335. The Fires of Heaven - Robert Jordan

- Database ID: `8e76ede3-f62e-4872-8180-ba086697dc34`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 336. The Gathering Storm - Robert Jordan; Brandon Sanderson

- Database ID: `4ac6a4b4-6960-4c80-aa19-582cfdf843ec`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 337. The Grapes of Wrath - John Steinbeck

- Database ID: `c41f6118-6ec9-4564-ba1d-b96a05c5043f`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 338. The Great Hunt - Robert Jordan

- Database ID: `56791f5a-fa44-4751-811f-f533fb3f1c29`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 339. The Halfling's Gem - R.A. Salvatore

- Database ID: `5fe066ee-2382-4f3f-a562-1f8fce1a0d04`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 340. The Hand of Chaos - Margaret Weis; Tracy Hickman

- Database ID: `644daf81-3799-4def-8291-854fe1676e4d`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 341. The Handmaid's Tale - Margaret Atwood

- Database ID: `f073f62b-7c20-49de-8473-90bdb0057dcb`
- Current populated fields:
  - Themes: Dystopian Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Science Fiction` from `Dystopian Fiction`
  - Move Themes: `Dystopian Fiction` -> Subgenres: `Dystopian Fiction`

#### 342. The Hellbound Heart - Clive Barker

- Database ID: `52206339-434d-4eb6-909b-49671586c4ea`
- Current populated fields:
  - Themes: Horror; Dark Fantasy; Transgressive Fiction; Novella; British Literature; Demons; Hellraiser (film origin); Cenobites; Sadomasochism; Pain and pleasure; Desire and obsession; Supernatural creatures; Puzzle box; Other dimensions; Body horror; Transformation; Sexuality and transgression; Greed; Betrayal; Love triangle; Resurrection; Gothic atmosphere; Visceral prose; Cosmic horror; Moral corruption; The forbidden; Human nature; Lust; Violence; Occult; British horror; Cult classic; Short form fiction; Dark eroticism; Iconic villain
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Horror`
  - Move Themes: `Horror` -> Subgenres: `Horror`
  - Move Themes: `Dark Fantasy` -> Subgenres: `Dark Fantasy`
  - Move Themes: `Novella` -> Subgenres: `Novella`
  - Move Themes: `British Literature` -> Subgenres: `British Literature`
  - Move Themes: `Supernatural creatures` -> Subjects: `Supernatural creatures`
  - Move Themes: `Violence` -> Subjects: `Violence`
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 343. The Hero of Ages - Brandon Sanderson

- Database ID: `c4bedc40-320b-4aac-8b47-60140c7c669f`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 344. The History of England's Cathedrals - Nicholas Orme

- Database ID: `2cf1e105-b255-408a-9117-2ed63bc46d71`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 345. The Hobbit, or There and Back Again - J.R.R. Tolkien

- Database ID: `6e32ae67-ba4c-4afa-a050-329aa0b99c30`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 346. The Joiner King - Troy Denning

- Database ID: `d7a08d17-b537-4bbc-8ec5-46d8921b5705`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 347. The Kite Runner - Khaled Hosseini

- Database ID: `43da3af3-c4c3-43df-b003-371d09e8c5cd`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 348. The Last Command - Timothy Zahn

- Database ID: `19dc360f-b361-45f9-9c8f-d1fdf06f1b3c`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 349. The Legacy - R.A. Salvatore

- Database ID: `35fdf8b2-38d7-43be-873b-aaaaea43724b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 350. The Lost Metal - Brandon Sanderson

- Database ID: `79bcd7ba-3818-4f36-a48f-d2ecb0a41707`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 351. The Old Republic: Annihilation - Drew Karpyshyn

- Database ID: `9039b2da-8d47-49a9-a184-91a9560c15c0`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 352. The Old Republic: Deceived - Paul S. Kemp

- Database ID: `8476f5f4-3ccb-43de-b2b8-354b8870b977`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 353. The Old Republic: Fatal Alliance - Sean Williams

- Database ID: `61862de2-7dff-46ab-879f-039d38901c5c`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 354. The Old Republic: Revan - Drew Karpyshyn

- Database ID: `dd1b8ace-913d-4c06-8372-dee151a77438`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 355. The Path of Daggers - Robert Jordan

- Database ID: `a0ab04b6-11a9-4e2d-98fb-0a234fbfe6d3`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 356. The Pit and the Pendulum - Edgar Allan Poe

- Database ID: `b42327ab-9747-4261-9821-d3fb1fcd1122`
- Current populated fields:
  - Themes: Horror
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Horror`
  - Move Themes: `Horror` -> Subgenres: `Horror`

#### 357. The Priory of the Orange Tree - Samantha Shannon

- Database ID: `edab5fd5-c16b-4ef8-a8f4-d00ed817d61d`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 358. The Return of the King - J.R.R. Tolkien

- Database ID: `7c265d37-a74a-434f-838d-27c53b01a323`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 359. The Sailor on the Seas of Fate - Michael Moorcock

- Database ID: `3a9e3e3a-b73f-4ff6-bdef-1b843ba8292b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 360. The Second Generation - Margaret Weis; Tracy Hickman

- Database ID: `6758e356-12d0-4642-98b1-a1e24a5d9ec7`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 361. The Seventh Gate - Margaret Weis; Tracy Hickman

- Database ID: `2a4db1ca-54cf-45bc-be77-e505c4407503`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 362. The Shadow Rising - Robert Jordan

- Database ID: `b3d01658-8a71-492a-9a82-a121ef504cf1`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 363. The Silent Blade - R.A. Salvatore

- Database ID: `a5862867-8aee-4ade-a24a-06bfd20f02b5`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 364. The Silmarillion - J.R.R. Tolkien

- Database ID: `2af0657a-4ac1-49fb-81c7-618b9bcf55d6`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 365. The Soulforge - Margaret Weis

- Database ID: `e2bf8e34-88db-44fb-a8cc-91a7d2817238`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 366. The Spine of the World - R.A. Salvatore

- Database ID: `6c46055c-58e6-4a6c-891e-cc99ee63cc73`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 367. The Subtle Knife - Philip Pullman

- Database ID: `ee239bae-5327-4b57-868f-b4e90489b2a0`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 368. The Swarm War - Troy Denning

- Database ID: `26a7d882-8ea0-4e21-92be-4a1933d9cedc`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 369. The Sword of Shannara - Terry Brooks

- Database ID: `50656dd2-a7b9-4086-b030-8d9faabde328`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 370. The Taming of the Queen - Philippa Gregory

- Database ID: `1181fa95-9866-4f31-a7be-d32ebc33f218`
- Current populated fields:
  - Themes: Fiction, Queens, History, Fiction, biographical, Fiction, historical
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Split comma-packed Themes value `Fiction, Queens, History, Fiction, biographical, Fiction, historical` into: Fiction; Queens; History; biographical; historical
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Move Themes: `History` -> Subgenres: `History`
  - Manually place comma-packed components: Queens; biographical; historical
- Manual review:
  - Classify comma-packed components from `Fiction, Queens, History, Fiction, biographical, Fiction, historical`

#### 371. The Truce at Bakura - Kathy Tyers

- Database ID: `76f9f91d-a55c-4a1f-9778-97c7630b77db`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 372. The Two Towers - J.R.R. Tolkien

- Database ID: `1eb23e28-6f9f-4e6a-bc7c-16b32212f341`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 373. The Unifying Force - James Luceno

- Database ID: `1362f7ab-3dd0-40b1-9d95-b5afad7b5ed3`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 374. The Unseen Queen - Troy Denning

- Database ID: `9cd610b0-1d4d-4437-95f2-3864a830c430`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 375. The War in the Air - H.G. Wells

- Database ID: `e83c3e39-5754-49b8-b83b-9955b1f359e8`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 376. The Way of Kings - Brandon Sanderson

- Database ID: `8a90e8b2-1abf-4844-9f7b-d93ee3a5ef9b`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 377. The Weird of the White Wolf - Michael Moorcock

- Database ID: `ea2a440d-fab1-404f-9ee3-1869c4839b77`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 378. The Well of Ascension - Brandon Sanderson

- Database ID: `6ab65676-663d-41ce-9a46-3a9e91e81e4d`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 379. Tifón - Joseph Conrad

- Database ID: `7aa70e58-bb2f-44d2-b00e-c7184591b0ca`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 380. Time of the Twins - Margaret Weis; Tracy Hickman

- Database ID: `210d1cf2-d970-410c-aa91-3225ce7424e0`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 381. To the Lighthouse - Virginia Woolf

- Database ID: `69a103d8-9f7e-4e86-8e09-1925c0a24dd2`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 382. Todo bajo el Cielo - Matilde Asensi

- Database ID: `92e8eb63-dc62-465f-a2ff-b206023df277`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 383. Tokio año cero - David Peace

- Database ID: `4981b137-efb3-415d-abfc-88f7192847c5`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 384. Tokio blues - Haruki Murakami

- Database ID: `e9a2fe14-13d3-4b88-832b-9e42d0282f3e`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 385. Towers of Midnight - Robert Jordan; Brandon Sanderson

- Database ID: `073496aa-8faf-49c6-a66b-0ded695b938e`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 386. Trafalgar - Benito Pérez Galdós

- Database ID: `77646614-ec18-4466-9da2-571aa792ba91`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 387. Traitor - Matthew Stover

- Database ID: `ebeeaa39-e9be-4b45-835e-1c3a48da0cff`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 388. Tres cantos fúnebres por Kosovo - Ismail Kadare

- Database ID: `8cbd9e78-92fd-4c73-a9bd-b0f4b2ccb147`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 389. Twilight in the Forbidden City - Reginald F. Johnston

- Database ID: `114915af-038c-470e-a1c0-015db7edb602`
- Current populated fields:
  - Themes: Memoir; History; Biography; Travel Writing; Sinology / Asian Studies; Puyi (Last Emperor of China); Qing dynasty; Forbidden City; Beijing; Imperial China; Fall of the Qing; 1911 Revolution; Chinese Republic; Manchu dynasty; Imperial court life; Palace rituals and ceremonies; Eunuchs; Imperial Household Department; Western perspective on China; British colonialism; Tutor-pupil relationship; Political intrigue; Monarchism; Boxer Rebellion; Empress Dowager Cixi; Manchukuo; Japanese influence in China; Early 20th-century China; Eyewitness account; Diplomatic memoir; Sinophilia; Summer Palace; Cultural transition; Film adaptation (The Last Emperor); 1930s non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Memoir` -> Subgenres: `Memoir`
  - Move Themes: `History` -> Subgenres: `History`
  - Move Themes: `Biography` -> Genres: `Biography`
  - Move Themes: `Travel Writing` -> Subgenres: `Travel Writing`
  - Move Themes: `Qing dynasty` -> Historical Periods: `Qing dynasty`
  - Move Themes: `Beijing` -> Settings: `Beijing`
  - Move Themes: `1911 Revolution` -> Historical Periods: `1911 Revolution`
  - Move Themes: `Manchu dynasty` -> Historical Periods: `Manchu dynasty`
  - Move Themes: `British colonialism` -> Subjects: `British colonialism`
  - Move Themes: `Early 20th-century China` -> Historical Periods: `Early 20th-century China`
  - Move Themes: `Diplomatic memoir` -> Subgenres: `Memoir`
  - Remove every moved major genre label from Themes after populating Genres
  - Rebuild the remaining classification fields from individual semicolon-delimited values; the legacy Themes payload mixes semantic levels

#### 390. Ulysses - James Joyce

- Database ID: `511a8dda-d123-46c4-8250-f78ca7bb458e`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 391. Un caso de tres perros - S.J. Bennett

- Database ID: `eb0bdc3f-ca5c-480f-bf74-bdc27e2dd683`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 392. Un crimen entre la realeza - S.J. Bennett

- Database ID: `8baa42fb-fcc3-4bad-bfc6-b415deb2e4c4`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 393. Un gato en el palomar - Agatha Christie

- Database ID: `34f24bf5-b53e-4d19-a482-83e4f1cb8488`
- Current populated fields:
  - Themes: Crime Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Crime Fiction`
  - Move Themes: `Crime Fiction` -> Subgenres: `Crime Fiction`

#### 394. Una flor - Yuriko Miyamoto

- Database ID: `4f0c6ab2-1237-45cb-a9c9-e9efd205bc88`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 395. Una mujer - Annie Ernaux

- Database ID: `93c2b458-4229-4398-995f-8014bdd5de31`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 396. Una tienda en Chicken Hill - James McBride

- Database ID: `e49c43ab-0c89-4e1d-95fc-578e0245fb3f`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 397. Under the Dome - Stephen  King

- Database ID: `92a390d7-eac8-4728-8f8f-016d1bd1808b`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 398. Vector Prime - R.A. Salvatore

- Database ID: `187a5eee-dda4-420a-93b7-8136d6123122`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 399. Veinte mil leguas de viaje submarino - Jules Verne

- Database ID: `a9120c65-da64-4e79-a9eb-1c7c7bff0347`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 400. Veinticuatro horas en la vida de una mujer - Stefan Zweig

- Database ID: `07b381e8-bfc3-4cc0-aa35-0a730fd634e2`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 401. Viaje al pasado - Stefan Zweig

- Database ID: `131347c6-9b62-4582-bbcd-19354e93918c`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 402. Viaje de Egeria - Egeria

- Database ID: `774bc22c-d757-43e4-a7b2-07d5f444d1dd`
- Current populated fields:
  - Themes: Travel Literature
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Travel Literature`
  - Move Themes: `Travel Literature` -> Subgenres: `Travel Writing`

#### 403. Vida líquida - Zygmunt Bauman

- Database ID: `15a9b631-0471-46a1-9c31-bb0e7e0c1ec5`
- Current populated fields:
  - Themes: Philosophy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Non-Fiction` from `Philosophy`
  - Move Themes: `Philosophy` -> Subgenres: `Philosophy`

#### 404. Voces humanas - Penelope Fitzgerald

- Database ID: `f76d060f-4e78-4807-b252-d5c5340765ad`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 405. War of the Twins - Margaret Weis; Tracy Hickman

- Database ID: `4f351cea-facf-4409-9001-d1d8557f0bf5`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 406. Wind and Truth - Brandon Sanderson

- Database ID: `cedac856-2e41-4415-b24b-89156a159a64`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 407. Winter's Heart - Robert Jordan

- Database ID: `36e501b1-b0d4-4841-bf39-8dd3a8aba614`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 408. Words of Radiance - Brandon Sanderson

- Database ID: `455260dc-8a70-4445-b51b-369148f83f2f`
- Current populated fields:
  - Themes: Fantasy
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fantasy` -> Genres: `Fantasy`
  - Remove every moved major genre label from Themes after populating Genres

#### 409. World Without End - Ken Follett

- Database ID: `d0a84247-a21e-4ed4-8f2b-ed371b46f295`
- Current populated fields:
  - Themes: Historical Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Assign major Genre `Fiction` from `Historical Fiction`
  - Move Themes: `Historical Fiction` -> Subgenres: `Historical Fiction`

#### 410. X-Wing: Mercy Kill - Aaron Allston

- Database ID: `11df04e2-5172-4d35-a575-21f4df935208`
- Current populated fields:
  - Themes: Science Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Science Fiction` -> Genres: `Science Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 411. ¡Viven! - Piers Paul Read

- Database ID: `6dc3ee0f-7e6c-43a4-899b-639326285e05`
- Current populated fields:
  - Themes: Non-fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Non-fiction` -> Genres: `Non-Fiction`
  - Remove every moved major genre label from Themes after populating Genres

#### 412. «Lucerna» y «Albert» - Leo Tolstoy

- Database ID: `60b9da1f-c668-4e5d-9e82-b7d471082c23`
- Current populated fields:
  - Themes: Fiction
- Verdict: **Non-compliant until the legacy Themes payload is reclassified**
- Required corrections:
  - Move Themes: `Fiction` -> Genres: `Fiction`
  - Remove every moved major genre label from Themes after populating Genres

## Completion Checklist

- [x] Audit all 719 books in the current database
- [x] Identify the 33 books with at least one current classification value
- [x] Check every populated book against the taxonomy guidelines
- [x] Check exact duplicate placements across categories
- [x] Check interchangeable wording that can prevent Similar Works matches
- [x] Preserve the superseded 412-book pre-clear audit for provenance
- [ ] Apply the current listed corrections only after manual confirmation of the flagged items

The report is a correction plan, not a migration. It intentionally leaves the live database unchanged.
