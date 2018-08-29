var initialize = function () {
    $('input[name="text"]').on('keypress', function () {
        $('.errorlist').hide();
    });
};