"""Обработчики статических страниц и системных ошибок проекта."""

from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    """Страница о проекте."""

    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """Страница правила."""

    template_name = 'pages/rules.html'


def csrf_failure(request, reason=''):
    """Ошибка CSRF."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Ошибка 500."""
    return render(request, 'pages/500.html', status=500)


def page_not_found(request, exception):
    """Ошибка 404."""
    return render(request, 'pages/404.html', status=404)
