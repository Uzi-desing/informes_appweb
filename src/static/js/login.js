const html = document.documentElement;

// Restaurar preferencia guardada
if (localStorage.getItem('dark-mode') === 'true' ||
    (!localStorage.getItem('dark-mode') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    html.classList.add('dark');
}

// Change mode: Cambiar al modo oscuro
document.getElementById('toggle-dark').addEventListener('click', function() {
    html.classList.toggle('dark');
    localStorage.setItem('dark-mode', html.classList.contains('dark'));
});

// Change mode: Mostrar la contraseña "...." --> "1234"
document.getElementById('toggle-password').addEventListener('click', function() {
    const input = document.getElementById('id_password');
    const eyeOpen = document.getElementById('eye-open');
    const eyeClosed = document.getElementById('eye-closed');
    if (input.type === 'password') {
        input.type = 'text';
        eyeOpen.classList.add('hidden');
        eyeClosed.classList.remove('hidden');
    } else {
        input.type = 'password';
        eyeOpen.classList.remove('hidden');
        eyeClosed.classList.add('hidden');
    }
});
