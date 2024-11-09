from django.shortcuts import render
from django.http import JsonResponse
from app.models import Profile, Lead
from utils import utility
from django.db.models import Q
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

def update_lead_status(request):
    lead_id = int(request.POST.get('lead'))
    status = str(request.POST.get('status')).strip().upper()
    lead = Lead.objects.get(id=lead_id)
    if lead and status in const.MARKET_LEAD:
        lead.status = status
        lead.save()
        return JsonResponse({'status': 200})
    else:
        return JsonResponse({'status': 404})

def sort_market_leads(request):
    status = str(request.GET.get('status'))
    filter_dict = dict()
    if (status in const.MARKET_LEAD) and (status != const.ALL):
        filter_dict['status'] = status
    leads = Lead.objects.filter(**filter_dict)
    leads_list = []
    if leads:
        for lead in leads:
            leads_list.append(utility.as_dict(lead))
    return JsonResponse({"leads": leads_list})

def search_market_leads(request):
    term = str(request.GET.get('term')).strip()
    leads = Lead.objects.filter(
        Q(client_name__icontains=term) |
        Q(client_email__icontains=term) |
        Q(client_contact__icontains=term) |
        Q(notes__icontains=term) |
        Q(status__icontains=term) |
        Q(id__icontains=term)
    )
    leads_list = []
    if leads:
        for lead in leads:
            leads_list.append(utility.as_dict(lead))
    return JsonResponse({"leads": leads_list})