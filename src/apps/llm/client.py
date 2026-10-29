from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def claude_istemcisi():
    """Claude API istemcisi. Anahtar yalnızca ortam değişkeninden okunur."""
    if not settings.ANTHROPIC_API_KEY:
        raise ImproperlyConfigured("ANTHROPIC_API_KEY ortam değişkeni tanımlı değil.")
    import anthropic

    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
