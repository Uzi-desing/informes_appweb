const html = document.documentElement;

if (localStorage.getItem('dark-mode') === 'true' ||
    (!localStorage.getItem('dark-mode') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    html.classList.add('dark');
}

document.getElementById('toggle-dark').addEventListener('click', function() {
    html.classList.toggle('dark');
    localStorage.setItem('dark-mode', html.classList.contains('dark'));
});
