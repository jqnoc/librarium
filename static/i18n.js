// ═══════════════════════════════════════════════════════════════════════════
// Ashinami – Internationalisation (EN / ES)
// ═══════════════════════════════════════════════════════════════════════════
(function () {
    'use strict';

    var STORAGE_KEY = 'ashinami_lang';

    // ── Translation dictionaries ────────────────────────────────────────
    var translations = {
        // ── Navigation & global ─────────────────────────────────────────
        'nav.library':      { en: 'Library',      es: 'Biblioteca' },
        'nav.authors':      { en: 'Authors',      es: 'Autores' },
        'nav.stats':        { en: 'Stats',        es: 'Estadísticas' },
        'nav.activity':     { en: 'Activity',     es: 'Actividad' },
        'nav.sources':      { en: 'Sources',      es: 'Fuentes' },
        'nav.addBook':      { en: '+ Add Book',   es: '+ Añadir Libro' },
        'footer.copy':      { en: 'Ashinami',     es: 'Ashinami' },

        // ── Index page ──────────────────────────────────────────────────
        'index.title':          { en: 'Library',            es: 'Biblioteca' },
        'index.totalBooks':     { en: 'Total Books',        es: 'Total de Libros' },
        'index.totalPages':     { en: 'Total Pages',        es: 'Total de Páginas' },
        'index.totalTimeRead':  { en: 'Total Time Read',    es: 'Tiempo Total de Lectura' },
        'index.uniqueAuthors':  { en: 'Unique Authors',     es: 'Autores Únicos' },
        'index.finished':       { en: 'Finished',           es: 'Terminados' },
        'index.currentlyReading': { en: 'Currently Reading', es: 'Leyendo' },
        'index.notStarted':    { en: 'Not Started',         es: 'Sin Empezar' },
        'index.view':          { en: 'View:',               es: 'Vista:' },
        'index.filter':        { en: 'Filter:',             es: 'Filtro:' },
        'index.sortBy':        { en: 'Sort by:',            es: 'Ordenar por:' },
        'index.thenBy':        { en: 'then by:',            es: 'y luego:' },
        'index.filterAll':     { en: 'All',                 es: 'Todos' },
        'index.filterReading': { en: 'Reading',             es: 'Leyendo' },
        'index.filterFinished':{ en: 'Finished',            es: 'Terminados' },
        'index.filterNotStarted':{ en: 'Not Started',       es: 'Sin Empezar' },
        'index.filterAbandoned':{ en: 'Abandoned',          es: 'Abandonados' },
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

        // ── Book detail ─────────────────────────────────────────────────
        'book.backToLibrary':   { en: '← Back to Library',   es: '← Volver a la Biblioteca' },
        'book.author':          { en: 'Author',              es: 'Autor' },
        'book.authors':         { en: 'Authors',             es: 'Autores' },
        'book.status':          { en: 'Status',              es: 'Estado' },
        'book.pages':           { en: 'Pages',               es: 'Páginas' },
        'book.genre':           { en: 'Genre',               es: 'Género' },
        'book.language':        { en: 'Language',             es: 'Idioma' },
        'book.publisher':       { en: 'Publisher',            es: 'Editorial' },
        'book.pubDate':         { en: 'Publication Date',     es: 'Fecha de Publicación' },
        'book.isbn':            { en: 'ISBN',                 es: 'ISBN' },
        'book.originalTitle':   { en: 'Original Title',      es: 'Título Original' },
        'book.originalLang':    { en: 'Original Language',    es: 'Idioma Original' },
        'book.originalDate':    { en: 'Original Date',        es: 'Fecha Original' },
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
        'authorDetail.empty':         { en: 'No books found for this author.', es: 'No se encontraron libros de este autor.' },

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

        // ── New book & Edit metadata (shared) ───────────────────────────
        'bookForm.backToLibrary':   { en: '← Back to Library',   es: '← Volver a la Biblioteca' },
        'bookForm.backToBook':      { en: '← Back to Book',      es: '← Volver al Libro' },
        'bookForm.addNewBook':      { en: 'Add New Book',        es: 'Añadir Nuevo Libro' },
        'bookForm.editMetadata':    { en: 'Edit Metadata',       es: 'Editar Metadatos' },
        'bookForm.basicInfo':       { en: 'Basic Information',   es: 'Información Básica' },
        'bookForm.title':           { en: 'Title',               es: 'Título' },
        'bookForm.titleReq':        { en: 'Title *',             es: 'Título *' },
        'bookForm.authorReq':       { en: 'Author(s) *',        es: 'Autor(es) *' },
        'bookForm.authorLabel':     { en: 'Author(s)',           es: 'Autor(es)' },
        'bookForm.genre':           { en: 'Genre',               es: 'Género' },
        'bookForm.status':          { en: 'Status',              es: 'Estado' },
        'bookForm.statusReading':   { en: 'Reading',             es: 'Leyendo' },
        'bookForm.statusFinished':  { en: 'Finished',            es: 'Terminado' },
        'bookForm.statusNotStarted':{ en: 'Not Started',         es: 'Sin Empezar' },
        'bookForm.statusAbandoned': { en: 'Abandoned',           es: 'Abandonado' },
        'bookForm.pages':           { en: 'Pages',               es: 'Páginas' },
        'bookForm.frontmatter':     { en: 'Frontmatter Pages',   es: 'Páginas Preliminares' },
        'bookForm.language':        { en: 'Language',             es: 'Idioma' },
        'bookForm.pubDetails':      { en: 'Publication Details', es: 'Detalles de Publicación' },
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
        'bookForm.saveChanges':     { en: '💾 Save Changes',     es: '💾 Guardar Cambios' },

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
        'stats.libraryStats':       { en: 'Library Stats 📊',           es: 'Estadísticas de la Biblioteca 📊' },
        'stats.highestRated':       { en: 'Highest Rated Book',        es: 'Libro Mejor Valorado' },
        'stats.avgRating':          { en: 'Average Rating (Finished)', es: 'Valoración Promedio (Terminados)' },
        'stats.acrossRated':        { en: 'across rated books',        es: 'entre libros valorados' },
        'stats.longestBook':        { en: 'Longest Book Read',         es: 'Libro Más Largo Leído' },
        'stats.shortestBook':       { en: 'Shortest Book Read',        es: 'Libro Más Corto Leído' },
        'stats.mostReread':         { en: 'Most Re-read',              es: 'Más Releído' },
        'stats.byStatus':           { en: 'Books by Status',           es: 'Libros por Estado' },
        'stats.byLanguage':         { en: 'Books by Language',         es: 'Libros por Idioma' },
        'stats.byGenre':            { en: 'Books by Genre',            es: 'Libros por Género' },
        'stats.byOrigLang':         { en: 'Books by Original Language', es: 'Libros por Idioma Original' },
        'stats.ratingDist':         { en: 'Rating Distribution',       es: 'Distribución de Valoraciones' },
        'stats.byPublisher':        { en: 'Books by Publisher',        es: 'Libros por Editorial' },
        'stats.topAuthors':         { en: 'Top Authors by Number of Books', es: 'Autores con Más Libros' },
        'stats.empty':              { en: 'No reading data yet. Start tracking your reading to see statistics!', es: '¡Aún no hay datos. Empieza a registrar tu lectura para ver estadísticas!' },
        'stats.times':              { en: 'times',                     es: 'veces' },

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
    };

    // ── Public API ──────────────────────────────────────────────────────
    function getLang() {
        return localStorage.getItem(STORAGE_KEY) || 'en';
    }

    function setLang(lang) {
        localStorage.setItem(STORAGE_KEY, lang);
        applyTranslations(lang);
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

    // ── Initialise on DOM ready ─────────────────────────────────────────
    function init() {
        var lang = getLang();
        applyTranslations(lang);
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

    // Expose for usage in inline scripts
    window.ashinamiI18n = { t: t, getLang: getLang, setLang: setLang, applyTranslations: applyTranslations };
})();
