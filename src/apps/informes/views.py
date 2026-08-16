from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .decorators import solo_operarios


# Create your views here.
@never_cache
@require_http_methods(["GET", "POST"])
@solo_operarios
def home(request):
    return render(request, 'home.html')

