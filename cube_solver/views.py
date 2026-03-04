from pathlib import Path

from django.http import HttpResponse


def index(request):
    project_root = Path(__file__).resolve().parent.parent
    html = (project_root / 'index.html').read_text(encoding='utf-8')
    return HttpResponse(html)
