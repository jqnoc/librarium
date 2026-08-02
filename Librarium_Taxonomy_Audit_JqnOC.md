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

- **Category drift:** Themes contain concrete or domain values such as `Architecture`, `Books`, `Diamond Trafficking`, `Religion`, `War`, and `Fear and Cinema`; each requires either movement to Subjects or a deliberate split into independent concepts.
- **Historical-period precision:** `Modern` is often stored alongside a more precise decade or named period; `New Hollywood` is a film movement, not a Historical Period.
- **Similar Works fragmentation:** the same concept is represented by spelling, grammatical, or category-specific variants. The recommended canonical forms are listed below; these are correction candidates, not database writes.

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

## Completion Checklist

- [x] Audit all 719 books in the current database
- [x] Identify the 33 books with at least one current classification value
- [x] Check every populated book against the taxonomy guidelines
- [x] Check exact duplicate placements across categories
- [x] Check interchangeable wording that can prevent Similar Works matches
- [x] Preserve the superseded 412-book pre-clear audit for provenance
- [ ] Apply the current listed corrections only after manual confirmation of the flagged items

The report is a correction plan, not a migration. It intentionally leaves the live database unchanged.
