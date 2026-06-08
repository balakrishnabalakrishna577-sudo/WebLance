import json
import re
import os
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import BotSession, BotMessage

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# ── Compact system prompt ────────────────────────────────────────
SYSTEM_PROMPT = """You are the AI assistant for WEBLANCE, a web development company in Devanahalli, Karnataka, India.

SERVICES & PRICES:
- Custom Website: from ₹15,000 (15-20 days)
- E-Commerce: from ₹25,000 (30-45 days)
- SEO: from ₹8,000/month
- Web Design: from ₹10,000
- Redesign: from ₹12,000
- Maintenance: from ₹3,000/month

CONTACT: +91 7892934437 | infoweblance01@gmail.com | WhatsApp: wa.me/917892934437
TEAM: Balakrishna (Lead Dev), Varun (UI/UX), Sumith (Frontend), Bindu (SEO)
STATS: 150+ projects, 120+ clients, 5 stars, 5+ years
TECH: Python, Django, HTML, CSS, JS, Bootstrap, React, PostgreSQL
PAYMENT: 50% advance + 50% on delivery. UPI/Bank/Razorpay/PayPal.
PAGES: Home(/), About(/about/), Services(/services/), Portfolio(/portfolio/), Pricing(/pricing/), Contact(/contact/), Request(/request-website/)

Be helpful, friendly, concise. Use markdown. Answer web dev questions too. Suggest WEBLANCE services when relevant."""

MODELS = [
    'gemini-flash-latest',
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash',
    'gemini-2.5-flash',
]

GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', os.environ.get('GEMINI_API_KEY', ''))
_client = None


def get_client():
    global _client
    if _client is None and GENAI_AVAILABLE and GEMINI_API_KEY and GEMINI_API_KEY != 'YOUR_GEMINI_API_KEY_HERE':
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def call_gemini(client, message, history):
    contents = []
    for msg in history[-6:]:
        role = "user" if msg.get("role") == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg.get("text", ""))]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.7,
        max_output_tokens=400,
    )

    last_error = None
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model, contents=contents, config=config
            )
            return response.text
        except Exception as e:
            last_error = e
            continue
    raise last_error


# ── Fallback rule-based engine ───────────────────────────────────
KB = {
    "greeting":  (r"\b(hi|hello|hey|namaste)\b", "👋 Hello! Welcome to **WEBLANCE**!\n\nAsk me about:\n• 💻 Services & pricing\n• ⏱️ Timelines\n• 📞 Contact info\n• 📁 Portfolio"),
    "services":  (r"\b(service|services|what do you (do|offer|build)|offer|provide)\b", "🚀 **WEBLANCE Services:**\n\n1. Custom Website — from ₹15,000\n2. E-Commerce — from ₹25,000\n3. SEO — from ₹8,000/month\n4. Web Design — from ₹10,000\n5. Redesign — from ₹12,000\n6. Maintenance — from ₹3,000/month"),
    "pricing":   (r"\b(price|pricing|cost|how much|rate|package|budget|fee)\b", "💰 **Pricing:**\n\n• Starter Website: ₹15,000\n• Business Website: ₹25,000\n• E-Commerce: ₹40,000+\n• SEO: ₹8,000/mo\n• Maintenance: ₹3,000/mo\n\n[Get a Quote](/request-website/)"),
    "contact":   (r"\b(contact|reach|call|phone|email|whatsapp|location|address)\b", "📞 **Contact:**\n\n📍 Devanahalli, Karnataka\n📱 +91 7892934437\n📧 infoweblance01@gmail.com\n💬 [WhatsApp](https://wa.me/917892934437)\n🕐 Mon–Sat 9AM–6PM"),
    "portfolio": (r"\b(portfolio|project|work|example|sample|previous)\b", "📁 **Portfolio:** 150+ projects\n\n• Corporate websites\n• E-commerce stores\n• Landing pages\n\n[View Portfolio](/portfolio/)"),
    "timeline":  (r"\b(how long|timeline|time|days|weeks|duration|delivery|deadline)\b", "⏱️ **Timelines:**\n\n• Landing Page: 7–10 days\n• Business Website: 15–20 days\n• E-Commerce: 30–45 days"),
    "payment":   (r"\b(payment|pay|advance|upi|bank|installment)\b", "💳 **Payment:** UPI, Bank Transfer, Razorpay, PayPal\n\n50% advance + 50% on delivery"),
    "about":     (r"\b(about|who are you|weblance|company|team|founded)\b", "🏢 **WEBLANCE** — Devanahalli, Karnataka\n\n👥 Team: Balakrishna, Varun, Sumith, Bindu\n📅 5+ years | ✅ 150+ projects | ⭐ 5 stars\n\n[About Us](/about/)"),
    "thanks":    (r"\b(thank|thanks|great|awesome|perfect|helpful)\b", "😊 You're welcome! Anything else I can help with?"),
    "bye":       (r"\b(bye|goodbye|see you|later)\b", "👋 Bye! Have a great day!\n\n📞 Need help? Call: +91 7892934437"),
}

DEFAULT = "🤔 I can help with **services**, **pricing**, **timeline**, or **contact** info.\n\nOr [contact us directly](/contact/)!"


def rule_based_response(message):
    msg = message.lower().strip()
    for _, (pattern, response) in KB.items():
        if re.search(pattern, msg, re.IGNORECASE):
            return response
    return DEFAULT


def get_visitor_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


@require_POST
def chat(request):
    try:
        data    = json.loads(request.body)
        message = data.get("message", "").strip()
        history = data.get("history", [])
        session_id = data.get("session_id", "")

        if not message:
            return JsonResponse({"error": "Empty message"}, status=400)
        if len(message) > 800:
            return JsonResponse({"error": "Message too long"}, status=400)

        # ── Get or create the BotSession ──────────────────────────
        session = None
        if session_id:
            try:
                import uuid
                session = BotSession.objects.get(session_id=uuid.UUID(session_id))
            except (BotSession.DoesNotExist, ValueError):
                session = None

        if session is None:
            session = BotSession.objects.create(
                visitor_ip=get_visitor_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                page_url=request.META.get('HTTP_REFERER', '')[:500],
            )

        # ── Save the user message ─────────────────────────────────
        BotMessage.objects.create(session=session, role='user', text=message)

        # ── Generate reply ────────────────────────────────────────
        client = get_client()
        if client:
            try:
                reply = call_gemini(client, message, history)
            except Exception:
                reply = rule_based_response(message)
        else:
            reply = rule_based_response(message)

        # ── Save the bot reply ────────────────────────────────────
        BotMessage.objects.create(session=session, role='bot', text=reply)

        return JsonResponse({
            "response":   reply,
            "status":     "ok",
            "session_id": str(session.session_id),
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception:
        return JsonResponse({"error": "Server error"}, status=500)
