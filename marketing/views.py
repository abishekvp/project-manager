from django.shortcuts import render
from django.http import JsonResponse
from app.models import Profile, Lead
from utils import utility
from constants import constants as const

def view_market_leads(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        leads = Lead.objects.all()
        leads_list = []
        for lead in leads:
            lead_dict = utility.as_dict(lead)
            leads_list.append(lead_dict)
        return JsonResponse({"leads": leads_list})
    return render(request, 'marketing/view_leads.html')

def create_market_leads(request):
    client_name = request.POST.get('client_name')
    client_email = request.POST.get('client_email')
    client_contact = request.POST.get('client_contact')
    notes = request.POST.get('notes')
    status = const.ACTIVE
    Lead.objects.create(client_name=client_name, client_email=client_email, client_contact=client_contact, status=status, notes=notes)
    return JsonResponse({'status': 200})

def update_market_leads(request):
    lead_id = request.POST.get('lead_id')
    status = request.POST.get('status')
    lead = Lead.objects.get(id=lead_id)
    if lead:
        lead.status = status
        lead.save()
        return JsonResponse({'status': 200})
    else:
        return JsonResponse({'status': 404})

def delete_market_leads(request):
    lead_id = request.POST.get('lead_id')
    lead = Lead.objects.get(id=lead_id)
    if lead:
        lead.delete()
        return JsonResponse({'status': 200})
    else:
        return JsonResponse({'status': 404})

def get_market_lead(request):
    lead_id = request.GET.get('lead_id')
    lead = Lead.objects.get(id=lead_id)
    if lead:
        lead_dict = utility.as_dict(lead)
        return JsonResponse({'lead': lead_dict})
    else:
        return JsonResponse({'status': 404})

def get_market_lead_status(request):
    return JsonResponse({'status': const.MARKET_LEAD})