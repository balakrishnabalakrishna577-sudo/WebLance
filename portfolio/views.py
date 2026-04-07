from django.shortcuts import render
from .models import PortfolioItem

def portfolio(request):
    # Get all portfolio items
    portfolio_items = PortfolioItem.objects.all()
    
    context = {
        'portfolio_items': portfolio_items,
    }
    return render(request, 'portfolio/portfolio.html', context)
