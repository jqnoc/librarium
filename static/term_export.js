(function () {
    window.downloadTermList = function (kind, counts) {
        var rows = [['Term', 'Book count']];
        Object.entries(counts || {})
            .sort(function (a, b) {
                return a[0].localeCompare(b[0], undefined, { sensitivity: 'base' });
            })
            .forEach(function (entry) {
                rows.push([entry[0], String(entry[1])]);
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