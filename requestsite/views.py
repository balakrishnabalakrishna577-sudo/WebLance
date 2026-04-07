from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import WebsiteRequest
from .forms import WebsiteRequestForm

@login_required
def request_website(request):
    plan    = request.GET.get('plan', '')
    service = request.GET.get('service', '')
    label   = service or plan  # whichever is set

    # Map to website_type dropdown value
    type_map = {
        'custom website development': 'custom',
        'e-commerce development':     'ecommerce',
        'seo optimization':           'custom',
        'web design':                 'custom',
        'website redesign':           'custom',
        'website maintenance':        'custom',
        'starter website':            'business',
        'business website':           'business',
        'e-commerce website':         'ecommerce',
    }
    preset_type = type_map.get(label.lower(), '')

    if request.method == 'POST':
        form = WebsiteRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            # Prepend service label to description so admin sees it
            svc = request.POST.get('_service_label', '')
            if svc:
                obj.description = f"[Service: {svc}]\n\n{obj.description}"
            obj.save()
            messages.success(
                request,
                'Thank you for your request! Our team will contact you within 24 hours.'
            )
            return redirect('request_website')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WebsiteRequestForm()

    return render(request, 'requestsite/request.html', {
        'form':          form,
        'selected_plan': plan,
        'service_label': label,
        'preset_type':   preset_type,
    })
