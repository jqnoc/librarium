# Librarium Taxonomy Guidelines (v2.0)

## Purpose

The purpose of this taxonomy is to classify books consistently, allowing users to discover related works through meaningful browsing and filtering.

Each category answers a different question. Categories should complement one another and **should not duplicate information**.

A value should appear in **one category only**, unless there is a compelling semantic reason for duplication.

---

## 1. Genre

### Purpose

Describes the book's **highest-level classification**.

It answers:

> **"What fundamental kind of work is this?"**

Every book should have **exactly one major Genre**. Genres should be mutually exclusive, intuitive for browsing, and highly reusable.

### Major Genres

- Fantasy
- Fiction
- Science Fiction
- Non-Fiction
- Biography

These major Genres form two broad families:

#### Fictional works

- Fantasy
- Fiction
- Science Fiction

#### Non-fictional works

- Non-Fiction
- Biography

### Major Genre Examples

| Genre | Examples |
| --- | --- |
| Fantasy | *The Lord of the Rings*, *Rhythm of War*, *A Game of Thrones* |
| Fiction | *The Stranger*, *A Little Trickerie*, *Taras Bulba*, *Black Water* |
| Science Fiction | *Rendezvous with Rama*, *Flowers for Algernon*, *Dune* |
| Non-Fiction | *The Myth of Sisyphus*, *Conquest of the Useless*, *Scotland*, *Descripción de China* |
| Biography | *Amerigo*, *Steve Jobs*, *Churchill* |

### Biography as a Major Genre

Strictly speaking, Biography is a subset of Non-Fiction because it is a factual account of a person's life. It is nevertheless promoted to major Genre status because biographies are commonly searched as a distinct category in libraries and bookshops. This makes discovery easier while preserving the factual nature of the work.

### Guidelines

✔ Assign exactly one major Genre to every book.

✔ Use the Genre to identify the fundamental kind of work, not its subject, period, style, or narrative technique.

✘ Do not assign both Fantasy and Fiction, or both Biography and Non-Fiction. The major Genre must be mutually exclusive at the catalogue level.

✘ Do not use History, Philosophy, Memoir, Horror, Literary Fiction, or Historical Fiction as major Genres. These belong in Subgenres or Forms.

✘ Do not include national literatures, academic disciplines, or stylistic labels as major Genres.

---

## 2. Subgenre

### Purpose

Describes the book's **more specific literary, academic or stylistic classification**.

It answers:

> **"What specific kind of book is it?"**

### Examples by Major Genre

#### Fantasy

- Epic Fantasy
- High Fantasy
- Grimdark
- Urban Fantasy
- Sword and Sorcery

#### Fiction

- Historical Fiction
- Literary Fiction
- Gothic Fiction
- Thriller
- Romance
- Horror
- Satirical Fiction
- Adventure Fiction
- Coming-of-Age Fiction

#### Science Fiction

- Hard Science Fiction
- Space Opera
- Dystopian Fiction
- First Contact
- Cyberpunk

#### Non-Fiction

- History
- Philosophy
- Memoir, when it identifies a literary classification rather than only a presentation Form
- Film Studies
- Popular Science
- Travel Writing

#### Biography

- Memoir
- Autobiography
- Collective Biography

### Guidelines

Subgenres include:

- literary movements
- academic disciplines
- national literatures
- publishing traditions
- critical classifications

They refine the major Genre and should never be used as substitutes for it. In particular, Horror, Historical Fiction, Literary Fiction, Gothic Fiction, Adventure Fiction, and Coming-of-Age Fiction are Subgenres rather than major Genres.

Do not normalize apparently synonymous values mechanically. First verify the book's Genre and the semantic role of the value. For example, `Adventure` may be normalized to **Adventure Fiction** only when it is actually functioning as a Fiction Subgenre; an `Adventure` value on a Non-Fiction work must not be converted into Adventure Fiction. Likewise, `Coming-of-Age` may be a Theme rather than a Subgenre.

### Controlled naming: Adventure Fiction

Prefer **Adventure Fiction** over the shorter `Adventure` when the value is a Fiction Subgenre. Adventure Fiction should describe works in which adventure is a defining narrative mode: journeys, exploration, quests, survival, physical danger, unfamiliar environments, or sustained encounters with challenges.

Do not assign Adventure Fiction merely because a work contains travel, action, battles, danger, or one exciting episode. Most importantly, **Adventure Fiction is a fictional literary classification and cannot be used as the Subgenre of a Non-Fiction work**.

Example: *Conquest of the Useless* by Werner Herzog is Non-Fiction. If it has an existing `Adventure` value, that value must not be mechanically changed to Adventure Fiction. It should instead be removed or replaced according to the Non-Fiction taxonomy.

### Controlled naming: Coming-of-Age Fiction

Prefer **Coming-of-Age Fiction** over the shorter `Coming-of-Age` when the value is functioning as a Fiction Subgenre. Use it when the transition from childhood or adolescence toward adulthood is a defining structural or literary characteristic of the work.

Do not assign Coming-of-Age Fiction merely because a character matures, learns lessons, undergoes psychological development, or appears at different ages. The work itself must meaningfully belong to the coming-of-age literary tradition.

`Coming-of-Age` without `Fiction` should generally not be used as a Fiction Subgenre. When it describes maturation as a recurring human experience, it belongs in Themes.

Examples:

- *Northern Lights* → Coming-of-Age Fiction is appropriate.
- *Harry Potter and the Philosopher's Stone* → Coming-of-Age Fiction may be an appropriate secondary Subgenre alongside Fantasy.
- *It* → Coming-of-Age may be a Theme, but it should not automatically become Coming-of-Age Fiction.
- *Rhythm of War* → character development alone is not sufficient reason to classify it as Coming-of-Age Fiction.

Do not use presentation formats such as Essay, Novel, Novella, Short Story, Letters, Dialogue, Interview, Diary, Treatise, or Speech as Subgenres when they belong in Form. A term such as Memoir may remain a Subgenre when it identifies a literary tradition or classification, but it should not be duplicated without a clear reason.

---

## 3. Form

### Purpose

Describes **how the work is written or presented**.

It answers:

> **"What form does the work take?"**

Form is separate from Genre, Subgenre, Themes, and Subjects. Genre identifies the broad kind of work; Form identifies its presentation or compositional mode. For example, an essay can be Non-Fiction with Philosophy as its Subgenre, while a novel can be Science Fiction with Psychological Fiction as its Subgenre.

### Controlled Form values

- Essay
- Epic
- Guide
- Monograph
- Novel
- Novella
- Short Story
- Memoir
- Letters
- Dialogue
- Interview
- Diary
- Treatise
- Speech

### Guidelines

Use the controlled Form values above whenever they fit. Prefer the singular controlled value, such as **Essay**, rather than creating synonyms such as Essays or Personal Essay.

Use **Epic** for extended narrative works rooted in oral or traditional storytelling that were later compiled or written down. This is a Form, not the **Epic Fantasy** Subgenre.

Forms may be combined when a work genuinely uses more than one presentation mode, but do not use Form for a subject, academic discipline, theme, setting, historical period, or literary classification. For example, Film Criticism belongs in Subgenres, while Cinema belongs in Subjects.

### Examples

#### *The Myth of Sisyphus*

- Genre: Non-Fiction
- Form: Essay
- Subgenre: Philosophy; Existentialism

#### *Conquest of the Useless*

- Genre: Non-Fiction
- Form: Diary
- Subgenre: Memoir; Film Diary

#### *Reina del grito*

- Genre: Non-Fiction
- Form: Essay
- Subgenre: Film Criticism; Cultural Criticism

#### *Flowers for Algernon*

- Genre: Science Fiction
- Form: Novel
- Subgenre: Psychological Fiction; Epistolary Novel

---

## 4. Themes

### Purpose

Themes describe the **ideas, lived human experiences, values, emotions, conflicts and philosophical questions** explored by the work.

They answer:

> **"What ideas does the book explore?"**

Themes are **never concrete entities, domains, or topics.**

### Themes should contain

#### Emotions

- Love
- Fear
- Hope
- Grief
- Loneliness

#### Relationships

- Friendship
- Family
- Betrayal
- Parenthood

#### Values

- Justice
- Freedom
- Loyalty
- Honor
- Duty

#### Psychology

- Identity
- Alienation
- Madness
- Memory
- Trauma

#### Philosophy

- Mortality
- Absurdism
- Meaning
- Faith
- Free Will

#### Conflict

- Revenge
- Ambition
- Power
- Survival
- Oppression

### Themes should NOT contain

#### People

❌ Philip II

❌ Amerigo Vespucci

#### Places

❌ Scotland

❌ Tokyo

❌ Peru

#### Disciplines

❌ Cinema

❌ Philosophy

❌ Anthropology

#### Animals

❌ Cats

❌ Sharks

#### Works

❌ Jaws

❌ Rashomon

#### Historical events

❌ World War II

❌ French Revolution

#### Technologies

❌ Artificial Intelligence

#### Objects

❌ Books

❌ Steamships

---

## 5. Setting

### Purpose

Describes **where** the story takes place or **where** the subject of the book is situated.

It answers:

> **"Where does it happen?"**

### Examples

- Tokyo
- Scotland
- Amazon Rainforest
- Seville
- Mars
- Gethen

Settings are geographical.

Do not use historical periods here.

---

## 6. Historical Period

### Purpose

Describes **when** the story or subject takes place.

It answers:

> **"When does it happen?"**

### Examples

- Bronze Age
- Roman Empire
- Middle Ages
- Renaissance
- Meiji Era
- Victorian Era
- Belle Époque
- Spanish Golden Age
- World War II
- Cold War
- Contemporary

Use the most specific historically meaningful period available.

---

## 7. Subject

### Purpose

Subjects describe the **concrete topics** covered by the book.

They answer:

> **"What is the book about?"**

Subjects are **always nouns** representing real entities or recognised concepts.

### Subjects may include

#### People

- Philip II
- Akira Kurosawa
- Matteo Ricci

#### Places

- Scotland
- Cornwall
- Japan

#### Events

- World War II
- Chappaquiddick Incident

#### Disciplines

- Cinema
- Cartography
- Meteorology
- Theology

#### Religions

- Shinto
- Christianity

#### Animals

- Cats
- Sharks

#### Objects

- Books
- Steamships

#### Works

- Jaws
- Fitzcarraldo

#### Institutions

- Catholic Church
- Universal Pictures

#### Movements

- New Hollywood
- Counter-Reformation

#### Species

- Wolves
- Horses

#### Historical topics

- Cossacks
- Dry Docks
- Industrial Heritage

### Subjects should NOT contain

Abstract ideas.

Never include:

❌ Love

❌ Revenge

❌ Identity

❌ Friendship

❌ Hope

❌ Fear

❌ Alienation

❌ Freedom

These belong in Themes.

---

## 8. Audience

### Purpose

Describes the intended readership.

### Examples

- Children
- Middle Grade
- Young Adult
- Adult
- General Readers
- Academic Readers

Audience should never describe quality or difficulty.

---

## Relationship between Themes and Subjects

This is the most important rule in the taxonomy.

## One Important Realization

While doing this audit, an important distinction emerged:

**Themes do not have to be purely philosophical abstractions.** They can also be **human experiences**.

Examples include:

- Aging
- Motherhood
- Womanhood
- Fear
- Trauma
- Desire

These are not concrete entities, but neither are they purely philosophical concepts. They are recurring aspects of the human condition, and they work naturally as Themes.

By contrast:

- Horror Cinema
- Film Criticism
- Gender Studies
- Cinema
- Popular Culture

are clearly **Subjects**, because they are identifiable fields, disciplines, or cultural objects.

The guiding distinction is:

- **Themes** = ideas and lived experiences
- **Subjects** = concrete domains and topics

### Themes

Answer:

> **"What ideas does the book explore?"**

#### Examples

- Identity
- Love
- Revenge
- Fear
- Justice
- Freedom

### Subjects

Answer:

> **"What concrete things is the book about?"**

#### Examples

- Cinema
- Scotland
- Philip II
- Cats
- World War II
- Shinto

### Example

#### *I Am a Cat*

**Themes**

- Identity
- Alienation
- Social Satire
- Modernity

**Subjects**

- Cats
- Animal Narrators
- Meiji Japan
- Japanese Society
- Philosophy

---

#### *Conquest of the Useless*

**Themes**

- Obsession
- Perseverance
- Madness
- Ambition

**Subjects**

- Cinema
- Werner Herzog
- Film Production
- Amazon Rainforest
- Fitzcarraldo

---

#### *Black Water*

**Themes**

- Fear
- Trauma
- Patriarchy
- Mortality

**Subjects**

- Chappaquiddick Incident
- American Politics
- Drowning
- Feminism

---

## General Principles

When assigning a value, ask these questions in order:

### Taxonomy audit rule: validate before normalizing

When auditing existing values, work **book by book**, not by mechanical find-and-replace. Before changing a value, determine:

1. the book's Genre;
2. the category in which the existing value is being used;
3. whether the proposed replacement has the same semantic level;
4. whether the replacement actually describes the work as a whole rather than one plot element.

Examples:

- `Adventure` + Fiction → may become **Adventure Fiction** after review.
- `Adventure` + Non-Fiction → must **not** become Adventure Fiction.
- `Coming-of-Age` + Fiction → review whether it is a Theme or the Subgenre **Coming-of-Age Fiction**.
- A novel containing a journey is not automatically Adventure Fiction.
- A novel containing childhood and adult sections is not automatically Coming-of-Age Fiction.
- A novel containing battles is not automatically Military Fiction.
- A novel containing a crime is not automatically Crime Fiction.

The classification must describe the work as a whole.

### What fundamental kind of work is it?

→ Genre

Assign exactly one major Genre: Fantasy, Fiction, Science Fiction, Non-Fiction, or Biography.

---

### Is it a more specific literary or academic classification?

→ Subgenre

---

### Is it the way the work is written or presented?

→ Form

Use a controlled value such as Essay, Novel, Diary, Interview, or Letters.

---

### Is it an idea or lived human experience?

→ Theme

---

### Is it a place?

→ Setting

---

### Is it a historical era?

→ Historical Period

---

### Is it a concrete person, place, discipline, event, work, religion, species or topic?

→ Subject

---

### Is it about who should read the book?

→ Audience

---

## Consistency Rules

- Use **American English** consistently throughout the taxonomy (e.g. *Modernization*, *Humor*, *Center*).
- Use singular nouns unless a plural is the accepted term (e.g. **Meteorology**, **Cats in Literature**, **World War II**).
- Prefer established historical and academic terms over descriptive phrases.
- Avoid synonyms that duplicate existing controlled vocabulary.
- Prefer explicit controlled Subgenre names such as **Adventure Fiction** and **Coming-of-Age Fiction** over ambiguous shorthand when the literary classification is intended.
- Never perform mechanical synonym replacement without checking Genre and semantic category first.
- Reuse existing values whenever possible instead of creating new ones.
- Every new value should be applicable to more than one book whenever feasible.
- Keep presentation modes in Forms and literary, academic, or critical classifications in Subgenres.
- When in doubt between **Theme** and **Subject**, ask: *Is this an idea, or is it a thing?* If it is an idea, it belongs in **Themes**. If it is a thing, it belongs in **Subjects**.

## Naming Convention for Future Consistency

Avoid mixing semantic levels within a single controlled-vocabulary value. Each value should focus on one concept so that it remains reusable across different books.

Prefer:

- **Memory** instead of **Childhood Memories**
- **Catharsis** or **Art as Catharsis** instead of **Film as Catharsis**
- **Fear** plus **Horror Cinema** instead of a hybrid value such as **Fear and Cinema**

Keeping concepts separate makes the controlled vocabulary easier to maintain, search, and reuse.

## Recommendation for version 2.0

After reviewing the taxonomy we've built together, I would add one overarching principle:

> **Every category should answer a unique question, and no value should need to appear in more than one category.**

This single principle naturally prevents overlap, keeps the taxonomy intuitive for users, and ensures that each field has a clear semantic purpose. I think it should become the guiding philosophy for all future additions to your catalogue.
