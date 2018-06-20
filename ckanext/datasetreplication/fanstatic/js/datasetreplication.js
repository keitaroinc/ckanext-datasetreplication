$(document).ready(function () {

    $('.dataset-upload-form').on('show.bs.modal', function () {
        // This is a hack, and must be implemented in a better way.
        $(this).find('.image-upload .btn:last-child').addClass('hidden');
    });

});