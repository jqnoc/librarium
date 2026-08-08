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
        'nav.minimize':     { en: 'Minimize Librarium', es: 'Minimizar Librarium' },
        'nav.maximize':     { en: 'Maximize Librarium', es: 'Maximizar Librarium' },
        'nav.restore':      { en: 'Restore Librarium',  es: 'Restaurar Librarium' },
        'nav.close':        { en: 'Close Librarium', es: 'Cerrar Librarium' },
        'theme.toggle':     { en: 'Toggle dark mode', es: 'Alternar modo oscuro' },
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
        'library.cloudStorage':  { en: 'Cloud Storage',          es: 'Almacenamiento en la Nube' },
        'library.dropboxPath':   { en: 'Apps/LibrariumApp/',     es: 'Apps/LibrariumApp/' },
        'settings.similarWorksTitle': { en: 'Similar Works', es: 'Obras Similares' },
        'settings.similarWorksDescription': { en: 'Choose which classification categories contribute to Similar Works.', es: 'Elige qué categorías de clasificación contribuyen a las obras similares.' },
        'settings.categoriesLabel': { en: 'Classification categories', es: 'Categorías de clasificación' },
        'settings.allCategories': { en: 'All categories', es: 'Todas las categorías' },
        'settings.noCategories': { en: 'No categories', es: 'Ninguna categoría' },
        'settings.categoriesSelected': { en: 'categories selected', es: 'categorías seleccionadas' },

        // ── Database backup ──────────────────────────────────────────────────────
        'backup.title':          { en: 'Database Backup',        es: 'Copia de Seguridad' },
        'backup.create':         { en: 'Create Backup Now',      es: 'Crear Copia Ahora' },
        'backup.shuttingDown':   { en: 'Backing up & closing\u2026', es: 'Guardando copia y cerrando\u2026' },
        'backup.directory':      { en: 'Backup Directory',       es: 'Directorio de Copias' },
        'backup.dirDefault':     { en: 'Default',                es: 'Por defecto' },
        'backup.saveDir':        { en: 'Save',                   es: 'Guardar' },
        'backup.dirHint':        { en: 'Leave empty to use the default location.', es: 'Dejar vacío para usar la ubicación por defecto.' },
        'backup.dropboxHint':    { en: 'Backups are stored in your Dropbox (Apps/LibrariumApp/backups/).', es: 'Las copias de seguridad se guardan en tu Dropbox (Apps/LibrariumApp/backups/).' },

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

        // ── Dropbox auth & sync ─────────────────────────────────────────
        'auth.connectDropbox':   { en: 'Connect to Dropbox',    es: 'Conectar con Dropbox' },
        'auth.description':      { en: 'Librarium stores your reading data securely in your Dropbox account. Connect your Dropbox to get started.', es: 'Librarium almacena tus datos de lectura de forma segura en tu cuenta de Dropbox. Conecta tu Dropbox para empezar.' },
        'auth.connectButton':    { en: 'Connect with Dropbox',  es: 'Conectar con Dropbox' },
        'auth.note':             { en: 'Your data is stored in the Apps/LibrariumApp folder in your Dropbox. Librarium cannot access any other files.', es: 'Tus datos se almacenan en la carpeta Apps/LibrariumApp de tu Dropbox. Librarium no puede acceder a otros archivos.' },
        'auth.connected':        { en: 'Dropbox Connected',     es: 'Dropbox Conectado' },
        'auth.successMessage':   { en: 'Your Dropbox account has been connected successfully. Librarium will continue in the desktop app.', es: 'Tu cuenta de Dropbox se ha conectado correctamente. Librarium continuará en la aplicación de escritorio.' },
        'auth.continue':         { en: 'Continue to Librarium', es: 'Continuar a Librarium' },
        'auth.closeTab':         { en: 'Close Tab', es: 'Cerrar pestaña' },
        'auth.closeTabHint':     { en: 'This browser tab can now be closed. Librarium will continue in the desktop app.', es: 'Esta pestaña del navegador ya puede cerrarse. Librarium continuará en la aplicación de escritorio.' },
        'auth.disconnect':       { en: 'Disconnect',            es: 'Desconectar' },
        'auth.waitingTitle':     { en: 'Waiting for Dropbox…',   es: 'Esperando a Dropbox…' },
        'auth.waitingMessage':   { en: 'A browser window has been opened for you to authorize Librarium. Please complete the login in your browser and return here.', es: 'Se ha abierto una ventana del navegador para que autorices Librarium. Completa el inicio de sesión en tu navegador y vuelve aquí.' },
        'auth.retryLink':        { en: 'Click here to try again', es: 'Haz clic aquí para intentar de nuevo' },
        'auth.syncingTitle':     { en: 'Syncing with Dropbox…', es: 'Sincronizando con Dropbox…' },
        'auth.syncingMessage':   { en: 'Downloading your library data. This may take a moment on the first launch.', es: 'Descargando los datos de tu biblioteca. Esto puede tardar un momento en el primer inicio.' },

        // ── Error pages ─────────────────────────────────────────────────
        'error.notFound':        { en: 'Page not found',        es: 'Página no encontrada' },
        'error.notFoundHint':    { en: 'The page you are looking for does not exist or has been moved.', es: 'La página que buscas no existe o ha sido movida.' },
        'error.backHome':        { en: 'Back to dashboard',     es: 'Volver al panel' },

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
        'index.filterWishlist':{ en: 'Wishlist',           es: 'Lista de Deseos' },
        'index.filterDraft':    { en: 'Draft',              es: 'Borradores' },
        'index.filteringByTag': { en: 'Filtering by tag:',  es: 'Filtrando por etiqueta:' },
        'index.clearTagFilter': { en: '✕ Clear',            es: '✕ Quitar' },
        'index.filteringByGenre': { en: 'Filtering by genre:', es: 'Filtrando por género:' },
        'index.clearGenreFilter': { en: '✕ Clear',           es: '✕ Quitar' },
        'index.filteringByClassification': { en: 'Filtering by', es: 'Filtrando por' },
        'index.showingBooksWithout': { en: 'Showing books without', es: 'Mostrando libros sin' },
        'index.clearClassificationFilter': { en: '✕ Clear', es: '✕ Quitar' },
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
        'book.genresSection':   { en: 'Genres',              es: 'Géneros' },
        'book.classification':  { en: 'Classification',       es: 'Clasificación' },
        'book.cleanClassification': { en: 'Clean Classification', es: 'Limpiar clasificación' },
        'book.cleanClassificationWarning': { en: 'This will remove all values from every classification category. This cannot be undone.', es: 'Esto eliminará todos los valores de cada categoría de clasificación. Esta acción no se puede deshacer.' },
        'book.cleanClassificationConfirm': { en: 'Yes, Clean Classification', es: 'Sí, limpiar clasificación' },
        'book.similarWorks':    { en: 'Similar Works',        es: 'Obras Similares' },
        'book.sharedItems':     { en: 'shared items',         es: 'elementos compartidos' },
        'book.similarityScore': { en: 'Score:',                es: 'Puntuación:' },
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
        'book.bindingSoftcover':{ en: 'Softcover',           es: 'Tapa Flexible' },
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
        'book.forewordAuthor':  { en: 'Foreword/Introduction Author',  es: 'Autor del Prólogo/Introducción' },
        'book.forewordAuthors': { en: 'Foreword/Introduction Authors', es: 'Autores del Prólogo/Introducción' },
        'book.epilogueAuthor':  { en: 'Epilogue Author',    es: 'Autor del Epílogo' },
        'book.epilogueAuthors': { en: 'Epilogue Authors',   es: 'Autores del Epílogo' },
        'book.contributingAuthor':  { en: 'Contributing Author',  es: 'Autor Colaborador' },
        'book.contributingAuthors': { en: 'Contributing Authors', es: 'Autores Colaboradores' },
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
        'book.generateInfographic': { en: 'Generate Infographic', es: 'Generar Infografía' },
        'book.readingInfographic.title': { en: 'Generate Infographic', es: 'Generar Infografía' },
        'book.readingInfographic.note': { en: "Export the selected reading's dates and statistics as a PNG.", es: 'Exporta las fechas y estadísticas de la lectura seleccionada como PNG.' },
        'book.readingInfographic.header': { en: 'Reading summary', es: 'Resumen de lectura' },
        'book.readingInfographic.started': { en: 'Started', es: 'Inicio' },
        'book.readingInfographic.finished': { en: 'Finished', es: 'Fin' },
        'book.readingInfographic.inProgress': { en: 'In progress', es: 'En curso' },
        'book.readingInfographic.overallRating': { en: 'Overall Rating', es: 'Valoración General' },
        'book.readingInfographic.avgTimeDay': { en: 'Avg Time/Day', es: 'Prom. Tiempo/Día' },
        'book.readingInfographic.noTimelineData': { en: 'No reading timeline data', es: 'Sin datos de línea temporal de lectura' },
        'book.readingInfographic.generatedWith': { en: 'Generated with Librarium v{version}', es: 'Generado con Librarium v{version}' },
        'book.readingInfographic.error': { en: 'Unable to generate the infographic.', es: 'No se pudo generar la infografía.' },
        'book.avgPagesDay':     { en: 'Avg Pages/Day',       es: 'Prom. Páginas/Día' },
        'book.mostPagesDay':    { en: 'Most Pages/Day',      es: 'Máx. Páginas/Día' },
        'book.mostTimeDay':     { en: 'Most Time/Day',       es: 'Máx. Tiempo/Día' },
        'book.avgPagesHour':    { en: 'Avg Pages/Hour',      es: 'Prom. Páginas/Hora' },
        'book.progress':        { en: 'Progress',            es: 'Progreso' },
        'book.pagesRemaining':  { en: 'Pages Remaining',     es: 'Páginas Restantes' },
        'book.estFinish':       { en: 'Est. Time to Finish', es: 'Tiempo Est. para Terminar' },
        'book.finishPlan':      { en: 'Finish Plan',          es: 'Plan de Finalización' },
        'book.finishPlanDescription': { en: 'Set an expected finish date to plan the remaining pages and reading time.', es: 'Establece una fecha prevista de finalización para planificar las páginas y el tiempo de lectura restantes.' },
        'book.expectedFinishDate': { en: 'Expected Finish Date', es: 'Fecha Prevista de Finalización' },
        'book.saveFinishDate':  { en: 'Save Date',             es: 'Guardar Fecha' },
        'book.clearFinishDate': { en: 'Clear',                 es: 'Borrar' },
        'book.expectedFinish':  { en: 'Expected Finish',       es: 'Finalización Prevista' },
        'book.finishPlanReadingDays': { en: 'Reading Days',     es: 'Días de Lectura' },
        'book.finishPlanPagesRemaining': { en: 'Pages Remaining', es: 'Páginas Restantes' },
        'book.finishPlanPace':  { en: 'Current Pace',           es: 'Ritmo Actual' },
        'book.finishPlanPagesHour': { en: 'pages/hour',         es: 'páginas/hora' },
        'book.finishPlanComplete': { en: 'All pages have been read.', es: 'Ya se han leído todas las páginas.' },
        'book.finishPlanToday': { en: 'Today',                  es: 'Hoy' },
        'book.finishPlanTodayGoalReached': { en: "Today's reading goal reached! ✅", es: '¡Objetivo de lectura de hoy alcanzado! ✅' },
        'book.finishPlanPages': { en: 'pages',                  es: 'páginas' },
        'book.finishPlanPlannedTime': { en: 'Planned time',      es: 'Tiempo planificado' },
        'book.finishPlanNoPace': { en: 'No timed sessions',     es: 'Sin sesiones cronometradas' },
        'book.finishPlanTimeReadToday': { en: 'Time read today', es: 'Tiempo leído hoy' },
        'book.finishPlanAlreadyRead': { en: 'Already read today', es: 'Ya leído hoy' },
        'book.finishPlanFollowingDays': { en: 'Each following day', es: 'Cada día siguiente' },
        'book.finishPlanDays':  { en: 'days',                   es: 'días' },
        'book.startReadingSession': { en: 'Start Reading Session', es: 'Iniciar Sesión de Lectura' },
        'book.readingSessionFor':   { en: 'Reading',               es: 'Lectura' },
        'book.readingSessionPlay':  { en: 'Play',                  es: 'Iniciar' },
        'book.readingSessionResume': { en: 'Resume',               es: 'Reanudar' },
        'book.readingSessionPause': { en: 'Pause',                 es: 'Pausar' },
        'book.readingSessionSave': { en: 'Save Session',            es: 'Guardar Sesión' },
        'book.readingSessionAddQuote': { en: 'Add Quote',             es: 'Añadir cita' },
        'book.readingSessionAddWord': { en: 'Add Word',              es: 'Añadir palabra' },
        'book.readingSessionAddThought': { en: 'Add Thought',         es: 'Añadir reflexión' },
        'book.readingSessionQuoteText': { en: 'Quote',                es: 'Cita' },
        'book.readingSessionSaveQuote': { en: 'Save Quote',            es: 'Guardar cita' },
        'book.readingSessionSaveWord': { en: 'Save Word',             es: 'Guardar palabra' },
        'book.readingSessionSaveThought': { en: 'Save Thought',       es: 'Guardar reflexión' },
        'book.readingSessionEditingLastThought': { en: 'Editing the last saved thought', es: 'Editando la última reflexión guardada' },
        'book.readingSessionWritingNewThought': { en: 'Writing a new thought', es: 'Escribiendo una nueva reflexión' },
        'book.readingSessionNewThought': { en: 'New Thought',         es: 'Nueva reflexión' },
        'book.readingSessionEditLastThought': { en: 'Edit Last Thought', es: 'Editar última reflexión' },
        'book.readingSessionSaveError': { en: 'The annotation could not be saved.', es: 'No se pudo guardar la anotación.' },
        'book.dictionarySource': { en: 'Dictionary source',        es: 'Fuente del diccionario' },
        'book.dictionaryLanguage': { en: 'Dictionary language',    es: 'Idioma del diccionario' },
        'book.dictionaryLookup': { en: 'Look Up',                  es: 'Buscar' },
        'book.dictionaryTranslate': { en: 'Translate',             es: 'Traducir' },
        'book.dictionarySourceFreeDictionary': { en: 'Free Dictionary API', es: 'Free Dictionary API' },
        'book.dictionarySourceWiktionary': { en: 'Wiktionary',       es: 'Wiktionary' },
        'book.dictionaryLanguageEnglish': { en: 'English',           es: 'Inglés' },
        'book.dictionaryLanguageSpanish': { en: 'Spanish',           es: 'Español' },
        'book.dictionaryLanguageFrench': { en: 'French',             es: 'Francés' },
        'book.dictionaryLanguageGerman': { en: 'German',             es: 'Alemán' },
        'book.dictionaryLanguageItalian': { en: 'Italian',           es: 'Italiano' },
        'book.dictionaryLanguagePortuguese': { en: 'Portuguese',     es: 'Portugués' },
        'book.dictionaryWordRequired': { en: 'Enter a word first.',  es: 'Escribe una palabra primero.' },
        'book.dictionaryLookingUp': { en: 'Looking up...',           es: 'Buscando...' },
        'book.dictionaryFoundIn': { en: 'Found in',                 es: 'Encontrado en' },
        'book.dictionaryLookupError': { en: 'Dictionary lookup failed.', es: 'La búsqueda en el diccionario ha fallado.' },
        'book.dictionaryTargetRequired': { en: 'Choose a translation language first.', es: 'Elige primero un idioma de traducción.' },
        'book.dictionaryTranslationError': { en: 'Translation failed.', es: 'La traducción ha fallado.' },
        'book.quoteRequired': { en: 'Quote text is required.', es: 'El texto de la cita es obligatorio.' },
        'book.thoughtRequired': { en: 'Thought text is required.',  es: 'El texto de la reflexión es obligatorio.' },
        'book.readingSessionClassificationSave': { en: 'Save Classification', es: 'Guardar clasificación' },
        'book.readingSessionClassificationError': { en: 'Classification could not be saved. Try again.', es: 'No se pudo guardar la clasificación. Inténtalo de nuevo.' },
        'book.readingSessionStartPage': { en: 'Start Page',          es: 'Página Inicial' },
        'book.readingSessionEndPage': { en: 'End Page',              es: 'Página Final' },
        'book.readingSessionPace': { en: 'Average pace',             es: 'Ritmo medio' },
        'book.readingSessionPagesPerHour': { en: 'pages/hour',        es: 'páginas/hora' },
        'book.readingSessionNoPace': { en: 'End page estimate unavailable until this reading has a pace.', es: 'La estimación de la página final estará disponible cuando esta lectura tenga un ritmo.' },
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
        'book.colTime':         { en: 'Time',                es: 'Tiempo' },
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
        'form.apply':    { en: 'Apply',    es: 'Aplicar' },
        'form.cancel':   { en: 'Cancel',   es: 'Cancelar' },

        // ── Authors page ────────────────────────────────────────────────
        'authors.title':     { en: 'Authors',       es: 'Autores' },
        'authors.sortBy':    { en: 'Sort by:',      es: 'Ordenar por:' },
        'authors.sortName':  { en: 'Name',          es: 'Nombre' },
        'authors.sortBooks': { en: 'Number of Books', es: 'Número de Libros' },
        'authors.sortBooksRead': { en: 'Books Read',  es: 'Libros Leídos' },
        'authors.sortTimeRead':  { en: 'Time Read',   es: 'Tiempo Leído' },
        'authors.noBooksRead':   { en: 'No books read', es: 'Ningún libro leído' },
        'authors.oneBookRead':   { en: '1 book read',   es: '1 libro leído' },
        'authors.booksReadSuffix': { en: 'books read', es: 'libros leídos' },
        'authors.penNames':  { en: 'Pen names:',    es: 'Seudónimos:' },
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
        'authorDetail.penNames':      { en: 'Pen Names',           es: 'Seudónimos' },
        'authorDetail.publishedAs':   { en: 'Published as',        es: 'Publicado como' },
        'authorDetail.empty':         { en: 'No books found for this author.', es: 'No se encontraron libros de este autor.' },
        'authorDetail.quotes':        { en: 'Quotes',              es: 'Citas' },

        // ── Edit author ─────────────────────────────────────────────────
        'editAuthor.backToAuthor':  { en: '← Back to Author',     es: '← Volver al Autor' },
        'editAuthor.title':         { en: 'Edit Author Details',  es: 'Editar Detalles del Autor' },
        'editAuthor.photo':         { en: 'Photo',                es: 'Foto' },
        'editAuthor.removePhoto':   { en: 'Remove current photo', es: 'Eliminar foto actual' },
        'editAuthor.replacePhoto':  { en: 'Replace Photo',        es: 'Reemplazar Foto' },
        'editAuthor.uploadPhoto':   { en: 'Upload Photo',         es: 'Subir Foto' },
        'editAuthor.identity':      { en: 'Identity',             es: 'Identidad' },
        'editAuthor.penNameOf':     { en: 'Pen name of',          es: 'Seudónimo de' },
        'editAuthor.penNameOfHint': { en: 'Leave empty if this is the main author identity.', es: 'Déjalo vacío si esta es la identidad principal del autor.' },
        'editAuthor.penNames':      { en: 'Pen names',            es: 'Seudónimos' },
        'editAuthor.penNamesHint':  { en: 'Separate multiple pen names with semicolons.', es: 'Separa varios seudónimos con punto y coma.' },
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

        // ── Markdown toolbar ────────────────────────────────────────────
        'md.bold':          { en: 'Bold',             es: 'Negrita' },
        'md.italic':        { en: 'Italic',           es: 'Cursiva' },
        'md.strike':        { en: 'Strikethrough',    es: 'Tachado' },
        'md.h2':            { en: 'Heading 2',        es: 'Encabezado 2' },
        'md.h3':            { en: 'Heading 3',        es: 'Encabezado 3' },
        'md.ul':            { en: 'Bulleted list',    es: 'Lista con viñetas' },
        'md.ol':            { en: 'Numbered list',    es: 'Lista numerada' },
        'md.quote':         { en: 'Blockquote',       es: 'Cita en bloque' },
        'md.link':          { en: 'Insert link',      es: 'Insertar enlace' },
        'md.code':          { en: 'Inline code',      es: 'Código en línea' },
        'md.codeblock':     { en: 'Code block',       es: 'Bloque de código' },
        'md.hr':            { en: 'Horizontal rule',  es: 'Línea horizontal' },

        // ── New book & Edit metadata (shared) ───────────────────────────
        'bookForm.backToLibrary':   { en: '← Back to Library',   es: '← Volver a la Biblioteca' },
        'bookForm.backToBook':      { en: '← Back to Book',      es: '← Volver al Libro' },
        'bookForm.addNewBook':      { en: 'Add New Book',        es: 'Añadir Nuevo Libro' },
        'bookForm.editMetadata':    { en: 'Edit Metadata',       es: 'Editar Metadatos' },
        'bookForm.basicInfo':       { en: 'Basic Information',   es: 'Información Básica' },
        'bookForm.classification':  { en: 'Classification',       es: 'Clasificación' },
        'bookForm.title':           { en: 'Title',               es: 'Título' },
        'bookForm.titleReq':        { en: 'Title *',             es: 'Título *' },
        'bookForm.subtitle':        { en: 'Subtitle',            es: 'Subtítulo' },
        'bookForm.authorReq':       { en: 'Author(s) *',        es: 'Autor(es) *' },
        'bookForm.authorLabel':     { en: 'Author(s)',           es: 'Autor(es)' },
        'bookForm.genres':          { en: 'Genres',              es: 'Géneros' },
        'bookForm.tags':            { en: 'Tags',                es: 'Etiquetas' },
        'bookForm.themes':          { en: 'Themes',              es: 'Temas' },
        'bookForm.settings':        { en: 'Settings',            es: 'Ambientaciones' },
        'bookForm.historicalPeriods': { en: 'Historical Periods', es: 'Períodos Históricos' },
        'bookForm.subjects':        { en: 'Subjects',            es: 'Materias' },
        'bookForm.audiences':       { en: 'Audiences',           es: 'Públicos' },
        'bookForm.subgenres':       { en: 'Subgenres',           es: 'Subgéneros' },
        'bookForm.forms':           { en: 'Forms',               es: 'Formas' },
        'bookForm.genreDescription': { en: "The broadest literary or factual category: what kind of book it is. Use only a few broad, reusable values.", es: 'La categoría literaria o factual más amplia: qué tipo de libro es. Usa pocos valores amplios y reutilizables.' },
        'bookForm.subgenreDescription': { en: 'A more specific literary, academic, or stylistic classification, including movements, disciplines, or national literatures.', es: 'Una clasificación literaria, académica o estilística más específica, como movimientos, disciplinas o literaturas nacionales.' },
        'bookForm.formDescription': { en: 'The way a work is written or presented, such as a novel, essay, diary, memoir, or letters.', es: 'La manera en que está escrita o presentada una obra, como novela, ensayo, diario, memorias o cartas.' },
        'bookForm.themesDescription': { en: 'Abstract ideas, emotions, values, conflicts, and philosophical questions explored by the work, never concrete people, places, events, or objects.', es: 'Ideas abstractas, emociones, valores, conflictos y preguntas filosóficas que explora la obra; nunca personas, lugares, acontecimientos u objetos concretos.' },
        'bookForm.settingDescription': { en: "Geographical places or environments where the story happens or where the book's subject is situated. Do not use historical periods.", es: 'Lugares o entornos geográficos donde sucede la historia o se sitúa el tema del libro. No uses períodos históricos.' },
        'bookForm.historicalPeriodDescription': { en: 'The most specific meaningful era or chronological period when the story or subject takes place.', es: 'La época o período cronológico significativo más específico en el que transcurre la historia o se sitúa el tema.' },
        'bookForm.subjectDescription': { en: 'Concrete people, places, events, disciplines, works, institutions, species, or topics the book is about. Keep abstract ideas in Themes.', es: 'Personas, lugares, acontecimientos, disciplinas, obras, instituciones, especies o temas concretos sobre los que trata el libro. Las ideas abstractas pertenecen a Temas.' },
        'bookForm.audienceDescription': { en: "The intended readership, such as children, young adults, adults, or academic readers; never the book's quality or difficulty.", es: 'El público lector al que va dirigido el libro, como niños, jóvenes, adultos o lectores académicos; no describe su calidad o dificultad.' },
        'bookForm.addGenre':        { en: 'Add a genre...',       es: 'Añadir un género...' },
        'bookForm.addTag':          { en: 'Add a tag...',         es: 'Añadir una etiqueta...' },
        'bookForm.addTheme':        { en: 'Add a theme...',       es: 'Añadir un tema...' },
        'bookForm.addSetting':      { en: 'Add a setting...',     es: 'Añadir una ambientación...' },
        'bookForm.addHistoricalPeriod': { en: 'Add a historical period...', es: 'Añadir un período histórico...' },
        'bookForm.addSubject':      { en: 'Add a subject...',     es: 'Añadir una materia...' },
        'bookForm.addAudience':     { en: 'Add an audience...',   es: 'Añadir un público...' },
        'bookForm.addSubgenre':     { en: 'Add a subgenre...',    es: 'Añadir un subgénero...' },
        'bookForm.addForm':         { en: 'Add a form...',        es: 'Añadir una forma...' },
        'bookForm.classificationHint': { en: 'Type a value and press Enter or semicolon to add it. Existing values are suggested as you type. You can also drag a value to another category.', es: 'Escribe un valor y pulsa Intro o punto y coma para añadirlo. Los valores existentes aparecen como sugerencias. También puedes arrastrar un valor a otra categoría.' },
        'bookForm.tagsPlaceholder': { en: 'e.g. cozy; dark; slow-burn', es: 'ej. acogedor; oscuro; lento' },
        'bookForm.status':          { en: 'Status',              es: 'Estado' },
        'bookForm.statusReading':   { en: 'Reading',             es: 'Leyendo' },
        'bookForm.statusFinished':  { en: 'Finished',            es: 'Terminado' },
        'bookForm.statusNotStarted':{ en: 'Not Started',         es: 'Sin Empezar' },
        'bookForm.statusAbandoned': { en: 'Abandoned',           es: 'Abandonado' },
        'bookForm.statusWishlist':  { en: 'Wishlist',            es: 'Lista de Deseos' },
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
        'bookForm.bindingSoftcover':{ en: 'Softcover',          es: 'Tapa Flexible' },
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
        'bookForm.forewordAuthor':  { en: 'Foreword/Introduction Author(s)', es: 'Autor(es) del Prólogo/Introducción' },
        'bookForm.epilogueAuthor':  { en: 'Epilogue Author(s)', es: 'Autor(es) del Epílogo' },
        'bookForm.contributingAuthor': { en: 'Contributing Author(s)', es: 'Autor(es) Colaborador(es)' },
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
        'bookForm.editionHint':     { en: 'Work-level fields (author, original work info, classification) are pre-filled. Edition-level fields (language, publisher, pages, cover) are for this specific edition.', es: 'Los campos a nivel de obra (autor, información original y clasificación) están pre-rellenados. Los campos a nivel de edición (idioma, editorial, páginas, portada) son para esta edición específica.' },
        'bookForm.sharedClassificationHint': { en: 'Classification is shared by all editions of this work. Changes here update every linked edition.', es: 'La clasificación se comparte entre todas las ediciones de esta obra. Los cambios aquí actualizan cada edición vinculada.' },
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
        'sources.type':       { en: 'Type',        es: 'Tipo' },
        'sources.locationUrl':{ en: 'Location / URL', es: 'Ubicación / URL' },
        'sources.notes':      { en: 'Notes',       es: 'Notas' },
        'sources.actions':    { en: 'Actions',     es: 'Acciones' },
        'sources.addNew':     { en: 'Add New Source', es: 'Añadir Nueva Fuente' },
        'sources.addBtn':     { en: '+ Add Source',   es: '+ Añadir Fuente' },
        'sources.name':       { en: 'Name',       es: 'Nombre' },
        'sources.nameReq':    { en: 'Name *',     es: 'Nombre *' },
        'sources.location':   { en: 'Location',    es: 'Ubicación' },
        'sources.address':    { en: 'Address',     es: 'Dirección' },
        'sources.latitude':   { en: 'Latitude',    es: 'Latitud' },
        'sources.longitude':  { en: 'Longitude',   es: 'Longitud' },
        'sources.coordinates':{ en: 'Coordinates', es: 'Coordenadas' },
        'sources.closed':     { en: 'Permanently Closed', es: 'Cerrado Permanentemente' },
        'sources.closedCheckbox': { en: 'Permanently closed', es: 'Cerrado permanentemente' },
        'sources.mapTitle':   { en: 'Place Map',   es: 'Mapa de Lugares' },
        'sources.mapDesc':    { en: 'Physical stores and libraries with coordinates appear here.', es: 'Las tiendas físicas y bibliotecas con coordenadas aparecen aquí.' },
        'sources.mapEmpty':   { en: 'Add coordinates to your physical stores and libraries to display them on the map.', es: 'Añade coordenadas a tus tiendas físicas y bibliotecas para mostrarlas en el mapa.' },
        'sources.mapUnavailable': { en: 'The map library could not be loaded.', es: 'No se pudo cargar la biblioteca del mapa.' },
        'sources.placeSectionHint': { en: 'Address, closure status, and map coordinates are available for place-based sources.', es: 'Las fuentes basadas en lugares admiten dirección, estado de cierre y coordenadas para el mapa.' },
        'sources.generalSectionHint': { en: 'Use these entries for online stores and people you buy from or borrow from.', es: 'Usa estas entradas para tiendas online y personas a las que compras o de quienes tomas prestado.' },
        'sources.missingCoordinates': { en: 'missing coordinates', es: 'sin coordenadas' },
        'sources.mapLink':    { en: 'Map',         es: 'Mapa' },
        'sources.openInMap':  { en: 'Show in Map', es: 'Mostrar en el mapa' },
        'sources.details':    { en: 'Address / URL',     es: 'Dirección / URL' },
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
        'stats.authorsReadByYear':  { en: 'Authors Read by Year',      es: 'Autores Leídos por Año' },
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
        'stats.genreCloud':         { en: 'Genre Cloud',               es: 'Nube de Géneros' },
        'stats.tagCloud':           { en: 'Tag Cloud',                 es: 'Nube de Etiquetas' },
        'stats.themeCloud':         { en: 'Theme Cloud',               es: 'Nube de Temas' },
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
        'yearBooks.generateInfographic':    { en: 'Generate Infographic',   es: 'Generar Infografía' },
        'yearBooks.infographic.title':      { en: 'Generate Infographic',   es: 'Generar Infografía' },
        'yearBooks.infographic.width':      { en: 'Width (px)',             es: 'Ancho (px)' },
        'yearBooks.infographic.height':     { en: 'Height (px)',            es: 'Alto (px)' },
        'yearBooks.infographic.booksPerRow': { en: 'Books per row (optional)', es: 'Libros por fila (opcional)' },
        'yearBooks.infographic.autoHeightHint': { en: 'Leave this empty to set height manually. Fill it in to infer height from the width.', es: 'Déjalo vacío para fijar la altura manualmente. Complétalo para inferir la altura a partir del ancho.' },
        'yearBooks.infographic.cancel':     { en: 'Cancel',                 es: 'Cancelar' },
        'yearBooks.infographic.generate':   { en: 'Generate & Download',    es: 'Generar y Descargar' },
        'yearBooks.infographic.header':     { en: 'Books Read',             es: 'Libros Leídos' },
        'yearBooks.infographic.bookSingular': { en: 'book',                 es: 'libro' },
        'yearBooks.infographic.bookPlural':   { en: 'books',                es: 'libros' },
        'yearBooks.infographic.pageSingular': { en: 'page',                 es: 'página' },
        'yearBooks.infographic.pagePlural':   { en: 'pages',                es: 'páginas' },
        'yearBooks.infographic.readingDaySingular': { en: 'reading day',    es: 'día de lectura' },
        'yearBooks.infographic.readingDayPlural':   { en: 'reading days',   es: 'días de lectura' },
        'yearBooks.infographic.generatedWith': { en: 'Generated with Librarium v{version}', es: 'Generado con Librarium v{version}' },

        // ── Year time ──────────────────────────────────────────────────
        'yearTime.backToGlobal':   { en: '← Back to Global Stats',     es: '← Volver a Estadísticas Globales' },
        'yearTime.title':          { en: 'Time Read in',               es: 'Tiempo Leído en' },
        'yearTime.booksLabel':     { en: 'with tracked or inferred time', es: 'con tiempo registrado o inferido' },
        'yearTime.totalTime':      { en: 'Total Time:',                es: 'Tiempo Total:' },
        'yearTime.timeRead':       { en: 'Time Read',                  es: 'Tiempo Leído' },
        'yearTime.readingDays':    { en: 'Reading Days',               es: 'Días de Lectura' },
        'yearTime.empty':          { en: 'No tracked reading time was found in', es: 'No se encontró tiempo de lectura registrado en' },

        // ── Year authors ───────────────────────────────────────────────
        'yearAuthors.backToGlobal': { en: '← Back to Global Stats',    es: '← Volver a Estadísticas Globales' },
        'yearAuthors.title':        { en: 'Authors Read in',           es: 'Autores Leídos en' },
        'yearAuthors.sortBy':       { en: 'Sort by:',                  es: 'Ordenar por:' },
        'yearAuthors.sortName':     { en: 'Name',                      es: 'Nombre' },
        'yearAuthors.sortBooks':    { en: 'Number of Books',           es: 'Número de Libros' },
        'yearAuthors.sortDays':     { en: 'Reading Days',              es: 'Días de Lectura' },
        'yearAuthors.sortTime':     { en: 'Time Read',                 es: 'Tiempo Leído' },
        'yearAuthors.orderBy':      { en: 'Order:',                    es: 'Orden:' },
        'yearAuthors.orderAsc':     { en: 'Ascending',                 es: 'Ascendente' },
        'yearAuthors.orderDesc':    { en: 'Descending',                es: 'Descendente' },
        'yearAuthors.booksLabel':   { en: 'Number of Books',           es: 'Número de Libros' },
        'yearAuthors.readingDaysLabel': { en: 'Reading Days',          es: 'Días de Lectura' },
        'yearAuthors.timeReadLabel': { en: 'Time Read',                es: 'Tiempo Leído' },
        'yearAuthors.empty':        { en: 'No authors were read in',   es: 'No se leyeron autores en' },

        // ── Year bought ─────────────────────────────────────────────────
        'yearBought.backToGlobal': { en: '← Back to Global Stats',     es: '← Volver a Estadísticas Globales' },
        'yearBought.title':        { en: 'Books Bought in',            es: 'Libros Comprados en' },
        'yearBought.bought':       { en: 'bought',                     es: 'comprado(s)' },
        'yearBought.sortBy':       { en: 'Sort by:',                   es: 'Ordenar por:' },
        'yearBought.sortDate':     { en: 'Date',                       es: 'Fecha' },
        'yearBought.sortTitle':    { en: 'Title',                      es: 'Título' },
        'yearBought.sortAuthor':   { en: 'Author',                     es: 'Autor' },
        'yearBought.sortPrice':    { en: 'Price',                      es: 'Precio' },
        'yearBought.sourceLabel':  { en: 'Source',                     es: 'Origen' },
        'yearBought.empty':        { en: 'No books were bought in',    es: 'No se compraron libros en' },
        'yearBought.gift':         { en: 'Gift',                       es: 'Regalo' },

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
        'dash.editWord':            { en: 'Edit word',              es: 'Editar palabra' },
        'dash.timeReadSuffix':      { en: 'read',                   es: 'leído' },
        'dash.timeLeft':             { en: 'left',                   es: 'restantes' },
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
        'dash.lastBooksAcquired':   { en: 'Last Books Acquired',   es: 'Últimos Libros Adquiridos' },
        'dash.topRated':            { en: 'Top Rated',             es: 'Mejor Valorados' },
        'dash.records':             { en: 'Records',               es: 'Récords' },
        'dash.formatSource':        { en: 'Format & Source',       es: 'Formato y Fuente' },
        'dash.byFormat':            { en: 'By Format',             es: 'Por Formato' },
        'dash.bySource':            { en: 'By Source',             es: 'Por Fuente' },
        'dash.genreCloud':          { en: 'Genre Cloud',           es: 'Nube de Géneros' },
        'dash.tagCloud':            { en: 'Tag Cloud',             es: 'Nube de Etiquetas' },
        'dash.themeCloud':          { en: 'Theme Cloud',           es: 'Nube de Temas' },
        'dash.settingCloud':        { en: 'Setting Cloud',         es: 'Nube de Ambientaciones' },
        'dash.historicalPeriodCloud': { en: 'Historical Period Cloud', es: 'Nube de Períodos Históricos' },
        'dash.subjectCloud':        { en: 'Subject Cloud',         es: 'Nube de Materias' },
        'dash.audienceCloud':       { en: 'Audience Cloud',        es: 'Nube de Públicos' },
        'dash.subgenreCloud':       { en: 'Subgenre Cloud',        es: 'Nube de Subgéneros' },
        'dash.formCloud':           { en: 'Form Cloud',             es: 'Nube de Formas' },
        'dash.classification':     { en: 'Classification',        es: 'Clasificación' },
        'dash.downloadTaxonomyAudit': { en: 'Download taxonomy audit', es: 'Descargar auditoría taxonómica' },
        'dash.downloadTaxonomyAuditTitle': { en: 'Download every taxonomy value as CSV', es: 'Descargar todos los valores taxonómicos como CSV' },
        'dash.noTaxonomyValues':    { en: 'No values yet.',        es: 'Aún no hay valores.' },
        'dash.downloadGenres':      { en: 'Download all genres',    es: 'Descargar todos los géneros' },
        'dash.downloadGenresTitle': { en: 'Download all genres as CSV', es: 'Descargar todos los géneros como CSV' },
        'dash.downloadTags':        { en: 'Download all tags',      es: 'Descargar todas las etiquetas' },
        'dash.downloadTagsTitle':   { en: 'Download all tags as CSV', es: 'Descargar todas las etiquetas como CSV' },
        'dash.authorSpotlight':     { en: 'Author Spotlight',      es: 'Autor Destacado' },
        'dash.booksInLibrary':      { en: 'books in your library', es: 'libros en tu biblioteca' },
        'dash.seriesProgress':      { en: 'Series Progress',       es: 'Progreso de Series' },
        'dash.languages':           { en: 'Languages',             es: 'Idiomas' },
        'dash.readIn':              { en: 'You read in',           es: 'Lees en' },
        'dash.languages2':          { en: 'languages',             es: 'idiomas' },
        'dash.tbrPile':             { en: 'TBR Pile',              es: 'Pendientes de Leer' },
        'dash.booksWaiting':        { en: 'books waiting',         es: 'libros esperando' },
        'dash.show':                { en: 'Show:',                es: 'Mostrar:' },
        'dash.tbrSortRandom':       { en: 'Random Set',           es: 'Selección Aleatoria' },
        'dash.tbrSortRecent':       { en: 'Most Recently Acquired', es: 'Adquiridos Más Recientemente' },
        'dash.tbrSortOldest':       { en: 'Least Recently Acquired', es: 'Adquiridos Menos Recientemente' },
        'dash.wishlistPile':        { en: 'Wishlist',              es: 'Lista de Deseos' },
        'dash.booksToBuy':          { en: 'books you want to buy', es: 'libros que quieres comprar' },
        'dash.libraryHealth':       { en: 'Library Health',        es: 'Salud de la Biblioteca' },
        'dash.unratedBooks':        { en: 'finished books unrated',es: 'libros terminados sin valorar' },
        'dash.noCover':             { en: 'books without cover',   es: 'libros sin portada' },
        'dash.noPhoto':             { en: 'authors without photo', es: 'autores sin foto' },
        'dash.noTags':              { en: 'books without tags',    es: 'libros sin etiquetas' },
        'dash.noGenres':            { en: 'books without genres',  es: 'libros sin géneros' },
        'dash.noThemes':            { en: 'books without themes',  es: 'libros sin temas' },
        'dash.noSettings':          { en: 'books without settings', es: 'libros sin ambientaciones' },
        'dash.noHistoricalPeriods': { en: 'books without historical periods', es: 'libros sin períodos históricos' },
        'dash.noSubjects':          { en: 'books without subjects', es: 'libros sin materias' },
        'dash.noAudiences':         { en: 'books without audiences', es: 'libros sin públicos' },
        'dash.noSubgenres':         { en: 'books without subgenres', es: 'libros sin subgéneros' },
        'dash.noForms':             { en: 'books without forms', es: 'libros sin formas' },
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
        'book.synonyms':            { en: 'Synonyms',              es: 'Sinónimos' },
        'book.synonymsPlaceholder': { en: 'Synonyms...',           es: 'Sinónimos...' },
        'book.translation':         { en: 'Translation',           es: 'Traducción' },
        'book.translationPlaceholder': { en: 'Translation...',     es: 'Traducción...' },
        'book.translationLanguagePlaceholder': { en: 'Translation language', es: 'Idioma de traducción' },

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

        // Accessible labels
        document.querySelectorAll('[data-i18n-aria-label]').forEach(function (el) {
            var key = el.getAttribute('data-i18n-aria-label');
            var entry = translations[key];
            if (entry) el.setAttribute('aria-label', entry[lang] || entry['en']);
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
        if (typeof window.updateLibrariumThemeControl === 'function') {
            window.updateLibrariumThemeControl();
        }

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

    // ── Markdown toolbar for textareas ───────────────────────────────
    function initMarkdownToolbar(textareaId) {
        var ta = document.getElementById(textareaId);
        if (!ta) return;

        var toolbar = document.createElement('div');
        toolbar.className = 'rt-toolbar';

        var buttons = [
            { label: '<b>B</b>',  key: 'md.bold',      wrap: '**' },
            { label: '<i>I</i>',  key: 'md.italic',    wrap: '*' },
            { label: '<s>S</s>',  key: 'md.strike',    wrap: '~~' },
            { sep: true },
            { label: 'H2',        key: 'md.h2',        prefix: '## ' },
            { label: 'H3',        key: 'md.h3',        prefix: '### ' },
            { sep: true },
            { label: '• ―',       key: 'md.ul',        prefix: '- ' },
            { label: '1. ―',      key: 'md.ol',        prefix: '1. ' },
            { label: '❝',         key: 'md.quote',     prefix: '> ' },
            { sep: true },
            { label: '🔗',        key: 'md.link',      action: 'link' },
            { label: '&lt;&gt;',  key: 'md.code',      wrap: '`' },
            { label: '{ }',       key: 'md.codeblock', action: 'codeblock' },
            { label: '—',         key: 'md.hr',        action: 'hr' },
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
                handleMarkdownAction(ta, b);
            });
            toolbar.appendChild(btn);
        });

        ta.parentNode.insertBefore(toolbar, ta);
    }

    function handleMarkdownAction(ta, b) {
        var start = ta.selectionStart;
        var end   = ta.selectionEnd;
        var text  = ta.value;
        var sel   = text.substring(start, end);
        var replacement;
        var cursorOffset = 0;

        if (b.action === 'link') {
            var url = prompt(t('md.link'), 'https://');
            if (!url) return;
            replacement = '[' + (sel || 'link') + '](' + url + ')';
        } else if (b.action === 'codeblock') {
            replacement = '```\n' + (sel || '') + '\n```';
        } else if (b.action === 'hr') {
            var before = text.substring(0, start);
            var needNewline = before.length > 0 && !before.endsWith('\n');
            replacement = (needNewline ? '\n' : '') + '---\n';
        } else if (b.wrap) {
            replacement = b.wrap + sel + b.wrap;
            if (!sel) cursorOffset = -b.wrap.length;
        } else if (b.prefix) {
            if (sel) {
                var lines = sel.split('\n');
                replacement = lines.map(function(l) { return b.prefix + l; }).join('\n');
            } else {
                replacement = b.prefix;
            }
        } else {
            replacement = sel;
        }

        ta.value = text.substring(0, start) + replacement + text.substring(end);
        ta.focus();
        var cursorPos = start + replacement.length + cursorOffset;
        ta.setSelectionRange(cursorPos, cursorPos);
        ta.dispatchEvent(new Event('input'));
    }

    // Expose for usage in inline scripts
    window.librariumI18n = { t: t, getLang: getLang, setLang: setLang, apply: applyTranslations, applyTranslations: applyTranslations, initRichTextToolbar: initRichTextToolbar, initMarkdownToolbar: initMarkdownToolbar, formatDisplayDate: formatDisplayDate, formatDates: formatDates };
})();
