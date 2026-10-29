import json
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.wells.models import Event
from apps.wells.state import ORTAK_ALANLAR, derinlik_var_mi

from .models import Proposal


def _geri(request, oneri):
    sonraki = request.POST.get("next", "")
    if sonraki.startswith("/") and not sonraki.startswith("//"):
        return redirect(sonraki)
    return redirect("report_detail", pk=oneri.rapor_id)


def _bekleyen(pk):
    return get_object_or_404(Proposal.objects.select_for_update(), pk=pk)


@login_required
@require_POST
@transaction.atomic
def approve(request, pk):
    oneri = _bekleyen(pk)
    if oneri.durum != Proposal.Durum.ONAY_BEKLIYOR:
        messages.error(request, "Bu öneri zaten karara bağlanmış.")
        return _geri(request, oneri)

    try:
        parametreler = json.loads(request.POST.get("parametreler") or "{}")
        if not isinstance(parametreler, dict):
            raise ValueError
    except ValueError:
        messages.error(request, "Parametreler geçerli bir JSON nesnesi olmalı.")
        return _geri(request, oneri)

    if oneri.bilgi_mi:
        oneri.durum = Proposal.Durum.KAPATILDI
    else:
        try:
            olay_tarihi = date.fromisoformat(str(parametreler.get("olay_tarihi")))
        except ValueError:
            messages.error(request, "Geçerli bir olay tarihi (YYYY-MM-DD) gerekli.")
            return _geri(request, oneri)
        if derinlik_var_mi(parametreler) and parametreler.get("birim") not in ("m", "ft"):
            messages.error(request, "Derinlik birimi (m veya ft) seçilmeden onaylanamaz.")
            return _geri(request, oneri)

        veri = {k: v for k, v in parametreler.items() if k not in ORTAK_ALANLAR}
        olay = Event.objects.create(
            well=oneri.well,
            tip=oneri.arac_adi,
            olay_tarihi=olay_tarihi,
            veri=veri,
            dayanak_alinti=str(parametreler.get("dayanak_alinti", "")),
            rapor=oneri.rapor,
            onaylayan=request.user,
        )
        oneri.olay = olay
        oneri.olay_tarihi = olay_tarihi
        degisti = parametreler != oneri.parametreler
        # Orijinal LLM çıktısı `parametreler`de kalır; düzeltilmiş hâli olayın `veri` alanındadır.
        oneri.durum = Proposal.Durum.DUZELTILDI if degisti else Proposal.Durum.ONAYLANDI

    oneri.karar_veren, oneri.karar_zamani = request.user, timezone.now()
    oneri.save()
    messages.success(request, "Karar kaydedildi; sketch olay geçmişinden baştan hesaplanır.")
    return _geri(request, oneri)


@login_required
@require_POST
@transaction.atomic
def reject(request, pk):
    oneri = _bekleyen(pk)
    if oneri.durum != Proposal.Durum.ONAY_BEKLIYOR:
        messages.error(request, "Bu öneri zaten karara bağlanmış.")
        return _geri(request, oneri)
    oneri.durum = Proposal.Durum.REDDEDILDI
    oneri.karar_veren, oneri.karar_zamani = request.user, timezone.now()
    oneri.save()
    messages.success(request, "Öneri reddedildi.")
    return _geri(request, oneri)
