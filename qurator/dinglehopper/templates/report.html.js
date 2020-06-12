function find_diff_class(classes) {
    return classes.split(/\s+/).find(x => x.match(/.diff\d.*/));
}

$(document).ready(function() {
    $('.diff').mouseover(function() {
        let c = find_diff_class($(this).attr('class'));
        $('.' + c).addClass('diff-highlight');

        segment_id = $(this).attr('data-segment-id');
        $('#status-box').text(segment_id);
    });
    $('.diff').mouseout(function() {
        let c = find_diff_class($(this).attr('class'));
        $('.' + c).removeClass('diff-highlight');

        $('#status-box').text('');
    });
});
