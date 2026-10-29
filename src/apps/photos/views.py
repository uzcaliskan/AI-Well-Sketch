from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.wells.models import Well

from .models import Photo


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ["tarih", "dosya", "not_metni"]
        widgets = {"tarih": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}


@login_required
def photo_create(request, well_id):
    well = get_object_or_404(Well, pk=well_id)
    form = PhotoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        foto = form.save(commit=False)
        foto.well, foto.yukleyen = well, request.user
        foto.save()
        return redirect("well_detail", pk=well.pk)
    return render(request, "form.html", {"form": form, "baslik": f"{well.ad}: fotoğraf yükle", "multipart": True})
