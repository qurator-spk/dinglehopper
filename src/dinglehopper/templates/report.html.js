function find_diff_class(classes) {
    return $('.' + classes.split(/\s+/).find(x => x.match(/.diff\d.*/)));
}

$(document).ready(function() {
    /* Enable Bootstrap tooltips */
    $('[data-toggle="tooltip"]').tooltip();

    $('.diff').mouseover(function() {
        find_diff_class($(this).attr('class')).addClass('diff-highlight');
    });
    $('.diff').mouseout(function() {
        find_diff_class($(this).attr('class')).removeClass('diff-highlight');
    });

    /* Sort this column of the table */
    $('th').click(function () {
        var table = $(this).closest('table');
        var rows = table.find('tbody > tr').toArray().sort(compareRows($(this).index()));
        this.asc = !this.asc;
        if (!this.asc) {
            rows = rows.reverse();
        }
        for (var i = 0; i < rows.length; i++) {
            table.children('tbody').append(rows[i]);
        }
    });

    function compareRows(index) {
        return function (row1, row2) {
            var cell1 = $(row1).children('td').eq(index).text().toLowerCase();
            var cell2 = $(row2).children('td').eq(index).text().toLowerCase();
            return cell1.localeCompare(cell2, undefined, {
                numeric: true,
                sensitivity: 'base'
            });
        }
    }
});
