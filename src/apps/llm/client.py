"""vLLM istemcisi (OpenAI uyumlu `/chat/completions` uç noktası, `requests` ile).

Veri dışarı çıkmamalıdır (kurallar-ve-sinirlar.md §2): istemci yalnızca şirket içi/özel ağ adreslerine bağlanır.
"""
import ipaddress
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class LlmHatasi(Exception):
    pass


def adres_icerde_mi(host):
    """Host localhost, özel/loopback IP veya `VLLM_IZINLI_HOSTLAR` listesindeyse True."""
    host = (host or "").lower()
    if host == "localhost" or host in settings.VLLM_IZINLI_HOSTLAR:
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback


class VllmIstemcisi:
    def __init__(self, base_url, model, api_key="", max_tokens=4096, timeout=300):
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.oturum = requests.Session()
        # Ortamdaki proxy ayarları kullanılmaz: istek yalnızca belirtilen adrese gider.
        self.oturum.trust_env = False

    def govde(self, mesajlar, araclar):
        return {
            "model": self.model,
            "messages": mesajlar,
            "tools": araclar,
            "tool_choice": "required",
            "temperature": 0,
            "max_tokens": self.max_tokens,
        }

    def sohbet(self, mesajlar, araclar):
        """Sohbet isteği gönderir; yanıtın JSON sözlüğünü döndürür."""
        basliklar = {"Content-Type": "application/json"}
        if self.api_key:
            basliklar["Authorization"] = f"Bearer {self.api_key}"
        try:
            # Yönlendirmeler izlenmez: yanıt başka bir adrese (dışarıya) yönlendirse bile veri gönderilmez.
            yanit = self.oturum.post(
                self.url,
                json=self.govde(mesajlar, araclar),
                headers=basliklar,
                timeout=self.timeout,
                allow_redirects=False,
            )
        except requests.RequestException as exc:
            raise LlmHatasi(f"vLLM sunucusuna ulaşılamadı: {exc}") from exc
        if yanit.status_code != 200:
            raise LlmHatasi(f"vLLM HTTP {yanit.status_code} döndürdü: {yanit.text[:300]}")
        try:
            return yanit.json()
        except ValueError as exc:
            raise LlmHatasi("vLLM yanıtı geçerli bir JSON değil.") from exc


def vllm_istemcisi():
    if not settings.VLLM_BASE_URL or not settings.VLLM_MODEL:
        raise ImproperlyConfigured("VLLM_BASE_URL ve VLLM_MODEL ortam değişkenleri tanımlı olmalı.")
    adres = urlparse(settings.VLLM_BASE_URL)
    if adres.scheme not in ("http", "https") or not adres.hostname:
        raise ImproperlyConfigured("VLLM_BASE_URL geçerli bir http(s) adresi olmalı.")
    if not adres_icerde_mi(adres.hostname):
        raise ImproperlyConfigured(
            f"'{adres.hostname}' özel ağ adresi değil; veri dışarı çıkmaması için reddedildi. "
            "Şirket içi vLLM sunucusunun adını VLLM_IZINLI_HOSTLAR listesine ekleyin."
        )
    return VllmIstemcisi(
        settings.VLLM_BASE_URL,
        settings.VLLM_MODEL,
        api_key=settings.VLLM_API_KEY,
        max_tokens=settings.VLLM_MAX_TOKENS,
        timeout=settings.VLLM_TIMEOUT,
    )
