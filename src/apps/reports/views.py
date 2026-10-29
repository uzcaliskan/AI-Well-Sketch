from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.llm.service import analiz_et
from apps.wells.models import Well

from .extraction import MetinCikarmaHatasi, metin_cikar
from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["rapor_tarihi", "dosya"]
        widgets = {"rapor_tarihi": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}


def isim_uyarisi(well, metin):
    """Raporda kuyunun güncel/eski adlarından biri geçmiyorsa uyarı üretir (K-13)."""
    kucuk = metin.lower()
    if any(ad.lower() in kucuk for ad in well.tum_adlar()):
        return []
    return [f"Raporda kuyu adı bulunamadı (aranan: {', '.join(well.tum_adlar())}). Doğru kuyuya yüklediğinizden emin olun."]


@login_required
def report_create(request, well_id):
    well = get_object_or_404(Well, pk=well_id)
    form = ReportForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        rapor = form.save(commit=False)
        rapor.well, rapor.yukleyen = well, request.user
        rapor.save()
        try:
            metin, uyarilar = metin_cikar(rapor.dosya.open("rb"))
            rapor.metin = metin
            rapor.uyarilar = uyarilar + (isim_uyarisi(well, metin) if metin else [])
            rapor.durum = Report.Durum.METIN_HAZIR
        except MetinCikarmaHatasi as exc:
            rapor.durum, rapor.hata = Report.Durum.HATA, str(exc)
        rapor.save()
        return redirect("report_detail", pk=rapor.pk)
    return render(request, "form.html", {"form": form, "baslik": f"{well.ad}: rapor yükle", "multipart": True})


@login_required
def report_detail(request, pk):
    rapor = get_object_or_404(Report.objects.select_related("well"), pk=pk)
    return render(
        request,
        "reports/detail.html",
        {"rapor": rapor, "oneriler": rapor.oneriler.all(), "metin_onizleme": rapor.metin[:3000]},
    )


@login_required
@require_POST
def report_analyze(request, pk):
    rapor = get_object_or_404(Report, pk=pk)
    try:
        oneriler = analiz_et(rapor)
    except (ImproperlyConfigured, ValueError) as exc:
        messages.error(request, str(exc))
    except Exception as exc:  # API/ağ hataları: kuyu durumu değişmez
        rapor.durum, rapor.hata = Report.Durum.HATA, str(exc)
        rapor.save(update_fields=["durum", "hata"])
        messages.error(request, f"Analiz başarısız: {exc}")
    else:
        messages.success(request, f"{len(oneriler)} öneri üretildi; onayınızı bekliyor.")
    return redirect("report_detail", pk=rapor.pk)
