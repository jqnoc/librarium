# Librarium Taxonomy Duplicate Audit - JqnOC

Generated: 2026-08-07 23:16:45 +02:00
Source database: `C:\Users\Joaquín2\Joaquín Dropbox\JqnOC\Apps\LibrariumApp\jqnoc.db`
Observed database modification time: 2026-08-07 23:03:19 +02:00
Database age when scanned: 13.4 minutes
Database integrity check: `ok`

## Purpose

This is a read-only audit of the classification vocabulary in the requested JqnOC database. Its primary purpose is to find classification values that may describe the same concept but are written differently across books, so they can be reviewed and manually normalized in Librarium.

The report does not modify the database. It records candidate matches, not automatic corrections. A candidate may be a true duplicate, a broader/narrower relationship, or a deliberate distinction that needs a human decision.

## Scope and method

- Scanned all **723** rows in `books`.
- Applied Librarium's effective work-level taxonomy rule: when a book has a matching `work_id` in `work_taxonomy`, the shared work record replaces the book-level taxonomy values for all eight taxonomy fields.
- Included **12** shared work-taxonomy rows and **24** linked-edition book rows that inherit those values.
- Found **448** book rows with at least one effective taxonomy value, representing **436** distinct works or standalone records.
- The raw book columns alone contain classifications for 424 rows; the higher effective count includes inherited work-level classifications.
- Compared values within each taxonomy field using case-folding, accent-insensitive comparison, punctuation and hyphen normalization, singular/plural inspection, word-order inspection, and conservative semantic review.
- Exact normalized variants are marked **High confidence**. Broader synonym, granularity, or wording families are marked **Manual review**.
- Values that are merely related, hierarchical, or distinguishable in meaning are listed under false positives and should not be merged automatically.

### Effective field population

| Field | Book rows with a value | Tokens | Unique values |
| --- | ---: | ---: | ---: |
| Genres | 128 | 128 | 5 |
| Subgenres | 128 | 505 | 192 |
| Forms | 127 | 132 | 19 |
| Themes | 447 | 3,733 | 857 |
| Settings | 109 | 324 | 183 |
| Historical Periods | 108 | 223 | 84 |
| Subjects | 128 | 2,690 | 1,776 |
| Audiences | 124 | 263 | 5 |

The audit found **52 candidate duplicate families**: 5 in Subgenres, 18 in Themes, 6 in Settings, 4 in Historical Periods, and 19 in Subjects. No likely same-field wording family was found in Genres, Forms, or Audiences.

## Priority guidance

1. Normalize the **High confidence** case, punctuation, hyphenation, spelling, singular/plural, or obvious typo variants first.
2. Review the **Manual review** families against the book content before selecting a canonical value. Do not merge a broad term into a narrower one without deciding the intended taxonomy level.
3. For linked editions, edit the shared work classification once when the value is stored in `work_taxonomy`; the change will apply to all editions of that work.
4. Keep each concept in the category that answers the category's question. For example, a place belongs in Settings, an era or event in Historical Periods, and a concrete topic in Subjects.

# Candidate duplicate families

## Subgenres

### 1. `Adventure` / `Adventure Fiction`

**Confidence:** Manual review
**Suggested review:** Prefer the reusable literary label `Adventure Fiction` if both values mean the same subgenre. `Adventure` may be an incomplete shorthand.

- `Adventure`
  - Conquista de lo inútil - Werner Herzog --------> THIS IS NOT FICTION, SO LET'S REMOVE THIS ENTIRELY
- `Adventure Fiction`
  - El albatros negro - María Oruña
  - El círculo de los días - Ken Follett
  - El emblema del traidor - Juan Gómez-Jurado
  - Jurassic Park - Michael Crichton
  - La leyenda del ladrón - Juan Gómez-Jurado
  - Las aventuras de Simbad el marino - René Khawam
  - Moby Dick - Herman Melville
  - Rhythm of War - Brandon Sanderson
  - Shadows of the Empire - Steve Perry
  - Splinter of the Mind's Eye - Alan Dean Foster
  - Taras Bulba - Nikolai Gogol
  - The Lost World - Michael Crichton
  - The Talisman - Stephen King; Peter Straub
  - Veinte mil leguas de viaje submarino - Jules Verne

### 2. `Coming-of-Age` / `Coming-of-Age Fiction`

**Confidence:** Manual review
**Suggested review:** Choose one reusable subgenre convention. The shorter form may be intended as a theme in some records, while the `... Fiction` form is explicitly a literary classification.

- `Coming-of-Age`
  - A Little Trickerie - Rosanna Pike
  - El emblema del traidor - Juan Gómez-Jurado
  - Flowers for Algernon - Daniel Keyes
  - Gods of Jade and Shadow - Silvia Moreno-Garcia
  - It - Stephen King
  - La leyenda del ladrón - Juan Gómez-Jurado
  - Northern Lights - Philip Pullman
  - The Talisman - Stephen King; Peter Straub
  - Tokio blues - Haruki Murakami
- `Coming-of-Age Fiction` ---------------> THIS IS BETTER
  - 22 largos - Caroline Wahl
  - Harry Potter and the Philosopher's Stone - J.K. Rowling
  - Harry Potter y la piedra filosofal - J.K. Rowling
  - La muerte de Vivek Oji - Akwaeke Emezi
  - Rhythm of War - Brandon Sanderson

### 3. `Cinema History` / `Film History`

**Confidence:** High semantic confidence
**Suggested review:** Select one canonical label for the history of cinema/film. The same concept also appears as `History of Cinema` in Subjects; see the cross-category note below.

- `Cinema History`
  - Conversaciones con Akira Kurosawa - Akira Kurosawa
  - Tiburón - Quim Casas; Juan Manuel Corral; Juan Andrés Pedrero Santos
- `Film History` ----------> THIS IS BETTER
  - Conquista de lo inútil - Werner Herzog
  - Tiburón - Quim Casas; Juan Manuel Corral; Juan Andrés Pedrero Santos

### 4. `Modernist Fiction` / `Modernist Literature`

**Confidence:** Manual review
**Suggested review:** These may be intended as the same modernist literary classification. Decide whether the taxonomy distinguishes fiction specifically from literature generally.

- `Modernist Fiction`
  - El castillo - Franz Kafka
  - Rashōmon e outros relatos - Ryūnosuke Akutagawa
- `Modernist Literature` -----------> THIS IS BETTER 
  - País de nieve - Yasunari Kawabata
  - Soy un gato - Natsume Sōseki

### 5. `Media Tie-In` / `Tie-in Fiction`

**Confidence:** Manual review
**Suggested review:** These appear to express the same tie-in classification, but `Media Tie-In` is broader than `Tie-in Fiction`. Select one category label and keep presentation Form separate.

- `Media Tie-In` ----------> THIS IS BETTER
  - Shadows of the Empire - Steve Perry
  - Splinter of the Mind's Eye - Alan Dean Foster
- `Tie-in Fiction`
  - Legacy of Blood - Richard A. Knaak

## Themes

### 6. `Anti-Semitism` / `Antisemitism`

**Confidence:** High confidence
**Suggested review:** Keep `Antisemitism` to follow the current American-English consistency rule.

- `Anti-Semitism`
  - El emblema del traidor - Juan Gómez-Jurado
- `Antisemitism` -----------> THIS IS BETTER
  - Mendel el de los libros - Stefan Zweig
  - Una tienda en Chicken Hill - James McBride

### 7. `Coming of Age` / `Coming-of-Age` / `Coming-of-age`

**Confidence:** High confidence
**Suggested review:** Keep one capitalization and hyphenation convention. Also review whether this belongs in Themes or Subgenres for each book.

- `Coming of Age` -----------> THIS IS BETTER
  - El ojo del mundo - Robert Jordan
  - La leyenda del ladrón - Juan Gómez-Jurado
  - Northern Lights - Philip Pullman
  - The Eye of the World - Robert Jordan
  - The Talisman - Stephen King; Peter Straub
  - Tokio blues - Haruki Murakami
- `Coming-of-Age`
  - La isla del tesoro - Robert Louis Stevenson
- `Coming-of-age`
  - Los libros de Terramar - Ursula K. Le Guin

### 8. `Cultural observation` / `Cultural Observation`

**Confidence:** High confidence
**Suggested review:** Keep one capitalization convention.

- `Cultural observation`
  - Chroniques de Jérusalem - Guy Delisle
- `Cultural Observation` -----------> THIS IS BETTER
  - La mano izquierda de la oscuridad - Ursula K. Le Guin

### 9. `Female protagonist` / `Female Protagonist` / `Female protagonists`

**Confidence:** High confidence
**Suggested review:** Use the singular controlled wording `Female Protagonist` unless the plural is intentionally describing multiple protagonists.

- `Female protagonist`
  - El bosque de los cuatro vientos - María Oruña
  - Hierba - Keum Suk Gendry-Kim
- `Female Protagonist` -----------> THIS IS BETTER
  - Hija de la venganza - Michael McDowell
- `Female protagonists`
  - Los libros de Terramar - Ursula K. Le Guin

### 10. `Good and Evil` / `Good versus Evil` / `Good vs. evil` / `Good vs. Evil`

**Confidence:** High semantic confidence
**Suggested review:** Choose one canonical wording, preferably `Good versus Evil` or another single project-wide convention.

- `Good and Evil`
  - Dracula - Bram Stoker
  - Harry Potter and the Philosopher's Stone - J.K. Rowling
  - Harry Potter y la piedra filosofal - J.K. Rowling
- `Good versus Evil` -----------> THIS IS BETTER
  - El clan - Carmen Mola
  - Good Omens - Terry Pratchett; Neil Gaiman
  - Hija de la venganza - Michael McDowell
  - It - Stephen King
  - Shadows of the Empire - Steve Perry
  - Splinter of the Mind's Eye - Alan Dean Foster
  - The Talisman - Stephen King; Peter Straub
- `Good vs. evil`
  - Dragons of Autumn Twilight - Margaret Weis; Tracy Hickman
  - Dragons of Winter Night - Margaret Weis; Tracy Hickman
  - La isla del tesoro - Robert Louis Stevenson
  - Los libros de Terramar - Ursula K. Le Guin
- `Good vs. Evil`
  - El ojo del mundo - Robert Jordan
  - The Eye of the World - Robert Jordan

### 11. `Human Nature` / `Human nature`

**Confidence:** High confidence
**Suggested review:** Keep one capitalization convention.

- `Human Nature` -----------> THIS IS BETTER
  - A Storm of Swords - George R.R. Martin
  - Conversaciones con Akira Kurosawa - Akira Kurosawa
  - Lord of the Flies - William Golding
  - Rashōmon e outros relatos - Ryūnosuke Akutagawa
  - Soy un gato - Natsume Sōseki
- `Human nature`
  - The Hellbound Heart - Clive Barker

### 12. `Love Triangle` / `Love triangle`

**Confidence:** High confidence
**Suggested review:** Keep one capitalization convention.

- `Love Triangle` -----------> THIS IS BETTER
  - El palacio del agua - Laura Portas
- `Love triangle`
  - The Hellbound Heart - Clive Barker

### 13. `Moral Ambiguity` / `Moral ambiguity`

**Confidence:** High confidence
**Suggested review:** Keep one capitalization convention.

- `Moral Ambiguity` -----------> THIS IS BETTER
  - Agua negra - Joyce Carol Oates
  - El clan - Carmen Mola
  - El extranjero - Albert Camus
  - El tiempo entre costuras - María Dueñas
  - Las madres - Carmen Mola
  - Rashōmon e outros relatos - Ryūnosuke Akutagawa
- `Moral ambiguity`
  - La isla del tesoro - Robert Louis Stevenson

### 14. `Non-fiction` / `Non-Fiction`

**Confidence:** High confidence, with a category warning
**Suggested review:** Normalize capitalization, then decide whether these values belong in Themes at all. `Non-Fiction` is a major Genre in the taxonomy, not normally a Theme.

---------------- THIS SHOULD NOT BE A THEME

- `Non-fiction`
  - Al Polo Norte en avión - Roald Amundsen
  - Brevísima relación de la destruición de las Indias - Bartolomé de las Casas
  - Comercios de Tokio - Mateusz Urbanowicz
  - Cultura japonesa - Federico Lanzaco Salafranca
  - El affaire Arnolfini - Jean-Philippe Postel
  - El fin del «Homo sovieticus» - Svetlana Aleksiévich
  - Hacia la tierra del Zar - Teodoro M. Kalaw
  - Into Thin Air - Jon Krakauer
  - La felicidad de los pececillos - Simon Leys
  - Misceláneas japonesas - Lafcadio Hearn
  - Orient-Express - Mauricio Wiesenthal
  - Pasión de las santas Perpetua y Felicidad - Alejandra de Riquer
  - Peregrinatio - Matilde Asensi
  - Sepulcros estruscos - Nicanor Gómez Villegas
  - The History of England's Cathedrals - Nicholas Orme
  - ¡Viven! - Piers Paul Read
- `Non-Fiction`
  - Chroniques de Jérusalem - Guy Delisle
  - Hierba - Keum Suk Gendry-Kim

### 15. `Outsider perspective` / `Outsider Perspective`

**Confidence:** High confidence
**Suggested review:** Keep one capitalization convention.

- `Outsider perspective`
  - Chroniques de Jérusalem - Guy Delisle
- `Outsider Perspective`
  - La mano izquierda de la oscuridad - Ursula K. Le Guin

### 16. `Political intrigue` / `Political Intrigue`

**Confidence:** High confidence
**Suggested review:** Keep one capitalization convention.

- `Political intrigue`
  - Dragons of Autumn Twilight - Margaret Weis; Tracy Hickman
  - Dragons of Winter Night - Margaret Weis; Tracy Hickman
  - Twilight in the Forbidden City - Reginald F. Johnston
- `Political Intrigue` ----------> THIS IS BETTER
  - El emblema del traidor - Juan Gómez-Jurado
  - La mano izquierda de la oscuridad - Ursula K. Le Guin

### 17. `Tradition and Modernity` / `Tradition versus Modernity`

**Confidence:** High semantic confidence
**Suggested review:** Keep `Tradition and Modernity` as the canonical wording if the intended concept is the relationship or tension between the two.

- `Tradition and Modernity` ---------> THIS IS BETTER
  - Conversaciones con Akira Kurosawa - Akira Kurosawa
  - Scotland: From Prehistory to the Present - Fiona Watson
  - Soy un gato - Natsume Sōseki
- `Tradition versus Modernity`
  - Rhythm of War - Brandon Sanderson

### 18. `Mages and wizardry` / `Mages and wizards`

**Confidence:** Manual review
**Suggested review:** These look like wording variants for the same fantasy concept. Choose either a people-focused label or a practice-focused label, not both interchangeably.

- `Mages and wizardry`
  - Dragons of Winter Night - Margaret Weis; Tracy Hickman
- `Mages and Wizards` -----------> THIS IS BETTER
  - Dragons of Autumn Twilight - Margaret Weis; Tracy Hickman

### 19. `Man versus Nature` / `Nature versus Humanity`

**Confidence:** High semantic confidence
**Suggested review:** Choose one canonical conflict-theme wording. The current values differ only in the human/nature framing.

- `Man versus Nature` -----------> THIS IS BETTER
  - Conquista de lo inútil - Werner Herzog
- `Nature versus Humanity`
  - Tiburón - Quim Casas; Juan Manuel Corral; Juan Andrés Pedrero Santos

### 20. `Multi-generational family saga` / `Multi-Generational Saga`

**Confidence:** Manual review
**Suggested review:** These likely describe the same theme, but the first explicitly includes family and the second may be intended as a literary classification. Confirm before merging.

- `Multi-generational family saga`
  - Sorgo rojo - Mo Yan
- `Multi-Generational Saga` -----------> THIS IS BETTER
  - La dama de La Cartuja - Inma Aguilera

### 21. Class-related family: `Class` / `Class Differences` / `Class Struggle` / `Social Class`

**Confidence:** Manual review; do not blindly merge
**Suggested review:** These are related labels, but they may represent different levels: the social concept, differences between classes, and conflict between classes. Choose a controlled policy and retain narrower concepts only when they add information.

- `Class`
  - Agua negra - Joyce Carol Oates
  - Soy un gato - Natsume Sōseki
- `Class Differences`
  - La dama de La Cartuja - Inma Aguilera
- `Class Struggle`
  - La leyenda del ladrón - Juan Gómez-Jurado
- `Social Class`
  - A Little Trickerie - Rosanna Pike
  - Agnes Grey - Anne Brontë
  - Agua negra - Joyce Carol Oates
  - El palacio del agua - Laura Portas
  - Hija de la venganza - Michael McDowell
  - La dama de La Cartuja - Inma Aguilera
  - La leyenda del ladrón - Juan Gómez-Jurado

### 22. Travel-related labels: `Travel Literature` / `Travel Narrative` / `Travel Writing`

**Confidence:** Manual review; likely category drift rather than exact synonyms
**Suggested review:** The guidelines identify `Travel Writing` as a Subgenre. Decide whether these values should be one canonical Subgenre instead of Themes, and whether the form or presentation of each book warrants a separate Form.

- `Travel Literature`
  - Compostela y su ángel - Gonzalo Torrente Ballester
  - Viaje de Egeria - Egeria
- `Travel Narrative`
  - Chroniques de Jérusalem - Guy Delisle
- `Travel Writing`
  - Twilight in the Forbidden City - Reginald F. Johnston

### 23. `Magic and sorcery` / `Magic and wizardry`

**Confidence:** Manual review
**Suggested review:** These are close fantasy vocabulary variants, but `sorcery` and `wizardry` can be deliberately distinct in a world-specific classification. Confirm the intended level before merging.

- `Magic and sorcery`
  - Dragons of Autumn Twilight - Margaret Weis; Tracy Hickman
  - Dragons of Winter Night - Margaret Weis; Tracy Hickman
- `Magic and wizardry`
  - Los libros de Terramar - Ursula K. Le Guin

## Settings

### 24. `New York` / `New York City`

**Confidence:** Manual review; geographic granularity
**Suggested review:** Keep `New York City` when the book is set in the city. Reserve `New York` for the state or resolve it manually when the source is ambiguous.

- `New York`
  - Flowers for Algernon - Daniel Keyes
  - Hija de la venganza - Michael McDowell
- `New York City`
  - Flowers for Algernon - Daniel Keyes
  - Hija de la venganza - Michael McDowell
  - The Talisman - Stephen King; Peter Straub

### 25. `Mediterranean` / `Mediterranean Sea`

**Confidence:** Manual review
**Suggested review:** These may refer to the same geographical setting, but decide whether the taxonomy distinguishes a broad region from the sea itself.

- `Mediterranean`
  - El extranjero - Albert Camus
- `Mediterranean Sea`
  - Maldita Roma - Santiago Posteguillo
  - Veinte mil leguas de viaje submarino - Jules Verne

### 26. `Far West` / `Western United States`

**Confidence:** Manual review
**Suggested review:** These may be alternate labels for the same American region. `Western United States` is clearer and consistent with the geographic setting rule.

- `Far West`
  - Araña - Jon Bilbao
  - Basilisco - Jon Bilbao
  - Matamonstruos - Jon Bilbao
- `Western United States`
  - The Talisman - Stephen King; Peter Straub

### 27. `Britain` / `Great Britain` / `United Kingdom`

**Confidence:** Manual review; geopolitical granularity
**Suggested review:** Do not automatically merge these. Establish whether the taxonomy distinguishes the island/geographical term, the state, and the modern United Kingdom.

- `Britain`
  - El círculo de los días - Ken Follett
- `Great Britain`
  - Scotland: From Prehistory to the Present - Fiona Watson
- `United Kingdom`
  - El nudo Windsor - S.J. Bennett
  - Harry Potter and the Philosopher's Stone - J.K. Rowling
  - Harry Potter y la piedra filosofal - J.K. Rowling

### 28. `Outer Space` / `Space`

**Confidence:** Manual review
**Suggested review:** These may be broad-setting wording variants. Use one project-wide label if both mean the general extraterrestrial setting; retain a more specific astronomical setting when available.

- `Outer Space`
  - Horizonte de estrellas - Víctor Conde; Guillem Sánchez
  - Tau Zero - Poul Anderson
- `Space`
  - Rendezvous With Rama - Arthur C. Clarke

### 29. `Mondariz` / `Balneario de Mondariz`

**Confidence:** Manual review; same-book specificity
**Suggested review:** Both values occur on the same book and may represent a town versus its spa. Keep both only if the distinction is intentional; otherwise use the more precise place.

- `Mondariz`
  - El palacio del agua - Laura Portas
- `Balneario de Mondariz`
  - El palacio del agua - Laura Portas

## Historical Periods

### 30. `Early Modern` / `Early Modern Period`

**Confidence:** High semantic confidence
**Suggested review:** Choose one canonical period label. `Early Modern` is shorter and already more common.

- `Early Modern`
  - A Short History of Dublin - Pat Boran
  - Cuando los inviernos eran inviernos - Bernd Brunner
  - Descripción de China - Matteo Ricci
  - Felipe II - Manuel Fernández Álvarez
  - La leyenda del ladrón - Juan Gómez-Jurado
  - Scotland: From Prehistory to the Present - Fiona Watson
  - Taras Bulba - Nikolai Gogol
- `Early Modern Period`
  - Dios creó los números - Stephen Hawking
  - Monasterio de Samos - Pedro de la Portilla

### 31. `Medieval` / `Middle Ages`

**Confidence:** High semantic confidence
**Suggested review:** Choose one canonical period name. The guidelines use `Middle Ages` as an example but the database currently uses both.

- `Medieval`
  - A Short History of Dublin - Pat Boran
  - Cuando los inviernos eran inviernos - Bernd Brunner
  - Las aventuras de Simbad el marino - René Khawam
  - Scotland: From Prehistory to the Present - Fiona Watson
- `Middle Ages`
  - Dios creó los números - Stephen Hawking
  - El románico de Cantabria en sus cinco colegiatas - María Eálo de Sá
  - Los pilares de la Tierra - Ken Follett
  - Monasterio de Samos - Pedro de la Portilla
  - Roncesvalles - María Antonia del Burgo

### 32. `Modern` / `Modern Era`

**Confidence:** High wording confidence
**Suggested review:** Normalize `Modern Era` to the chosen canonical term. Separately decide whether broad `Modern` should remain alongside more precise decades or named periods.

- `Modern`
  - A Short History of Dublin - Pat Boran
  - Agua negra - Joyce Carol Oates
  - Cuando los inviernos eran inviernos - Bernd Brunner
  - El dique de carena de Gamazo - Andrés Ortega Piris; Víctor Manuel Moreno Sáiz
  - El emblema del traidor - Juan Gómez-Jurado
  - El extranjero - Albert Camus
  - El palacio del agua - Laura Portas
  - Hija de la venganza - Michael McDowell
  - La dama de La Cartuja - Inma Aguilera
  - Mendel el de los libros - Stefan Zweig
  - Scotland: From Prehistory to the Present - Fiona Watson
- `Modern Era`
  - Dios creó los números - Stephen Hawking

### 33. `Postwar Japan` / `Post-World War II`

**Confidence:** Manual review; related but not always interchangeable
**Suggested review:** These can overlap chronologically, but `Postwar Japan` is Japan-specific while `Post-World War II` is a broader period. Merge only if the intended period meaning is genuinely the same.

- `Postwar Japan`
  - Conversaciones con Akira Kurosawa - Akira Kurosawa
  - Kioto - Yasunari Kawabata
  - La casa de las bellas durmientes - Yasunari Kawabata
  - Tokio blues - Haruki Murakami
- `Post-World War II`
  - Lord of the Flies - William Golding

## Subjects

### 34. `Animal Behavior` / `Animal Behaviour`

**Confidence:** High confidence
**Suggested review:** Keep `Animal Behavior` to follow the project's American-English rule.

- `Animal Behavior`
  - The Lost World - Michael Crichton
- `Animal Behaviour`
  - Sobre la muerte de un perro - Jean Grenier

### 35. `Animal Companions` / `Animal Companionship`

**Confidence:** Manual review
**Suggested review:** These may be related but are not identical: one names animals as companions, the other names the relationship or condition. Confirm the intended subject.

- `Animal Companions`
  - Northern Lights - Philip Pullman
- `Animal Companionship`
  - Sobre la muerte de un perro - Jean Grenier

### 36. `Classic Literature` / `Classical Literature`

**Confidence:** Manual review
**Suggested review:** These are often used interchangeably, but `classic` can mean canonical status while `classical` can refer to a historical tradition. Choose one only if that distinction is not intended.

- `Classic Literature`
  - Rendezvous With Rama - Arthur C. Clarke
- `Classical Literature`
  - Tokio blues - Haruki Murakami

### 37. `Classical Japanese Literature` / `Japanese Classical Literature`

**Confidence:** High semantic confidence
**Suggested review:** Keep one word order, preferably `Classical Japanese Literature`.

- `Classical Japanese Literature`
  - Heike monogatari - Anonymous
- `Japanese Classical Literature`
  - Rashōmon e outros relatos - Ryūnosuke Akutagawa

### 38. `Cinema History` / `Film History` / `History of Cinema`

**Confidence:** High semantic confidence
**Suggested review:** Select one canonical subject label. The same concept also appears in Subgenres as `Cinema History` and `Film History`.

- `Cinema History`
  - Conversaciones con Akira Kurosawa - Akira Kurosawa
- `Film History`
  - Conquista de lo inútil - Werner Herzog
  - Conversaciones con Akira Kurosawa - Akira Kurosawa
  - Tiburón - Quim Casas; Juan Manuel Corral; Juan Andrés Pedrero Santos
- `History of Cinema`
  - Tiburón - Quim Casas; Juan Manuel Corral; Juan Andrés Pedrero Santos

### 39. `Cold Case` / `Cold Cases`

**Confidence:** High confidence
**Suggested review:** Use the singular controlled wording unless the plural is deliberately required.

- `Cold Case`
  - Un caso de tres perros - S.J. Bennett
- `Cold Cases`
  - Los inocentes - María Oruña

### 40. `Family Business` / `Family Businesses`

**Confidence:** High confidence
**Suggested review:** Use one singular/plural convention.

- `Family Business`
  - La fortuna - Michael McDowell
  - Lluvia - Michael McDowell
- `Family Businesses`
  - Los inocentes - María Oruña
  - Una tienda en Chicken Hill - James McBride

### 41. `Frame Narrative` / `Frame Narratives`

**Confidence:** High confidence
**Suggested review:** Use one singular/plural convention.

- `Frame Narrative`
  - Cruces - Alex Landragin
  - Las aventuras de Simbad el marino - René Khawam
  - Mendel el de los libros - Stefan Zweig
- `Frame Narratives`
  - Rashōmon e outros relatos - Ryūnosuke Akutagawa

### 42. `Indigenous Culture` / `Indigenous Cultures`

**Confidence:** High confidence
**Suggested review:** Use one singular/plural convention unless the plural is deliberate.

- `Indigenous Culture`
  - Gods of Jade and Shadow - Silvia Moreno-Garcia
- `Indigenous Cultures`
  - Cruces - Alex Landragin

### 43. `Magic Education` / `Magical Education`

**Confidence:** High semantic confidence
**Suggested review:** Choose one canonical wording.

- `Magic Education`
  - Harry Potter and the Philosopher's Stone - J.K. Rowling
  - Harry Potter y la piedra filosofal - J.K. Rowling
- `Magical Education`
  - Quidditch Through the Ages - Kennilworthy Whisp

### 44. `Mythical Creatures` / `Mythological Creatures`

**Confidence:** Manual review
**Suggested review:** These are close but can differ in scope. Choose one if both mean creatures from mythology rather than using the terms interchangeably.

- `Mythical Creatures`
  - Las aventuras de Simbad el marino - René Khawam
  - The Essex Serpent - Sarah Perry
- `Mythological Creatures`
  - Norse Mythology - Neil Gaiman

### 45. `Post-Apocalyptic Society` / `Post-Apocalyptic Societies`

**Confidence:** High confidence
**Suggested review:** Use one singular/plural convention.

- `Post-Apocalyptic Society`
  - Do Androids Dream of Electric Sheep? - Philip K. Dick
- `Post-Apocalyptic Societies`
  - Mortal Engines - Philip Reeve

### 46. `Royal Household` / `Royal Households`

**Confidence:** High confidence
**Suggested review:** Use one singular/plural convention unless the plural is intentionally comparative.

- `Royal Household`
  - Un caso de tres perros - S.J. Bennett
- `Royal Households`
  - El nudo Windsor - S.J. Bennett

### 47. `Serial Murder` / `Serial Murders`

**Confidence:** High confidence
**Suggested review:** Use one singular/plural convention.

- `Serial Murder`
  - Las madres - Carmen Mola
- `Serial Murders`
  - It - Stephen King

### 48. `Succession Crisis` / `Succession Crises`

**Confidence:** High confidence
**Suggested review:** Use one singular/plural convention.

- `Succession Crisis`
  - Los pilares de la Tierra - Ken Follett
- `Succession Crises`
  - A Storm of Swords - George R.R. Martin
  - The Priory of the Orange Tree - Samantha Shannon

### 49. `Unified Field Theory` / `Unified Field Theories`

**Confidence:** High confidence
**Suggested review:** Use the singular or plural consistently according to whether the subject is the discipline/concept or multiple proposed theories.

- `Unified Field Theory`
  - La teoría del todo - Stephen Hawking
- `Unified Field Theories`
  - El camino a la realidad - Roger Penrose

### 50. `World-Building` / `Worldbuilding`

**Confidence:** High confidence
**Suggested review:** Keep one spelling, preferably `Worldbuilding` or the project's existing preferred form.

- `World-Building`
  - La mano izquierda de la oscuridad - Ursula K. Le Guin
- `Worldbuilding`
  - El ojo del mundo - Robert Jordan
  - Mistborn: Secret History - Brandon Sanderson
  - Oathbringer - Brandon Sanderson
  - The Eye of the World - Robert Jordan
  - The Priory of the Orange Tree - Samantha Shannon

### 51. `Twentieth-CCentury America` / `Twentieth-Century America`

**Confidence:** High confidence; typo
**Suggested review:** Correct `Twentieth-CCentury America` to `Twentieth-Century America`.

- `Twentieth-CCentury America`
  - Lluvia - Michael McDowell
- `Twentieth-Century America`
  - La fortuna - Michael McDowell

### 52. `Violence against Women` / `Violence Against Women`

**Confidence:** High confidence
**Suggested review:** Keep one capitalization convention, preferably title case if that is the project-wide subject style.

- `Violence against Women`
  - El clan - Carmen Mola
  - Las madres - Carmen Mola
- `Violence Against Women`
  - La Nena - Carmen Mola
  - Malaventura - Fernando Navarro
  - Reina del grito - Desirée de Fez

# Important false positives and non-merge cases

The scan deliberately excluded the following as automatic duplicate families. They are similar in spelling or share words, but they represent different concepts, levels, or periods:

- `World War I` and `World War II`: different historical events.
- `9th Century`, `19th Century`, `16th Century`, and `17th Century`: different centuries, not wording variants.
- `Early 16th Century` and `Early 17th Century`: different periods.
- `Late 15th Century`, `Late 16th Century`, and `Late 19th Century`: different periods.
- `20th Century`, `Early 20th Century`, `Mid-20th Century`, and `Late 20th Century`: hierarchical precision levels.
- `Victorian Era` and `Late Victorian Era`: broad period versus narrower period.
- `Roman Republic` and `Late Roman Republic`: broad period versus narrower period.
- `Psychological Fiction` and `Psychological Non-Fiction`: fiction and non-fiction are distinct classifications.
- `Literary Science Fiction` and `Military Science Fiction`: different Science Fiction subgenres.
- `Morality` and `Mortality`: different concepts.
- `Immortality` and `Mortality`: related but not synonymous.
- `Depression` and `Repression`: different psychological concepts.
- `Evolution`, `Revolution`, and `Devolution`: different processes.
- `New York` and `New York City`: potentially ambiguous geographic granularity, requiring review rather than automatic merging.
- `Modern` and `Contemporary`: related broad time labels, but not always interchangeable; use the most specific period supported by the book.
- `Great Britain`, `Britain`, and `United Kingdom`: related geopolitical labels with different possible meanings.
- `Classic Literature` and `Classical Literature`: possible near-duplicates, but the distinction may be intentional, so they remain a manual-review family rather than an automatic merge.
- `Animal Companions` and `Animal Companionship`: related but not identical grammatical concepts.
- `Mythical Creatures` and `Mythological Creatures`: close vocabulary, but scope should be confirmed.
- `Postwar Japan` and `Post-World War II`: related periods with different geographic scope.

# Secondary diagnostic: cross-category collisions

The same normalized value appears in more than one taxonomy field in **256** groups. These are not necessarily phrasing duplicates across books; they are category-placement collisions that may affect browsing and Similar Works. The most important examples include:

| Value or family | Fields involved | Review direction |
| --- | --- | --- |
| `Cinema History` / `Film History` / `History of Cinema` | Subgenres, Subjects | Keep film/cinema history in the chosen academic Subgenre or concrete Subject policy, not both without a reason |
| `Adventure Fiction` | Subgenres, Forms, Themes | Keep it as a Subgenre; remove it from Forms or Themes unless a deliberate local convention exists |
| `Science Fiction` | Genres, Subgenres, Themes, Subjects | Keep the major Genre; remove redundant copies from other fields unless they answer a distinct question |
| `Fiction` | Genre, Form, Themes | Keep `Fiction` as Genre; Forms should use `Novel`, `Novella`, or another presentation mode |
| `Biography` | Genre, Subgenres, Themes, Subjects | Keep the major Genre and review all other placements |
| `Memoir` | Subgenres, Forms, Themes | Keep the presentation Form where applicable; retain a Subgenre only when it has a distinct literary-classification purpose |
| `Non-Fiction` | Genre, Themes | Keep it as Genre, not Theme |
| `New Hollywood` | Historical Periods, Subjects | Treat as a film movement/Subject rather than a historical period unless a period policy explicitly supports it |
| `World War I` / `World War II` | Historical Periods, Subjects, and in one case Themes | Keep events in Historical Periods or Subjects according to the chosen event policy; remove redundant placements |
| Place names such as `Japan`, `Scotland`, `Tokyo`, `Seville`, `Peru`, and `Stonehenge` | Settings and Subjects | Keep geographical locations in Settings; retain a Subject only when the book is concretely about the place and the distinction is intentional |
| `Polish-Lithuanian Commonwealth` | Settings, Historical Periods, Subjects | Decide whether the record is using it as a place, period, or subject; do not keep all three by default |
| `World-Building` / `Worldbuilding` | Themes, Subjects | Treat world-building as a reusable literary/technical Subject or Subgenre policy, not both Theme and Subject by default |

The 256-group collision count is a diagnostic total, not a recommendation to delete 256 values. Many are legitimate overlaps that require a category decision rather than a vocabulary merge.

# Recommended cleanup order

1. Fix the obvious typo and case, punctuation, hyphenation, and singular/plural groups: items 6-17, 34, 36-43, and 45-52.
2. Resolve the shared vocabulary policy for `Adventure Fiction`, `Cinema History`/`Film History`, `Coming-of-Age`, `Early Modern`, `Medieval`, and `Modern`.
3. Decide the geographic granularity policy for `New York`, `Mediterranean`, `Britain`, and `Outer Space`.
4. Review cross-category collisions after the vocabulary is canonicalized, because moving a value between categories can change which apparent duplicates remain.
5. Re-run a duplicate audit after manual edits; do not treat this report as a migration script.

## Audit conclusion

The database contains a small set of straightforward spelling and formatting variants, but the larger consistency problem is vocabulary drift: the same idea is sometimes represented as a different grammatical form, a broader or narrower phrase, a different word order, or a value in the wrong category. The report identifies every candidate family retained by the conservative scan and lists the books carrying each variant. No database values were changed.
