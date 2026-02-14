import csv
from io import StringIO
from django import forms
from .models import Campaign, CampaignSystem, Collateral, FieldRep


class CampaignForm(forms.ModelForm):
    systems = forms.MultipleChoiceField(
        choices=CampaignSystem.SYSTEM_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Campaign
        fields = ['company_name', 'brand_name', 'expected_doctors', 'contact_name', 'contact_phone', 'contact_email', 'desktop_banner', 'mobile_banner']


class InClinicConfigForm(forms.ModelForm):
    class Meta:
        model = CampaignSystem
        exclude = ['campaign', 'system']


class FieldRepCSVUploadForm(forms.Form):
    csv_file = forms.FileField()

    def parse(self):
        reader = csv.DictReader(StringIO(self.cleaned_data['csv_file'].read().decode()))
        required = {'field-rep-name', 'email-id', 'phone-number', 'brand-supplied-field-rep-id'}
        if set(reader.fieldnames or []) != required:
            raise forms.ValidationError('CSV headers are invalid')
        return list(reader)


class FieldRepForm(forms.ModelForm):
    class Meta:
        model = FieldRep
        fields = ['brand_rep_id', 'name', 'email', 'phone']


class CollateralForm(forms.ModelForm):
    class Meta:
        model = Collateral
        exclude = ['campaign', 'system', 'is_active']

    def clean_vimeo_url(self):
        value = self.cleaned_data.get('vimeo_url', '')
        if value and 'vimeo.com' not in value:
            raise forms.ValidationError('Only Vimeo URLs are allowed.')
        return value


class FieldRepLoginForm(forms.Form):
    campaign_id = forms.UUIDField()
    field_rep_id = forms.CharField()
    email = forms.EmailField()


class ShareForm(forms.Form):
    doctor_name = forms.CharField(max_length=255)
    doctor_whatsapp = forms.CharField(min_length=10, max_length=10)
    collateral = forms.IntegerField()
