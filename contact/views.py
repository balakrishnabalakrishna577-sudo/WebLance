from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ContactMessage
from .forms import ContactForm

@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for contacting WEBLANCE. We will contact you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})
