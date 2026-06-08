from django.shortcuts import render, get_object_or_404
from .models import PricingPlan

def pricing(request):
    plans = PricingPlan.objects.all()
    return render(request, 'pricing/pricing.html', {'plans': plans})

def plan_detail(request, pk):
    plan = get_object_or_404(PricingPlan, pk=pk)
    plans = PricingPlan.objects.all()
    return render(request, 'pricing/plan_detail.html', {'plan': plan, 'plans': plans})
