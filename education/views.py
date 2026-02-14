from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import CampaignForm, CollateralForm, FieldRepCSVUploadForm, FieldRepForm, FieldRepLoginForm, InClinicConfigForm, ShareForm
from .models import Campaign, CampaignSystem, Collateral, Doctor, Event, FieldRep, RecruitmentLink, ShareInstance, UserProfile, ReportingEvent
from .services import create_share, doctor_status, ensure_link_clicked


def home(request):
    return redirect('login')


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')
    return render(request, 'education/login.html', {'form': form})

@login_required
def dashboard(request):
    role = request.user.userprofile.role
    if role == 'publisher':
        campaigns = Campaign.objects.filter(created_by=request.user)
        return render(request, 'education/publisher_dashboard.html', {'campaigns': campaigns})
    if role == 'brand_manager':
        campaigns = Campaign.objects.all()
        return render(request, 'education/brand_dashboard.html', {'campaigns': campaigns})
    return HttpResponse(status=403)

@login_required
def add_campaign(request):
    if request.user.userprofile.role != 'publisher':
        return HttpResponse(status=403)
    form = CampaignForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        systems = form.cleaned_data.pop('systems')
        campaign = form.save(commit=False)
        campaign.created_by = request.user
        campaign.save()
        for system in systems:
            CampaignSystem.objects.create(campaign=campaign, system=system)
        RecruitmentLink.objects.create(campaign=campaign)
        return redirect('campaign_result', campaign_id=campaign.id)
    return render(request, 'education/add_campaign.html', {'form': form})

@login_required
def campaign_result(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    return render(request, 'education/campaign_result.html', {'campaign': campaign})

@login_required
def inclinic_config(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    config = get_object_or_404(CampaignSystem, campaign=campaign, system='inclinic')
    form = InClinicConfigForm(request.POST or None, request.FILES or None, instance=config)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('campaign_detail', campaign_id=campaign.id)
    return render(request, 'education/inclinic_config.html', {'form': form, 'campaign': campaign})

@login_required
def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    config = CampaignSystem.objects.filter(campaign=campaign, system='inclinic').first()
    return render(request, 'education/campaign_detail.html', {'campaign': campaign, 'config': config})

@login_required
def upload_field_reps(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    form = FieldRepCSVUploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        rows = form.parse()
        for row in rows:
            FieldRep.objects.get_or_create(
                campaign=campaign,
                brand_rep_id=row['brand-supplied-field-rep-id'],
                defaults={'name': row['field-rep-name'], 'email': row['email-id'], 'phone': row['phone-number']},
            )
        messages.success(request, 'Field reps uploaded.')
        return redirect('campaign_detail', campaign_id=campaign.id)
    return render(request, 'education/upload_field_reps.html', {'form': form, 'campaign': campaign})

@login_required
def collateral_manage(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    collaterals = Collateral.objects.filter(campaign=campaign)
    return render(request, 'education/collateral_manage.html', {'campaign': campaign, 'collaterals': collaterals})

@login_required
def collateral_add(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    system = get_object_or_404(CampaignSystem, campaign=campaign, system='inclinic')
    form = CollateralForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        collateral = form.save(commit=False)
        collateral.campaign = campaign
        collateral.system = system
        collateral.save()
        return redirect('collateral_manage', campaign_id=campaign.id)
    return render(request, 'education/collateral_add.html', {'form': form, 'campaign': campaign})


def preview_collateral(request, collateral_id):
    collateral = get_object_or_404(Collateral, id=collateral_id)
    return render(request, 'education/collateral_preview.html', {'collateral': collateral})


def field_rep_login(request):
    form = FieldRepLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        rep = FieldRep.objects.filter(
            campaign_id=form.cleaned_data['campaign_id'],
            brand_rep_id=form.cleaned_data['field_rep_id'],
            email=form.cleaned_data['email'],
            is_active=True,
        ).first()
        if rep:
            request.session['field_rep_id'] = rep.id
            return redirect('field_rep_share')
        form.add_error(None, 'Invalid credentials')
    return render(request, 'education/field_rep_login.html', {'form': form})


def field_rep_share(request):
    rep = get_object_or_404(FieldRep, id=request.session.get('field_rep_id'))
    doctors = rep.doctors.all()
    collaterals = Collateral.objects.filter(campaign=rep.campaign, is_active=True)
    form = ShareForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        doctor, _ = Doctor.objects.get_or_create(
            campaign=rep.campaign,
            field_rep=rep,
            whatsapp_number=form.cleaned_data['doctor_whatsapp'],
            defaults={'name': form.cleaned_data['doctor_name']},
        )
        collateral = get_object_or_404(Collateral, id=form.cleaned_data['collateral'])
        _, wa_url = create_share(rep.campaign, rep, doctor, collateral)
        return redirect(wa_url)
    statuses = {d.id: doctor_status(rep, d) for d in doctors}
    return render(request, 'education/field_rep_share.html', {'form': form, 'doctors': doctors, 'collaterals': collaterals, 'statuses': statuses})


def short_link(request, code):
    share = get_object_or_404(ShareInstance, short_code=code)
    ensure_link_clicked(share)
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if phone == share.doctor.whatsapp_number:
            Event.objects.create(
                event_type='landing_access', campaign=share.campaign, collateral=share.collateral,
                field_rep=share.field_rep, doctor=share.doctor, share_instance=share,
            )
            request.session[f'verified_{share.id}'] = True
            return redirect('doctor_landing', code=code)
        messages.error(request, 'Verification failed')
    return render(request, 'education/doctor_verify.html', {'share': share})


def doctor_landing(request, code):
    share = get_object_or_404(ShareInstance, short_code=code)
    if not request.session.get(f'verified_{share.id}'):
        return redirect('short_link', code=code)
    return render(request, 'education/collateral_preview.html', {'collateral': share.collateral, 'share': share})


def track_event(request, code):
    share = get_object_or_404(ShareInstance, short_code=code)
    kind = request.GET.get('type')
    percentage = request.GET.get('percentage')
    Event.objects.create(
        event_type=kind,
        campaign=share.campaign,
        collateral=share.collateral,
        field_rep=share.field_rep,
        doctor=share.doctor,
        share_instance=share,
        video_percentage=int(percentage) if percentage else None,
    )
    return JsonResponse({'status': 'ok'})

@login_required
def brand_field_reps(request, campaign_id):
    if request.user.userprofile.role != 'brand_manager':
        return HttpResponse(status=403)
    campaign = get_object_or_404(Campaign, id=campaign_id)
    search = request.GET.get('q', '')
    reps = campaign.field_reps.filter(Q(brand_rep_id__icontains=search) | Q(email__icontains=search))
    return render(request, 'education/brand_field_reps.html', {'campaign': campaign, 'reps': reps})

@login_required
def brand_reports(request, campaign_id):
    if request.user.userprofile.role != 'brand_manager':
        return HttpResponse(status=403)
    events = ReportingEvent.objects.using('reporting').filter(campaign_id=campaign_id)
    summary = {
        'unique_doctors': events.values('doctor_id').distinct().count(),
        'clicked': events.filter(event_type='link_clicked').values('doctor_id').distinct().count(),
        'downloads': events.filter(event_type='pdf_downloaded').values('doctor_id').distinct().count(),
        'last_page': events.filter(event_type='pdf_last_page').values('doctor_id').distinct().count(),
        'video_50': events.filter(event_type='video_progress', video_percentage__gte=50).values('doctor_id').distinct().count(),
        'video_100': events.filter(event_type='video_progress', video_percentage=100).values('doctor_id').distinct().count(),
        'total': events.count(),
    }
    return render(request, 'education/brand_reports.html', {'summary': summary, 'events': events[:100]})
