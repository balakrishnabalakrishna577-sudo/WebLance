from django.shortcuts import render
from .models import PortfolioItem

def portfolio(request):
    portfolio_items = PortfolioItem.objects.all()

    # Build ordered list of (value, label) for categories that have items
    cat_map = dict(PortfolioItem.CATEGORY_CHOICES)
    seen = []
    seen_set = set()
    for item in portfolio_items:
        if item.category not in seen_set:
            seen_set.add(item.category)
            seen.append((item.category, cat_map.get(item.category, item.category)))

    return render(request, 'portfolio/portfolio.html', {
        'portfolio_items': portfolio_items,
        'categories': seen,
    })
