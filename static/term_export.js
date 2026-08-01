(function () {
    function escapeCsv(rows) {
        return rows.map(function (row) {
            return row.map(function (value) {
                var text = String(value).replace(/"/g, '""');
                return '"' + text + '"';
            }).join(',');
        }).join('\r\n') + '\r\n';
    }

    window.downloadTaxonomyAudit = function (taxonomyAudit) {
        var rows = [['Classification type', 'Value', 'Book count', 'Book titles']];
        (taxonomyAudit || []).forEach(function (classification) {
            Object.entries(classification.counts || {})
                .sort(function (a, b) {
                    return a[0].localeCompare(b[0], undefined, { sensitivity: 'base' });
                })
                .forEach(function (entry) {
                    var titles = classification.books && Array.isArray(classification.books[entry[0]])
                        ? classification.books[entry[0]].slice().sort(function (a, b) {
                            return a.localeCompare(b, undefined, { sensitivity: 'base' });
                        })
                        : [];
                    rows.push([classification.type, entry[0], String(entry[1]), titles.join('; ')]);
                });
        });

        var blob = new Blob(['\ufeff' + escapeCsv(rows)], { type: 'text/csv;charset=utf-8' });
        var url = URL.createObjectURL(blob);
        var link = document.createElement('a');
        link.href = url;
        link.download = 'librarium-taxonomy-audit.csv';
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(function () { URL.revokeObjectURL(url); }, 0);
    };
})();