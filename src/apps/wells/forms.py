from django import forms

from .models import Well, WellName


class WellForm(forms.ModelForm):
    class Meta:
        model = Well
        fields = ["ad", "referans_tipi", "referans_yuksekligi"]

    def clean_ad(self):
        ad = self.cleaned_data["ad"].strip()
        # Ad benzersizdir; başka bir kuyunun güncel veya eski adı olamaz (K-13).
        cakisan = WellName.objects.filter(ad__iexact=ad)
        if self.instance.pk:
            cakisan = cakisan.exclude(well=self.instance)
        if cakisan.exists():
            raise forms.ValidationError("Bu ad başka bir kuyu tarafından kullanılıyor veya kullanılmış.")
        return ad
