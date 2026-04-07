from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from contact.models import ContactMessage
from requestsite.models import WebsiteRequest
from portfolio.models import PortfolioItem
from pricing.models import PricingPlan
from home.models import Testimonial


def is_admin(user):
    return user.is_authenticated and user.is_staff


def admin_required(view_func):
    decorated = login_required(login_url='/accounts/login/')(
        user_passes_test(is_admin, login_url='/accounts/login/')(view_func)
    )
    return decorated


@admin_required
def dashboard(request):
    total_users = User.objects.count()
    total_contacts = ContactMessage.objects.count()
    total_requests = WebsiteRequest.objects.count()
    total_portfolio = PortfolioItem.objects.count()
    new_contacts = ContactMessage.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    new_requests = WebsiteRequest.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    recent_contacts = ContactMessage.objects.order_by('-created_at')[:5]
    recent_requests = WebsiteRequest.objects.order_by('-created_at')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]
    ctx = {
        'total_users': total_users,
        'total_contacts': total_contacts,
        'total_requests': total_requests,
        'total_portfolio': total_portfolio,
        'new_contacts': new_contacts,
        'new_requests': new_requests,
        'recent_contacts': recent_contacts,
        'recent_requests': recent_requests,
        'recent_users': recent_users,
    }
    return render(request, 'adminpanel/dashboard.html', ctx)


@admin_required
def contacts_list(request):
    contacts = ContactMessage.objects.order_by('-created_at')
    return render(request, 'adminpanel/contacts.html', {'contacts': contacts})


@admin_required
def contact_edit(request, pk):
    obj = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        obj.name = request.POST.get('name', obj.name)
        obj.email = request.POST.get('email', obj.email)
        obj.phone = request.POST.get('phone', obj.phone)
        obj.business_type = request.POST.get('business_type', obj.business_type)
        obj.message = request.POST.get('message', obj.message)
        obj.save()
        messages.success(request, 'Contact message updated.')
        return redirect('admin_contacts')
    return render(request, 'adminpanel/contact_edit.html', {'obj': obj})


@admin_required
def contact_delete(request, pk):
    obj = get_object_or_404(ContactMessage, pk=pk)
    obj.delete()
    messages.success(request, 'Contact message deleted.')
    return redirect('admin_contacts')


@admin_required
def requests_list(request):
    reqs = WebsiteRequest.objects.order_by('-created_at')
    return render(request, 'adminpanel/requests.html', {'reqs': reqs})


@admin_required
def request_delete(request, pk):
    obj = get_object_or_404(WebsiteRequest, pk=pk)
    obj.delete()
    messages.success(request, 'Website request deleted.')
    return redirect('admin_requests')


@admin_required
def request_status(request, pk):
    obj = get_object_or_404(WebsiteRequest, pk=pk)
    status = request.POST.get('status')
    if status in dict(WebsiteRequest.STATUS_CHOICES):
        obj.status = status
        obj.save()
        messages.success(request, f'Status updated to {obj.get_status_display()}.')
    return redirect('admin_requests')


@admin_required
def users_list(request):
    users = User.objects.order_by('-date_joined')
    for u in users:
        u.contact_count = ContactMessage.objects.filter(email=u.email).count() if u.email else 0
        u.request_count = WebsiteRequest.objects.filter(email=u.email).count() if u.email else 0
    return render(request, 'adminpanel/users.html', {'users': users})


@admin_required
def user_edit(request, pk):
    u = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        u.username = request.POST.get('username', u.username).strip()
        u.email = request.POST.get('email', u.email).strip()
        u.first_name = request.POST.get('first_name', u.first_name).strip()
        u.last_name = request.POST.get('last_name', u.last_name).strip()
        u.is_active = bool(request.POST.get('is_active'))
        u.is_staff = bool(request.POST.get('is_staff'))
        new_pass = request.POST.get('password', '').strip()
        if new_pass:
            u.set_password(new_pass)
        u.save()
        messages.success(request, f'User {u.username} updated.')
        return redirect('admin_users')
    return render(request, 'adminpanel/user_edit.html', {'u': u})


@admin_required
def user_toggle_staff(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.is_staff = not user.is_staff
        user.save()
        messages.success(request, f"{'Granted' if user.is_staff else 'Revoked'} admin for {user.username}.")
    return redirect('admin_users')


@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.delete()
        messages.success(request, 'User deleted.')
    return redirect('admin_users')


@admin_required
def portfolio_list(request):
    items = PortfolioItem.objects.order_by('-created_at')
    return render(request, 'adminpanel/portfolio.html', {'items': items})


@admin_required
def portfolio_add(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'business')
        description = request.POST.get('description', '').strip()
        live_url = request.POST.get('live_url', '').strip()
        image = request.FILES.get('image')
        if title and description and image:
            PortfolioItem.objects.create(
                title=title, category=category,
                description=description, live_url=live_url, image=image
            )
            messages.success(request, 'Portfolio item added.')
            return redirect('admin_portfolio')
        else:
            messages.error(request, 'Title, description and image are required.')
    return render(request, 'adminpanel/portfolio_add.html')


@admin_required
def portfolio_edit(request, pk):
    item = get_object_or_404(PortfolioItem, pk=pk)
    if request.method == 'POST':
        item.title = request.POST.get('title', item.title)
        item.category = request.POST.get('category', item.category)
        item.description = request.POST.get('description', item.description)
        item.live_url = request.POST.get('live_url', item.live_url)
        if request.FILES.get('image'):
            item.image = request.FILES['image']
        item.save()
        messages.success(request, 'Portfolio item updated.')
        return redirect('admin_portfolio')
    return render(request, 'adminpanel/portfolio_edit.html', {'item': item})


@admin_required
def portfolio_delete(request, pk):
    obj = get_object_or_404(PortfolioItem, pk=pk)
    obj.delete()
    messages.success(request, 'Portfolio item deleted.')
    return redirect('admin_portfolio')


@admin_required
def pricing_list(request):
    plans = PricingPlan.objects.all()
    return render(request, 'adminpanel/pricing.html', {'plans': plans})


@admin_required
def pricing_add(request):
    if request.method == 'POST':
        PricingPlan.objects.create(
            name=request.POST.get('name', ''),
            price=request.POST.get('price', ''),
            description=request.POST.get('description', ''),
            features=request.POST.get('features', ''),
            delivery_time=request.POST.get('delivery_time', ''),
            is_popular=bool(request.POST.get('is_popular')),
            order=int(request.POST.get('order', 0)),
        )
        messages.success(request, 'Pricing plan added.')
        return redirect('admin_pricing')
    return render(request, 'adminpanel/pricing_form.html', {'plan': None})


@admin_required
def pricing_edit(request, pk):
    plan = get_object_or_404(PricingPlan, pk=pk)
    if request.method == 'POST':
        plan.name = request.POST.get('name', plan.name)
        plan.price = request.POST.get('price', plan.price)
        plan.description = request.POST.get('description', plan.description)
        plan.features = request.POST.get('features', plan.features)
        plan.delivery_time = request.POST.get('delivery_time', plan.delivery_time)
        plan.is_popular = bool(request.POST.get('is_popular'))
        plan.order = int(request.POST.get('order', plan.order))
        plan.save()
        messages.success(request, 'Pricing plan updated.')
        return redirect('admin_pricing')
    return render(request, 'adminpanel/pricing_form.html', {'plan': plan})


@admin_required
def pricing_delete(request, pk):
    get_object_or_404(PricingPlan, pk=pk).delete()
    messages.success(request, 'Pricing plan deleted.')
    return redirect('admin_pricing')


@admin_required
def testimonials_list(request):
    items = Testimonial.objects.all()
    return render(request, 'adminpanel/testimonials.html', {'items': items})


@admin_required
def testimonial_add(request):
    if request.method == 'POST':
        Testimonial.objects.create(
            name=request.POST.get('name', '').strip(),
            role=request.POST.get('role', '').strip(),
            initials=request.POST.get('initials', '').strip().upper()[:3],
            text=request.POST.get('text', '').strip(),
            rating=int(request.POST.get('rating', 5)),
            is_active=bool(request.POST.get('is_active')),
            order=int(request.POST.get('order', 0)),
        )
        messages.success(request, 'Testimonial added.')
        return redirect('admin_testimonials')
    return render(request, 'adminpanel/testimonial_form.html', {'item': None})


@admin_required
def testimonial_edit(request, pk):
    item = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        item.name = request.POST.get('name', item.name).strip()
        item.role = request.POST.get('role', item.role).strip()
        item.initials = request.POST.get('initials', item.initials).strip().upper()[:3]
        item.text = request.POST.get('text', item.text).strip()
        item.rating = int(request.POST.get('rating', item.rating))
        item.is_active = bool(request.POST.get('is_active'))
        item.order = int(request.POST.get('order', item.order))
        item.save()
        messages.success(request, 'Testimonial updated.')
        return redirect('admin_testimonials')
    return render(request, 'adminpanel/testimonial_form.html', {'item': item})


@admin_required
def testimonial_delete(request, pk):
    get_object_or_404(Testimonial, pk=pk).delete()
    messages.success(request, 'Testimonial deleted.')
    return redirect('admin_testimonials')
