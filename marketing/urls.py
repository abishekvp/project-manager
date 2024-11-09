from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('view-market-leads', views.view_market_leads, name='view-market-leads'),
    path('create-market-leads', views.create_market_leads, name='create-market-leads'),
    path('update-market-leads', views.update_market_leads, name='update-market-leads'),
    path('delete-market-lead', views.delete_market_leads, name='delete-market-leads'),
    path('get-market-lead', views.get_market_lead, name='get-market-lead'),
    path('get-market-lead-status', views.get_market_lead_status, name='get-market-lead-status'),
    path('update-lead-status', views.update_lead_status, name='update-lead-status'),
    path('sort-market-leads', views.sort_market_leads, name='sort-market-leads'),
    path('search-market-leads/', views.search_market_leads, name='search-market-leads'),
]
