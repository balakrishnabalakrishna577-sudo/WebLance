from django.shortcuts import render
from .models import PricingPlan

def pricing(request):
    plans = PricingPlan.objects.all()
    return render(request, 'pricing/pricing.html', {'plans': plans})
