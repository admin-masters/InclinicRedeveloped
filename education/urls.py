from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('publisher/campaign/add/', views.add_campaign, name='add_campaign'),
    path('publisher/campaign/<uuid:campaign_id>/result/', views.campaign_result, name='campaign_result'),
    path('publisher/campaign/<uuid:campaign_id>/inclinic/', views.inclinic_config, name='inclinic_config'),
    path('publisher/campaign/<uuid:campaign_id>/detail/', views.campaign_detail, name='campaign_detail'),
    path('publisher/campaign/<uuid:campaign_id>/field-reps/upload/', views.upload_field_reps, name='upload_field_reps'),
    path('publisher/campaign/<uuid:campaign_id>/collaterals/', views.collateral_manage, name='collateral_manage'),
    path('publisher/campaign/<uuid:campaign_id>/collaterals/add/', views.collateral_add, name='collateral_add'),
    path('collateral/<int:collateral_id>/preview/', views.preview_collateral, name='preview_collateral'),
    path('field/login/', views.field_rep_login, name='field_rep_login'),
    path('field/share/', views.field_rep_share, name='field_rep_share'),
    path('s/<str:code>/', views.short_link, name='short_link'),
    path('s/<str:code>/landing/', views.doctor_landing, name='doctor_landing'),
    path('s/<str:code>/track/', views.track_event, name='track_event'),
    path('brand/<uuid:campaign_id>/field-reps/', views.brand_field_reps, name='brand_field_reps'),
    path('brand/<uuid:campaign_id>/reports/', views.brand_reports, name='brand_reports'),
]
