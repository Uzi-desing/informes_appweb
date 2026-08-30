document.addEventListener('DOMContentLoaded', function () {
    var container = document.getElementById('formset-container');
    var addBtn = document.getElementById('add-form-btn');
    var totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');
    var emptyFormTemplate = document.getElementById('empty-form').innerHTML;
    var bannerMensajes = document.getElementById('banner-mensajes');
    var pzCountLabel = document.getElementById('pz-count-label');
    var pzProgressFill = document.getElementById('pz-progress-fill');
    var pzDoneLabel = document.getElementById('pz-done-label');
    var CAMPOS_REQUERIDOS = ['pieza', 'categoria_dano', 'cantidad', 'imagen'];

    function actualizarProgreso() {
        var formsVisibles = Array.from(container.querySelectorAll('.pieza-form'))
            .filter(function (div) { return !div.hidden; });
        var total = formsVisibles.length;

        if (total === 0) {
            pzCountLabel.textContent = '0 piezas';
            pzProgressFill.style.width = '0%';
            pzDoneLabel.textContent = '—';
            return;
        }

        var completas = 0;
        formsVisibles.forEach(function (div) {
            var todosCompletos = CAMPOS_REQUERIDOS.every(function (campo) {
                var input = div.querySelector('[name$="-' + campo + '"]');
                if (!input) return false;
                return input.type === 'file' ? input.files.length > 0 : !!input.value;
            });
            if (todosCompletos) completas++;
        });

        var pct = Math.round((completas / total) * 100);
        pzCountLabel.textContent = total === 1 ? '1 pieza' : total + ' piezas';
        pzProgressFill.style.width = pct + '%';
        pzDoneLabel.textContent = completas + '/' + total;
    }

    function actualizarFotoLabel() {
        container.querySelectorAll('input[type="file"]').forEach(function (input) {
            var label = input.closest('p') ? input.closest('p').querySelector('.foto-label') : null;
            if (!label) {
                label = document.createElement('span');
                label.className = 'foto-label text-xs font-medium text-green-600 dark:text-green-400 mt-1 hidden';
                label.innerHTML = '&#10003; Imagen asignada';
                var parent = input.closest('p') || input.parentNode;
                parent.appendChild(label);
            }
            if (input.files.length > 0) {
                label.classList.remove('hidden');
            } else {
                label.classList.add('hidden');
            }
        });
    }

    function renumerarPiezas() {
        var formsVisibles = Array.from(container.querySelectorAll('.pieza-form'))
            .filter(function (div) { return !div.hidden; });
        formsVisibles.forEach(function (div, i) {
            var h3 = div.querySelector('.pz-title');
            if (h3) h3.textContent = 'Pieza Dañada Nº ' + (i + 1);
        });
    }

    function agregarFormulario() {
        var formCount = parseInt(totalFormsInput.value);
        var newFormHtml = emptyFormTemplate.replace(/__prefix__/g, formCount);
        container.insertAdjacentHTML('beforeend', newFormHtml);
        totalFormsInput.value = formCount + 1;
        renumerarPiezas();
        actualizarProgreso();
    }

    function mostrarMensaje(texto) {
        bannerMensajes.innerHTML = '';
        var parrafo = document.createElement('p');
        parrafo.className = 'text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg px-4 py-2 mb-4';
        parrafo.textContent = texto;
        bannerMensajes.appendChild(parrafo);
    }

    function limpiarMensaje() {
        bannerMensajes.innerHTML = '';
    }

    addBtn.addEventListener('click', function (e) {
        e.preventDefault();
        agregarFormulario();
        limpiarMensaje();
    });

    function reindexForms() {
        var forms = container.querySelectorAll('.pieza-form');
        forms.forEach(function (div, index) {
            div.querySelectorAll('input, select, textarea, label').forEach(function (el) {
                ['name', 'id', 'for'].forEach(function (attr) {
                    var val = el.getAttribute(attr);
                    if (val) {
                        el.setAttribute(attr, val.replace(/-\d+-/g, '-' + index + '-'));
                    }
                });
            });
        });
        totalFormsInput.value = forms.length;
        renumerarPiezas();
        actualizarProgreso();
    }

    container.addEventListener('click', function (e) {
        if (!e.target.classList.contains('remove-form-btn')) return;
        e.preventDefault();
        var formDiv = e.target.closest('.pieza-form');
        var idInput = formDiv.querySelector('input[name$="-id"]');
        var esNuevaFila = !idInput || !idInput.value;

        if (esNuevaFila) {
            formDiv.remove();
            reindexForms();
        } else {
            var deleteInput = formDiv.querySelector('input[name$="-DELETE"]');
            if (deleteInput) deleteInput.checked = true;
            formDiv.hidden = true;
            actualizarProgreso();
            renumerarPiezas();
        }
    });

    container.addEventListener('input', function () {
        actualizarProgreso();
    });

    container.addEventListener('change', function () {
        actualizarProgreso();
        actualizarFotoLabel();
    });

    actualizarProgreso();
    renumerarPiezas();
    actualizarFotoLabel();

    var formulario = document.getElementById('formulario-piezas');
    var submitBtn = document.getElementById('submit-btn');

    formulario.addEventListener('submit', function (e) {
        var formsVisibles = Array.from(container.querySelectorAll('.pieza-form'))
            .filter(function (div) { return !div.hidden; });

        if (formsVisibles.length === 0) {
            e.preventDefault();
            agregarFormulario();
            mostrarMensaje('Debe registrar al menos una pieza.');
            var nuevoForm = container.querySelector('.pieza-form:last-child');
            if (nuevoForm) nuevoForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        var primerError = null;

        formsVisibles.forEach(function (div) {
            CAMPOS_REQUERIDOS.forEach(function (campo) {
                var input = div.querySelector('[name$="-' + campo + '"]');
                if (!input) return;
                var vacio = input.type === 'file'
                    ? input.files.length === 0
                    : input.type === 'number'
                        ? (input.value === '' || parseFloat(input.value) < parseInt(input.min || 1))
                        : !input.value;
                if (vacio) {
                    input.classList.add('campo-invalido');
                    if (!primerError) primerError = input;
                } else {
                    input.classList.remove('campo-invalido');
                }
            });
        });

        if (primerError) {
            e.preventDefault();
            mostrarMensaje('Complete todos los campos obligatorios.');
            primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        limpiarMensaje();

        submitBtn.disabled = true;
        submitBtn.innerText = 'Guardando';
    });

    var cancelBtn = document.getElementById('cancel-btn');
    var cancelForm = document.getElementById('cancel-form');
    cancelBtn.addEventListener('click', function () {
        if (confirm('¿Cancelar el informe? Se eliminará del sistema.')) {
            cancelForm.submit();
        }
    });
});
