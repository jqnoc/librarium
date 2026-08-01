(function () {
    window.downloadTermList = function (kind, counts, termBooks) {
        var rows = [['Term', 'Book count', 'Book titles']];
        Object.entries(counts || {})
            .sort(function (a, b) {
                return a[0].localeCompare(b[0], undefined, { sensitivity: 'base' });
            })
            .forEach(function (entry) {
                var titles = termBooks && Array.isArray(termBooks[entry[0]])
                    ? termBooks[entry[0]].slice().sort(function (a, b) {
                        return a.localeCompare(b, undefined, { sensitivity: 'base' });
                    })
                    : [];
                rows.push([entry[0], String(entry[1]), titles.join('; ')]);
            });

        var csv = rows.map(function (row) {
            return row.map(function (value) {
                var text = String(value).replace(/"/g, '""');
                return '"' + text + '"';
            }).join(',');
        }).join('\r\n') + '\r\n';

        var blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' });
        var url = URL.createObjectURL(blob);
        var link = document.createElement('a');
        link.href = url;
        link.download = 'librarium-' + kind + '.csv';
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(function () { URL.revokeObjectURL(url); }, 0);
    };
})();