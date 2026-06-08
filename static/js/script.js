/* ========================================
   WEBLANCE - Advanced JavaScript
   ======================================== */

/* ── Preloader ── */
(function () {
    const loader  = document.getElementById('preloader');
    const pct     = document.getElementById('preloader-pct');
    const barFill = document.getElementById('preloader-bar-fill');
    const circle  = document.getElementById('preloader-ring-circle');
    const status  = loader && loader.querySelector('.preloader-status');
    const DASH    = 213; // circumference of r=34 circle

    if (!loader) return;

    function setProgress(n) {
        n = Math.min(Math.max(n, 0), 100);
        if (pct)     pct.textContent = Math.floor(n) + '%';
        if (barFill) barFill.style.width = n + '%';
        if (circle)  circle.style.strokeDashoffset = DASH - (DASH * n / 100);
    }

    function hide() {
        setProgress(100);
        if (status) status.textContent = 'Ready!';
        setTimeout(() => loader.classList.add('hidden'), 500);
    }

    // Animate progress naturally
    let n = 0;
    const iv = setInterval(() => {
        // Slow down as it approaches 90
        const step = n < 70 ? Math.random() * 12 : Math.random() * 3;
        n = Math.min(n + step, 90);
        setProgress(n);
    }, 120);

    // On full page load, complete it
    window.addEventListener('load', () => {
        clearInterval(iv);
        hide();
    });

    // Safety fallback — never hang forever
    setTimeout(() => {
        clearInterval(iv);
        hide();
    }, 5000);
})();

/* ── Scroll Progress Bar ── */
(function () {
    const bar = document.getElementById('scroll-progress');
    if (!bar) return;
    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        const total    = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.width = (total > 0 ? (scrolled / total) * 100 : 0) + '%';
    }, { passive: true });
})();

/* ── Navbar scroll ── */
(function () {
    const nav = document.querySelector('.wl-nav');
    if (!nav) return;
    window.addEventListener('scroll', () => nav.classList.toggle('scrolled', window.scrollY > 60), { passive: true });
})();

/* ── Mobile menu ── */
(function () {
    const hamburger  = document.getElementById('wlHamburger');
    const mobileMenu = document.getElementById('wlMobileMenu');
    const closeBtn   = document.getElementById('wlMobileClose');
    if (!hamburger || !mobileMenu) return;

    // Move mobile menu to body so sticky nav doesn't clip it
    document.body.appendChild(mobileMenu);

    // Backdrop
    const backdrop = document.createElement('div');
    backdrop.style.cssText = 'display:none;position:fixed;inset:0;background:rgba(0,0,0,0.65);z-index:1998;backdrop-filter:blur(3px);transition:opacity 0.3s;';
    document.body.appendChild(backdrop);

    const open = () => {
        mobileMenu.classList.add('open');
        backdrop.style.display = 'block';
        document.body.style.overflow = 'hidden';
        // Animate hamburger to X
        const spans = hamburger.querySelectorAll('span');
        if (spans[0]) spans[0].style.cssText = 'transform:rotate(45deg) translate(5px,5px);background:#6366F1;';
        if (spans[1]) spans[1].style.cssText = 'opacity:0;';
        if (spans[2]) spans[2].style.cssText = 'transform:rotate(-45deg) translate(5px,-5px);background:#6366F1;';
    };
    const close = () => {
        mobileMenu.classList.remove('open');
        backdrop.style.display = 'none';
        document.body.style.overflow = '';
        const spans = hamburger.querySelectorAll('span');
        spans.forEach(s => s.style.cssText = '');
    };

    hamburger.addEventListener('click', () => mobileMenu.classList.contains('open') ? close() : open());
    if (closeBtn) closeBtn.addEventListener('click', close);
    backdrop.addEventListener('click', close);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
})();

/* ── User dropdown — pure JS ── */
(function () {
    const btn      = document.getElementById('wlUserBtn');
    const dropdown = document.getElementById('wlUserDropdown');
    const chevron  = document.getElementById('wlChevron');
    if (!btn || !dropdown) return;

    // Use fixed positioning so it never overflows on mobile
    dropdown.style.position = 'fixed';
    dropdown.style.zIndex   = '9999';

    function positionDropdown() {
        const rect  = btn.getBoundingClientRect();
        const w     = Math.min(240, window.innerWidth - 20);
        let   left  = rect.right - w;
        let   top   = rect.bottom + 8;
        // Keep within viewport
        if (left < 10) left = 10;
        if (left + w > window.innerWidth - 10) left = window.innerWidth - w - 10;
        dropdown.style.width = w + 'px';
        dropdown.style.left  = left + 'px';
        dropdown.style.top   = top  + 'px';
    }

    const open = () => {
        positionDropdown();
        dropdown.classList.add('open');
        if (chevron) chevron.style.transform = 'rotate(180deg)';
    };
    const close = () => {
        dropdown.classList.remove('open');
        if (chevron) chevron.style.transform = 'rotate(0deg)';
    };

    btn.addEventListener('click', e => {
        e.stopPropagation();
        dropdown.classList.contains('open') ? close() : open();
    });
    dropdown.addEventListener('click', e => e.stopPropagation());
    document.addEventListener('click', close);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
    window.addEventListener('scroll', close, true);
    window.addEventListener('resize', () => { if (dropdown.classList.contains('open')) positionDropdown(); });
})();


/* ── Back to Top with progress ring ── */
(function () {
    const btn    = document.getElementById('back-to-top');
    const circle = document.getElementById('btt-ring');
    if (!btn) return;
    const circumference = 2 * Math.PI * 26; // r=26
    if (circle) { circle.style.strokeDasharray = circumference; circle.style.strokeDashoffset = circumference; }

    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        const total    = document.documentElement.scrollHeight - window.innerHeight;
        btn.classList.toggle('visible', scrolled > 300);
        if (circle && total > 0) {
            circle.style.strokeDashoffset = circumference - (scrolled / total) * circumference;
        }
    }, { passive: true });

    btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
})();

/* ── Toast Notification System ── */
window.WLToast = (function () {
    const stack = document.getElementById('toastStack');
    const icons = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };

    function show(title, msg, type = 'success', duration = 4000) {
        if (!stack) return;
        const t = document.createElement('div');
        t.className = `wl-toast ${type}`;
        t.innerHTML = `
            <i class="fas ${icons[type] || icons.info} wl-toast-icon"></i>
            <div class="wl-toast-body">
                <div class="wl-toast-title">${title}</div>
                <div class="wl-toast-msg">${msg}</div>
            </div>
            <button class="wl-toast-close" aria-label="Close"><i class="fas fa-times"></i></button>`;
        stack.appendChild(t);
        requestAnimationFrame(() => { requestAnimationFrame(() => t.classList.add('show')); });
        const close = () => {
            t.classList.remove('show');
            setTimeout(() => t.remove(), 400);
        };
        t.querySelector('.wl-toast-close').addEventListener('click', close);
        setTimeout(close, duration);
    }
    return { show };
})();

/* ── Cookie Banner ── */
(function () {
    const banner  = document.getElementById('cookie-banner');
    const accept  = document.getElementById('cookieAccept');
    const decline = document.getElementById('cookieDecline');
    if (!banner) return;

    const forceShow = banner.dataset.force === '1';

    // Show if forced (just logged in) OR never seen before
    if (forceShow || !localStorage.getItem('wl_cookie')) {
        setTimeout(() => banner.classList.add('show'), 800);
        // Clear the server-side session flag silently
        if (forceShow) {
            fetch('/clear-cookie-flag/', { method: 'POST',
                headers: { 'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '' }
            }).catch(() => {});
        }
    }

    const dismiss = (accepted) => {
        banner.classList.remove('show');
        localStorage.setItem('wl_cookie', accepted ? 'accepted' : 'declined');
        if (accepted) WLToast.show('Cookies Accepted', 'Thanks! Your preferences have been saved.', 'success');
    };
    if (accept)  accept.addEventListener('click',  () => dismiss(true));
    if (decline) decline.addEventListener('click', () => dismiss(false));
})();

/* ── Scroll Animations (staggered) ── */
(function () {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const siblings = entry.target.parentElement
                ? [...entry.target.parentElement.children].filter(el => el.classList.contains('scroll-animate'))
                : [];
            const idx = siblings.indexOf(entry.target);
            entry.target.style.transitionDelay = `${idx * 90}ms`;
            entry.target.classList.add('show');
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -50px 0px' });
    document.querySelectorAll('.scroll-animate').forEach(el => observer.observe(el));
})();

/* ── Animated Counters ── */
(function () {
    const counters = document.querySelectorAll('[data-target]');
    if (!counters.length) return;
    const obs = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const el     = entry.target;
            const target = parseInt(el.dataset.target);
            const suffix = el.dataset.suffix || '';
            let current  = 0;
            const step   = target / (1800 / 16);
            const tick   = () => {
                current = Math.min(current + step, target);
                el.textContent = Math.floor(current) + suffix;
                if (current < target) requestAnimationFrame(tick);
            };
            requestAnimationFrame(tick);
            obs.unobserve(el);
        });
    }, { threshold: 0.5 });
    counters.forEach(c => obs.observe(c));
})();

/* ── Skill Bars ── */
(function () {
    const bars = document.querySelectorAll('.skill-bar-fill[data-width]');
    if (!bars.length) return;
    const obs = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            entry.target.style.width = entry.target.dataset.width;
            obs.unobserve(entry.target);
        });
    }, { threshold: 0.3 });
    bars.forEach(b => obs.observe(b));
})();

/* ── Portfolio Filtering ── */
(function () {
    const btns  = document.querySelectorAll('.filter-btn');
    const items = document.querySelectorAll('.portfolio-item[data-category]');
    if (!btns.length || !items.length) return;
    btns.forEach(btn => {
        btn.addEventListener('click', function () {
            btns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const filter = this.dataset.filter;
            items.forEach(item => {
                const show = filter === 'all' || item.dataset.category === filter;
                item.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
                if (show) {
                    item.style.display = '';
                    requestAnimationFrame(() => { item.style.opacity = '1'; item.style.transform = 'scale(1)'; });
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'scale(0.9)';
                    setTimeout(() => { item.style.display = 'none'; }, 350);
                }
            });
        });
    });
})();

/* ── Typing Animation ── */
window.initTyping = function (el, words, speed = 90, pause = 2000) {
    if (!el) return;
    let wi = 0, ci = 0, deleting = false;
    const cursor = document.createElement('span');
    cursor.className = 'typed-cursor';
    el.parentNode.insertBefore(cursor, el.nextSibling);
    const tick = () => {
        const word = words[wi];
        if (!deleting) {
            el.textContent = word.slice(0, ++ci);
            if (ci === word.length) { deleting = true; setTimeout(tick, pause); return; }
        } else {
            el.textContent = word.slice(0, --ci);
            if (ci === 0) { deleting = false; wi = (wi + 1) % words.length; }
        }
        setTimeout(tick, deleting ? speed / 2 : speed);
    };
    tick();
};

/* ── Magnetic Buttons ── */
(function () {
    document.querySelectorAll('.btn-green, .btn-outline-green').forEach(btn => {
        btn.addEventListener('mousemove', e => {
            const rect = btn.getBoundingClientRect();
            const x = (e.clientX - rect.left - rect.width  / 2) * 0.25;
            const y = (e.clientY - rect.top  - rect.height / 2) * 0.25;
            btn.style.transform = `translate(${x}px, ${y}px) translateY(-3px)`;
        });
        btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
    });
})();

/* ── Live Chat Widget ── */
(function () {
    const widget   = document.getElementById('chat-widget');
    const closeBtn = document.getElementById('chatClose');
    const sendBtn  = document.getElementById('chatSend');
    const input    = document.getElementById('chatInput');
    const messages = document.getElementById('chatMessages');
    if (!widget) return;

    // Open via WhatsApp button long-press or dedicated trigger
    window.openChat = () => widget.classList.toggle('open');
    if (closeBtn) closeBtn.addEventListener('click', () => widget.classList.remove('open'));

    const addBubble = (text, isUser = false) => {
        const b = document.createElement('div');
        b.className = 'chat-bubble';
        b.style.cssText = isUser
            ? 'align-self:flex-end;background:rgba(99,102,241,0.1);border-color:rgba(99,102,241,0.2);border-radius:14px 14px 4px 14px;'
            : '';
        b.textContent = text;
        messages.appendChild(b);
        messages.scrollTop = messages.scrollHeight;
    };

    const autoReplies = [
        "Thanks for reaching out! Our team will get back to you shortly.",
        "Great question! Please share your project details and we'll prepare a quote.",
        "We'd love to help! You can also call us at +91 7892934437.",
        "Feel free to fill out our Request Website form for a detailed quote!"
    ];
    let replyIdx = 0;

    const sendMessage = () => {
        const text = input.value.trim();
        if (!text) return;
        addBubble(text, true);
        input.value = '';
        setTimeout(() => addBubble(autoReplies[replyIdx % autoReplies.length]), 900);
        replyIdx++;
    };

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (input)   input.addEventListener('keydown', e => { if (e.key === 'Enter') sendMessage(); });
})();

/* ── Form loading state ── */
(function () {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function () {
            const btn = form.querySelector('button[type="submit"]');
            if (btn && form.checkValidity()) {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            }
        });
    });
})();

/* ── Smooth anchor scroll ── */
(function () {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
        });
    });
})();

/* ── Search Overlay ── */
/* ── Smart Assistant ── */
(function () {
    const overlay   = document.getElementById('search-overlay');
    if (!overlay) return;

    // ── Knowledge base ──
    const kb = [
        // Services
        { keys: ['service','offer','provide','do you','what do','build','create','make','develop'],
          answer: `We offer 6 core services:<br><br>
          🔹 <strong>Custom Website Development</strong> — from ₹15,000<br>
          🔹 <strong>E-Commerce Development</strong> — from ₹25,000<br>
          🔹 <strong>SEO Optimization</strong> — from ₹8,000/mo<br>
          🔹 <strong>Web Design</strong> — from ₹10,000<br>
          🔹 <strong>Website Redesign</strong> — from ₹12,000<br>
          🔹 <strong>Website Maintenance</strong> — from ₹3,000/mo<br><br>
          <a href="/services/">View all services →</a>` },

        // Pricing
        { keys: ['price','cost','charge','fee','rate','budget','how much','₹','rupee','package','plan'],
          answer: `Our pricing packages:<br><br>
          💼 <strong>Starter</strong> — Basic business website<br>
          🏢 <strong>Business</strong> — Full-featured with SEO & CMS<br>
          🛒 <strong>E-Commerce</strong> — Online store with payments<br>
          ⭐ <strong>Premium</strong> — Advanced web application<br><br>
          Custom website starts at <strong>₹15,000</strong>. E-commerce from <strong>₹25,000</strong>.<br>
          <a href="/pricing/">See full pricing →</a>` },

        // Timeline
        { keys: ['time','long','days','week','month','deadline','deliver','fast','quick','duration','how soon'],
          answer: `Our typical delivery timelines:<br><br>
          ⚡ <strong>Landing Page</strong> — 7–10 days<br>
          🏢 <strong>Business Website</strong> — 15–20 days<br>
          🛒 <strong>E-Commerce Store</strong> — 25–35 days<br>
          🔧 <strong>Website Redesign</strong> — 10–15 days<br><br>
          We always provide a clear timeline before starting your project.` },

        // Contact
        { keys: ['contact','reach','call','phone','email','whatsapp','location','address','where','talk'],
          answer: `You can reach us through:<br><br>
          📞 <strong>Phone:</strong> +91 7892934437 | +91 8867156958<br>
          📧 <strong>Email:</strong> infoweblance01@gmail.com<br>
          💬 <strong>WhatsApp:</strong> <a href="https://wa.me/917892934437" target="_blank">Chat with us</a><br>
          📍 <strong>Location:</strong> Devanahalli, Karnataka, India<br><br>
          <a href="/contact/">Go to contact page →</a>` },

        // SEO
        { keys: ['seo','rank','google','search engine','organic','keyword','traffic','optimize'],
          answer: `Yes! We offer professional SEO services:<br><br>
          ✅ Keyword research & analysis<br>
          ✅ On-page SEO optimization<br>
          ✅ Technical SEO audit<br>
          ✅ Content strategy & link building<br>
          ✅ Monthly performance reports<br><br>
          Starting from <strong>₹8,000/month</strong>.<br>
          <a href="/services/#seo-optimization">Learn more →</a>` },

        // Tech stack
        { keys: ['tech','technology','stack','language','framework','django','react','python','html','css','javascript','wordpress'],
          answer: `We use modern, battle-tested technologies:<br><br>
          🐍 <strong>Backend:</strong> Python, Django, Node.js<br>
          🎨 <strong>Frontend:</strong> HTML5, CSS3, JavaScript, React, Bootstrap<br>
          🗄️ <strong>Database:</strong> PostgreSQL, MySQL<br>
          ☁️ <strong>Hosting:</strong> AWS, Render, Nginx<br>
          🎯 <strong>Design:</strong> Figma, Adobe XD<br>
          💳 <strong>Payments:</strong> Razorpay, Stripe, PayPal` },

        // Get started / quote
        { keys: ['start','begin','get started','quote','request','hire','book','order','project'],
          answer: `Getting started is easy! 🚀<br><br>
          1️⃣ <strong>Submit a quote request</strong> with your requirements<br>
          2️⃣ We review and contact you within <strong>24 hours</strong><br>
          3️⃣ We send a detailed proposal with timeline & pricing<br>
          4️⃣ 50% advance → development begins → 50% on delivery<br><br>
          <a href="/request-website/">Get a free quote →</a>` },

        // Team
        { keys: ['team','who','founder','developer','designer','member','staff','people','balakrishna','varun','sumith','bindu'],
          answer: `Meet the Weblance team:<br><br>
          👨‍💻 <strong>Balakrishna</strong> — Founder & Lead Developer (Python, Django, React)<br>
          🎨 <strong>Varun</strong> — UI/UX Designer (Figma, Adobe XD)<br>
          💻 <strong>Sumith</strong> — Frontend Developer (JS, Bootstrap, GSAP)<br>
          📈 <strong>Bindu</strong> — SEO & Marketing (Analytics, Content)<br><br>
          <a href="/about/#team">Meet the team →</a>` },

        // Maintenance
        { keys: ['maintain','maintenance','support','update','fix','bug','security','backup','care'],
          answer: `Our maintenance plans cover everything:<br><br>
          🔒 Regular security updates<br>
          🐛 Bug fixes & troubleshooting<br>
          📝 Content updates (up to 5/month)<br>
          📊 Performance monitoring<br>
          💾 Weekly backups<br>
          🕐 24/7 technical support<br><br>
          Starting from <strong>₹3,000/month</strong>. Cancel anytime.<br>
          <a href="/services/#maintenance">Learn more →</a>` },

        // Payment
        { keys: ['payment','pay','upi','razorpay','stripe','paypal','advance','deposit','bank'],
          answer: `We accept multiple payment methods:<br><br>
          📱 UPI (Google Pay, PhonePe, Paytm)<br>
          🏦 Bank Transfer (NEFT/IMPS)<br>
          💳 Razorpay & Stripe<br>
          🌐 PayPal (international clients)<br><br>
          Our model: <strong>50% advance</strong> to start + <strong>50% on delivery</strong>. Fair for both sides!` },

        // Portfolio
        { keys: ['portfolio','work','project','example','sample','previous','case study','showcase'],
          answer: `We've delivered 150+ projects across India! Our portfolio includes:<br><br>
          🛒 E-commerce stores<br>
          🏢 Business websites<br>
          🚀 Landing pages<br>
          📱 Web applications<br><br>
          <a href="/portfolio/">View our portfolio →</a>` },

        // About
        { keys: ['about','company','weblance','who are','story','mission','vision','based','location','india'],
          answer: `<strong>WEBLANCE</strong> is a professional web development agency based in <strong>Devanahalli, Karnataka, India</strong>.<br><br>
          We specialize in building fast, SEO-ready, and beautiful websites for businesses of all sizes. With 4+ years of experience and 150+ projects delivered, we serve clients across India and internationally.<br><br>
          <a href="/about/">Learn more about us →</a>` },

        // Ecommerce
        { keys: ['ecommerce','e-commerce','online store','shop','sell','product','cart','checkout','payment gateway'],
          answer: `Our E-Commerce development includes:<br><br>
          🛒 Full-featured online store<br>
          💳 Razorpay, Stripe & PayPal integration<br>
          📦 Inventory management<br>
          🚚 Order tracking system<br>
          👤 Customer accounts & wishlist<br>
          📱 Mobile-optimized shopping<br><br>
          Starting from <strong>₹25,000</strong>. Delivery in 25–35 days.<br>
          <a href="/services/#ecommerce">Get a quote →</a>` },
    ];

    const greetings = ['hi','hello','hey','hii','helo','namaste','good morning','good evening','good afternoon'];
    const thanks = ['thank','thanks','ok','okay','got it','great','perfect','awesome','nice','cool'];

    function getAnswer(q) {
        const ql = q.toLowerCase().trim();

        if (greetings.some(g => ql.startsWith(g) || ql === g)) {
            return `Hello! 👋 I'm the Weblance assistant. How can I help you today?<br><br>You can ask me about our <strong>services</strong>, <strong>pricing</strong>, <strong>timeline</strong>, <strong>team</strong>, or anything about building your website!`;
        }
        if (thanks.some(t => ql.includes(t))) {
            return `You're welcome! 😊 Is there anything else I can help you with? Feel free to ask about our services, pricing, or <a href="/contact/">contact us</a> directly.`;
        }

        for (const item of kb) {
            if (item.keys.some(k => ql.includes(k))) {
                return item.answer;
            }
        }

        // Fallback
        return `I'm not sure about that specific question, but I can help with:<br><br>
        💡 <strong>Services</strong> — what we build<br>
        💰 <strong>Pricing</strong> — our packages & costs<br>
        ⏱️ <strong>Timeline</strong> — how long projects take<br>
        📞 <strong>Contact</strong> — how to reach us<br><br>
        Or <a href="/contact/">contact our team directly</a> for a personalised answer!`;
    }

    function addMessage(text, isUser) {
        const messages = document.getElementById('wlAsstMessages');
        if (!messages) return;
        const div = document.createElement('div');
        div.className = `wl-asst-msg ${isUser ? 'wl-asst-user' : 'wl-asst-bot'}`;
        div.innerHTML = `<div class="wl-asst-bubble">${text}</div>`;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }

    function showTyping() {
        const messages = document.getElementById('wlAsstMessages');
        if (!messages) return;
        const div = document.createElement('div');
        div.className = 'wl-asst-msg wl-asst-bot wl-asst-typing';
        div.id = 'wlTyping';
        div.innerHTML = `<div class="wl-asst-bubble"><span></span><span></span><span></span></div>`;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    function removeTyping() {
        const t = document.getElementById('wlTyping');
        if (t) t.remove();
    }

    // ── Session ID: persist across page loads ──────────────────
    let wlBotSessionId = localStorage.getItem('wl_bot_session') || '';

    // ── Conversation history for Gemini context ─────────────────
    let wlBotHistory = [];

    // ── CSRF token from cookie ───────────────────────────────────
    function getCsrf() {
        const m = document.cookie.match(/csrftoken=([^;]+)/);
        return m ? m[1] : '';
    }

    async function handleQuery(q) {
        if (!q.trim()) return;
        addMessage(q, true);
        const inputEl   = document.getElementById('searchInput');
        const suggsWrap = document.getElementById('wlAsstSuggestions');
        if (inputEl) inputEl.value = '';
        if (suggsWrap) suggsWrap.style.display = 'none';
        showTyping();

        // Add to local history for Gemini context
        wlBotHistory.push({ role: 'user', text: q });

        try {
            const res = await fetch('/agent/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrf(),
                },
                body: JSON.stringify({
                    message:    q,
                    history:    wlBotHistory.slice(-6),
                    session_id: wlBotSessionId,
                }),
            });

            const data = await res.json();
            removeTyping();

            if (data.session_id) {
                wlBotSessionId = data.session_id;
                localStorage.setItem('wl_bot_session', wlBotSessionId);
            }

            const reply = data.response || data.error || 'Sorry, something went wrong.';
            wlBotHistory.push({ role: 'bot', text: reply });
            addMessage(reply, false);

        } catch (err) {
            removeTyping();
            // Fallback to local KB if network fails
            addMessage(getAnswer(q), false);
        }
    }

    // Open/close
    const open = () => {
        const panel = document.getElementById('wlChatPanel');
        if (panel) {
            panel.style.display = 'flex';
            const inp = document.getElementById('wlChatInput');
            setTimeout(() => { if (inp) inp.focus(); }, 100);
        }
    };
    const close = () => {
        const panel = document.getElementById('wlChatPanel');
        if (panel) panel.style.display = 'none';
    };

    const trigger = document.getElementById('searchTrigger');
    if (trigger) trigger.addEventListener('click', open);

    // Wire all interactive elements after DOM is fully ready
    function wireButtons() {
        const floatBtn  = document.getElementById('ai-chat-float');
        if (floatBtn) floatBtn.addEventListener('click', open);
        const closeBtn  = document.getElementById('wlChatClose');
        if (closeBtn) closeBtn.addEventListener('click', close);
        // Legacy close button
        const legacyClose = document.getElementById('wlAsstClose');
        if (legacyClose) legacyClose.addEventListener('click', close);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', wireButtons);
    } else {
        wireButtons();
    }

    overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
})();

/* ── Theme: Light mode only — toggle removed ── */
(function () {
    // Always light mode — remove any saved dark preference
    document.body.classList.remove('light-mode');
    localStorage.removeItem('wl_theme');
})();

/* ── Lazy Image Loading (blur-up) ── */
(function () {
    const imgs = document.querySelectorAll('img[data-src]');
    if (!imgs.length) return;
    const obs = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const img = entry.target;
            img.classList.add('lazy');
            const tmp = new Image();
            tmp.onload = () => {
                img.src = img.dataset.src;
                img.classList.add('loaded');
            };
            tmp.src = img.dataset.src;
            obs.unobserve(img);
        });
    }, { rootMargin: '200px' });
    imgs.forEach(img => obs.observe(img));
})();

/* ── Active nav link highlight on scroll (single-page sections) ── */
(function () {
    const sections = document.querySelectorAll('section[id]');
    if (!sections.length) return;
    const navLinks = document.querySelectorAll('.nav-link[href*="#"]');
    const obs = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            navLinks.forEach(link => {
                link.classList.toggle('active', link.getAttribute('href').includes(entry.target.id));
            });
        });
    }, { threshold: 0.4 });
    sections.forEach(s => obs.observe(s));
})();

/* ── Confetti on form success ── */
window.WLConfetti = function () {
    const colors = ['#6366F1','#4F46E5','#ffffff','#818CF8'];
    for (let i = 0; i < 80; i++) {
        const el = document.createElement('div');
        el.style.cssText = `
            position:fixed;
            top:-10px;
            left:${Math.random()*100}vw;
            width:${6+Math.random()*6}px;
            height:${6+Math.random()*6}px;
            background:${colors[Math.floor(Math.random()*colors.length)]};
            border-radius:${Math.random()>0.5?'50%':'2px'};
            z-index:99999;
            pointer-events:none;
            animation: confettiFall ${1.5+Math.random()*2}s ease-in forwards;
            animation-delay:${Math.random()*0.5}s;
        `;
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 4000);
    }
};

// Inject confetti keyframes once
if (!document.getElementById('confetti-style')) {
    const s = document.createElement('style');
    s.id = 'confetti-style';
    s.textContent = `@keyframes confettiFall {
        0%   { transform: translateY(0) rotate(0deg); opacity:1; }
        100% { transform: translateY(100vh) rotate(720deg); opacity:0; }
    }`;
    document.head.appendChild(s);
}

/* ── FAQ Accordion ── */
(function () {
    document.querySelectorAll('.faq-q').forEach(btn => {
        btn.addEventListener('click', function () {
            const item = this.closest('.faq-item');
            const isOpen = item.classList.contains('open');
            // Close all
            document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
            // Toggle clicked
            if (!isOpen) item.classList.add('open');
        });
    });
})();

/* ── Hero Canvas Particles ── */
(function () {
    const canvas = document.getElementById('hero-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W, H, particles = [];

    const resize = () => {
        W = canvas.width  = canvas.offsetWidth;
        H = canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    class Particle {
        constructor() { this.reset(); }
        reset() {
            this.x  = Math.random() * W;
            this.y  = Math.random() * H;
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = (Math.random() - 0.5) * 0.4;
            this.r  = Math.random() * 1.5 + 0.5;
            this.a  = Math.random() * 0.5 + 0.1;
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0 || this.x > W) this.vx *= -1;
            if (this.y < 0 || this.y > H) this.vy *= -1;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(99,102,241,${this.a})`;
            ctx.fill();
        }
    }

    for (let i = 0; i < 80; i++) particles.push(new Particle());

    const drawLines = () => {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(99,102,241,${0.08 * (1 - dist / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
    };

    const animate = () => {
        ctx.clearRect(0, 0, W, H);
        particles.forEach(p => { p.update(); p.draw(); });
        drawLines();
        requestAnimationFrame(animate);
    };
    animate();
})();

/* ── Service Card Popup ── */
(function () {
    const overlay   = document.getElementById('card-popup-overlay');
    const popup     = document.getElementById('cardPopup');
    const closeBtn  = document.getElementById('cardPopupClose');
    const iconEl    = document.getElementById('cardPopupIcon');
    const titleEl   = document.getElementById('cardPopupTitle');
    const descEl    = document.getElementById('cardPopupDesc');
    if (!overlay) return;

    document.querySelectorAll('.card-3d-more').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const card  = this.closest('.card-3d');
            const title = card.dataset.popupTitle;
            const desc  = card.dataset.popupDesc;
            const icon  = card.dataset.popupIcon;
            const color = card.dataset.popupColor || '#6366F1';
            if (iconEl) {
                iconEl.innerHTML = `<i class="fas ${icon}"></i>`;
                iconEl.style.cssText = `background:${color}22;color:${color};width:72px;height:72px;border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:1.8rem;margin:0 auto 20px;`;
            }
            if (titleEl) titleEl.textContent = title;
            if (descEl)  descEl.textContent  = desc;
            overlay.classList.add('open');
        });
    });

    const close = () => overlay.classList.remove('open');
    if (closeBtn) closeBtn.addEventListener('click', close);
    overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
})();

/* ── Newsletter ── */
window.handleNewsletter = function (e) {
    e.preventDefault();
    const form  = e.target;
    const input = form.querySelector('input[type="email"]');
    const btn   = form.querySelector('button[type="submit"]');
    if (!input || !input.value) return;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Subscribing...';
    setTimeout(() => {
        btn.disabled = false;
        btn.innerHTML = 'Subscribe <i class="fas fa-arrow-right ms-1"></i>';
        input.value = '';
        WLToast.show('Subscribed!', 'Thanks for joining. Watch your inbox for tips.', 'success');
        WLConfetti();
    }, 1200);
};

/* ── Tech stack hover ripple ── */
(function () {
    document.querySelectorAll('.tech-item').forEach(item => {
        item.addEventListener('mouseenter', function () {
            this.style.setProperty('--ripple-color', 'rgba(99,102,241,0.15)');
        });
    });
})();

/* ── Scroll-reveal with data-reveal types ── */
(function () {
    const map = {
        'fade-up':    'translateY(40px)',
        'fade-down':  'translateY(-40px)',
        'fade-left':  'translateX(-40px)',
        'fade-right': 'translateX(40px)',
        'zoom-in':    'scale(0.85)',
        'zoom-out':   'scale(1.1)',
    };
    const els = document.querySelectorAll('[data-reveal]');
    if (!els.length) return;

    els.forEach(el => {
        const type  = el.dataset.reveal;
        const delay = el.dataset.delay || 0;
        el.style.opacity   = '0';
        el.style.transform = map[type] || 'translateY(30px)';
        el.style.transition = `opacity 0.7s ease ${delay}ms, transform 0.7s ease ${delay}ms`;
    });

    const obs = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            entry.target.style.opacity   = '1';
            entry.target.style.transform = 'none';
            obs.unobserve(entry.target);
        });
    }, { threshold: 0.1 });

    els.forEach(el => obs.observe(el));
})();






/* ── Site Search Modal ── */
(function () {
    const modal     = document.getElementById('wlSiteSearch');
    const openBtn   = document.getElementById('wlSiteSearchBtn');
    const searchInp = document.getElementById('wlSiteSearchInput');
    const results   = document.getElementById('wlSiteSearchResults');
    const defaultEl = document.getElementById('wlSiteSearchDefault');
    if (!modal) return;

    const pages = [
        { title: 'Home',            url: '/',                  icon: 'fa-home',          desc: 'Welcome to Weblance' },
        { title: 'About Us',        url: '/about/',            icon: 'fa-users',         desc: 'Our team & story' },
        { title: 'Services',        url: '/services/',         icon: 'fa-cogs',          desc: 'What we build' },
        { title: 'Portfolio',       url: '/portfolio/',        icon: 'fa-briefcase',     desc: 'Our work' },
        { title: 'Pricing',         url: '/pricing/',          icon: 'fa-tag',           desc: 'Plans & packages' },
        { title: 'Contact',         url: '/contact/',          icon: 'fa-envelope',      desc: 'Get in touch' },
        { title: 'Request Website', url: '/request-website/', icon: 'fa-paper-plane',   desc: 'Get a free quote' },
        { title: 'Book a Call',     url: '/features/booking/',icon: 'fa-calendar-check', desc: 'Schedule a meeting' },
        { title: 'SEO Services',    url: '/services/#seo-optimization', icon: 'fa-search', desc: 'Rank higher on Google' },
        { title: 'E-Commerce',      url: '/services/#ecommerce', icon: 'fa-shopping-cart', desc: 'Online store development' },
    ];

    // Populate quick links grid on first open
    function populateDefault() {
        const grid = modal.querySelector('.wl-sr-grid');
        if (!grid || grid.children.length) return;
        pages.slice(0, 6).forEach(p => {
            const a = document.createElement('a');
            a.href = p.url;
            a.className = 'wl-sr-item';
            a.innerHTML = `<i class="fas ${p.icon}"></i><div><span>${p.title}</span><span class="wl-sr-desc">${p.desc}</span></div>`;
            grid.appendChild(a);
        });
    }

    function openModal() {
        populateDefault();
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        setTimeout(() => { if (searchInp) searchInp.focus(); }, 80);
    }

    function closeModal() {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        if (searchInp) searchInp.value = '';
        if (results && defaultEl) {
            results.innerHTML = '';
            results.appendChild(defaultEl);
        }
    }

    function doSearch(q) {
        if (!q.trim()) {
            if (results && defaultEl) {
                results.innerHTML = '';
                results.appendChild(defaultEl);
            }
            return;
        }
        const ql = q.toLowerCase();
        const hits = pages.filter(p =>
            p.title.toLowerCase().includes(ql) ||
            p.desc.toLowerCase().includes(ql)
        );
        if (!results) return;
        results.innerHTML = '';
        if (!hits.length) {
            results.innerHTML = `<div class="wl-sr-no-results"><i class="fas fa-search"></i>No results for "<strong>${q}</strong>"</div>`;
            return;
        }
        hits.forEach(p => {
            const a = document.createElement('a');
            a.href = p.url;
            a.className = 'wl-sr-item';
            a.innerHTML = `<i class="fas ${p.icon}"></i><div><span>${p.title}</span><span class="wl-sr-desc">${p.desc}</span></div>`;
            results.appendChild(a);
        });
    }

    if (openBtn)   openBtn.addEventListener('click', openModal);
    if (searchInp) searchInp.addEventListener('input', e => doSearch(e.target.value));
    modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeModal();
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); openModal(); }
    });
})();
