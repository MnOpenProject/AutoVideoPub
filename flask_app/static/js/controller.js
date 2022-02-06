$('#btnSpiderStart').on('click', function () {
    var $btn = $(this).button('loading')
    // business logic...
    $btn.button('reset')
})