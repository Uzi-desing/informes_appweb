// Lightbox para visualizar en grande las imágenes de las piezas rechazadas y cerrarlo con la X, el fondo o la tecla Escape
(function () {
    var modal = document.getElementById('modal-imagen');
    var modalImg = document.getElementById('modal-img');
    var modalCerrar = document.getElementById('modal-cerrar');
    var modalFondo = document.getElementById('modal-fondo');

    if (!modal || !modalImg || !modalCerrar || !modalFondo) return;

    function abrirModal(src) {
        modalImg.src = src;
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';
    }

    function cerrarModal() {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        modalImg.src = '';
        document.body.style.overflow = '';
    }

    document.addEventListener('click', function (e) {
        var boton = e.target.closest('[data-imagen]');
        if (boton) { abrirModal(boton.getAttribute('data-imagen')); return; }

        if (e.target === modalCerrar || e.target === modalFondo) {
            cerrarModal();
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') cerrarModal();
    });
})();