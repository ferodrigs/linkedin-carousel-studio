"""adapters.py — Slide discovery and forced activation for Africa Content-Lab V18 & generic HTML decks."""

# Kill transitions/animations, reveal .step elements, and hide presenter/floating UI during measurement
ZERO_ANIMATIONS_CSS = r"""
    if (!document.getElementById('pptx-zero-anim')) {
        const styleEl = document.createElement('style');
        styleEl.id = 'pptx-zero-anim';
        styleEl.textContent = `
            *, *::before, *::after {
                animation-duration: 0.0001s !important;
                animation-delay: 0s !important;
                transition-duration: 0s !important;
                transition-delay: 0s !important;
            }
            [data-anim], [data-animate], [data-aos], [data-scroll],
            [data-motion], [data-reveal], [data-fade], [data-stagger],
            .reveal, .fade-in, .animate-in, .aos-init, .motion-element,
            .step {
                opacity: 1 !important;
                transform: none !important;
                visibility: visible !important;
                filter: none !important;
            }
            #presenterDrawer, #deckToolbar, #presenterModal,
            .presenter-toggle-btn, .studio-floating-ui,
            #stage-brand-signature {
                display: none !important;
                opacity: 0 !important;
                visibility: hidden !important;
            }
            [data-pptx-target] .slide-brand-print {
                display: flex !important;
                position: absolute !important;
                right: 72px !important;
                bottom: 28px !important;
                align-items: center !important;
                gap: 10px !important;
                z-index: 40 !important;
                pointer-events: none !important;
            }
        `;
        document.head.appendChild(styleEl);
    }
"""

DISCOVER_JS = r"""
() => {
    const explicit = document.querySelectorAll('[data-pptx-slide]');
    let group = explicit.length >= 1 ? Array.from(explicit) : null;

    if (!group) {
        const africaSlides = document.querySelectorAll('#stage > section.slide, .deck > section.slide, section.slide');
        if (africaSlides.length >= 1) {
            group = Array.from(africaSlides);
        }
    }

    if (!group) {
        const vw = window.innerWidth, vh = window.innerHeight;
        const minW = vw * 0.5, minH = vh * 0.5;
        const candidates = [];
        for (const el of document.body.querySelectorAll('*')) {
            const r = el.getBoundingClientRect();
            if (r.width >= minW && r.height >= minH) candidates.push(el);
        }
        let bestGroup = [], bestScore = 1;
        for (const cand of candidates) {
            const parent = cand.parentElement;
            if (!parent || parent === document.documentElement) continue;
            const sameTag = Array.from(parent.children).filter(ch => {
                if (ch.tagName !== cand.tagName) return false;
                const r = ch.getBoundingClientRect();
                return (r.width >= minW && r.height >= minH)
                    || r.width === 0 || r.height === 0;
            });
            if (sameTag.length > bestScore) {
                bestScore = sameTag.length;
                bestGroup = sameTag;
            }
        }
        if (bestGroup.length === 0 && candidates.length >= 1) {
            candidates.sort((a, b) => {
                let da = 0, db = 0;
                for (let c = a; c; c = c.parentElement) da++;
                for (let c = b; c; c = c.parentElement) db++;
                return db - da;
            });
            bestGroup = [candidates.find(c => (c.innerText || '').trim()) || candidates[0]];
        }
        group = bestGroup;
    }

    let naturalDisplay = 'flex';
    for (const s of group) {
        const d = getComputedStyle(s).display;
        if (d && d !== 'none') { naturalDisplay = d; break; }
    }

    window.__pptxSlides = group;
    window.__pptxNaturalDisplay = naturalDisplay;
    return group;
}
"""

FORCE_POSITION_CSS = r"""
    if (!document.getElementById('pptx-force-position')) {
        const s = document.createElement('style');
        s.id = 'pptx-force-position';
        s.textContent = `
            #stage, .deck {
                width: 1920px !important;
                height: 1080px !important;
                transform: none !important;
                top: 0 !important;
                left: 0 !important;
                margin: 0 !important;
            }
            [data-pptx-target] {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                margin: 0 !important;
                transform: none !important;
                opacity: 1 !important;
                visibility: visible !important;
                z-index: 2147483647 !important;
            }
        `;
        document.head.appendChild(s);
    }
"""

ACTIVATE_JS = r"""
(idx) => {
    const slides = window.__pptxSlides || [];
    if (!slides[idx]) return { error: 'index out of range' };
    const target = slides[idx];
    const naturalDisplay = window.__pptxNaturalDisplay || 'flex';

    if (window.AfricaDeck && typeof window.AfricaDeck.goTo === 'function') {
        try {
            window.AfricaDeck.goTo(idx, { resetSteps: 'all-visible' });
        } catch (e) {}
    }

    for (const s of slides) {
        s.removeAttribute('data-pptx-target');
        s.classList.remove('is-active', 'active');
        s.style.removeProperty('display');
    }
    if (window.__pptxClearedAncestors) {
        for (const [el, prev] of window.__pptxClearedAncestors) {
            if (prev === '') el.style.removeProperty('transform');
            else el.style.setProperty('transform', prev);
        }
    }
    window.__pptxClearedAncestors = [];

    target.setAttribute('data-pptx-target', '');
    target.classList.add('is-active', 'active');
    target.style.setProperty('display', naturalDisplay, 'important');
    target.querySelectorAll('.step').forEach(st => st.classList.add('visible'));

    let cur = target.parentElement;
    while (cur && cur !== document.body) {
        const cs = getComputedStyle(cur);
        if (cs.transform && cs.transform !== 'none') {
            window.__pptxClearedAncestors.push([cur, cur.style.transform || '']);
            cur.style.setProperty('transform', 'none', 'important');
        }
        cur = cur.parentElement;
    }

    target.getBoundingClientRect();
    return { ok: true };
}
"""

PREPARE_JS = """
    () => {
        """ + ZERO_ANIMATIONS_CSS + """
        """ + FORCE_POSITION_CSS + """
        (""" + DISCOVER_JS + """)();
    }
"""

ENUMERATE_JS = "() => (window.__pptxSlides || []).length"
