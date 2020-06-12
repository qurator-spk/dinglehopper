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
});
