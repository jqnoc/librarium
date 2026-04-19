# Librarium Opportunities

This document captures product opportunities discussed for Librarium so they can be reviewed later without committing to implementation now.

It is intentionally product-oriented rather than code-oriented. The goal is to identify where Librarium can become more useful, broader in scope, and stronger in its core workflows.

## Current Product Position

Librarium already does several things unusually well for a personal reading tracker:

- detailed book cataloging with rich metadata
- per-book reading sessions and reading periods
- re-reads
- multi-edition linking
- multi-library support
- authors, series, and acquisition sources
- quotes, thoughts, and words annotations
- yearly and global statistics
- dashboard, calendar, and activity views
- multi-user local setup
- Dropbox-backed sync and backup

That means the app is already strong as a personal reading archive and retrospective analytics tool.

The main product gaps are not around basic cataloging anymore. They are in four areas:

1. planning what to read
2. capturing reading activity faster
3. turning stored data into guidance and decisions
4. making data more portable and reusable

## Main Product Opportunities

### 1. Reading Goals And Reading Plans

This is the clearest missing product layer.

Possible additions:

- yearly goals for books, pages, and reading time
- monthly goals and rolling pace targets
- series completion goals
- re-read goals
- a structured "next up" queue instead of only relying on `not-started`
- dashboard progress widgets and goal trend indicators

Why it matters:

- adds an active loop to the app instead of only reflective tracking
- makes the app useful before a book is started, not only after data is recorded
- fits the existing analytics and dashboard structure very naturally

Expected product impact:

- high

Expected implementation cost:

- low to medium

### 2. Collections, Wishlists, And Queues

Tags exist, but tags are not the same as intention.

Possible additions:

- wishlist
- next-up queue
- buy later list
- revisit soon list
- user-defined collections such as "books about memory" or "2026 shortlist"
- manual ordering inside selected collections

Why it matters:

- expands Librarium from tracker into organizer
- makes TBR management much more deliberate
- reduces the need to overload tags with planning semantics

Expected product impact:

- high

Expected implementation cost:

- low to medium

### 3. Global Annotation Hub / Commonplace Book

Annotations are already one of the strongest and most distinctive parts of Librarium, but they are still mostly book-centered.

Possible additions:

- a global notebook view for all quotes, thoughts, and words
- filters by author, tag, language, source, year, and rating
- full-text search across annotations
- pinned or favorite annotations
- export of selected notes as Markdown, text, or PDF
- a "commonplace book" reading journal built from saved highlights and thoughts

Why it matters:

- turns annotations from attached metadata into a real long-term knowledge system
- increases the value of the existing quotes/thoughts/words model
- differentiates Librarium from more generic reading trackers

Expected product impact:

- very high

Expected implementation cost:

- medium

### 4. Import / Export And Data Portability

Librarium already has useful targeted import helpers like ISBN lookup and Bookly import, but not a broader data portability story.

Possible additions:

- CSV export of books, readings, ratings, and annotations
- JSON export of full library data
- import from Goodreads CSV or StoryGraph exports
- portable full-library backup package for migration
- annotation export to Markdown for external note systems

Why it matters:

- removes lock-in anxiety
- improves onboarding for users migrating from other reading tools
- makes the app more trustworthy and future-proof
- increases compatibility with spreadsheets and outside analysis

Expected product impact:

- very high

Expected implementation cost:

- medium

### 5. Personal Recommendations Based On Existing Library Data

This should not be a generic AI feature. The opportunity is in using the data Librarium already stores.

Possible additions:

- books in your library that best match your highest-rated patterns
- authors you rate highly but still have unread books from
- unfinished series worth resuming
- books most aligned with favorite tags or rating dimensions
- resurfacing abandoned or stalled books that still fit your taste profile

Why it matters:

- turns passive storage into active guidance
- makes the rating system and tags more valuable
- helps solve the "what should I read next?" problem

Expected product impact:

- high

Expected implementation cost:

- medium to high

### 6. Shareable And Printable Reading Reports

The app already has enough analytics to support strong output artifacts.

Possible additions:

- yearly recap report
- printable reading summary PDF
- exportable chart images
- shareable "year in reading" cards
- library summary documents by year, tag, or author

Why it matters:

- makes existing stats more reusable
- increases perceived value of the analytics layer
- lets users turn their reading history into an artifact

Expected product impact:

- medium to high

Expected implementation cost:

- medium

### 7. Sync Model Expansion

Dropbox-first sync is coherent for the current product, but it is also a strategic limitation.

Possible additions:

- optional local-only mode without Dropbox requirement
- alternative sync providers in the future
- better offline-first behavior
- clearer sync state, pending work, and conflict visibility

Why it matters:

- broadens adoption
- reduces dependency on one external service
- improves confidence when using the app across machines

Expected product impact:

- high strategically

Expected implementation cost:

- high

## Best Improvements To Existing Features

### 1. Advanced Search And Saved Filters

The library is already filterable, but serious use cases quickly demand compound queries.

Possible improvements:

- combine multiple criteria at once
- multi-select filters
- better date-based filtering
- saved searches / saved views
- full-text search on titles, summaries, notes, and annotations

Why it matters:

- makes the existing library far more powerful
- improves day-to-day use without changing the core concept
- especially important as the library grows large

Priority:

- very high

### 2. Bulk Actions

The current model appears optimized around one-book-at-a-time workflows.

Possible improvements:

- bulk tag add/remove
- bulk status updates
- bulk move to library
- bulk source assignment
- bulk cleanup for metadata fields

Why it matters:

- reduces maintenance friction significantly
- becomes more important as collection size grows

Priority:

- very high

### 3. Faster Reading Capture

Librarium tracks reading well, but logging still appears mostly manual.

Possible improvements:

- quick-add session modal
- session timer / stopwatch
- recently used values
- keyboard shortcuts for capture
- "log reading now" shortcut from dashboard or book detail

Why it matters:

- improves data quality over time
- reduces user friction in the most repeated task after cataloging

Priority:

- high

### 4. Reminders And Attention Systems

The data model already includes borrowed dates and due dates, but the product does not seem to turn them into action.

Possible improvements:

- borrowed book due reminders
- overdue visibility
- inactive current-read nudges
- reminders for books with no session in X days
- optional desktop notifications for targets reached or deadlines approaching

Why it matters:

- turns stored dates into actionable utility
- makes Librarium useful as a management tool, not only a recorder

Priority:

- high

### 5. Rating Intelligence

The 51-dimension rating model is rich, but users need synthesis from it.

Possible improvements:

- taste profile summaries
- strongest and weakest dimensions over time
- rating patterns by genre, author, language, or format
- comparisons between readings of the same book
- author-level and series-level rating aggregates

Why it matters:

- makes the rating system feel insightful rather than merely exhaustive
- adds value without requiring new raw data

Priority:

- high

### 6. Work-Level And Re-Read Insights

Librarium already supports editions and re-reads, which is a strength few simpler reading trackers have.

Possible improvements:

- compare two readings of the same book
- compare editions of the same work
- show how rating changed across re-reads
- show reading-time differences between editions
- work-level analytics instead of only edition-level analytics where appropriate

Why it matters:

- deepens one of Librarium's more distinctive existing systems
- aligns strongly with serious readers and collectors

Priority:

- medium to high

### 7. Real Settings / Preferences Surface

Preferences currently appear scattered rather than centralized.

Possible improvements:

- default library view
- dashboard widget toggles
- language and formatting defaults
- export defaults
- reminder behavior
- sync and backup preferences
- future feature flags or personalization settings

Why it matters:

- makes the product easier to evolve cleanly
- gives the user more control without cluttering unrelated pages

Priority:

- medium to high

### 8. Sync Transparency And Conflict Handling

Sync is already serious infrastructure, but the product surface can improve.

Possible improvements:

- clearer last sync status
- pending upload/download indicators
- better failure messages
- conflict awareness when data changes across machines
- sync activity log

Why it matters:

- improves trust
- reduces fear around multi-device usage

Priority:

- medium

## Best Low-Effort / High-Value Wins

If the goal is to improve Librarium later without taking on large new systems first, these seem like the highest-value smaller changes:

1. borrowed-book reminders and overdue highlighting
2. saved filters and richer compound library filtering
3. bulk tag and bulk status actions
4. CSV export for books, readings, and annotations
5. quick-add reading session flow
6. a proper settings/preferences page

These all improve real usage frequency and utility without changing the identity of the app.

## Larger Strategic Bets

These are not necessarily the next things to build, but they are the biggest opportunities if Librarium is meant to grow in scope.

### 1. Goals And Reading Planning Layer

Why strategic:

- changes Librarium from retrospective archive into active reading companion

### 2. Commonplace Book / Annotation Workspace

Why strategic:

- gives Librarium a more distinctive long-term knowledge role
- leverages an already strong annotation foundation

### 3. Recommendation Layer

Why strategic:

- turns existing structured data into decisions and discovery

### 4. Strong Import / Export Ecosystem

Why strategic:

- lowers switching cost and increases trust dramatically

### 5. Sync Provider Flexibility

Why strategic:

- expands potential audience and reduces dependence on Dropbox-only operation

## Suggested Directional Priority

If these opportunities are reviewed in the future, a strong order of consideration would be:

1. strengthen the current core workflow
2. add planning features
3. deepen Librarium's unique systems
4. improve portability and output
5. only then consider larger platform-like expansion

Concretely:

### Phase 1: Core workflow improvements

- advanced search and saved filters
- bulk actions
- quick reading capture
- reminders and overdue visibility
- settings page

### Phase 2: Planning layer

- goals
- queues
- wishlists
- collections

### Phase 3: Librarium-specific depth

- global annotation hub
- commonplace book workflows
- rating intelligence
- work / re-read comparison

### Phase 4: Portability and outputs

- CSV / JSON export
- third-party imports
- printable and shareable reports

### Phase 5: Strategic expansion

- personal recommendation layer
- sync flexibility and broader ecosystem thinking

## Three Strongest Opportunities Overall

If only three opportunities are kept in mind for the future, the strongest candidates are:

1. reading goals and planning features
2. a global annotation / commonplace-book system
3. import, export, and data portability

Those three would most expand Librarium's purpose while staying aligned with what the app already does well.
