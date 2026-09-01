(function () {
    var contenedor = document.getElementById('tabla-contenedor');
    var form = document.getElementById('form-filtros');
    var inputQ = document.getElementById('filtro-q');

    if (!contenedor || !form) return;

    var ordenActual = 'nombre_asc';
    var timeout = null;

    function construirURL(page) {
        var params = new URLSearchParams();
        if (inputQ.value.trim()) params.set('q', inputQ.value.trim());
        params.set('orden', ordenActual);
        if (page) params.set('page', page);
        return window.location.pathname + '?' + params.toString();
    }

    function cargar(page) {
        fetch(construirURL(page), {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(function (resp) {
                if (!resp.ok) throw new Error('Error ' + resp.status);
                return resp.text();
            })
            .then(function (html) {
                contenedor.innerHTML = html;
                if (page) window.history.replaceState(null, '', construirURL(page));
            })
            .catch(function (err) { console.error('Error al cargar clientes:', err); });
    }

    inputQ.addEventListener('input', function () {
        clearTimeout(timeout);
        timeout = setTimeout(function () { cargar(1); }, 300);
    });

    contenedor.addEventListener('click', function (e) {
        var boton = e.target.closest('[data-page]');
        if (boton) { cargar(boton.getAttribute('data-page')); return; }

        var ordenBtn = e.target.closest('[data-orden]');
        if (ordenBtn) {
            var clave = ordenBtn.getAttribute('data-orden');
            var dirAsc = (ordenActual === clave + '_desc');
            ordenActual = clave + (dirAsc ? '_asc' : '_desc');
            cargar(1);
        }
    });
})();
