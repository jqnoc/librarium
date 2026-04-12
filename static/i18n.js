// ═══════════════════════════════════════════════════════════════════════════
// Librarium – Internationalisation (EN / ES)
// ═══════════════════════════════════════════════════════════════════════════
(function () {
    'use strict';

    var STORAGE_KEY = 'librarium_lang';

    // ── Translation dictionaries ────────────────────────────────────────
    var translations = {
        // ── Navigation & global ─────────────────────────────────────────
        'nav.dashboard':    { en: 'Dashboard',    es: 'Panel' },
        'nav.library':      { en: 'Library',      es: 'Biblioteca' },
        'nav.authors':      { en: 'Authors',      es: 'Autores' },
        'nav.series':       { en: 'Series',       es: 'Series' },
        'nav.stats':        { en: 'Stats',        es: 'Estadísticas' },
        'nav.activity':     { en: 'Activity',     es: 'Actividad' },
        'nav.calendar':     { en: 'Calendar',     es: 'Calendario' },
        'nav.sources':      { en: 'Sources',      es: 'Fuentes' },
        'nav.addBook':      { en: '+ Add Book',   es: '+ Añadir Libro' },
        'nav.close':        { en: 'Close Librarium', es: 'Cerrar Librarium' },
        'footer.copy':      { en: 'Librarium',     es: 'Librarium' },

        // ── Library selector / management ───────────────────────────────
        'library.select':        { en: 'Select libraries',      es: 'Seleccionar bibliotecas' },
        'library.allLibraries':  { en: 'All libraries',         es: 'Todas las bibliotecas' },
        'library.manage':        { en: 'Manage libraries',      es: 'Gestionar bibliotecas' },
        'library.manageTitle':   { en: 'Manage Libraries',      es: 'Gestionar Bibliotecas' },
        'library.createNew':     { en: 'Create New Library',    es: 'Crear Nueva Biblioteca' },
        'library.namePlaceholder': { en: 'Library name',        es: 'Nombre de la biblioteca' },
        'library.create':        { en: 'Create',                es: 'Crear' },
        'library.existing':      { en: 'Existing Libraries',    es: 'Bibliotecas Existentes' },
        'library.rename':        { en: 'Rename',                es: 'Renombrar' },
        'library.delete':        { en: 'Delete',                es: 'Eliminar' },
        'library.databasePath':  { en: 'Database Path',          es: 'Ruta de la Base de Datos' },

        // ── Database backup ──────────────────────────────────────────────────────
        'backup.title':          { en: 'Database Backup',        es: 'Copia de Seguridad' },
        'backup.create':         { en: 'Create Backup Now',      es: 'Crear Copia Ahora' },
        'backup.shuttingDown':   { en: 'Backing up & closing\u2026', es: 'Guardando copia y cerrando\u2026' },
        'backup.directory':      { en: 'Backup Directory',       es: 'Directorio de Copias' },
        'backup.dirDefault':     { en: 'Default',                es: 'Por defecto' },
        'backup.saveDir':        { en: 'Save',                   es: 'Guardar' },
        'backup.dirHint':        { en: 'Leave empty to use the default location.', es: 'Dejar vacío para usar la ubicación por defecto.' },

        // ── User management ─────────────────────────────────────────────
        'users.selectUser':      { en: 'Select User',           es: 'Seleccionar Usuario' },
        'users.createUser':      { en: 'Create New User',       es: 'Crear Nuevo Usuario' },
        'users.name':            { en: 'Name',                  es: 'Nombre' },
        'users.namePlaceholder': { en: 'Your name',             es: 'Tu nombre' },
        'users.database':        { en: 'Database',              es: 'Base de Datos' },
        'users.newDatabase':     { en: 'Create new database',   es: 'Crear nueva base de datos' },
        'users.importLegacy':    { en: 'Import existing librarium.db', es: 'Importar librarium.db existente' },
        'users.importFile':      { en: 'Import from file',      es: 'Importar desde archivo' },
        'users.create':          { en: 'Create',                es: 'Crear' },

        // ── Error pages ─────────────────────────────────────────────────
        'error.notFound':        { en: 'Page not found',        es: 'Página no encontrada' },
        'error.notFoundHint':    { en: 'The page you are looking for does not exist or has been moved.', es: 'La página que buscas no existe o ha sido movida.' },
        'error.backHome':        { en: 'Back to library',       es: 'Volver a la biblioteca' },

        // ── Add Book dialog ─────────────────────────────────────────────
        'addBook.title':         { en: 'Add Book',              es: 'Añadir Libro' },
        'addBook.manually':      { en: 'Add Manually',          es: 'Añadir Manualmente' },
        'addBook.fromIsbn':      { en: 'Add From ISBN',         es: 'Añadir Desde ISBN' },
        'addBook.isbnPlaceholder': { en: '978-0-123456-78-9',   es: '978-0-123456-78-9' },
        'addBook.search':        { en: 'Search',                es: 'Buscar' },
        'bookForm.coverFromIsbn': { en: 'Cover from ISBN lookup (will be used if no file is uploaded)', es: 'Portada del ISBN (se usará si no se sube un archivo)' },

        // ── Index page ──────────────────────────────────────────────────
        'index.title':          { en: 'Library',            es: 'Biblioteca' },
        'index.epigraph':       { en: '\u201CDomus sine librario, sicut castrum sine armamentario.\u201D', es: '\u201CDomus sine librario, sicut castrum sine armamentario.\u201D' },
        'index.totalBooks':     { en: 'Total Books',        es: 'Total de Libros' },
        'index.totalPages':     { en: 'Total Pages',        es: 'Total de Páginas' },
        'index.totalTimeRead':  { en: 'Total Time Read',    es: 'Tiempo Total de Lectura' },
        'index.uniqueAuthors':  { en: 'Unique Authors',     es: 'Autores Únicos' },
        'index.finished':       { en: 'Finished',           es: 'Terminados' },
        'index.currentlyReading': { en: 'Currently Reading', es: 'Leyendo' },
        'index.notStarted':    { en: 'Not Started',         es: 'Sin Empezar' },
        'index.booksOwned':    { en: 'Books Owned',         es: 'Libros Propios' },
        'index.view':          { en: 'View:',               es: 'Vista:' },
        'index.filter':        { en: 'Filter:',             es: 'Filtro:' },
        'index.sortBy':        { en: 'Sort by:',            es: 'Ordenar por:' },
        'index.thenBy':        { en: 'then by:',            es: 'y luego:' },
        'index.filterAll':     { en: 'All',                 es: 'Todos' },
        'index.filterReading': { en: 'Reading',             es: 'Leyendo' },
        'index.filterFinished':{ en: 'Finished',            es: 'Terminados' },
        'index.filterNotStarted':{ en: 'Not Started',       es: 'Sin Empezar' },
        'index.filterAbandoned':{ en: 'Abandoned',          es: 'Abandonados' },
        'index.filterDraft':    { en: 'Draft',              es: 'Borradores' },
        'index.filteringByTag': { en: 'Filtering by tag:',  es: 'Filtrando por etiqueta:' },
        'index.clearTagFilter': { en: '✕ Clear',            es: '✕ Quitar' },
        'index.sortAlpha':     { en: 'Alphabetically',      es: 'Alfabéticamente' },
        'index.sortAuthor':    { en: 'Author',              es: 'Autor' },
        'index.sortLastSession':{ en: 'Last Reading Session/Period', es: 'Última Sesión/Periodo' },
        'index.sortRating':    { en: 'Rating',              es: 'Valoración' },
        'index.sortStatus':    { en: 'Status',              es: 'Estado' },
        'index.sortTimeRead':  { en: 'Time Read',           es: 'Tiempo Leído' },
        'index.sortNone':      { en: '— None —',            es: '— Ninguno —' },
        'index.columns':       { en: 'Columns:',            es: 'Columnas:' },
        'index.colCover':      { en: 'Cover',               es: 'Portada' },
        'index.colTitle':      { en: 'Title',               es: 'Título' },
        'index.colAuthor':     { en: 'Author',              es: 'Autor' },
        'index.colStatus':     { en: 'Status',              es: 'Estado' },
        'index.colStartDate':  { en: 'Start Date',          es: 'Fecha de Inicio' },
        'index.colLatestDate': { en: 'Latest Date',         es: 'Última Fecha' },
        'index.colTimeRead':   { en: 'Time Read',           es: 'Tiempo Leído' },
        'index.colPubDate':    { en: 'Publication Date',    es: 'Fecha de Publicación' },
        'index.colPublisher':  { en: 'Publisher',           es: 'Editorial' },
        'index.colRating':     { en: 'Rating',              es: 'Valoración' },
        'index.colPages':      { en: 'Pages',               es: 'Páginas' },
        'index.colLanguage':   { en: 'Language',            es: 'Idioma' },
        'index.emptyLibrary':  { en: 'Your library is empty. Add your first book to get started!', es: '¡Tu biblioteca está vacía. Añade tu primer libro para empezar!' },
        'index.noBooks':       { en: 'Show All Books',      es: 'Mostrar Todos' },
        'index.btnCardView':   { en: 'Card view',           es: 'Vista tarjeta' },
        'index.btnCoverView':  { en: 'Cover view',          es: 'Vista portada' },
        'index.btnListView':   { en: 'List view',           es: 'Vista lista' },
        'index.showAllEditions': { en: 'Show All Editions',  es: 'Mostrar Todas las Ediciones' },
        'index.showAllReadings': { en: 'Show All Readings',  es: 'Mostrar Todas las Lecturas' },
        'index.searchPlaceholder': { en: 'Search...',        es: 'Buscar...' },

        // ── Book detail ─────────────────────────────────────────────────
        'book.backToLibrary':   { en: '← Back to Library',   es: '← Volver a la Biblioteca' },
        'book.author':          { en: 'Author',              es: 'Autor' },
        'book.authors':         { en: 'Authors',             es: 'Autores' },
        'book.status':          { en: 'Status',              es: 'Estado' },
        'book.pages':           { en: 'Pages',               es: 'Páginas' },
        'book.tags':            { en: 'Tags',                es: 'Etiquetas' },
        'book.tagsSection':     { en: 'Tags',                es: 'Etiquetas' },
        'book.language':        { en: 'Language',             es: 'Idioma' },
        'book.publisher':       { en: 'Publisher',            es: 'Editorial' },
        'book.pubDate':         { en: 'Publication Date',     es: 'Fecha de Publicación' },
        'book.isbn':            { en: 'ISBN',                 es: 'ISBN' },
        'book.format':          { en: 'Format',              es: 'Formato' },
        'book.formatPaper':     { en: 'Paper Book',          es: 'Libro Físico' },
        'book.formatAudiobook': { en: 'Audiobook',           es: 'Audiolibro' },
        'book.formatEbook':     { en: 'Ebook',               es: 'Ebook' },
        'book.binding':         { en: 'Binding',             es: 'Encuadernación' },
        'book.bindingPaperback':{ en: 'Paperback',           es: 'Tapa Blanda' },
        'book.bindingHardcover':{ en: 'Hardcover',           es: 'Tapa Dura' },
        'book.bindingManga':    { en: 'Manga',               es: 'Manga' },
        'book.audioFormat':     { en: 'Audio Format',        es: 'Formato de Audio' },
        'book.audioDigitalFile':{ en: 'Digital File',        es: 'Archivo Digital' },
        'book.audioCd':         { en: 'CD',                  es: 'CD' },
        'book.audioStreaming':  { en: 'Streaming',           es: 'Streaming' },
        'book.originalTitle':   { en: 'Original Title',      es: 'Título Original' },
        'book.originalLang':    { en: 'Original Language',    es: 'Idioma Original' },
        'book.originalDate':    { en: 'Original Date',        es: 'Fecha Original' },
        'book.series':          { en: 'Series',               es: 'Serie' },
        'book.translator':      { en: 'Translator',          es: 'Traductor' },
        'book.translators':     { en: 'Translators',         es: 'Traductores' },
        'book.illustrator':     { en: 'Illustrator',         es: 'Ilustrador' },
        'book.illustrators':    { en: 'Illustrators',        es: 'Ilustradores' },
        'book.editor':          { en: 'Editor',              es: 'Editor' },
        'book.editors':         { en: 'Editors',             es: 'Editores' },
        'book.prologueAuthor':  { en: 'Prologue Author',    es: 'Autor del Prólogo' },
        'book.prologueAuthors': { en: 'Prologue Authors',   es: 'Autores del Prólogo' },
        'book.source':          { en: 'Source',              es: 'Fuente' },
        'book.owned':           { en: 'Owned',               es: 'Propio' },
        'book.borrowed':        { en: 'Borrowed',            es: 'Prestado' },
        'book.gift':            { en: 'Gift 🎁',             es: 'Regalo 🎁' },
        'book.purchasePlace':   { en: 'Purchase Place',      es: 'Lugar de Compra' },
        'book.giftFrom':        { en: 'Gift From',           es: 'Regalo de' },
        'book.purchaseDate':    { en: 'Purchase Date',       es: 'Fecha de Compra' },
        'book.dateReceived':    { en: 'Date Received',       es: 'Fecha de Recepción' },
        'book.price':           { en: 'Price',               es: 'Precio' },
        'book.originalOwner':   { en: 'Original Owner',      es: 'Dueño Original' },
        'book.borrowedFrom':    { en: 'Borrowed From',       es: 'Prestado Desde' },
        'book.returnedOn':      { en: 'Returned On',         es: 'Devuelto el' },
        'book.editMetadata':    { en: '✏️ Edit Metadata',    es: '✏️ Editar Metadatos' },
        'book.exportCover':     { en: '⬇ Export Cover',      es: '⬇ Exportar Portada' },
        'book.startReRead':     { en: '🔄 Start Re-Read',    es: '🔄 Iniciar Relectura' },
        'book.deleteBook':      { en: '🗑️ Delete Book',     es: '🗑️ Eliminar Libro' },
        'book.editions':        { en: 'Editions',            es: 'Ediciones' },
        'book.editionsTotalReadings': { en: 'Total readings across all editions:', es: 'Total de lecturas en todas las ediciones:' },
        'book.currentEdition':  { en: 'Current',             es: 'Actual' },
        'book.primaryEdition':  { en: 'Primary',             es: 'Principal' },
        'book.setPrimary':      { en: 'Set Primary',         es: 'Hacer Principal' },
        'book.unlinkEdition':   { en: 'Unlink',              es: 'Desvincular' },
        'book.addNewEdition':   { en: '📗 Add New Edition',  es: '📗 Añadir Nueva Edición' },
        'book.linkExistingEdition': { en: '🔗 Link Existing Book as Edition', es: '🔗 Vincular Libro Existente como Edición' },
        'book.linkEditionTitle':{ en: 'Link Existing Book as Edition', es: 'Vincular Libro Existente como Edición' },
        'book.selectBookToLink':{ en: 'Select a book to link:', es: 'Selecciona un libro para vincular:' },
        'book.linkBtn':         { en: 'Link',                es: 'Vincular' },
        'index.editionsBadge':  { en: 'editions',            es: 'ediciones' },
        'book.readable':        { en: 'readable',            es: 'legibles' },
        'book.rating':          { en: 'Rating',              es: 'Valoración' },
        'book.saveRatings':     { en: '💾 Save Ratings',     es: '💾 Guardar Valoraciones' },
        'book.readings':        { en: 'Readings',            es: 'Lecturas' },
        'book.readingStats':    { en: 'Reading Stats',       es: 'Estadísticas de Lectura' },
        'book.dateStarted':     { en: 'Date Started',        es: 'Fecha de Inicio' },
        'book.dateFinished':    { en: 'Date Finished',       es: 'Fecha de Fin' },
        'book.readingDays':     { en: 'Reading Days',        es: 'Días de Lectura' },
        'book.pagesRead':       { en: 'Pages Read',          es: 'Páginas Leídas' },
        'book.totalTime':       { en: 'Total Time',          es: 'Tiempo Total' },
        'book.avgPagesDay':     { en: 'Avg Pages/Day',       es: 'Prom. Páginas/Día' },
        'book.mostPagesDay':    { en: 'Most Pages/Day',      es: 'Máx. Páginas/Día' },
        'book.mostTimeDay':     { en: 'Most Time/Day',       es: 'Máx. Tiempo/Día' },
        'book.avgPagesHour':    { en: 'Avg Pages/Hour',      es: 'Prom. Páginas/Hora' },
        'book.progress':        { en: 'Progress',            es: 'Progreso' },
        'book.pagesRemaining':  { en: 'Pages Remaining',     es: 'Páginas Restantes' },
        'book.estFinish':       { en: 'Est. Time to Finish', es: 'Tiempo Est. para Terminar' },
        'book.readingProgress': { en: 'Reading Progress',    es: 'Progreso de Lectura' },
        'book.cumulative':      { en: 'Cumulative',          es: 'Acumulado' },
        'book.perDay':          { en: 'Per Day',             es: 'Por Día' },
        'book.chartPages':      { en: 'Pages',               es: 'Páginas' },
        'book.chartTime':       { en: 'Time',                es: 'Tiempo' },
        'book.hideIdleDays':    { en: 'Hide idle days',      es: 'Ocultar días inactivos' },
        'book.readingTimeline': { en: 'Reading Timeline',    es: 'Línea Temporal de Lectura' },
        'book.sessions':        { en: 'Reading Sessions',    es: 'Sesiones de Lectura' },
        'book.allReadings':     { en: '(all readings)',      es: '(todas las lecturas)' },
        'book.colNum':          { en: '#',                   es: '#' },
        'book.colReading':      { en: 'Reading',             es: 'Lectura' },
        'book.colDate':         { en: 'Date',                es: 'Fecha' },
        'book.colPages':        { en: 'Pages',               es: 'Páginas' },
        'book.colProgress':     { en: 'Progress',            es: 'Progreso' },
        'book.colDuration':     { en: 'Duration',            es: 'Duración' },
        'book.colActions':      { en: 'Actions',             es: 'Acciones' },
        'book.addSession':      { en: 'Add New Session',     es: 'Añadir Nueva Sesión' },
        'book.noSessions':      { en: 'No reading sessions yet.', es: 'Aún no hay sesiones de lectura.' },
        'book.periods':         { en: 'Reading Periods',     es: 'Periodos de Lectura' },
        'book.periodsDesc':     { en: 'Date ranges when you read this book without detailed session tracking. Reading time is inferred from your tracked sessions\' average speed.', es: 'Rangos de fechas en los que leíste este libro sin seguimiento detallado. El tiempo se estima a partir de la velocidad promedio de tus sesiones.' },
        'book.noPeriods':       { en: 'No reading periods yet.', es: 'Aún no hay periodos de lectura.' },
        'book.addPeriod':       { en: 'Add Reading Period',  es: 'Añadir Periodo de Lectura' },
        'book.colStartDate':    { en: 'Start Date',          es: 'Fecha Inicio' },
        'book.colEndDate':      { en: 'End Date',            es: 'Fecha Fin' },
        'book.colNote':         { en: 'Note',                es: 'Nota' },
        'book.deleteTitle':     { en: 'Delete Book',         es: 'Eliminar Libro' },
        'book.deleteConfirm':   { en: 'Are you sure you want to delete',  es: '¿Estás seguro de que quieres eliminar' },
        'book.deleteWarn':      { en: '? This will remove all data and cannot be undone.', es: '? Esto eliminará todos los datos y no se puede deshacer.' },
        'book.yesDelete':       { en: 'Yes, Delete',         es: 'Sí, Eliminar' },
        'book.started':         { en: 'Started:',            es: 'Iniciado:' },
        'book.finishedLabel':   { en: 'Finished:',           es: 'Terminado:' },
        'book.addSessionBtn':   { en: '+ Add Session',       es: '+ Añadir Sesión' },
        'book.addPeriodBtn':    { en: '+ Add Reading Period', es: '+ Añadir Periodo' },

        // form labels inside session/period editors
        'form.date':     { en: 'Date',     es: 'Fecha' },
        'form.pages':    { en: 'Pages',    es: 'Páginas' },
        'form.progressPct': { en: 'Progress (%)', es: 'Progreso (%)' },
        'form.hours':    { en: 'Hours',    es: 'Horas' },
        'form.minutes':  { en: 'Minutes',  es: 'Minutos' },
        'form.min':      { en: 'Min',      es: 'Min' },
        'form.seconds':  { en: 'Seconds',  es: 'Segundos' },
        'form.sec':      { en: 'Sec',      es: 'Seg' },
        'form.start':    { en: 'Start',    es: 'Inicio' },
        'form.end':      { en: 'End',      es: 'Fin' },
        'form.note':     { en: 'Note',     es: 'Nota' },
        'form.save':     { en: 'Save',     es: 'Guardar' },
        'form.cancel':   { en: 'Cancel',   es: 'Cancelar' },

        // ── Authors page ────────────────────────────────────────────────
        'authors.title':     { en: 'Authors',       es: 'Autores' },
        'authors.sortBy':    { en: 'Sort by:',      es: 'Ordenar por:' },
        'authors.sortName':  { en: 'Name',          es: 'Nombre' },
        'authors.sortBooks': { en: 'Number of Books', es: 'Número de Libros' },
        'authors.empty':     { en: 'No authors found. Add some books to your library first.', es: 'No se encontraron autores. Añade libros a tu biblioteca primero.' },

        // ── Series page ────────────────────────────────────────────────────────
        'series.title':        { en: 'Series',          es: 'Series' },
        'series.view':         { en: 'View:',           es: 'Vista:' },
        'series.cardView':     { en: 'Card view',       es: 'Vista tarjeta' },
        'series.listView':     { en: 'List view',       es: 'Vista lista' },
        'series.sortBy':       { en: 'Sort by:',        es: 'Ordenar por:' },
        'series.sortName':     { en: 'Name',            es: 'Nombre' },
        'series.sortBooks':    { en: 'Number of Books', es: 'Número de Libros' },
        'series.colName':      { en: 'Name',            es: 'Nombre' },
        'series.colBooks':     { en: 'Books',           es: 'Libros' },
        'series.empty':        { en: 'No series found. You can assign books to a series when adding or editing a book.', es: 'No se encontraron series. Puedes asignar libros a una serie al añadir o editar un libro.' },
        'series.backToSeries': { en: '← Back to Series', es: '← Volver a Series' },
        'series.rename':       { en: 'Rename',          es: 'Renombrar' },
        'series.delete':       { en: 'Delete Series',   es: 'Eliminar Serie' },
        'series.noBooks':      { en: 'No books in this series yet.', es: 'Aún no hay libros en esta serie.' },

        // ── Author detail ───────────────────────────────────────────────
        'authorDetail.backToAuthors': { en: '← Back to Authors',  es: '← Volver a Autores' },
        'authorDetail.born':          { en: 'Born',               es: 'Nacimiento' },
        'authorDetail.birthplace':    { en: 'Birthplace',         es: 'Lugar de Nacimiento' },
        'authorDetail.died':          { en: 'Died',               es: 'Fallecimiento' },
        'authorDetail.deathPlace':    { en: 'Place of Death',     es: 'Lugar de Fallecimiento' },
        'authorDetail.booksInLibrary':{ en: 'Books in Library',   es: 'Libros en la Biblioteca' },
        'authorDetail.editDetails':   { en: '✏️ Edit Author Details', es: '✏️ Editar Detalles del Autor' },
        'authorDetail.books':         { en: 'Books',              es: 'Libros' },
        'authorDetail.sortBy':        { en: 'Sort by:',           es: 'Ordenar por:' },
        'authorDetail.sortDate':      { en: 'Original Publication Date', es: 'Fecha de Publicación Original' },
        'authorDetail.sortTitle':     { en: 'Title',              es: 'Título' },
        'authorDetail.sortRating':    { en: 'Rating',             es: 'Valoración' },
        'authorDetail.showAllEditions': { en: 'Show All Editions', es: 'Mostrar Todas las Ediciones' },
        'authorDetail.gender':        { en: 'Gender',              es: 'Género' },
        'authorDetail.empty':         { en: 'No books found for this author.', es: 'No se encontraron libros de este autor.' },
        'authorDetail.quotes':        { en: 'Quotes',              es: 'Citas' },

        // ── Edit author ─────────────────────────────────────────────────
        'editAuthor.backToAuthor':  { en: '← Back to Author',     es: '← Volver al Autor' },
        'editAuthor.title':         { en: 'Edit Author Details',  es: 'Editar Detalles del Autor' },
        'editAuthor.photo':         { en: 'Photo',                es: 'Foto' },
        'editAuthor.removePhoto':   { en: 'Remove current photo', es: 'Eliminar foto actual' },
        'editAuthor.replacePhoto':  { en: 'Replace Photo',        es: 'Reemplazar Foto' },
        'editAuthor.uploadPhoto':   { en: 'Upload Photo',         es: 'Subir Foto' },
        'editAuthor.lifeDetails':   { en: 'Life Details',         es: 'Datos Biográficos' },
        'editAuthor.born':          { en: 'Born',                 es: 'Nacimiento' },
        'editAuthor.birthplace':    { en: 'Birthplace',           es: 'Lugar de Nacimiento' },
        'editAuthor.died':          { en: 'Died',                 es: 'Fallecimiento' },
        'editAuthor.deathPlace':    { en: 'Place of Death',       es: 'Lugar de Fallecimiento' },
        'editAuthor.biography':     { en: 'Biography',            es: 'Biografía' },
        'editAuthor.saveChanges':   { en: '💾 Save Changes',      es: '💾 Guardar Cambios' },
        'editAuthor.gender':        { en: 'Gender',               es: 'Género' },

        // ── Rich-text toolbar ───────────────────────────────────────────
        'rt.bold':          { en: 'Bold',           es: 'Negrita' },
        'rt.italic':        { en: 'Italic',         es: 'Cursiva' },
        'rt.underline':     { en: 'Underline',      es: 'Subrayado' },
        'rt.strike':        { en: 'Strikethrough',  es: 'Tachado' },
        'rt.heading':       { en: 'Heading',        es: 'Encabezado' },
        'rt.ul':            { en: 'Bulleted list',  es: 'Lista con viñetas' },
        'rt.ol':            { en: 'Numbered list',  es: 'Lista numerada' },
        'rt.link':          { en: 'Insert link',    es: 'Insertar enlace' },
        'rt.clear':         { en: 'Clear formatting', es: 'Limpiar formato' },

        // ── New book & Edit metadata (shared) ───────────────────────────
        'bookForm.backToLibrary':   { en: '← Back to Library',   es: '← Volver a la Biblioteca' },
        'bookForm.backToBook':      { en: '← Back to Book',      es: '← Volver al Libro' },
        'bookForm.addNewBook':      { en: 'Add New Book',        es: 'Añadir Nuevo Libro' },
        'bookForm.editMetadata':    { en: 'Edit Metadata',       es: 'Editar Metadatos' },
        'bookForm.basicInfo':       { en: 'Basic Information',   es: 'Información Básica' },
        'bookForm.title':           { en: 'Title',               es: 'Título' },
        'bookForm.titleReq':        { en: 'Title *',             es: 'Título *' },
        'bookForm.subtitle':        { en: 'Subtitle',            es: 'Subtítulo' },
        'bookForm.authorReq':       { en: 'Author(s) *',        es: 'Autor(es) *' },
        'bookForm.authorLabel':     { en: 'Author(s)',           es: 'Autor(es)' },
        'bookForm.tags':            { en: 'Tags',                es: 'Etiquetas' },
        'bookForm.tagsPlaceholder': { en: 'e.g. cozy; dark; slow-burn', es: 'ej. acogedor; oscuro; lento' },
        'bookForm.status':          { en: 'Status',              es: 'Estado' },
        'bookForm.statusReading':   { en: 'Reading',             es: 'Leyendo' },
        'bookForm.statusFinished':  { en: 'Finished',            es: 'Terminado' },
        'bookForm.statusNotStarted':{ en: 'Not Started',         es: 'Sin Empezar' },
        'bookForm.statusAbandoned': { en: 'Abandoned',           es: 'Abandonado' },
        'bookForm.statusDraft':     { en: 'Draft',               es: 'Borrador' },
        'bookForm.pages':           { en: 'Pages',               es: 'Páginas' },
        'bookForm.frontmatter':     { en: 'Frontmatter Pages',   es: 'Páginas Preliminares' },
        'bookForm.language':        { en: 'Language',             es: 'Idioma' },
        'bookForm.library':         { en: 'Library',              es: 'Biblioteca' },
        'bookForm.pubDetails':      { en: 'Publication Details', es: 'Detalles de Publicación' },
        'bookForm.format':          { en: 'Format',             es: 'Formato' },
        'bookForm.formatPaper':     { en: 'Paper Book',         es: 'Libro Físico' },
        'bookForm.formatAudiobook': { en: 'Audiobook',          es: 'Audiolibro' },
        'bookForm.formatEbook':     { en: 'Ebook',              es: 'Ebook' },
        'bookForm.binding':         { en: 'Binding',            es: 'Encuadernación' },
        'bookForm.bindingPaperback':{ en: 'Paperback',          es: 'Tapa Blanda' },
        'bookForm.bindingHardcover':{ en: 'Hardcover',          es: 'Tapa Dura' },
        'bookForm.bindingManga':    { en: 'Manga',              es: 'Manga' },
        'bookForm.audioFormat':     { en: 'Audio Format',       es: 'Formato de Audio' },
        'bookForm.audioDigitalFile':{ en: 'Digital File',       es: 'Archivo Digital' },
        'bookForm.audioCd':         { en: 'CD',                 es: 'CD' },
        'bookForm.audioStreaming':  { en: 'Streaming',          es: 'Streaming' },
        'bookForm.totalTime':       { en: 'Total Time',         es: 'Duración Total' },
        'bookForm.totalTimeHours':  { en: 'Hours',              es: 'Horas' },
        'bookForm.totalTimeMin':    { en: 'Min',                es: 'Min' },
        'bookForm.totalTimeSec':    { en: 'Sec',                es: 'Seg' },
        'bookForm.publisher':       { en: 'Publisher',           es: 'Editorial' },
        'bookForm.pubDate':         { en: 'Publication Date',    es: 'Fecha de Publicación' },
        'bookForm.isbn':            { en: 'ISBN',                es: 'ISBN' },
        'bookForm.coverImage':      { en: 'Cover Image',        es: 'Imagen de Portada' },
        'bookForm.ganttColour':     { en: 'Gantt bar colour:',   es: 'Color de barra Gantt:' },
        'bookForm.originalWork':    { en: 'Original Work',       es: 'Obra Original' },
        'bookForm.origTitle':       { en: 'Original Title',      es: 'Título Original' },
        'bookForm.origLang':        { en: 'Original Language',   es: 'Idioma Original' },
        'bookForm.origPubDate':     { en: 'Original Publication Date', es: 'Fecha de Publicación Original' },
        'bookForm.contributors':    { en: 'Contributors',        es: 'Colaboradores' },
        'bookForm.translator':      { en: 'Translator(s)',       es: 'Traductor(es)' },
        'bookForm.illustrator':     { en: 'Illustrator(s)',      es: 'Ilustrador(es)' },
        'bookForm.editor':          { en: 'Editor(s)',           es: 'Editor(es)' },
        'bookForm.prologueAuthor':  { en: 'Prologue Author(s)',  es: 'Autor(es) del Prólogo' },
        'bookForm.summary':         { en: 'Summary',             es: 'Resumen' },
        'bookForm.bookSource':      { en: 'Book Source',         es: 'Fuente del Libro' },
        'bookForm.notSet':          { en: 'Not set',             es: 'Sin definir' },
        'bookForm.owned':           { en: 'Owned',               es: 'Propio' },
        'bookForm.borrowed':        { en: 'Borrowed',            es: 'Prestado' },
        'bookForm.receivedAsGift':  { en: '🎁 Received as gift', es: '🎁 Recibido como regalo' },
        'bookForm.purchaseDate':    { en: 'Purchase Date',       es: 'Fecha de Compra' },
        'bookForm.dateReceived':    { en: 'Date Received',       es: 'Fecha de Recepción' },
        'bookForm.purchasePlace':   { en: 'Purchase Place',      es: 'Lugar de Compra' },
        'bookForm.giftFrom':        { en: 'Gift From',           es: 'Regalo de' },
        'bookForm.selectSource':    { en: '— Select —',          es: '— Seleccionar —' },
        'bookForm.price':           { en: 'Price',               es: 'Precio' },
        'bookForm.origOwner':       { en: 'Original Owner',      es: 'Dueño Original' },
        'bookForm.borrowedFrom':    { en: 'Borrowed From',       es: 'Prestado Desde' },
        'bookForm.returnedOn':      { en: 'Returned On',         es: 'Devuelto el' },
        'bookForm.addBookBtn':      { en: '📚 Add Book',         es: '📚 Añadir Libro' },
        'bookForm.addingEditionOf': { en: 'Adding new edition of:', es: 'Añadiendo nueva edición de:' },
        'bookForm.editionHint':     { en: 'Work-level fields (author, original work info, tags) are pre-filled. Edition-level fields (language, publisher, pages, cover) are for this specific edition.', es: 'Los campos a nivel de obra (autor, información original, etiquetas) están pre-rellenados. Los campos a nivel de edición (idioma, editorial, páginas, portada) son para esta edición específica.' },
        'bookForm.saveChanges':     { en: '💾 Save Changes',     es: '💾 Guardar Cambios' },
        'bookForm.seriesSection':   { en: 'Series',                es: 'Serie' },
        'bookForm.seriesName':      { en: 'Series Name',           es: 'Nombre de la Serie' },
        'bookForm.seriesIndex':     { en: 'Index in Series',       es: 'Índice en la Serie' },
        'bookForm.seriesAdd':       { en: '+ Add Series',          es: '+ Añadir Serie' },
        'bookForm.seriesRemove':    { en: '✕',                     es: '✕' },
        'bookForm.seriesNoMatch':   { en: 'No matching series',    es: 'No hay series coincidentes' },

        // ── Sources page ────────────────────────────────────────────────
        'sources.title':      { en: 'Sources',    es: 'Fuentes' },
        'sources.desc':       { en: 'Manage places and people from where you acquire or borrow books.', es: 'Gestiona los lugares y personas de donde adquieres o tomas prestados libros.' },
        'sources.shortName':  { en: 'Short Name',  es: 'Nombre Corto' },
        'sources.fullName':   { en: 'Full Name',   es: 'Nombre Completo' },
        'sources.type':       { en: 'Type',        es: 'Tipo' },
        'sources.locationUrl':{ en: 'Location / URL', es: 'Ubicación / URL' },
        'sources.notes':      { en: 'Notes',       es: 'Notas' },
        'sources.actions':    { en: 'Actions',     es: 'Acciones' },
        'sources.addNew':     { en: 'Add New Source', es: 'Añadir Nueva Fuente' },
        'sources.addBtn':     { en: '+ Add Source',   es: '+ Añadir Fuente' },
        'sources.name':       { en: 'Name',       es: 'Nombre' },
        'sources.nameReq':    { en: 'Name *',     es: 'Nombre *' },
        'sources.short':      { en: 'Short Name',  es: 'Nombre Corto' },
        'sources.location':   { en: 'Location',    es: 'Ubicación' },
        'sources.url':        { en: 'URL',          es: 'URL' },
        'sources.notesLabel': { en: 'Notes',        es: 'Notas' },
        'sources.empty':      { en: 'No sources yet. Add your first source below.', es: 'Aún no hay fuentes. Añade tu primera fuente a continuación.' },

        // ── Global stats ────────────────────────────────────────────────
        'stats.title':              { en: 'Global Reading Statistics',   es: 'Estadísticas Globales de Lectura' },
        'stats.booksFinished':      { en: 'Books Finished by Year',     es: 'Libros Terminados por Año' },
        'stats.clickCovers':        { en: '(click to view covers)',     es: '(clic para ver portadas)' },
        'stats.pagesRead':          { en: 'Pages Read by Year',        es: 'Páginas Leídas por Año' },
        'stats.clickDetails':       { en: '(click to view details)',    es: '(clic para ver detalles)' },
        'stats.timeReadByYear':     { en: 'Time Read by Year',         es: 'Tiempo Leído por Año' },
        'stats.libraryStats':       { en: 'Library Stats 📊',           es: 'Estadísticas de la Biblioteca 📊' },
        'stats.highestRated':       { en: 'Highest Rated Book',        es: 'Libro Mejor Valorado' },
        'stats.avgRating':          { en: 'Average Rating (Finished)', es: 'Valoración Promedio (Terminados)' },
        'stats.acrossRated':        { en: 'across rated books',        es: 'entre libros valorados' },
        'stats.longestBook':        { en: 'Longest Book Read',         es: 'Libro Más Largo Leído' },
        'stats.shortestBook':       { en: 'Shortest Book Read',        es: 'Libro Más Corto Leído' },
        'stats.mostReread':         { en: 'Most Re-read',              es: 'Más Releído' },
        'stats.byStatus':           { en: 'Books by Status',           es: 'Libros por Estado' },
        'stats.byLanguage':         { en: 'Books by Language',         es: 'Libros por Idioma' },
        'stats.byOrigLang':         { en: 'Books by Original Language', es: 'Libros por Idioma Original' },
        'stats.ratingDist':         { en: 'Rating Distribution',       es: 'Distribución de Valoraciones' },
        'stats.byPublisher':        { en: 'Books by Publisher',        es: 'Libros por Editorial' },
        'stats.topAuthors':         { en: 'Top Authors by Number of Books', es: 'Autores con Más Libros' },
        'stats.statusTimeline':     { en: 'Books by Status Over Time',     es: 'Libros por Estado a lo Largo del Tiempo' },
        'stats.timelineAbsolute':   { en: 'Absolute',                      es: 'Absoluto' },
        'stats.timelineRelative':   { en: 'Relative (%)',                  es: 'Relativo (%)' },
        'stats.empty':              { en: 'No reading data yet. Start tracking your reading to see statistics!', es: '¡Aún no hay datos. Empieza a registrar tu lectura para ver estadísticas!' },
        'stats.times':              { en: 'times',                     es: 'veces' },
        'stats.timelineAll':        { en: 'All Time',                  es: 'Todo' },
        'stats.timeline5y':         { en: 'Last 5 Years',              es: 'Últimos 5 Años' },
        'stats.timeline1y':         { en: 'Last Year',                 es: 'Último Año' },
        'stats.tagCloud':           { en: 'Tag Cloud',                 es: 'Nube de Etiquetas' },
        'stats.booksBoughtByYear':  { en: 'Books Bought by Year',     es: 'Libros Comprados por Año' },

        // ── Year stats ──────────────────────────────────────────────────
        'yearStats.backToGlobal':   { en: '← Back to Global Stats',    es: '← Volver a Estadísticas Globales' },
        'yearStats.title':          { en: 'Reading Statistics for',     es: 'Estadísticas de Lectura de' },
        'yearStats.totalPages':     { en: 'Total Pages',               es: 'Total de Páginas' },
        'yearStats.totalTime':      { en: 'Total Time',                es: 'Tiempo Total' },
        'yearStats.readingSessions':{ en: 'Reading Sessions',          es: 'Sesiones de Lectura' },
        'yearStats.periodPages':    { en: 'Period Pages',              es: 'Páginas de Periodos' },
        'yearStats.inferredTime':   { en: '(inferred time)',           es: '(tiempo estimado)' },
        'yearStats.readingTimeline':{ en: 'Reading Timeline',          es: 'Línea Temporal de Lectura' },
        'yearStats.readingProgress':{ en: 'Reading Progress',          es: 'Progreso de Lectura' },
        'yearStats.cumulative':     { en: 'Cumulative',                es: 'Acumulado' },
        'yearStats.perDay':         { en: 'Per Day',                   es: 'Por Día' },
        'yearStats.pages':          { en: 'Pages',                     es: 'Páginas' },
        'yearStats.time':           { en: 'Time',                      es: 'Tiempo' },
        'yearStats.hideIdleDays':   { en: 'Hide idle days',            es: 'Ocultar días inactivos' },
        'yearStats.sessions':       { en: 'Reading Sessions',          es: 'Sesiones de Lectura' },
        'yearStats.colDate':        { en: 'Date',                      es: 'Fecha' },
        'yearStats.colBook':        { en: 'Book',                      es: 'Libro' },
        'yearStats.colPages':       { en: 'Pages',                     es: 'Páginas' },
        'yearStats.colDuration':    { en: 'Duration',                  es: 'Duración' },
        'yearStats.periods':        { en: 'Reading Periods',           es: 'Periodos de Lectura' },
        'yearStats.colStartDate':   { en: 'Start Date',               es: 'Fecha Inicio' },
        'yearStats.colEndDate':     { en: 'End Date',                  es: 'Fecha Fin' },
        'yearStats.colNote':        { en: 'Note',                      es: 'Nota' },
        'yearStats.noSessions':     { en: 'No reading sessions in',    es: 'Sin sesiones de lectura en' },
        'yearStats.activitySummary':{ en: 'Year Activity Summary',     es: 'Resumen de Actividad del Año' },

        // ── Year books ──────────────────────────────────────────────────
        'yearBooks.backToGlobal':  { en: '← Back to Global Stats',     es: '← Volver a Estadísticas Globales' },
        'yearBooks.title':         { en: 'Books Finished in',          es: 'Libros Terminados en' },
        'yearBooks.finished':      { en: 'finished',                   es: 'terminado(s)' },
        'yearBooks.sortBy':        { en: 'Sort by:',                   es: 'Ordenar por:' },
        'yearBooks.sortDate':      { en: 'Date Finished',              es: 'Fecha de Fin' },
        'yearBooks.sortTitle':     { en: 'Title',                      es: 'Título' },
        'yearBooks.sortAuthor':    { en: 'Author',                     es: 'Autor' },
        'yearBooks.sortRating':    { en: 'Rating',                     es: 'Valoración' },
        'yearBooks.finishedLabel': { en: 'Finished:',                  es: 'Terminado:' },
        'yearBooks.empty':         { en: 'No books were finished in',  es: 'No se terminaron libros en' },

        // ── Year bought ─────────────────────────────────────────────────
        'yearBought.backToGlobal': { en: '← Back to Global Stats',     es: '← Volver a Estadísticas Globales' },
        'yearBought.title':        { en: 'Books Bought in',            es: 'Libros Comprados en' },
        'yearBought.bought':       { en: 'bought',                     es: 'comprado(s)' },
        'yearBought.sortBy':       { en: 'Sort by:',                   es: 'Ordenar por:' },
        'yearBought.sortDate':     { en: 'Date',                       es: 'Fecha' },
        'yearBought.sortTitle':    { en: 'Title',                      es: 'Título' },
        'yearBought.sortAuthor':   { en: 'Author',                     es: 'Autor' },
        'yearBought.sortPrice':    { en: 'Price',                      es: 'Precio' },
        'yearBought.dateLabel':    { en: 'Date:',                      es: 'Fecha:' },
        'yearBought.locationLabel':{ en: 'Location:',                  es: 'Lugar:' },
        'yearBought.gift':         { en: 'Gift',                       es: 'Regalo' },
        'yearBought.empty':        { en: 'No books were bought in',    es: 'No se compraron libros en' },

        // ── Calendar page ──────────────────────────────────────────────
        'cal.title':                 { en: 'Calendar',                 es: 'Calendario' },
        'cal.today':                 { en: 'Today',                    es: 'Hoy' },
        'cal.noActivity':            { en: 'No activity on this day',  es: 'Sin actividad este día' },
        'cal.mon':                   { en: 'Mon',                      es: 'Lun' },
        'cal.tue':                   { en: 'Tue',                      es: 'Mar' },
        'cal.wed':                   { en: 'Wed',                      es: 'Mié' },
        'cal.thu':                   { en: 'Thu',                      es: 'Jue' },
        'cal.fri':                   { en: 'Fri',                      es: 'Vie' },
        'cal.sat':                   { en: 'Sat',                      es: 'Sáb' },
        'cal.sun':                   { en: 'Sun',                      es: 'Dom' },
        'cal.january':               { en: 'January',                  es: 'Enero' },
        'cal.february':              { en: 'February',                 es: 'Febrero' },
        'cal.march':                 { en: 'March',                    es: 'Marzo' },
        'cal.april':                 { en: 'April',                    es: 'Abril' },
        'cal.may':                   { en: 'May',                      es: 'Mayo' },
        'cal.june':                  { en: 'June',                     es: 'Junio' },
        'cal.july':                  { en: 'July',                     es: 'Julio' },
        'cal.august':                { en: 'August',                   es: 'Agosto' },
        'cal.september':             { en: 'September',                es: 'Septiembre' },
        'cal.october':               { en: 'October',                  es: 'Octubre' },
        'cal.november':              { en: 'November',                 es: 'Noviembre' },
        'cal.december':              { en: 'December',                 es: 'Diciembre' },

        // ── Activity page ───────────────────────────────────────────────
        'activity.title':            { en: 'Activity',                 es: 'Actividad' },
        'activity.last7':            { en: 'Last 7 Days',              es: 'Últimos 7 Días' },
        'activity.last30':           { en: 'Last 30 Days',             es: 'Últimos 30 Días' },
        'activity.lastYear':         { en: 'Last Year',                es: 'Último Año' },
        'activity.dailyActivity':    { en: 'Daily Activity',           es: 'Actividad Diaria' },
        'activity.pages':            { en: 'Pages',                    es: 'Páginas' },
        'activity.time':             { en: 'Time',                     es: 'Tiempo' },
        'activity.heatmap':          { en: 'Reading Heatmap',          es: 'Mapa de Calor de Lectura' },
        'activity.last52':           { en: '(last 52 weeks)',          es: '(últimas 52 semanas)' },
        'activity.less':             { en: 'Less',                     es: 'Menos' },
        'activity.more':             { en: 'More',                     es: 'Más' },
        'activity.dayOfWeek':        { en: 'Reading by Day of Week',   es: 'Lectura por Día de la Semana' },
        'activity.paceTrend':        { en: 'Reading Pace Trend',       es: 'Tendencia de Ritmo de Lectura' },
        'activity.rollingAvg':       { en: '(7-day rolling avg)',      es: '(promedio móvil 7 días)' },
        'activity.booksActive':      { en: 'Books Active in This Period', es: 'Libros Activos en Este Periodo' },
        'activity.estFinishDates':   { en: 'Estimated Finish Dates',   es: 'Fechas Estimadas de Fin' },
        'activity.estFinishDesc':    { en: 'Based on your reading pace over the last 30 days.', es: 'Basado en tu ritmo de lectura de los últimos 30 días.' },
        'activity.personalRecords':  { en: 'Personal Records 🏆',      es: 'Récords Personales 🏆' },
        'activity.empty':            { en: 'No reading activity yet. Start tracking your reading sessions to see your activity!', es: '¡Aún no hay actividad de lectura. Empieza a registrar tus sesiones para ver tu actividad!' },

        // heatmap day labels
        'activity.mon':    { en: 'Mon', es: 'Lun' },
        'activity.wed':    { en: 'Wed', es: 'Mié' },
        'activity.fri':    { en: 'Fri', es: 'Vie' },

        // JS-generated labels in activity page
        'activity.totalPages':       { en: 'Total Pages',             es: 'Total de Páginas' },
        'activity.totalTime2':       { en: 'Total Time',              es: 'Tiempo Total' },
        'activity.avgPagesDay':      { en: 'Avg Pages/Day',           es: 'Prom. Páginas/Día' },
        'activity.avgTimeDay':       { en: 'Avg Time/Day',            es: 'Prom. Tiempo/Día' },
        'activity.activeDays':       { en: 'Active Days',             es: 'Días Activos' },
        'activity.booksFinished':    { en: 'Books Finished',          es: 'Libros Terminados' },
        'activity.currentStreak':    { en: 'Current Streak',          es: 'Racha Actual' },
        'activity.longestStreak':    { en: 'Longest Streak',          es: 'Racha Más Larga' },
        'activity.consistency':      { en: 'Consistency',             es: 'Consistencia' },
        'activity.pagesPerSession':  { en: 'Pages/Session',           es: 'Páginas/Sesión' },
        'activity.days':             { en: 'days',                    es: 'días' },
        'activity.day':              { en: 'day',                     es: 'día' },
        'activity.pagesLabel':       { en: 'pages',                   es: 'páginas' },
        'activity.pagesReadLabel':   { en: 'pages read',              es: 'páginas leídas' },
        'activity.minLabel':         { en: 'min read',                es: 'min leídos' },
        'activity.noActivity':       { en: 'No activity',             es: 'Sin actividad' },
        'activity.estFinish':        { en: 'Est. finish:',            es: 'Fin est.:' },
        'activity.pagesLeft':        { en: 'pages left',              es: 'páginas restantes' },
        'activity.noPace':           { en: 'No pace data',            es: 'Sin datos de ritmo' },
        'activity.mostPagesDay':     { en: 'Most Pages in a Day',     es: 'Más Páginas en un Día' },
        'activity.mostTimeDay':      { en: 'Most Time in a Day',      es: 'Más Tiempo en un Día' },
        'activity.longestSession':   { en: 'Longest Single Session',  es: 'Sesión Más Larga' },
        'activity.fastestDay':       { en: 'Fastest Reading Day',     es: 'Día de Lectura Más Rápido' },
        'activity.bestWeek':         { en: 'Best Week',               es: 'Mejor Semana' },
        'activity.bestMonth':        { en: 'Best Month',              es: 'Mejor Mes' },
        'activity.mostBooksParallel':{ en: 'Most Books Read at Once', es: 'Más Libros Leídos a la Vez' },
        'activity.longestBookRead':  { en: 'Longest Book Read',       es: 'Libro Más Largo Leído' },
        'activity.mostRereadBook':   { en: 'Most Re-read Book',       es: 'Libro Más Releído' },
        'activity.totalPagesAll':    { en: 'Total Pages Read (All Time)', es: 'Total de Páginas Leídas (Histórico)' },
        'activity.totalTimeAll':     { en: 'Total Time Read (All Time)',  es: 'Tiempo Total de Lectura (Histórico)' },
        'activity.totalBooksFinished':{ en: 'Total Books Finished',    es: 'Total de Libros Terminados' },
        'activity.books':            { en: 'books',                    es: 'libros' },
        'activity.pagesSuffix':      { en: 'pp',                      es: 'pp' },
        'activity.readTimes':        { en: 'read(s)',                  es: 'lectura(s)' },

        // ── Dashboard ────────────────────────────────────────────────────
        'dash.title':               { en: 'Dashboard',             es: 'Panel' },
        'dash.avgRating':           { en: 'Avg Rating',            es: 'Valoración Media' },
        'dash.currentlyReading':    { en: 'Currently Reading',     es: 'Leyendo Actualmente' },
        'dash.thisYear':            { en: 'This Year at a Glance', es: 'Este Año de un Vistazo' },
        'dash.booksFinishedYear':   { en: 'Books Finished',        es: 'Libros Terminados' },
        'dash.pagesYear':           { en: 'Pages Read',            es: 'Páginas Leídas' },
        'dash.timeYear':            { en: 'Time Read',             es: 'Tiempo Leído' },
        'dash.vsLastYear':          { en: 'vs last year',          es: 'vs año pasado' },
        'dash.streaks':             { en: 'Streaks & Consistency', es: 'Rachas y Consistencia' },
        'dash.last52Weeks':         { en: '(last 52 weeks)',       es: '(últimas 52 semanas)' },
        'dash.recentActivity':      { en: 'Recent Activity',       es: 'Actividad Reciente' },
        'dash.read':                { en: 'Read',                  es: 'Leyó' },
        'dash.of':                  { en: 'of',                    es: 'de' },
        'dash.actFinished':         { en: 'Finished',              es: 'Terminó' },
        'dash.actStarted':          { en: 'Started reading',       es: 'Empezó a leer' },
        'dash.actBought':           { en: 'Bought',                es: 'Compró' },
        'dash.actBorrowed':         { en: 'Borrowed',              es: 'Pidió prestado' },
        'dash.actFrom':             { en: 'from',                  es: 'de' },
        'dash.actAt':               { en: 'at',                    es: 'en' },
        'dash.actGift':             { en: 'Received',              es: 'Recibió' },
        'dash.actAsGift':           { en: 'as a gift',             es: 'como regalo' },
        'dash.actStartedShort':     { en: 'started reading',       es: 'empezó a leer' },
        'dash.andRead':             { en: 'and read',              es: 'y leyó' },
        'dash.andFinished':         { en: 'and finished it',       es: 'y lo terminó' },
        'dash.andConnector':        { en: 'and',                   es: 'y' },
        'dash.actIt':               { en: 'it',                    es: '' },
        'dash.actReadLower':        { en: 'read',                  es: 'leyó' },
        'dash.actFinishedShort':    { en: 'finished it',           es: 'lo terminó' },
        'dash.ownedBought':         { en: 'Bought',                es: 'Comprado' },
        'dash.ownedGift':           { en: 'Received as a gift',    es: 'Recibido como regalo' },
        'dash.ownedOn':             { en: 'on',                    es: 'el' },
        'dash.lastBooksOwned':      { en: 'Last Books Owned',      es: 'Últimos Libros Adquiridos' },
        'dash.topRated':            { en: 'Top Rated',             es: 'Mejor Valorados' },
        'dash.records':             { en: 'Records',               es: 'Récords' },
        'dash.formatSource':        { en: 'Format & Source',       es: 'Formato y Fuente' },
        'dash.byFormat':            { en: 'By Format',             es: 'Por Formato' },
        'dash.bySource':            { en: 'By Source',             es: 'Por Fuente' },
        'dash.tagCloud':            { en: 'Tag Cloud',             es: 'Nube de Etiquetas' },
        'dash.authorSpotlight':     { en: 'Author Spotlight',      es: 'Autor Destacado' },
        'dash.booksInLibrary':      { en: 'books in your library', es: 'libros en tu biblioteca' },
        'dash.seriesProgress':      { en: 'Series Progress',       es: 'Progreso de Series' },
        'dash.languages':           { en: 'Languages',             es: 'Idiomas' },
        'dash.readIn':              { en: 'You read in',           es: 'Lees en' },
        'dash.languages2':          { en: 'languages',             es: 'idiomas' },
        'dash.tbrPile':             { en: 'TBR Pile',              es: 'Pendientes de Leer' },
        'dash.booksWaiting':        { en: 'books waiting',         es: 'libros esperando' },
        'dash.libraryHealth':       { en: 'Library Health',        es: 'Salud de la Biblioteca' },
        'dash.unratedBooks':        { en: 'finished books unrated',es: 'libros terminados sin valorar' },
        'dash.noCover':             { en: 'books without cover',   es: 'libros sin portada' },
        'dash.noPhoto':             { en: 'authors without photo', es: 'autores sin foto' },
        'dash.noTags':              { en: 'books without tags',    es: 'libros sin etiquetas' },
        'dash.abandonedBooks':      { en: 'abandoned books',       es: 'libros abandonados' },
        'dash.noPages':             { en: 'books without page count', es: 'libros sin número de páginas' },
        'dash.noSummary':           { en: 'books without summary', es: 'libros sin resumen' },
        'dash.noAuthor':            { en: 'books without author',  es: 'libros sin autor' },
        'dash.today':               { en: 'Today',                 es: 'Hoy' },
        'dash.yesterday':           { en: 'Yesterday',             es: 'Ayer' },
        'dash.daysAgo':             { en: 'days ago',              es: 'días atrás' },

        // ── Gender values ───────────────────────────────────────────────
        'gender.male':              { en: 'Male',                  es: 'Masculino' },
        'gender.female':            { en: 'Female',                es: 'Femenino' },
        'gender.unknown':           { en: 'Unknown',               es: 'Desconocido' },

        // ── Annotations (Quotes, Thoughts, Words) ──────────────────────
        'book.quotes':              { en: 'Quotes',                es: 'Citas' },
        'book.thoughts':            { en: 'Thoughts',              es: 'Reflexiones' },
        'book.words':               { en: 'Words',                 es: 'Palabras' },
        'book.noQuotes':            { en: 'No quotes yet.',        es: 'Aún no hay citas.' },
        'book.noThoughts':          { en: 'No thoughts yet.',      es: 'Aún no hay reflexiones.' },
        'book.noWords':             { en: 'No words yet.',         es: 'Aún no hay palabras.' },
        'book.addQuoteBtn':         { en: '+ Add Quote',           es: '+ Añadir Cita' },
        'book.addThoughtBtn':       { en: '+ Add Thought',         es: '+ Añadir Reflexión' },
        'book.addWordBtn':          { en: '+ Add Word',            es: '+ Añadir Palabra' },
        'book.quoteTextPlaceholder':  { en: 'Quote text...',       es: 'Texto de la cita...' },
        'book.thoughtTextPlaceholder': { en: 'Your thought...',    es: 'Tu reflexión...' },
        'book.pagePlaceholder':     { en: 'Page',                  es: 'Página' },
        'book.wordPlaceholder':     { en: 'Word',                  es: 'Palabra' },
        'book.definitionPlaceholder': { en: 'Definition...',       es: 'Definición...' },

        // ── Dashboard spotlights ────────────────────────────────────────
        'dash.quoteOfTheDay':       { en: 'Quote of the Day',      es: 'Cita del Día' },
        'dash.wordOfTheDay':        { en: 'Words of the Day',      es: 'Palabras del Día' },

        // ── Bookly import ───────────────────────────────────────────────
        'bookForm.booklyImportTitle': { en: '📕 Import from Bookly', es: '📕 Importar desde Bookly' },
        'bookForm.booklyImportDesc':  { en: 'Upload a Bookly summary PDF to import quotes, thoughts, and words.', es: 'Sube un PDF de resumen de Bookly para importar citas, reflexiones y palabras.' },
        'bookForm.booklyClearExisting': { en: 'Remove existing quotes, thoughts & words before importing', es: 'Eliminar citas, reflexiones y palabras existentes antes de importar' },
        'bookForm.booklyImportBtn': { en: '📥 Import',             es: '📥 Importar' },
    };

    // ── Public API ──────────────────────────────────────────────────────
    function getLang() {
        return localStorage.getItem(STORAGE_KEY) || 'en';
    }

    function setLang(lang) {
        localStorage.setItem(STORAGE_KEY, lang);
        applyTranslations(lang);
        formatDates(lang);
        updateToggleButtons(lang);
    }

    /** Translate a single key */
    function t(key) {
        var lang = getLang();
        var entry = translations[key];
        if (!entry) return key;
        return entry[lang] || entry['en'] || key;
    }

    /** Walk the DOM and apply all [data-i18n] translations */
    function applyTranslations(lang) {
        lang = lang || getLang();

        // Text content
        document.querySelectorAll('[data-i18n]').forEach(function (el) {
            var key = el.getAttribute('data-i18n');
            var entry = translations[key];
            if (entry) el.textContent = entry[lang] || entry['en'];
        });

        // Placeholders
        document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
            var key = el.getAttribute('data-i18n-placeholder');
            var entry = translations[key];
            if (entry) el.placeholder = entry[lang] || entry['en'];
        });

        // Title attributes
        document.querySelectorAll('[data-i18n-title]').forEach(function (el) {
            var key = el.getAttribute('data-i18n-title');
            var entry = translations[key];
            if (entry) el.title = entry[lang] || entry['en'];
        });
    }

    function updateToggleButtons(lang) {
        document.querySelectorAll('.lang-btn').forEach(function (btn) {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
    }

    // ── Date formatting ────────────────────────────────────────────────
    var MONTHS_EN = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var MONTHS_EN_FULL = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    var MONTHS_ES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
    var ORDINALS_EN = ['','1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','12th','13th','14th','15th','16th','17th','18th','19th','20th','21st'];
    var CENTURY_EN = ['','1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','12th','13th','14th','15th','16th','17th','18th','19th','20th','21st'];

    /**
     * Format a flexible date string for display based on language.
     * Supports: YYYY-MM-DD, YYYY-MM, YYYY, intervals (1912-1915),
     * approximate (ca. 1450), centuries (4th Century), B.C. dates.
     */
    function formatDisplayDate(raw, lang) {
        if (!raw || !raw.trim()) return '';
        raw = raw.trim();
        lang = lang || getLang();

        // Handle "ca. YEAR" approximate dates
        var caMatch = raw.match(/^ca\.?\s*(\d+)\s*(b\.?\s*c\.?)?$/i);
        if (caMatch) {
            var yr = caMatch[1];
            var bc = caMatch[2] ? (lang === 'es' ? ' a. C.' : ' B.C.') : '';
            return 'ca. ' + yr + bc;
        }

        // Handle century: "4th Century", "4th Century B.C.", "siglo IV"
        var cenMatch = raw.match(/^(\d+)(?:st|nd|rd|th)?\s*century\s*(b\.?\s*c\.?)?$/i);
        if (cenMatch) {
            var num = parseInt(cenMatch[1], 10);
            var bcSuffix = cenMatch[2] ? (lang === 'es' ? ' a. C.' : ' B.C.') : '';
            if (lang === 'es') {
                // Roman numeral for Spanish
                var roman = toRoman(num);
                return 'Siglo ' + roman + bcSuffix;
            }
            var ordinal = num <= 20 ? CENTURY_EN[num] : num + 'th';
            return ordinal + ' Century' + bcSuffix;
        }

        // Handle Spanish century input: "siglo IV"
        var sigloMatch = raw.match(/^siglo\s+([IVXLCDM]+)\s*(a\.?\s*c\.?)?$/i);
        if (sigloMatch) {
            var romanNum = fromRoman(sigloMatch[1].toUpperCase());
            var bcS = sigloMatch[2] ? (lang === 'es' ? ' a. C.' : ' B.C.') : '';
            if (lang === 'es') {
                return 'Siglo ' + sigloMatch[1].toUpperCase() + bcS;
            }
            var ord = romanNum <= 20 ? CENTURY_EN[romanNum] : romanNum + 'th';
            return ord + ' Century' + bcS;
        }

        // Handle year intervals: "1912-1915" (two 4-digit years)
        var intervalMatch = raw.match(/^(\d{4})\s*[-–]\s*(\d{4})$/);
        if (intervalMatch) {
            return intervalMatch[1] + '–' + intervalMatch[2];
        }

        // Handle B.C. year: "450 B.C." or "450 b.c."
        var bcYearMatch = raw.match(/^(\d+)\s*b\.?\s*c\.?$/i);
        if (bcYearMatch) {
            return bcYearMatch[1] + (lang === 'es' ? ' a. C.' : ' B.C.');
        }

        // Handle standard ISO dates
        // Full date: YYYY-MM-DD
        var fullMatch = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
        if (fullMatch) {
            var y = parseInt(fullMatch[1], 10);
            var m = parseInt(fullMatch[2], 10) - 1;
            var d = parseInt(fullMatch[3], 10);
            if (lang === 'es') {
                return d + ' de ' + MONTHS_ES[m] + ' de ' + fullMatch[1];
            }
            return MONTHS_EN[m] + ' ' + d + ', ' + fullMatch[1];
        }

        // Partial date: YYYY-MM
        var partialMatch = raw.match(/^(\d{4})-(\d{2})$/);
        if (partialMatch) {
            var mo = parseInt(partialMatch[2], 10) - 1;
            if (lang === 'es') {
                return MONTHS_ES[mo].charAt(0).toUpperCase() + MONTHS_ES[mo].slice(1) + ' de ' + partialMatch[1];
            }
            return MONTHS_EN_FULL[mo] + ' ' + partialMatch[1];
        }

        // Year only: YYYY
        var yearMatch = raw.match(/^(\d{4})$/);
        if (yearMatch) {
            return yearMatch[1];
        }

        // Fallback: return as-is
        return raw;
    }

    function toRoman(num) {
        var lookup = [[1000,'M'],[900,'CM'],[500,'D'],[400,'CD'],[100,'C'],[90,'XC'],[50,'L'],[40,'XL'],[10,'X'],[9,'IX'],[5,'V'],[4,'IV'],[1,'I']];
        var result = '';
        for (var i = 0; i < lookup.length; i++) {
            while (num >= lookup[i][0]) { result += lookup[i][1]; num -= lookup[i][0]; }
        }
        return result;
    }

    function fromRoman(s) {
        var map = {I:1,V:5,X:10,L:50,C:100,D:500,M:1000};
        var result = 0;
        for (var i = 0; i < s.length; i++) {
            var cur = map[s[i]] || 0;
            var next = map[s[i+1]] || 0;
            if (cur < next) { result -= cur; } else { result += cur; }
        }
        return result;
    }

    /** Format all elements with data-date attribute */
    function formatDates(lang) {
        lang = lang || getLang();
        document.querySelectorAll('[data-date]').forEach(function (el) {
            var raw = el.getAttribute('data-date');
            el.textContent = formatDisplayDate(raw, lang);
        });
    }

    // ── Initialise on DOM ready ─────────────────────────────────────────
    function init() {
        var lang = getLang();
        applyTranslations(lang);
        formatDates(lang);
        updateToggleButtons(lang);

        // Bind click handlers on language buttons (event delegation)
        document.addEventListener('click', function (e) {
            if (e.target.classList.contains('lang-btn')) {
                setLang(e.target.dataset.lang);
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ── Rich-text toolbar for textareas ──────────────────────────────
    function initRichTextToolbar(textareaId) {
        var ta = document.getElementById(textareaId);
        if (!ta) return;

        var toolbar = document.createElement('div');
        toolbar.className = 'rt-toolbar';

        var buttons = [
            { label: '<b>B</b>',  key: 'rt.bold',      tag: 'b' },
            { label: '<i>I</i>',  key: 'rt.italic',    tag: 'i' },
            { label: '<u>U</u>',  key: 'rt.underline', tag: 'u' },
            { label: '<s>S</s>',  key: 'rt.strike',    tag: 's' },
            { sep: true },
            { label: 'H',         key: 'rt.heading',   tag: 'h4' },
            { label: '• ―',       key: 'rt.ul',        tag: 'ul', wrap: 'li' },
            { label: '1. ―',      key: 'rt.ol',        tag: 'ol', wrap: 'li' },
            { sep: true },
            { label: '🔗',        key: 'rt.link',      action: 'link' },
            { label: '✕',         key: 'rt.clear',     action: 'clear' }
        ];

        buttons.forEach(function (b) {
            if (b.sep) {
                var sep = document.createElement('span');
                sep.className = 'rt-sep';
                toolbar.appendChild(sep);
                return;
            }
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'rt-btn';
            btn.innerHTML = b.label;
            btn.setAttribute('data-i18n-title', b.key);
            btn.title = t(b.key);
            btn.addEventListener('click', function () {
                handleToolbarAction(ta, b);
            });
            toolbar.appendChild(btn);
        });

        ta.parentNode.insertBefore(toolbar, ta);
    }

    function handleToolbarAction(ta, b) {
        var start = ta.selectionStart;
        var end   = ta.selectionEnd;
        var text  = ta.value;
        var sel   = text.substring(start, end);
        var replacement;

        if (b.action === 'link') {
            var url = prompt(t('rt.link'), 'https://');
            if (!url) return;
            replacement = '<a href="' + url.replace(/"/g, '&quot;') + '">' + (sel || url) + '</a>';
        } else if (b.action === 'clear') {
            replacement = sel.replace(/<[^>]+>/g, '');
        } else if (b.wrap) {
            var lines = sel ? sel.split('\n') : [''];
            var items = lines.map(function (l) { return '<' + b.wrap + '>' + l.trim() + '</' + b.wrap + '>'; }).join('\n');
            replacement = '<' + b.tag + '>\n' + items + '\n</' + b.tag + '>';
        } else {
            replacement = '<' + b.tag + '>' + sel + '</' + b.tag + '>';
        }

        ta.value = text.substring(0, start) + replacement + text.substring(end);
        ta.focus();
        var cursorPos = start + replacement.length;
        ta.setSelectionRange(cursorPos, cursorPos);
        ta.dispatchEvent(new Event('input'));
    }

    // Expose for usage in inline scripts
    window.librariumI18n = { t: t, getLang: getLang, setLang: setLang, applyTranslations: applyTranslations, initRichTextToolbar: initRichTextToolbar, formatDisplayDate: formatDisplayDate, formatDates: formatDates };
})();
