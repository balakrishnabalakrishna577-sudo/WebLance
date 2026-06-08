"""
Auto-generates a structured website proposal (3 template previews)
based on the website type selected by the user.
Uses Gemini AI if available, falls back to rich static data.
"""
import json
import os
from django.conf import settings

# ── Static fallback proposals per website type ───────────────────

STATIC_PROPOSALS = {
    'business': {
        'website_type': 'Business Website',
        'target_audience': 'Local businesses, professionals, and corporate clients looking for a credible online presence.',
        'key_features': ['About & Team section', 'Services showcase', 'Contact form', 'Google Maps', 'WhatsApp chat', 'SEO optimized'],
        'templates': [
            {
                'id': 1,
                'name': 'Corporate Pro',
                'style': 'Modern Corporate',
                'colors': {'primary': '#1a73e8', 'secondary': '#ffffff', 'accent': '#f4a261', 'bg': '#f8f9fa', 'text': '#1a1a2e'},
                'layout': 'Full-width hero, 3-column services, split about section',
                'sections': [
                    {'name': 'Header', 'desc': 'White navbar with logo left, nav links center, CTA button right'},
                    {'name': 'Hero', 'desc': 'Large blue gradient background, bold headline left, professional office image right'},
                    {'name': 'About', 'desc': 'Split layout — company story left, team photo right with stats counters'},
                    {'name': 'Services', 'desc': '3-column card grid with icons, titles, and short descriptions'},
                    {'name': 'Testimonials', 'desc': 'Light gray background, 3 client quote cards with star ratings'},
                    {'name': 'Contact', 'desc': 'Two-column — contact form left, address + map right'},
                    {'name': 'Footer', 'desc': 'Dark footer with logo, quick links, social icons, copyright'},
                ],
                'visual': 'Clean white and blue professional look. Bold typography, generous whitespace, subtle card shadows.',
                'dummy': {
                    'site_name': 'NexaCorp Solutions',
                    'headline': 'Building Businesses That Last',
                    'subheadline': 'Professional web solutions tailored for your growth',
                    'cta': 'Get Free Consultation',
                    'image_idea': 'Modern office team meeting, confident professionals',
                },
                'recommended': False,
            },
            {
                'id': 2,
                'name': 'Dark Elite',
                'style': 'Dark Premium',
                'colors': {'primary': '#00ff88', 'secondary': '#111111', 'accent': '#00cc6a', 'bg': '#0a0a0a', 'text': '#e8e8e8'},
                'layout': 'Dark full-screen hero, glowing accent cards, minimal sections',
                'sections': [
                    {'name': 'Header', 'desc': 'Dark sticky navbar, green logo glow, hamburger on mobile'},
                    {'name': 'Hero', 'desc': 'Full-screen dark background, large white headline, green CTA button, subtle particle animation'},
                    {'name': 'About', 'desc': 'Dark card with green border accent, company stats in glowing numbers'},
                    {'name': 'Services', 'desc': 'Dark cards with green icon tops, hover glow effect'},
                    {'name': 'Testimonials', 'desc': 'Dark carousel with client photos, green quote marks'},
                    {'name': 'Contact', 'desc': 'Dark form with green focus borders, floating label inputs'},
                    {'name': 'Footer', 'desc': 'Deep black footer, green brand name, minimal links'},
                ],
                'visual': 'Sleek dark theme with neon green accents. Premium, tech-forward feel. Glowing borders and smooth animations.',
                'dummy': {
                    'site_name': 'Vertex Digital',
                    'headline': 'We Build Digital Experiences',
                    'subheadline': 'Premium websites that convert visitors into clients',
                    'cta': 'Start Your Project',
                    'image_idea': 'Dark tech workspace, glowing screens, modern setup',
                },
                'recommended': True,
            },
            {
                'id': 3,
                'name': 'Minimal Clean',
                'style': 'Minimal & Elegant',
                'colors': {'primary': '#2d2d2d', 'secondary': '#ffffff', 'accent': '#e63946', 'bg': '#ffffff', 'text': '#333333'},
                'layout': 'Centered content, lots of whitespace, thin typography',
                'sections': [
                    {'name': 'Header', 'desc': 'Minimal white navbar, centered logo, underline nav links'},
                    {'name': 'Hero', 'desc': 'Centered text on white, large serif headline, small red accent line, subtle background pattern'},
                    {'name': 'About', 'desc': 'Centered paragraph with thin divider lines, black and white team photo'},
                    {'name': 'Services', 'desc': 'Simple list or 2-column layout, thin border cards, no heavy shadows'},
                    {'name': 'Testimonials', 'desc': 'Italic quotes centered, client name in small caps'},
                    {'name': 'Contact', 'desc': 'Minimal form, thin input borders, red submit button'},
                    {'name': 'Footer', 'desc': 'White footer, small text, centered copyright'},
                ],
                'visual': 'Ultra-clean white design. Lots of breathing room. Elegant serif fonts. Red accent for CTAs only.',
                'dummy': {
                    'site_name': 'Lumina Studio',
                    'headline': 'Crafted with Purpose',
                    'subheadline': 'Simple. Elegant. Effective.',
                    'cta': 'View Our Work',
                    'image_idea': 'Clean desk, minimal workspace, white and neutral tones',
                },
                'recommended': False,
            },
        ],
        'best_template': 2,
        'best_reason': 'The Dark Elite template stands out with a premium feel that builds instant trust and authority for business clients.',
    },

    'ecommerce': {
        'website_type': 'E-Commerce Website',
        'target_audience': 'Online shoppers looking for products, deals, and a smooth buying experience.',
        'key_features': ['Product catalog', 'Shopping cart', 'Razorpay/UPI payment', 'Order tracking', 'Customer login', 'Admin panel'],
        'templates': [
            {
                'id': 1,
                'name': 'ShopBold',
                'style': 'Bold & Vibrant',
                'colors': {'primary': '#ff6b35', 'secondary': '#ffffff', 'accent': '#ffd700', 'bg': '#fff8f5', 'text': '#1a1a1a'},
                'layout': 'Banner hero, product grid, category strips, flash sale section',
                'sections': [
                    {'name': 'Header', 'desc': 'White navbar with search bar, cart icon with badge, login button'},
                    {'name': 'Hero', 'desc': 'Full-width promotional banner with product image, discount badge, shop now button'},
                    {'name': 'Categories', 'desc': 'Horizontal scrollable category chips with icons'},
                    {'name': 'Products', 'desc': '4-column product grid with image, name, price, add-to-cart button'},
                    {'name': 'Flash Sale', 'desc': 'Orange banner with countdown timer and featured products'},
                    {'name': 'Testimonials', 'desc': 'Star ratings, customer photos, verified purchase badges'},
                    {'name': 'Footer', 'desc': 'Multi-column footer with links, payment icons, newsletter signup'},
                ],
                'visual': 'Energetic orange and white. Bold product images. Urgency-driven design with sale badges and timers.',
                'dummy': {
                    'site_name': 'ZapMart',
                    'headline': 'Shop Smart. Save Big.',
                    'subheadline': 'Thousands of products, delivered to your door',
                    'cta': 'Shop Now',
                    'image_idea': 'Colorful product flat lay, shopping bags, happy customer',
                },
                'recommended': False,
            },
            {
                'id': 2,
                'name': 'LuxStore',
                'style': 'Dark Luxury',
                'colors': {'primary': '#c9a84c', 'secondary': '#1a1a1a', 'accent': '#ffffff', 'bg': '#0d0d0d', 'text': '#e8e8e8'},
                'layout': 'Dark full-screen hero, gold accent product cards, editorial layout',
                'sections': [
                    {'name': 'Header', 'desc': 'Dark navbar, gold logo, minimal nav, cart and wishlist icons'},
                    {'name': 'Hero', 'desc': 'Full-screen dark background, large product image, gold headline, elegant CTA'},
                    {'name': 'Featured', 'desc': 'Dark cards with gold borders, product name in serif font, price in gold'},
                    {'name': 'Collections', 'desc': 'Full-width editorial images with collection name overlay'},
                    {'name': 'Testimonials', 'desc': 'Dark background, gold star ratings, italic customer quotes'},
                    {'name': 'Newsletter', 'desc': 'Dark section with gold border input, exclusive offer text'},
                    {'name': 'Footer', 'desc': 'Deep black, gold brand name, payment methods, social links'},
                ],
                'visual': 'Premium dark luxury feel. Gold accents on black. Serif fonts for product names. Feels like a high-end brand.',
                'dummy': {
                    'site_name': 'Aurum Boutique',
                    'headline': 'Luxury Redefined',
                    'subheadline': 'Exclusive collections for the discerning buyer',
                    'cta': 'Explore Collection',
                    'image_idea': 'Luxury product on dark background, gold lighting, premium packaging',
                },
                'recommended': True,
            },
            {
                'id': 3,
                'name': 'FreshShop',
                'style': 'Clean & Minimal',
                'colors': {'primary': '#4caf50', 'secondary': '#ffffff', 'accent': '#ff5722', 'bg': '#fafafa', 'text': '#212121'},
                'layout': 'Clean grid, category sidebar, simple product cards',
                'sections': [
                    {'name': 'Header', 'desc': 'White header, green logo, search bar, cart icon'},
                    {'name': 'Hero', 'desc': 'Clean banner with product image, simple headline, green CTA'},
                    {'name': 'Categories', 'desc': 'Left sidebar with category list, main area product grid'},
                    {'name': 'Products', 'desc': 'Clean white cards, product image, name, price, green add-to-cart'},
                    {'name': 'Offers', 'desc': 'Green banner with discount code and limited time offer'},
                    {'name': 'Reviews', 'desc': 'Simple star ratings, text reviews, helpful vote count'},
                    {'name': 'Footer', 'desc': 'Light gray footer, green links, payment icons'},
                ],
                'visual': 'Fresh and clean. Green and white with orange accents. Easy to browse. Feels trustworthy and approachable.',
                'dummy': {
                    'site_name': 'GreenBasket',
                    'headline': 'Fresh Finds Every Day',
                    'subheadline': 'Quality products at honest prices',
                    'cta': 'Browse Products',
                    'image_idea': 'Fresh products on white background, clean flat lay',
                },
                'recommended': False,
            },
        ],
        'best_template': 2,
        'best_reason': 'LuxStore creates a premium shopping experience that increases perceived product value and drives higher conversions.',
    },

    'landing': {
        'website_type': 'Landing Page',
        'target_audience': 'Potential customers or leads who need to be converted quickly with a focused message.',
        'key_features': ['Hero with CTA', 'Lead capture form', 'Benefits section', 'Social proof', 'WhatsApp button', 'Fast loading'],
        'templates': [
            {
                'id': 1,
                'name': 'ConvertX',
                'style': 'High-Converting Bold',
                'colors': {'primary': '#6c63ff', 'secondary': '#ffffff', 'accent': '#ff6584', 'bg': '#f0efff', 'text': '#1a1a2e'},
                'layout': 'Single scroll page, large hero, benefit icons, form, social proof',
                'sections': [
                    {'name': 'Header', 'desc': 'Minimal sticky bar with logo and phone number only'},
                    {'name': 'Hero', 'desc': 'Purple gradient background, bold headline, subtext, lead form on right side'},
                    {'name': 'Benefits', 'desc': '3 icon cards with short benefit statements'},
                    {'name': 'How It Works', 'desc': '3-step numbered process with icons'},
                    {'name': 'Social Proof', 'desc': 'Client logos strip + 2 testimonial quotes'},
                    {'name': 'CTA Section', 'desc': 'Purple banner with large CTA button and urgency text'},
                    {'name': 'Footer', 'desc': 'Minimal — just copyright and privacy policy link'},
                ],
                'visual': 'Purple and white with pink accents. Energetic and conversion-focused. Bold headlines, clear CTAs.',
                'dummy': {
                    'site_name': 'LaunchPad',
                    'headline': 'Get More Leads in 30 Days',
                    'subheadline': 'The fastest way to grow your business online',
                    'cta': 'Get Free Demo',
                    'image_idea': 'Person on laptop, growth chart, success concept',
                },
                'recommended': False,
            },
            {
                'id': 2,
                'name': 'NightLaunch',
                'style': 'Dark & Impactful',
                'colors': {'primary': '#00ff88', 'secondary': '#0a0a0a', 'accent': '#00cc6a', 'bg': '#050505', 'text': '#ffffff'},
                'layout': 'Dark full-screen hero, glowing form, minimal sections',
                'sections': [
                    {'name': 'Header', 'desc': 'Dark transparent navbar, green logo, single CTA button'},
                    {'name': 'Hero', 'desc': 'Full-screen dark, large white headline, green subtext, glowing lead form'},
                    {'name': 'Benefits', 'desc': 'Dark cards with green check icons, short punchy benefit lines'},
                    {'name': 'Proof', 'desc': 'Dark section with large numbers (clients, projects, ratings) in green'},
                    {'name': 'Testimonial', 'desc': 'Single large quote with client photo, dark background'},
                    {'name': 'Final CTA', 'desc': 'Green gradient button, urgency text, WhatsApp icon'},
                    {'name': 'Footer', 'desc': 'Minimal dark footer, green brand name'},
                ],
                'visual': 'Dramatic dark theme with neon green. High-impact, premium feel. Perfect for tech or service businesses.',
                'dummy': {
                    'site_name': 'NovaSpark',
                    'headline': 'Your Business Deserves Better',
                    'subheadline': 'We build websites that work while you sleep',
                    'cta': 'Claim Your Free Audit',
                    'image_idea': 'Dark tech background, glowing elements, futuristic feel',
                },
                'recommended': True,
            },
            {
                'id': 3,
                'name': 'SunrisePage',
                'style': 'Warm & Friendly',
                'colors': {'primary': '#ff9800', 'secondary': '#ffffff', 'accent': '#4caf50', 'bg': '#fffbf5', 'text': '#333333'},
                'layout': 'Warm hero, friendly sections, approachable form',
                'sections': [
                    {'name': 'Header', 'desc': 'White navbar with orange logo, phone number visible'},
                    {'name': 'Hero', 'desc': 'Warm orange gradient, friendly headline, smiling person image, simple form'},
                    {'name': 'Benefits', 'desc': 'Orange icon cards, friendly short descriptions'},
                    {'name': 'About', 'desc': 'Warm section with founder photo and personal message'},
                    {'name': 'Testimonials', 'desc': 'Orange star ratings, friendly customer photos'},
                    {'name': 'CTA', 'desc': 'Orange button, green WhatsApp button side by side'},
                    {'name': 'Footer', 'desc': 'Warm white footer, orange links'},
                ],
                'visual': 'Warm orange and white. Friendly and approachable. Great for local businesses, coaches, or service providers.',
                'dummy': {
                    'site_name': 'BrightStart',
                    'headline': 'Let\'s Grow Together',
                    'subheadline': 'Friendly, affordable, and results-driven',
                    'cta': 'Talk to Us Today',
                    'image_idea': 'Friendly team, warm office, smiling people',
                },
                'recommended': False,
            },
        ],
        'best_template': 2,
        'best_reason': 'NightLaunch creates maximum impact with its dark premium design, making your offer stand out and driving higher conversions.',
    },

    'custom': {
        'website_type': 'Custom Website',
        'target_audience': 'Businesses or individuals needing a unique, tailored web solution beyond standard templates.',
        'key_features': ['Custom modules', 'User authentication', 'Admin dashboard', 'Database integration', 'API connections', 'Scalable architecture'],
        'templates': [
            {
                'id': 1,
                'name': 'TechForge',
                'style': 'Modern Tech',
                'colors': {'primary': '#7c3aed', 'secondary': '#ffffff', 'accent': '#06b6d4', 'bg': '#0f0f1a', 'text': '#e2e8f0'},
                'layout': 'Dark tech layout, gradient accents, dashboard-style sections',
                'sections': [
                    {'name': 'Header', 'desc': 'Dark navbar with purple logo, nav links, login/signup buttons'},
                    {'name': 'Hero', 'desc': 'Dark gradient background, animated headline, cyan accent lines, demo CTA'},
                    {'name': 'Features', 'desc': 'Dark cards with purple/cyan gradient icons, feature descriptions'},
                    {'name': 'How It Works', 'desc': 'Step-by-step with connecting lines, numbered dark cards'},
                    {'name': 'Dashboard Preview', 'desc': 'Mockup screenshot of the admin/user dashboard'},
                    {'name': 'Pricing', 'desc': 'Dark pricing cards with purple highlight for recommended plan'},
                    {'name': 'Footer', 'desc': 'Dark footer with purple brand, links, social icons'},
                ],
                'visual': 'Dark tech aesthetic with purple and cyan gradients. Feels like a SaaS product. Modern and powerful.',
                'dummy': {
                    'site_name': 'SynapseApp',
                    'headline': 'The Platform Built for Scale',
                    'subheadline': 'Custom solutions engineered for your exact needs',
                    'cta': 'Request a Demo',
                    'image_idea': 'Dashboard mockup, code editor, tech abstract',
                },
                'recommended': False,
            },
            {
                'id': 2,
                'name': 'NexaFlow',
                'style': 'Dark Premium',
                'colors': {'primary': '#00ff88', 'secondary': '#111111', 'accent': '#00cc6a', 'bg': '#0a0a0a', 'text': '#e8e8e8'},
                'layout': 'Dark full-screen sections, green accents, clean module cards',
                'sections': [
                    {'name': 'Header', 'desc': 'Dark sticky navbar, green logo, nav links, green CTA button'},
                    {'name': 'Hero', 'desc': 'Full-screen dark, large headline, green accent text, animated background'},
                    {'name': 'Features', 'desc': 'Dark cards with green top border, icon, title, description'},
                    {'name': 'Process', 'desc': 'Dark timeline with green dots and connecting line'},
                    {'name': 'Stats', 'desc': 'Dark section with large green numbers — projects, clients, uptime'},
                    {'name': 'Testimonials', 'desc': 'Dark cards with green quote marks, client details'},
                    {'name': 'Footer', 'desc': 'Deep dark footer, green brand, minimal links'},
                ],
                'visual': 'Sleek dark with neon green. Premium custom software feel. Clean, powerful, and professional.',
                'dummy': {
                    'site_name': 'CoreBuild',
                    'headline': 'Custom Built. Perfectly Yours.',
                    'subheadline': 'We engineer web solutions that fit your business like a glove',
                    'cta': 'Start Building',
                    'image_idea': 'Abstract code, dark workspace, green terminal glow',
                },
                'recommended': True,
            },
            {
                'id': 3,
                'name': 'ClearPath',
                'style': 'Clean Professional',
                'colors': {'primary': '#0ea5e9', 'secondary': '#ffffff', 'accent': '#10b981', 'bg': '#f8fafc', 'text': '#0f172a'},
                'layout': 'Light clean layout, blue accents, structured sections',
                'sections': [
                    {'name': 'Header', 'desc': 'White navbar, blue logo, clean nav, blue CTA button'},
                    {'name': 'Hero', 'desc': 'Light blue gradient, professional headline, product mockup image'},
                    {'name': 'Features', 'desc': 'White cards with blue icons, clean descriptions'},
                    {'name': 'Process', 'desc': '4-step horizontal process with blue numbered circles'},
                    {'name': 'Integrations', 'desc': 'Logo grid of supported tools and platforms'},
                    {'name': 'Testimonials', 'desc': 'Light gray cards, blue star ratings, client photos'},
                    {'name': 'Footer', 'desc': 'Light gray footer, blue links, newsletter signup'},
                ],
                'visual': 'Clean and professional. Blue and white with green accents. Trustworthy and enterprise-ready.',
                'dummy': {
                    'site_name': 'BluePrint Pro',
                    'headline': 'Built for Your Business',
                    'subheadline': 'Reliable, scalable, and tailored to your workflow',
                    'cta': 'Get Started Free',
                    'image_idea': 'Clean office, professional team, light workspace',
                },
                'recommended': False,
            },
        ],
        'best_template': 2,
        'best_reason': 'NexaFlow delivers a premium dark aesthetic that signals technical expertise and builds immediate confidence in your custom solution.',
    },
}


def _try_gemini(website_type_display, business_name, description):
    """Try to generate proposal via Gemini AI. Returns dict or None."""
    import logging
    logger = logging.getLogger(__name__)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        logger.warning('google-genai package not installed')
        return None

    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
    if not api_key or api_key == 'YOUR_GEMINI_API_KEY_HERE':
        logger.warning('GEMINI_API_KEY not set')
        return None

    prompt = f"""You are a web design assistant. Generate a website proposal as pure JSON only.
No markdown, no code fences, no explanation — just the raw JSON object.

Website Type: {website_type_display}
Business Name: {business_name}
Description: {description[:400]}

Return EXACTLY this structure (3 templates):
{{
  "website_type": "{website_type_display}",
  "target_audience": "describe the ideal visitors/customers",
  "key_features": ["feature1","feature2","feature3","feature4","feature5","feature6"],
  "templates": [
    {{
      "id": 1,
      "name": "Template Name",
      "style": "Modern Corporate",
      "colors": {{"primary":"#1a73e8","secondary":"#ffffff","accent":"#f4a261","bg":"#f8f9fa","text":"#1a1a2e"}},
      "layout": "Full-width hero, 3-column services, split about section",
      "sections": [
        {{"name":"Header","desc":"White navbar with logo left, nav links center, CTA button right"}},
        {{"name":"Hero","desc":"Large gradient background, bold headline left, image right"}},
        {{"name":"About","desc":"Split layout — story left, team photo right with stats"}},
        {{"name":"Services","desc":"3-column card grid with icons and descriptions"}},
        {{"name":"Testimonials","desc":"Light gray background, 3 client quote cards with stars"}},
        {{"name":"Contact","desc":"Two-column — form left, address and map right"}},
        {{"name":"Footer","desc":"Dark footer with logo, links, social icons, copyright"}}
      ],
      "visual": "Clean professional look with bold typography and generous whitespace",
      "dummy": {{
        "site_name": "Business name based on input",
        "headline": "Compelling headline for this business",
        "subheadline": "Supporting tagline",
        "cta": "Action button text",
        "image_idea": "Describe ideal hero image"
      }},
      "recommended": false
    }},
    {{
      "id": 2,
      "name": "Dark Premium",
      "style": "Dark Premium",
      "colors": {{"primary":"#00ff88","secondary":"#111111","accent":"#00cc6a","bg":"#0a0a0a","text":"#e8e8e8"}},
      "layout": "Dark full-screen hero, glowing accent cards",
      "sections": [
        {{"name":"Header","desc":"Dark sticky navbar, green logo glow"}},
        {{"name":"Hero","desc":"Full-screen dark, large white headline, green CTA"}},
        {{"name":"About","desc":"Dark card with green border, glowing stats"}},
        {{"name":"Services","desc":"Dark cards with green icon tops, hover glow"}},
        {{"name":"Testimonials","desc":"Dark carousel with green quote marks"}},
        {{"name":"Contact","desc":"Dark form with green focus borders"}},
        {{"name":"Footer","desc":"Deep black footer, green brand name"}}
      ],
      "visual": "Sleek dark theme with neon green accents. Premium tech-forward feel.",
      "dummy": {{
        "site_name": "Premium version of business name",
        "headline": "Bold impactful headline",
        "subheadline": "Premium supporting tagline",
        "cta": "Premium CTA text",
        "image_idea": "Dark premium image concept"
      }},
      "recommended": true
    }},
    {{
      "id": 3,
      "name": "Minimal Clean",
      "style": "Minimal & Elegant",
      "colors": {{"primary":"#2d2d2d","secondary":"#ffffff","accent":"#e63946","bg":"#ffffff","text":"#333333"}},
      "layout": "Centered content, lots of whitespace, thin typography",
      "sections": [
        {{"name":"Header","desc":"Minimal white navbar, centered logo"}},
        {{"name":"Hero","desc":"Centered text on white, large serif headline"}},
        {{"name":"About","desc":"Centered paragraph with thin divider lines"}},
        {{"name":"Services","desc":"Simple 2-column layout, thin border cards"}},
        {{"name":"Testimonials","desc":"Italic quotes centered, client name in small caps"}},
        {{"name":"Contact","desc":"Minimal form, thin input borders, red submit"}},
        {{"name":"Footer","desc":"White footer, small text, centered copyright"}}
      ],
      "visual": "Ultra-clean white design. Elegant serif fonts. Red accent for CTAs only.",
      "dummy": {{
        "site_name": "Elegant version of business name",
        "headline": "Elegant minimal headline",
        "subheadline": "Simple elegant tagline",
        "cta": "Minimal CTA text",
        "image_idea": "Clean minimal image concept"
      }},
      "recommended": false
    }}
  ],
  "best_template": 2,
  "best_reason": "Why the dark premium template is best for this specific business"
}}

Make all content specific to the business: {business_name} ({website_type_display}).
Return ONLY the JSON. No other text."""

    models_to_try = [
        'gemini-2.5-flash-lite',
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-2.0-flash',
        'gemini-2.0-flash-lite',
    ]

    client = genai.Client(api_key=api_key)

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=3000,
                ),
            )
            text = response.text.strip()

            # Strip any markdown code fences
            if '```' in text:
                parts = text.split('```')
                for part in parts:
                    part = part.strip()
                    if part.startswith('json'):
                        part = part[4:].strip()
                    if part.startswith('{'):
                        text = part
                        break

            # Find the JSON object boundaries
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                text = text[start:end]

            data = json.loads(text)
            if 'templates' in data and len(data['templates']) >= 3:
                logger.info(f'Gemini proposal generated via {model_name}')
                return data

        except json.JSONDecodeError as e:
            logger.warning(f'Gemini {model_name} returned invalid JSON: {e}')
            continue
        except Exception as e:
            logger.warning(f'Gemini {model_name} failed: {e}')
            continue

    logger.error('All Gemini models failed for proposal generation')
    return None


def generate_proposal(website_type, business_name='', description=''):
    """
    Returns a proposal dict for the given website_type.
    Tries Gemini first, falls back to static data.
    """
    # Try AI generation
    type_labels = {
        'business': 'Business Website',
        'ecommerce': 'E-Commerce Website',
        'landing': 'Landing Page',
        'custom': 'Custom Website',
    }
    label = type_labels.get(website_type, website_type.title())
    ai_result = _try_gemini(label, business_name, description)
    if ai_result and 'templates' in ai_result:
        return ai_result

    # Static fallback
    return STATIC_PROPOSALS.get(website_type, STATIC_PROPOSALS['business'])
