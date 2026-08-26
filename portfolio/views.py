from django.shortcuts import render
from django.core.paginator import Paginator
from .models import PortfolioItem


def portfolio(request):
    all_items = PortfolioItem.objects.all()

    # Build distinct category list from all items (for filter buttons)
    cat_map = dict(PortfolioItem.CATEGORY_CHOICES)
    seen, seen_set = [], set()
    for item in all_items:
        if item.category not in seen_set:
            seen_set.add(item.category)
            seen.append((item.category, cat_map.get(item.category, item.category)))

    # Category filter from GET param
    selected_cat = request.GET.get('category', 'all').strip()
    if selected_cat and selected_cat != 'all':
        items_qs = all_items.filter(category=selected_cat)
    else:
        items_qs = all_items

    # Pagination — 6 per page
    paginator = Paginator(items_qs, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'portfolio/portfolio.html', {
        'portfolio_items': page_obj,
        'page_obj':        page_obj,
        'categories':      seen,
        'selected_cat':    selected_cat,
        'total_count':     all_items.count(),
    })
