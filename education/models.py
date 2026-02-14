import uuid
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [('publisher', 'Publisher'), ('brand_manager', 'Brand Manager')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)


class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=255)
    expected_doctors = models.PositiveIntegerField(default=0)
    contact_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    desktop_banner = models.FileField(upload_to='banners/', blank=True, null=True)
    mobile_banner = models.FileField(upload_to='banners/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)


class CampaignSystem(models.Model):
    SYSTEM_CHOICES = [('red_flag', 'Red Flag Alerts'), ('patient', 'Patient Education'), ('inclinic', 'In-Clinic Education')]
    STATUS_CHOICES = [('draft', 'Draft'), ('active', 'Active')]
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='systems')
    system = models.CharField(max_length=32, choices=SYSTEM_CHOICES)
    in_charge_name = models.CharField(max_length=255, blank=True)
    in_charge_designation = models.CharField(max_length=255, blank=True)
    items_per_clinic_per_year = models.PositiveIntegerField(default=0)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    contract_upload = models.FileField(upload_to='contracts/', blank=True, null=True)
    brand_logo = models.FileField(upload_to='logos/', blank=True, null=True)
    company_logo = models.FileField(upload_to='logos/', blank=True, null=True)
    printing_required = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft')

    class Meta:
        unique_together = ('campaign', 'system')


class FieldRep(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='field_reps')
    brand_rep_id = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('campaign', 'brand_rep_id')


class RecruitmentLink(models.Model):
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Doctor(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    field_rep = models.ForeignKey(FieldRep, on_delete=models.CASCADE, related_name='doctors')
    name = models.CharField(max_length=255)
    whatsapp_number = models.CharField(max_length=10)
    clinic_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Collateral(models.Model):
    ITEM_CHOICES = [('pdf', 'PDF'), ('video', 'Video'), ('both', 'PDF + Video')]
    PURPOSE_CHOICES = [
        ('doctor_long', 'Doctor Education Long'), ('doctor_short', 'Doctor Education Short'),
        ('patient_long', 'Patient Education Long'), ('patient_short', 'Patient Education Short')
    ]
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='collaterals')
    system = models.ForeignKey(CampaignSystem, on_delete=models.CASCADE)
    cycle = models.CharField(max_length=64, default='default')
    classification = models.CharField(max_length=64, choices=PURPOSE_CHOICES)
    content_title = models.CharField(max_length=255)
    content_id = models.CharField(max_length=255, blank=True)
    item_type = models.CharField(max_length=10, choices=ITEM_CHOICES)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    vimeo_url = models.URLField(blank=True)
    banner_1 = models.FileField(upload_to='collateral_banners/', blank=True, null=True)
    banner_2 = models.FileField(upload_to='collateral_banners/', blank=True, null=True)
    doctor_name = models.CharField(max_length=255, blank=True)
    content_description = models.TextField(blank=True)
    webinar_link = models.URLField(blank=True)
    webinar_title = models.CharField(max_length=255, blank=True)
    webinar_description = models.TextField(blank=True)
    webinar_date = models.DateField(blank=True, null=True)
    whatsapp_template = models.TextField(default='Please review: $collateralLinks')
    is_active = models.BooleanField(default=True)


class ShareInstance(models.Model):
    short_code = models.CharField(max_length=24, unique=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    collateral = models.ForeignKey(Collateral, on_delete=models.CASCADE)
    field_rep = models.ForeignKey(FieldRep, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Event(models.Model):
    TYPE_CHOICES = [
        ('share_initiated', 'Share Initiated'), ('link_clicked', 'Link Clicked'),
        ('landing_access', 'Landing Page Access'), ('video_progress', 'Video Progress'),
        ('pdf_last_page', 'PDF Last Page Viewed'), ('pdf_downloaded', 'PDF Downloaded')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    collateral = models.ForeignKey(Collateral, on_delete=models.CASCADE)
    field_rep = models.ForeignKey(FieldRep, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    share_instance = models.ForeignKey(ShareInstance, on_delete=models.CASCADE)
    video_percentage = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ReportingEvent(models.Model):
    id = models.UUIDField(primary_key=True)
    event_type = models.CharField(max_length=32)
    campaign_id = models.UUIDField()
    collateral_id = models.BigIntegerField()
    field_rep_id = models.BigIntegerField()
    doctor_id = models.BigIntegerField()
    share_instance_id = models.BigIntegerField()
    video_percentage = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = True
