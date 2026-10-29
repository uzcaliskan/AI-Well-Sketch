from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from apps.proposals.models import Proposal
from apps.sketch.render import render_svg

from .forms import WellForm
from .models import Well
from .state import kuyu_durumu


@login_required
def well_list(request):
    kuyular = Well.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        kuyular = kuyular.filter(Q(ad__icontains=q) | Q(names__ad__icontains=q)).distinct()
    sayfa = Paginator(kuyular, 25).get_page(request.GET.get("sayfa"))
    return render(request, "wells/list.html", {"sayfa": sayfa, "q": q})


@login_required
def well_create(request):
    form = WellForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        well = form.save()
        return redirect("well_detail", pk=well.pk)
    return render(request, "form.html", {"form": form, "baslik": "Yeni kuyu"})


@login_required
def well_rename(request, pk):
    well = get_object_or_404(Well, pk=pk)
    form = WellForm(request.POST or None, instance=well)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("well_detail", pk=well.pk)
    return render(request, "form.html", {"form": form, "baslik": f"{well.ad}: düzenle (ad değişirse eski ad saklanır)"})


@login_required
def well_detail(request, pk):
    well = get_object_or_404(Well, pk=pk)
    tarih = parse_date(request.GET.get("tarih") or "")
    birim = request.GET.get("birim") if request.GET.get("birim") in ("m", "ft") else "m"
    durum = kuyu_durumu(well, tarih=tarih)
    return render(
        request,
        "wells/detail.html",
        {
            "well": well,
            "svg": render_svg(durum, birim),
            "tarih": tarih,
            "birim": birim,
            "adlar": well.names.all(),
            "raporlar": well.reports.all()[:20],
            "bekleyenler": well.oneriler.filter(durum=Proposal.Durum.ONAY_BEKLIYOR).select_related("rapor"),
            "olaylar": well.events.select_related("onaylayan")[:50],
            "fotograflar": well.photos.all()[:30],
        },
    )
