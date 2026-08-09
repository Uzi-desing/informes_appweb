from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LoginForm
from .services import procesar_login, procesar_logout


# Create your views here.
@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home_simulado')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            mensaje = procesar_login(request, form)
            messages.success(request, mensaje)

            next_url = request.GET.get('next')
            if not next_url or not url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()}
            ):
                next_url = 'home_simulado'

            return redirect(next_url)

        else:
            for error in form.non_field_errors():
                messages.error(request, error)

    else:
        form = LoginForm(request)

    return render(request, 'login.html', {'form': form})

@never_cache
@require_POST
def logout_view(request):
    mensaje = procesar_logout(request)
    messages.info(request, mensaje)
    return redirect('login')

@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def simulacion_home(request):
    return render(request, 'home_simulator.html')