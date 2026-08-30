document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-toast]').forEach(function (toast) {
        var cerrar = function () {
            toast.classList.add('toast-hide');
            setTimeout(function () { toast.remove(); }, 400);
        };
        toast.querySelector('[data-toast-close]').addEventListener('click', cerrar);
        setTimeout(cerrar, 5000);
    });
});