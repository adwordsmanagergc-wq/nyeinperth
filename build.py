#!/usr/bin/env python3
"""Static site generator for NYE in Perth.

Edit data/events.json (and the CONFIG block below), then run:
    python3 build.py
The complete site is written to ./docs, which Vercel serves as-is (see vercel.json).
"""
import json
import shutil
from datetime import date
from html import escape
from pathlib import Path

# --------------------------------------------------------------------------------------
# CONFIG: change these before going live
# --------------------------------------------------------------------------------------
CONFIG = {
    "site_name": "NYE in Perth",
    "site_url": "https://nyeinperth.com",   # your live domain, no trailing slash
    "contact_email": "aj@metatapdigital.com",
    "listing_price": 599,                              # AUD, inc GST
    # Listing submissions are emailed to contact_email via FormSubmit (no account needed;
    # the first submission sends a one-time activation email to that inbox).
    "form_endpoint": "https://formsubmit.co/ajax/aj@metatapdigital.com",
    # Stripe Payment Link (or similar) for the $599 listing fee. While it still contains
    # "YOUR_", submitters see a thank-you message and you email them an invoice instead.
    "payment_link": "https://buy.stripe.com/YOUR_PAYMENT_LINK",
    "year": 2026,
    "next_year": 2027,
}

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
EVENTS = json.loads((ROOT / "data" / "events.json").read_text())
TODAY = date.today().isoformat()
Y, NY = CONFIG["year"], CONFIG["next_year"]
URL = CONFIG["site_url"]

CATEGORY_LABELS = {
    "party": "Parties",
    "dining": "Dinners",
    "fine-dining": "Fine dining",
    "cruise": "Cruises",
    "rooftop": "Rooftops",
    "river": "Riverfront",
    "family": "Family-friendly",
    "budget": "Under $250",
    "vantage": "Fireworks events",
    "free": "Free",
    "beach": "Beach",
}
AREAS = sorted({e["area"] for e in EVENTS})

NAV = [
    ("/", "Home"),
    ("/#directory", "All events"),
    ("/new-years-eve-dinner-perth/", "Dinners"),
    ("/new-years-eve-cruises-perth/", "Cruises"),
    ("/new-years-eve-parties-perth/", "Parties"),
    ("/perth-fireworks-vantage-points/", "Vantage points"),
    ("/plan-your-night/", "Plan"),
]


def j(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1).replace("</", "<\\/")


def money(n):
    if n == 0:
        return "Free"
    return f"${n:,.0f}" if float(n).is_integer() else f"${n:,.2f}"


SKYLINE = """<svg class="skyline" viewBox="0 0 1440 230" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c0a26"/><stop offset="1" stop-color="#07061a"/></linearGradient>
<linearGradient id="wt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a1450" stop-opacity=".9"/><stop offset="1" stop-color="#07061a"/></linearGradient></defs>
<g fill="url(#sk)">
<rect x="0" y="120" width="40" height="80"/><rect x="44" y="96" width="34" height="104"/><rect x="82" y="130" width="28" height="70"/>
<rect x="114" y="70" width="40" height="130"/><rect x="158" y="108" width="30" height="92"/><rect x="192" y="86" width="26" height="114"/>
<rect x="222" y="124" width="36" height="76"/>
<path d="M300 200 L310 110 L318 52 L326 110 L336 200Z"/><path d="M286 200 Q296 150 312 112 L312 200Z M350 200 Q340 150 324 112 L324 200Z"/>
<rect x="372" y="132" width="34" height="68"/><rect x="410" y="78" width="46" height="122"/><rect x="460" y="104" width="30" height="96"/>
<rect x="494" y="38" width="44" height="162"/><rect x="514" y="10" width="4" height="30"/>
<rect x="542" y="88" width="36" height="112"/><rect x="582" y="56" width="38" height="144"/><rect x="624" y="96" width="40" height="104"/>
<rect x="668" y="64" width="30" height="136"/><rect x="702" y="112" width="44" height="88"/><rect x="750" y="84" width="34" height="116"/>
<rect x="788" y="128" width="40" height="72"/>
<rect x="1220" y="118" width="34" height="82"/><rect x="1258" y="92" width="28" height="108"/>
<rect x="1290" y="110" width="38" height="90"/><rect x="1332" y="84" width="30" height="116"/><rect x="1366" y="126" width="40" height="74"/><rect x="1410" y="100" width="30" height="100"/>
</g>
<g fill="none" stroke="#0c0a26" stroke-width="6"><path d="M880 196 Q960 118 1040 182 Q1120 118 1200 196"/></g>
<g stroke="#0c0a26" stroke-width="2">""" + "".join(
    f'<line x1="{x}" y1="196" x2="{x}" y2="{(196 - (1 - (((x - 880) % 160 - 80) / 80) ** 2) * 56):.0f}"/>'
    for x in range(896, 1200, 16)
) + """</g>
<rect x="0" y="198" width="1440" height="32" fill="url(#wt)"/>
</svg>"""


def countdown(mini=False):
    units = [("d", "Days"), ("h", "Hours"), ("m", "Minutes"), ("s", "Seconds")]
    inner = "".join(
        f'<div class="cd-unit"><div class="cd-num" data-u="{k}">--</div><div class="cd-label">{v}</div></div>'
        for k, v in units
    )
    return f'<div class="countdown{" mini" if mini else ""}" data-countdown role="timer" aria-label="Countdown to midnight, New Year\'s Eve {Y} in Perth">{inner}</div>'


def layout(path, title, description, body, schema=None, og_type="website", active=None):
    canonical = URL + path
    schemas = [
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": CONFIG["site_name"],
            "url": URL + "/",
            "potentialAction": {
                "@type": "SearchAction",
                "target": URL + "/?q={search_term_string}#directory",
                "query-input": "required name=search_term_string",
            },
        }
    ] if path == "/" else []
    schemas += schema or []
    cur = ' aria-current="page"'
    nav = "".join(
        f'<li><a href="{h}"{cur if h == (active or path) else ""}>{t}</a></li>' for h, t in NAV
    )
    ld = "".join(f'<script type="application/ld+json">{j(s)}</script>' for s in schemas)
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="geo.region" content="AU-WA"><meta name="geo.placename" content="Perth">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{CONFIG['site_name']}">
<meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{URL}/og.png"><meta property="og:locale" content="en_AU">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{URL}/og.png">
<meta name="theme-color" content="#07061a">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav"><div class="wrap">
<a class="logo" href="/">NYE <span>in Perth</span></a>
<nav aria-label="Main"><ul>{nav}</ul></nav>
<a class="btn btn-primary btn-sm" href="/list-your-event/">List your event</a>
<button class="menu-btn" aria-label="Menu" aria-expanded="false">☰</button>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
<div class="fgrid">
<div><a class="logo" href="/">NYE <span>in Perth</span></a>
<p class="muted">The independent guide to New Year's Eve {Y} in Perth: fireworks vantage points, Swan River cruises, dinners and parties, all in one place.</p>
{countdown(mini=True)}</div>
<div><h4>Explore</h4><ul>
<li><a href="/#directory">All NYE events</a></li><li><a href="/new-years-eve-dinner-perth/">NYE dinners</a></li>
<li><a href="/new-years-eve-cruises-perth/">NYE cruises</a></li><li><a href="/new-years-eve-parties-perth/">NYE parties</a></li>
<li><a href="/family-new-years-eve-perth/">Family NYE</a></li></ul></div>
<div><h4>Plan</h4><ul>
<li><a href="/perth-fireworks-vantage-points/">Vantage points</a></li><li><a href="/plan-your-night/">Fireworks times</a></li>
<li><a href="/plan-your-night/#transport">Transport</a></li><li><a href="/#faq">FAQ</a></li></ul></div>
<div><h4>Venues</h4><ul>
<li><a href="/list-your-event/">List your event: ${CONFIG['listing_price']}</a></li>
<li><a href="mailto:{CONFIG['contact_email']}">{CONFIG['contact_email']}</a></li></ul></div>
</div>
<p class="fine">NYE in Perth is an independent guide and is not affiliated with the City of Perth, Visit Perth or any official New Year's Eve event. Prices and details are supplied by venues or based on published information and may change. Prices marked "2025" are last year's published prices and are still to be confirmed for {Y}. Always confirm with the venue before booking. We acknowledge the Whadjuk Noongar people, the Traditional Custodians of Boorloo (Perth) and the Derbarl Yerrigan (Swan River). © {Y} {CONFIG['site_name']}.</p>
</div></footer>
<script src="/main.js" defer></script>
</body>
</html>"""


# --------------------------------------------------------------------------------------
# Components
# --------------------------------------------------------------------------------------
def card(e, i):
    cats = " ".join(e["categories"])
    search = " ".join([e["name"], e["venue"], e["suburb"], e["area"], " ".join(e["categories"]), e["blurb"]]).lower()
    tags = "".join(f'<span class="tag">{CATEGORY_LABELS.get(c, c)}</span>' for c in e["categories"][:3])
    price = e["price_from"]
    price_html = (
        "Free<small>see entry details</small>" if price == 0
        else f"{money(price)}<small>from, per person</small>" if price
        else "TBA<small>see venue</small>"
    )
    return f"""<article class="card{' featured' if e.get('featured') else ''}" data-cats="{cats}" data-area="{escape(e['area'])}" data-price="{price if price is not None else ''}" data-featured="{1 if e.get('featured') else 0}" data-order="{i}" data-search="{escape(search)}">
{'<span class="badge">Featured</span>' if e.get('featured') else ''}
<div class="loc">📍 {escape(e['suburb'] if e['suburb'] in e['area'] else e['suburb'] + ' · ' + e['area'])}</div>
<h3><a href="/events/{e['slug']}/">{escape(e['name'])}</a></h3>
<p>{escape(e['blurb'])}</p>
<div class="tags"><span class="tag fw">🎆 {escape(e['fireworks'])}</span>{tags}</div>
<div class="meta"><div class="price">{price_html}</div>
<div class="actions"><a class="btn btn-ghost btn-sm" href="/events/{e['slug']}/">Details</a><a class="btn btn-primary btn-sm" href="{e['url']}" target="_blank" rel="noopener sponsored">Book</a></div></div>
</article>"""


def directory(events, heading, sub, show_filters=True, anchor="directory"):
    used = []
    for e in events:
        for c in e["categories"]:
            if c not in used:
                used.append(c)
    order = [c for c in CATEGORY_LABELS if c in used]
    chips = '<button class="chip" data-cat="all" aria-pressed="true">All</button>' + "".join(
        f'<button class="chip" data-cat="{c}" aria-pressed="false">{CATEGORY_LABELS[c]}</button>' for c in order
    )
    areas = '<option value="all">All areas</option>' + "".join(
        f'<option>{escape(a)}</option>' for a in AREAS if any(e["area"] == a for e in events)
    )
    filters = f"""<div class="filters" role="group" aria-label="Filter by type">{chips}</div>
<div class="toolbar"><input id="q" type="search" placeholder="Search venue, suburb, vibe…" aria-label="Search events">
<select id="area" aria-label="Filter by area">{areas}</select>
<select id="sort" aria-label="Sort"><option value="featured">Sort: Featured</option><option value="low">Price: low to high</option><option value="high">Price: high to low</option></select></div>
<p class="count" aria-live="polite"></p>""" if show_filters else ""
    cards = "".join(card(e, i) for i, e in enumerate(events))
    return f"""<section id="{anchor}" data-directory><div class="wrap">
<div class="section-head"><h2>{heading}</h2><p>{sub}</p></div>
{filters}
<div class="grid">{cards}</div>
<p class="empty">No events match that search. Try another filter, or <a href="/list-your-event/">list yours</a>.</p>
</div></section>"""


def season_section(p):
    months = [
        ("October", "Planning begins",
         "Festivals, cruises and fireworks dinners release tickets, and Perth starts searching \"NYE in Perth\". Early birds lock in their plans and groups start comparing options.",
         "List now and you're live for the whole season, from day one."),
        ("November", "Comparing &amp; booking",
         "Searchers compare prices, inclusions and fireworks views side by side. This is when riverside tables, cruises and party tickets get booked.",
         "Your page, with its price, inclusions and a Book button, wins the comparison."),
        ("December", "Peak searches &amp; last-minute rush",
         "Search interest hits its peak. People chase the last tables, final release tiers and late tickets right up to 31 December.",
         "Sell your remaining tickets and late seatings while demand is at its highest."),
    ]
    cards = "".join(
        f'''<div class="card season-card"><span class="season-step">{i + 1}</span><div class="loc">{m}</div><h3>{t}</h3><p>{d}</p>
<p class="season-win">✦ {w}</p></div>''' for i, (m, t, d, w) in enumerate(months)
    )
    return f"""<section id="season"><div class="wrap">
<div class="section-head"><span class="eyebrow">The NYE search season</span>
<h2>Perth books New Year's Eve in <span class="grad">three months</span></h2>
<p>Every year, searches like "NYE in Perth", "New Year's Eve Perth" and "NYE dinner Perth" climb from October and peak in the final weeks of December. That's when people choose a venue and buy tickets. If your event isn't in front of them then, they book somewhere else.</p></div>
<div class="season-bar" aria-hidden="true"><span style="--h:34%">Oct</span><span style="--h:62%">Nov</span><span style="--h:100%">Dec</span></div>
<p class="muted" style="text-align:center;font-size:.8rem;margin:-6px 0 30px">Shows the typical seasonal pattern of search interest, not exact volumes.</p>
<div class="grid">{cards}</div>
<div class="band" style="margin-top:40px">
<div><h2>One listing. The whole season.</h2><p>At typical riverside NYE prices of $90–$400 a head, a handful of bookings covers your ${p} listing. Everything after that is profit, with zero commission.</p></div>
<a class="btn" href="#form">Claim your spot →</a></div>
</div></section>"""


def list_band():
    return f"""<section><div class="wrap"><div class="band">
<div><h2>Selling NYE tickets in Perth?</h2><p>October to December is when Perth searches for its New Year's Eve plans. Get your event in front of them for ${CONFIG['listing_price']} flat, with no commission.</p></div>
<a class="btn" href="/list-your-event/">List your event →</a></div></div></section>"""


def item_list(events, name):
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "numberOfItems": len(events),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": f"{URL}/events/{e['slug']}/", "name": e["name"]}
            for i, e in enumerate(events)
        ],
    }


def breadcrumbs(*pairs):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": URL + p} for i, (n, p) in enumerate(pairs)
        ],
    }


# --------------------------------------------------------------------------------------
# Content: FAQ, timeline, vantage points
# --------------------------------------------------------------------------------------
FAQ = [
    (f"What time are the Perth New Year's Eve fireworks in {Y}?",
     f"In 2025 the City of Perth ran two displays over the Swan River at Elizabeth Quay: a family fireworks show at 8:30pm (about 12–15 minutes) and the main show at midnight. The {Y} program is still to be announced, but the same format is expected on Thursday 31 December {Y}. Mandurah and Rockingham hold their own shows at 9pm and midnight, and Rottnest has an early family display over Thomson Bay."),
    ("Where is the best place to watch the Perth NYE fireworks?",
     "The closest free views are at Elizabeth Quay, Barrack Square, the Supreme Court Gardens and the foreshore along Birdiya Drive and Langley Park. Views from South Perth and Kings Park can be partly blocked. For a guaranteed spot without arriving hours early, book a riverside dinner such as The Reveley or 6HEAD, a river cruise, or a ticketed party with a view."),
    ("Are the Perth New Year's Eve fireworks free?",
     "Yes. New Year's Eve in the City at Elizabeth Quay is free and you don't need a ticket. The Mandurah, Rockingham, Mindarie and Rottnest fireworks are free too, although on Rottnest you still need a ferry ticket. Some venues with their own midnight fireworks, like Gloucester Park and the SNACK festival, are ticketed."),
    ("Is there a New Year's Eve cruise on the Swan River?",
     "Yes. Captain Cook Cruises runs a NYE cruise on the Swan River from 8pm to 12:30am, priced at $279 per adult for 2026, with dinner, a DJ and the midnight countdown on the water. Further south, Mandurah has family-friendly cruises that stop for the 9pm fireworks from about $65. Cruises are limited in Perth, so book early. See our <a href=\"/new-years-eve-cruises-perth/\">NYE cruises in Perth</a> list."),
    ("Where can I have dinner with a fireworks view in Perth?",
     "Elizabeth Quay is the place for a fireworks dinner. The Reveley (about $89pp in 2025), 6HEAD ($395 for 2026), The Island and Hearth at The Ritz-Carlton all sit on or beside the quay. C Restaurant revolves 33 floors above the CBD, and Fraser's in Kings Park looks over the city and river. See our <a href=\"/new-years-eve-dinner-perth/\">NYE dinners in Perth</a> list."),
    ("What time should I arrive at Elizabeth Quay?",
     "The riverside zones opened from about 5pm in 2025. For a front spot for the 8:30pm family fireworks, arrive in the late afternoon. The quay gets very crowded before midnight, so the Birdiya Drive foreshore and Langley Park are good back-ups with more space."),
    ("Is public transport free on New Year's Eve in Perth?",
     "Transperth travel is free from 12:01am to 6am on New Year's Day on all trains, buses and ferries, with no need to tag on. Trains ran through the night after NYE 2025, and extra buses ran to the CBD, Northbridge, Fremantle, Scarborough and Rockingham. Normal fares apply before midnight. Check transperth.wa.gov.au for the official timetable closer to the date."),
    ("Can I bring alcohol to the Perth NYE fireworks?",
     "The City of Perth's celebration at Elizabeth Quay is an alcohol-free event, although licensed venues on the quay and in the CBD trade as normal. Mandurah's foreshore event is smoke-free, alcohol-free and pet-free, and The Marina Mindarie is a licensed venue, so BYO alcohol, food and chairs aren't allowed. Check the rules for your spot before you go."),
    ("What are the best family-friendly NYE options in Perth?",
     "The 8:30pm family fireworks at Elizabeth Quay are made for kids, and in 2025 the Supreme Court Gardens hosted a free family fun zone with rides. Other good picks are the Rottnest family fireworks, the free Mandurah and Rockingham foreshore events, Zoo Year's Eve at Perth Zoo, the Aussie BBQ family party at The Vines and early dinner sittings with kids' pricing."),
    ("Is NYE in Perth the official Perth New Year's Eve website?",
     "No. NYE in Perth is an independent guide and event directory. The official celebration at Elizabeth Quay is run by the City of Perth. We bring together the free fireworks events and bookable dinners, cruises and parties so you can plan the whole night in one place."),
    ("How do I list my New Year's Eve event on NYE in Perth?",
     f"It's a one-off ${CONFIG['listing_price']} fee with no commission. Your event gets its own optimised page, a place in our directory and category pages, and a direct link to your booking page. <a href=\"/list-your-event/\">List your event here</a>."),
]


def faq_html(items):
    return "".join(f"<details><summary>{escape(q)}</summary><p>{a}</p></details>" for q, a in items)


def faq_schema(items):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items
        ],
    }


TIMELINE = [
    ("From 2pm", "Staged road closures begin around Elizabeth Quay, Barrack Square and the Riverside Drive area."),
    ("4pm", "Rottnest Island's free family program starts on Thomson Bay."),
    ("From 5pm", "New Year's Eve in the City opens across Elizabeth Quay, Barrack Square and the Supreme Court Gardens, with rides, DJs and food trucks."),
    ("About 8pm", "Family fireworks over Thomson Bay on Rottnest Island."),
    ("8:30pm", "Family fireworks over the Swan River at Elizabeth Quay, about 12–15 minutes. Mindarie's marina show is around the same time."),
    ("9:00pm", "First fireworks at the Mandurah and Rockingham foreshores."),
    ("Midnight", f"The main fireworks over the Swan River to welcome {NY}, plus midnight shows at Mandurah, Rockingham, Gloucester Park and the SNACK festival."),
    ("12:01am – 6am", "Free Transperth trains, buses and ferries. Trains ran all night after NYE 2025, and the last ferries left Elizabeth Quay at 2am."),
]


def timeline_html():
    return '<div class="timeline">' + "".join(
        f'<div class="tl"><b>{t}</b><p>{d}</p></div>' for t, d in TIMELINE
    ) + "</div>"


VANTAGE = [
    ("Elizabeth Quay", "Perth CBD", "Front row, fireworks over the quay", "free", "Heart of the City of Perth event; alcohol-free; busiest spot"),
    ("Barrack Square", "Perth CBD", "Riverside, beside the Bell Tower", "free", "Food trucks and seating in 2025; close to Elizabeth Quay Station"),
    ("Supreme Court Gardens", "Perth CBD", "Gardens just back from the river", "free", "Family fun zone with free rides in 2025"),
    ("Birdiya Drive foreshore & Langley Park", "Perth CBD", "Wide riverfront east of the quay", "free", "More space than the quay; a good back-up spot"),
    ("Sir James Mitchell Park", "South Perth", "Across the river to the city skyline", "check", "Quieter, but views can be partly blocked"),
    ("Kings Park", "Kings Park", "Elevated view over the city", "check", "Big skyline view; fireworks can be partly hidden"),
    ("Thomson Bay", "Rottnest Island", "Island beach and bay", "free-f", "Early family fireworks; ferries sell out"),
    ("Mandurah Eastern Foreshore", "Mandurah", "Over the water, 9pm & midnight", "free", "Smoke, alcohol and pet-free event"),
    ("Rockingham Foreshore", "Rockingham", "Beachside, 9pm & midnight", "free", "Rides, live music and a low-sensory zone"),
    ("The Marina Mindarie", "Mindarie", "Marina, early show", "free", "Licensed venue; no BYO alcohol, food or chairs"),
    ("Gloucester Park", "East Perth", "Own midnight show over the track", "paid", "From $35 adults in 2025; under 12s free with ticket"),
]
PILL = {
    "free": '<span class="pill free">Free</span>',
    "free-t": '<span class="pill free">Free · ticket</span>',
    "free-f": '<span class="pill free">Free · ferry needed</span>',
    "paid": '<span class="pill paid">Paid ticket</span>',
    "check": '<span class="pill af">Partial view</span>',
}


def vantage_table(rows=None):
    rows = rows or VANTAGE
    body = "".join(
        f"<tr><td><b>{n}</b></td><td>{a}</td><td>{v}</td><td>{PILL[t]}</td><td class='muted'>{note}</td></tr>"
        for n, a, v, t, note in rows
    )
    return f"""<div class="table-wrap"><table><thead><tr><th>Vantage point</th><th>Area</th><th>View</th><th>Entry</th><th>Good to know</th></tr></thead>
<tbody>{body}</tbody></table></div>"""


# --------------------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------------------
def page_home():
    featured = [e for e in EVENTS if e.get("featured")]
    rest = [e for e in EVENTS if not e.get("featured")]
    ordered = featured + rest
    n = len(EVENTS)
    body = f"""
<section class="hero"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap">
<span class="eyebrow">Thursday 31 December {Y} · Swan River, Perth</span>
<h1>New Year's Eve Perth {Y}<br><span class="grad">fireworks, parties &amp; dinners</span></h1>
<p class="lead">The best NYE events in Perth in one place: Elizabeth Quay fireworks dinners, Swan River cruises, rooftop parties, beach bars and every free fireworks spot from Rottnest to Mandurah. Compare, choose and book your night to welcome {NY}.</p>
{countdown()}
<p class="cd-note">until the midnight fireworks over the Swan River (AWST)</p>
<div class="cta-row"><a class="btn btn-primary" href="#directory">Browse {n} NYE events</a><a class="btn btn-ghost" href="/perth-fireworks-vantage-points/">Free fireworks spots</a></div>
</div></section>

<div class="wrap"><div class="facts">
<div class="fact"><b>8:30pm</b><span>Family fireworks at Elizabeth Quay (2025 time)</span></div>
<div class="fact"><b>Midnight</b><span>Main fireworks over the Swan River</span></div>
<div class="fact"><b>130,000</b><span>people at the City of Perth event in 2025</span></div>
<div class="fact"><b>{n}</b><span>dinners, cruises, parties &amp; free fireworks events</span></div>
</div></div>

{directory(ordered, f"Every Perth NYE {Y} event in one directory", "Filter by type, area or budget. Every listing shows what's included, which fireworks you'll see and a direct booking link.")}

{list_band()}

<section class="alt"><div class="wrap two">
<div><h2>Your NYE {Y} in Perth, <span class="grad">hour by hour</span></h2>
<p class="muted">Timings are based on New Year's Eve 2025. The City of Perth confirms the {Y} program closer to the night. Use this to plan when to arrive, eat and move.</p>
<a class="btn btn-ghost" href="/plan-your-night/">Full planning guide →</a></div>
{timeline_html()}
</div></section>

<section><div class="wrap">
<div class="section-head"><h2>Best places to watch the Perth fireworks</h2><p>Free riverside spots in the city, plus the beach and foreshore shows around Perth, with what you need to know about each one.</p></div>
{vantage_table(VANTAGE[:8])}
<p style="text-align:center;margin-top:24px"><a class="btn btn-ghost" href="/perth-fireworks-vantage-points/">See all vantage points →</a></p>
</div></section>

<section class="alt"><div class="wrap">
<div class="section-head"><h2>Find your kind of NYE</h2></div>
<div class="grid">
<div class="card"><h3><a href="/new-years-eve-dinner-perth/">🍽️ NYE dinners with fireworks views</a></h3><p>From $89 at The Reveley to $395 at 6HEAD, right on Elizabeth Quay.</p><a href="/new-years-eve-dinner-perth/">Browse dinners →</a></div>
<div class="card"><h3><a href="/new-years-eve-cruises-perth/">🛥️ Swan River &amp; Mandurah NYE cruises</a></h3><p>Midnight on the Swan River, or a 9pm fireworks cruise in Mandurah.</p><a href="/new-years-eve-cruises-perth/">Browse cruises →</a></div>
<div class="card"><h3><a href="/new-years-eve-parties-perth/">🎉 NYE parties &amp; rooftops</a></h3><p>SNACK festival, CBD rooftops, Leederville, Fremantle and beach bars.</p><a href="/new-years-eve-parties-perth/">Browse parties →</a></div>
<div class="card"><h3><a href="/family-new-years-eve-perth/">👨‍👩‍👧 Family-friendly NYE</a></h3><p>8:30pm fireworks, Rottnest, Perth Zoo and free foreshore events.</p><a href="/family-new-years-eve-perth/">Browse family events →</a></div>
</div></div></section>

<section id="faq"><div class="wrap">
<div class="section-head"><h2>New Year's Eve Perth {Y}: FAQ</h2></div>
<div class="faq">{faq_html(FAQ)}</div>
</div></section>
"""
    return layout(
        "/",
        f"New Year's Eve Perth {Y}: Fireworks, Events & Dinners | NYE in Perth",
        f"Plan New Year's Eve {Y} in Perth: live countdown, Elizabeth Quay fireworks times, the best free vantage points and {n} NYE dinners, Swan River cruises and parties.",
        body,
        schema=[item_list(ordered, f"New Year's Eve Perth {Y} events"), faq_schema(FAQ),
                {"@context": "https://schema.org", "@type": "Organization", "name": CONFIG["site_name"], "url": URL + "/",
                 "logo": URL + "/favicon.svg", "email": CONFIG["contact_email"]}],
    )


CATEGORY_PAGES = [
    {
        "path": "/new-years-eve-dinner-perth/",
        "filter": lambda e: "dining" in e["categories"] or "fine-dining" in e["categories"],
        "title": f"NYE Dinner Perth {Y}: New Year's Eve Restaurants with Fireworks Views",
        "h1": f"New Year's Eve dinners in Perth {Y}",
        "desc": f"The best New Year's Eve dinners in Perth {Y}: Elizabeth Quay restaurants with fireworks views, NYE degustations, family sittings and set menus, with prices and booking links.",
        "intro": "A table on Elizabeth Quay is the most comfortable way to watch the Perth fireworks: no jostling for a spot on the grass, and a long dinner while you wait for midnight. Early sittings line up with the 8:30pm family show and cost less, while late sittings carry you through to the midnight fireworks.",
        "tips": ["Book early. Quayside tables with a view sell out first.", "Early sittings are the best-value way to see the 8:30pm fireworks.", "Ask whether your table has a fireworks view or only the venue does.", "Allow extra travel time: road closures around the quay start from 2pm."],
    },
    {
        "path": "/new-years-eve-cruises-perth/",
        "filter": lambda e: "cruise" in e["categories"],
        "title": f"NYE Cruises Perth {Y}: Swan River & Mandurah New Year's Eve Cruises",
        "h1": f"New Year's Eve cruises in Perth {Y}",
        "desc": f"Compare New Year's Eve cruises in Perth for {Y}: a Swan River dinner cruise through midnight, plus Mandurah fireworks cruises for families, with prices and booking links.",
        "intro": "Perth has only a handful of ticketed NYE cruises, so they're worth booking early. The Swan River dinner cruise stays on the water through the midnight countdown, while the Mandurah boats tour the canal Christmas lights and stop for the 9pm fireworks, which suits families.",
        "tips": ["Check the boarding jetty and return time, as the city is busy after midnight.", "Free Transperth travel starts at 12:01am, handy after a late cruise.", "Mandurah cruises finish around 9:15pm, so they work well with kids.", "The Swan River dinner cruise is 18+. Check the age rules before booking."],
    },
    {
        "path": "/new-years-eve-parties-perth/",
        "filter": lambda e: "party" in e["categories"] or "rooftop" in e["categories"],
        "title": f"NYE Parties Perth {Y}: Best New Year's Eve Parties, Rooftops & Festivals",
        "h1": f"The best New Year's Eve parties in Perth {Y}",
        "desc": f"Perth's best New Year's Eve parties for {Y}: SNACK festival, CBD rooftops, Leederville, Northbridge, Fremantle and beach bars, with prices, inclusions and tickets.",
        "intro": "From the SNACK festival in Claremont to rooftop bars in the CBD and beach bars in Scarborough and Fremantle, these are the best NYE parties in Perth. Some sit right on the river with a view of the fireworks. Others are clubs, pubs and precinct parties where midnight is just part of the night.",
        "tips": ["Many parties release tickets in tiers, so the first release is the cheapest.", "Check whether drinks are included or pay-as-you-go.", "Most parties are 18+ with ID checks.", "Want the fireworks too? Pick a party near Elizabeth Quay or on the river."],
    },
    {
        "path": "/family-new-years-eve-perth/",
        "filter": lambda e: "family" in e["categories"] or "vantage" in e["categories"],
        "title": f"Family New Year's Eve Perth {Y}: Kid-Friendly NYE & Early Fireworks",
        "h1": f"Family-friendly New Year's Eve in Perth {Y}",
        "desc": f"Kid-friendly ways to celebrate New Year's Eve {Y} in Perth: 8:30pm family fireworks at Elizabeth Quay, Rottnest, Perth Zoo, free foreshore events and family dinners.",
        "intro": "Perth does early fireworks well. The family show at Elizabeth Quay was at 8:30pm in 2025, Rottnest's was around 8pm, and Mandurah and Rockingham go at 9pm, so you can see a full display and be home before midnight. Free family zones with rides make the wait easy.",
        "tips": ["Aim for the 8:30pm family fireworks with younger kids.", "Arrive in the late afternoon to find a spot with shade.", "Pack hats, sunscreen, water, a picnic rug and ear protection for little ones.", "Agree on a meeting point in case anyone gets separated."],
    },
]


def page_category(c):
    events = [e for e in EVENTS if c["filter"](e)]
    events.sort(key=lambda e: (not e.get("featured"), e["price_from"] if e["price_from"] is not None else 1e9))
    tips = "".join(f"<li>{t}</li>" for t in c["tips"])
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">NYE {Y} · Perth</span><h1>{c['h1']}</h1>
<p class="lead">{c['intro']}</p>{countdown(mini=True)}</div></section>
<section style="padding-bottom:0"><div class="wrap two">
<div class="panel"><h2 style="font-size:1.5rem">Booking tips</h2><ul class="ticks">{tips}</ul></div>
<div><h2 style="font-size:1.5rem">{len(events)} options, compared</h2><p class="muted">Every listing shows a "from" price, what's included and which fireworks you'll see. Prices are per person and based on published packages, so always confirm the current price with the venue.</p>
<a class="btn btn-primary" href="/list-your-event/">Add your venue: ${CONFIG['listing_price']}</a></div>
</div></section>
{directory(events, c['h1'], 'Filter and sort to find your night.')}
{list_band()}"""
    return layout(
        c["path"], c["title"] + " | NYE in Perth", c["desc"], body,
        schema=[item_list(events, c["h1"]), breadcrumbs(("Home", "/"), (c["h1"], c["path"]))],
    )


def page_event(e):
    path = f"/events/{e['slug']}/"
    inc = "".join(f"<li>{escape(x)}</li>" for x in e["includes"])
    cats = ", ".join(CATEGORY_LABELS.get(c, c) for c in e["categories"])
    related = [x for x in EVENTS if x["slug"] != e["slug"] and (x["area"] == e["area"] or set(x["categories"]) & set(e["categories"]))][:3]
    offer = {"@type": "Offer", "url": e["url"], "priceCurrency": "AUD", "availability": "https://schema.org/InStock",
             "validFrom": f"{Y}-01-01"}
    if e["price_from"] is not None:
        offer["price"] = e["price_from"]
    schema = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": f"{e['name']} – New Year's Eve {Y}",
        "description": e["blurb"] + " Includes: " + "; ".join(e["includes"]) + ".",
        "startDate": f"{Y}-12-31",
        "endDate": f"{NY}-01-01",
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "image": [f"{URL}/og.png"],
        "location": {
            "@type": "Place", "name": e["venue"],
            "address": {"@type": "PostalAddress", "addressLocality": e["suburb"], "addressRegion": "WA", "addressCountry": "AU"},
        },
        "organizer": {"@type": "Organization", "name": e["venue"].split(",")[0], "url": e["url"]},
        "offers": offer,
    }
    body = f"""
<section class="event-hero"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › <a href="/#directory">NYE events</a> › {escape(e['name'])}</nav>
<span class="eyebrow">New Year's Eve {Y} · {escape(e['suburb'])}</span>
<h1 style="font-size:clamp(2rem,5vw,3.4rem)">{escape(e['name'])}</h1>
<p class="lead muted" style="font-size:1.15rem;max-width:760px">{escape(e['blurb'])}</p>
</div></section>
<section style="padding-top:10px"><div class="wrap event-layout">
<div>
<div class="panel"><h2 style="font-size:1.5rem">What's included</h2><ul class="ticks">{inc}</ul></div>
<div class="prose" style="margin-top:30px">
<h2 style="font-size:1.5rem">About {escape(e['name'])}</h2>
<p>{escape(e['name'])} is at {escape(e['venue'])} in {escape(e['suburb'])} ({escape(e['area'])}). It's one of the {escape(cats.lower())} options for New Year's Eve {Y} in Perth. Fireworks: <b>{escape(e['fireworks'])}</b>. Age: <b>{escape(e['age'])}</b>.</p>
<p>Planning the rest of your night? Check the <a href="/plan-your-night/">fireworks timeline and transport tips</a> or compare <a href="/perth-fireworks-vantage-points/">fireworks vantage points around Perth</a>.</p>
<p class="notice">Details are based on the venue's published NYE information and can change. Confirm the price, times and inclusions with {escape(e['venue'].split(',')[0])} before booking. Are you the venue? <a href="/list-your-event/">Claim and upgrade this listing</a>.</p>
</div></div>
<aside class="side panel">
<div class="price" style="font-size:2rem">{"Free" if e['price_from']==0 else money(e['price_from']) if e['price_from'] else "TBA"}<small>{escape(e['price_text'])}</small></div>
<dl><dt>Date</dt><dd>Thursday 31 December {Y}</dd><dt>Time</dt><dd>{escape(e['time'])}</dd>
<dt>Where</dt><dd>{escape(e['venue'])}</dd><dt>Fireworks</dt><dd>🎆 {escape(e['fireworks'])}</dd><dt>Age</dt><dd>{escape(e['age'])}</dd></dl>
<a class="btn btn-primary" style="width:100%;justify-content:center" href="{e['url']}" target="_blank" rel="noopener sponsored">Book with the venue →</a>
<div style="margin-top:20px">{countdown(mini=True)}</div>
</aside>
</div></section>
<section class="alt"><div class="wrap"><div class="section-head"><h2>You might also like</h2></div>
<div class="grid">{''.join(card(x, i) for i, x in enumerate(related))}</div></div></section>
{list_band()}"""
    return layout(
        path,
        (f"{e['name']} {Y}" if "NYE" in e["name"] or "New Year" in e["name"] else f"{e['name']} NYE {Y}")
        + f" – {e['suburb']} | NYE in Perth",
        f"{e['name']} New Year's Eve {Y} in {e['suburb']}: {e['price_text']}. {e['blurb']}"[:300],
        body, og_type="article", active="/#directory",
        schema=[schema, breadcrumbs(("Home", "/"), ("NYE events", "/#directory"), (e["name"], path))],
    )


def page_vantage():
    vp = [e for e in EVENTS if "vantage" in e["categories"]]
    faq = FAQ[1:3] + FAQ[5:6] + FAQ[7:8]
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">NYE {Y} · Free &amp; ticketed</span>
<h1>Perth fireworks vantage points {Y}</h1>
<p class="lead">Where to watch the Perth New Year's Eve fireworks: free riverside spots around Elizabeth Quay, quieter foreshores, and the beach and island shows from Rottnest to Mandurah.</p></div></section>
<section><div class="wrap">
<div class="section-head"><h2>Vantage points at a glance</h2><p>Event zones and entry conditions are set by the City of Perth and local councils each year. Notes are based on New Year's Eve 2025, so check official updates on the day.</p></div>
{vantage_table()}
</div></section>
{directory(vp, "Fireworks events around Perth", "Free public celebrations and ticketed venues with their own fireworks, from the CBD to the coast.", show_filters=False)}
<section class="alt"><div class="wrap prose">
<h2>How to choose a vantage point</h2>
<p><b>For the closest view</b>, head to Elizabeth Quay or Barrack Square. The fireworks launch over the river right in front of you, but these are the busiest spots on the night.</p>
<p><b>For more space</b>, walk east along the river to the Birdiya Drive foreshore and Langley Park. You're still close to the show, with room to spread out a rug.</p>
<p><b>For a quieter night</b>, try Sir James Mitchell Park in South Perth or Kings Park. The skyline views are great, but buildings and trees can hide some of the fireworks.</p>
<p><b>Outside the city</b>, Mandurah and Rockingham run free foreshore shows at 9pm and midnight, Mindarie has an early marina show, and Rottnest's fireworks light up Thomson Bay in the early evening.</p>
<p><b>With kids</b>, make the 8:30pm family fireworks your main event and arrive in the late afternoon for a spot near the family zone.</p>
<h2>What to bring</h2>
<ul><li>Picnic rug and a low chair (check whether chairs are allowed)</li><li>Water, snacks, a hat and sunscreen. Perth's NYE is often hot</li><li>Charged phone and a power bank</li><li>A light layer for the river breeze after dark</li><li>No glass, and no alcohol at the City of Perth event zone</li></ul>
</div></section>
<section id="faq"><div class="wrap"><div class="section-head"><h2>Vantage point FAQ</h2></div><div class="faq">{faq_html(faq)}</div></div></section>
{list_band()}"""
    return layout(
        "/perth-fireworks-vantage-points/",
        f"Perth Fireworks New Year's Eve {Y}: Best Places to Watch | NYE in Perth",
        f"The best places to watch the Perth New Year's Eve fireworks in {Y}: Elizabeth Quay, Langley Park, South Perth, Kings Park, plus Rottnest, Mandurah and Rockingham shows and what time to arrive.",
        body, schema=[faq_schema(faq), item_list(vp, "Perth NYE fireworks events"),
                      breadcrumbs(("Home", "/"), ("Vantage points", "/perth-fireworks-vantage-points/"))],
    )


def page_plan():
    faq = [FAQ[0], FAQ[6], FAQ[7], FAQ[8]]
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">Planning guide</span>
<h1>Plan your Perth NYE {Y}</h1>
<p class="lead">Fireworks times, the run sheet for the night, getting there by Transperth, road closures, accessibility and what to bring.</p>
{countdown(mini=True)}</div></section>
<section><div class="wrap two" style="align-items:start">
<div><h2>Fireworks times &amp; the night's schedule</h2><p class="muted">Times are based on New Year's Eve 2025. The City of Perth publishes the final {Y} program closer to the night. Perth is on AWST (UTC+8) with no daylight saving.</p></div>
{timeline_html()}
</div></section>
<section class="alt" id="transport"><div class="wrap prose">
<h2>Getting there: Transperth</h2>
<p>Public transport is the easiest way in and out of the city on New Year's Eve. Elizabeth Quay Station and Elizabeth Quay Bus Station sit right next to the celebrations. For NYE 2025, the State Government made all Transperth trains, buses and ferries free from 12:01am to 6am on New Year's Day, with no need to tag on, and trains on every line ran through the night.</p>
<ul><li>Plan your trip on <a href="https://www.transperth.wa.gov.au/" rel="noopener" target="_blank">transperth.wa.gov.au</a> or the Transperth app and check the NYE timetable closer to the date.</li>
<li>In 2025, boarding points changed from 8:30pm to 10pm: Yanchep Line trains left from Perth Underground, Mandurah Line trains from Elizabeth Quay, and other lines from Perth Station.</li>
<li>Extra buses ran either side of midnight to and from the CBD, Northbridge, Fremantle, Scarborough Beach and Rockingham Beach.</li>
<li>Ferries ran before and after midnight, with the last departures at 2am from Elizabeth Quay and 2:15am from Mends Street.</li>
<li>After midnight, expect queues. Stay for a drink or snack and leave once the first wave has gone.</li></ul>
<h2 id="roads">Road closures &amp; driving</h2>
<p>In 2025, staged road closures started from 2pm and ran until about 1am to 2am around Barrack Square, Riverside Drive, Geoffrey Bolton Avenue, William Street and The Esplanade, and Elizabeth Quay Inlet was closed to boats from 4pm to 1am. Rideshare pick-ups were directed to St Georges Terrace and Mounts Bay Road. If you have to drive, park at the Convention Centre, Terrace Road or Council House car parks early, or park outside the city and finish the trip by train.</p>
<h2 id="boating">Boating on the Swan River</h2>
<p>Water closures apply around the fireworks zone, and the river is busy all night. For most people a licensed <a href="/new-years-eve-cruises-perth/">NYE cruise</a> is the easiest way to see in the new year from the water.</p>
<h2 id="alcohol">Alcohol-free zones</h2>
<p>The City of Perth's celebration at Elizabeth Quay is alcohol-free, although licensed bars and restaurants on the quay and in the CBD trade as normal. Mandurah's foreshore event is smoke-free, alcohol-free and pet-free. The Marina Mindarie is a licensed venue, so BYO alcohol, food and chairs aren't allowed.</p>
<h2 id="accessibility">Accessibility</h2>
<p>In 2025 the City of Perth event had wheelchair-friendly paths, accessible toilets, Auslan interpreters, sensory spaces and assistance animal relief areas, plus an audio-described accessible viewing area run with DADAA. Rockingham's event included a low-sensory zone. Check the official accessibility information for your site, and contact venues in our directory to confirm step-free access.</p>
<h2>Safety &amp; wellbeing</h2>
<ul><li>Drink plenty of water. Perth's NYE is often over 30°C.</li><li>Agree on a meeting point with your group.</li><li>Follow police and staff directions.</li><li>Look after your mates, and get help from first-aid stations if you need it.</li></ul>
</div></section>
<section id="faq"><div class="wrap"><div class="section-head"><h2>Planning FAQ</h2></div><div class="faq">{faq_html(faq)}</div></div></section>
{list_band()}"""
    return layout(
        "/plan-your-night/",
        f"Perth NYE {Y} Fireworks Times, Transport & Road Closures | NYE in Perth",
        f"Perth New Year's Eve {Y} planning guide: 8:30pm and midnight fireworks times, the schedule for the night, free Transperth travel after midnight, road closures, alcohol-free zones and accessibility.",
        body, schema=[faq_schema(faq), breadcrumbs(("Home", "/"), ("Plan your night", "/plan-your-night/"))],
    )


def page_list():
    p = CONFIG["listing_price"]
    has_pay = "YOUR_" not in CONFIG["payment_link"]
    form_sub = (f"Fill this in, then pay ${p} securely. We'll publish your page and email you the link." if has_pay
                else f"Fill this in and we'll email you a ${p} invoice within one business day. Your page goes live once it's paid.")
    submit_label = f"Continue to payment: ${p} →" if has_pay else "Send my listing request →"
    cats = "".join(f'<option value="{k}">{v}</option>' for k, v in CATEGORY_LABELS.items() if k not in ("budget", "free"))
    faq = [
        ("What do I get for $" + str(p) + "?", "A dedicated event page built for search, with Google Event structured data. You also get a listing in our main directory and the matching category pages (dinners, cruises, parties, family), a direct link to your own booking page, and edits until 31 December."),
        ("Why should I list now rather than in December?", "Search interest in Perth New Year's Eve builds from October and peaks in the final weeks of December. Listing early means your page is live and indexed by Google for the whole season, not just the last-minute rush. New pages can take days or weeks to rank, so the earlier you're in, the more of the season you capture. It's the same $" + str(p) + " whenever you list."),
        ("Do you take commission on bookings?", "No. Guests book directly with you through your own link, and you keep 100% of every ticket."),
        ("How long does my listing stay live?", f"Your listing stays live until New Year's Day {NY}, then rolls into our archive. Previous listers get first right to renew for next year."),
        ("How fast will my listing go live?", "Usually within one business day of payment. We'll email you the link."),
        ("Can I update prices or details?", "Yes. Email us any changes (sold-out tiers, price releases, new acts) and we'll update your page."),
    ]
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">For venues, promoters &amp; cruise operators</span>
<h1>List your New Year's Eve event</h1>
<p class="lead">October, November and December are when Perth searches for its New Year's Eve plans. Put your NYE {Y} event in front of people typing "NYE in Perth", "New Year's Eve Perth", "NYE dinner Perth" and "NYE cruise Perth" while they're choosing where to spend the night.</p>
{countdown(mini=True)}
<p class="cd-note" style="margin-top:0">left to sell. The NYE search season is on now.</p>
<div class="cta-row"><a class="btn btn-primary" href="#form">List my event: ${p}</a><a class="btn btn-ghost" href="#season">Why now?</a></div></div></section>
{season_section(p)}
<section><div class="wrap two" style="align-items:start">
<div>
<h2>Why list with <span class="grad">NYE in Perth</span>?</h2>
<ul class="ticks">
<li><b>High-intent visitors.</b> People only visit a NYE guide when they're about to book.</li>
<li><b>Your own SEO page.</b> Each event gets a dedicated page with Google Event schema, which can make it eligible for event rich results.</li>
<li><b>Listed where people browse.</b> You appear in the main directory plus every matching category: dinners, cruises, parties and family.</li>
<li><b>Zero commission.</b> Guests click straight through to your booking page.</li>
<li><b>Updates until NYE.</b> Change prices, add tiers or mark sold-out tiers whenever you like.</li>
<li><b>Our name is the search.</b> NYE in Perth is built around the exact phrases people type into Google, so every page targets them.</li>
<li><b>Countdown traffic.</b> Interest builds from October and peaks in December, right when you're selling.</li>
</ul>
</div>
<div class="pricing">
<span class="eyebrow">NYE {Y} listing</span>
<div class="amount"><sup>$</sup>{p}</div>
<p class="muted">AUD inc GST · one-off · no commission</p>
<ul class="ticks">
<li>Dedicated event page + Google Event schema</li>
<li>Directory &amp; category page placement</li>
<li>Direct "Book" button to your site</li>
<li>Unlimited edits until 31 Dec {Y}</li>
<li>Live within 1 business day</li>
</ul>
<a class="btn btn-primary" href="#form" style="width:100%;justify-content:center">List my event →</a>
</div>
</div></section>
<section class="alt" id="form"><div class="wrap" style="max-width:860px">
<div class="section-head"><h2>Your event details</h2><p>{form_sub}</p></div>
<form class="listing panel" data-endpoint="{CONFIG['form_endpoint']}" data-payment="{CONFIG['payment_link']}" data-email="{CONFIG['contact_email']}">
<div><label for="f-name">Event name *</label><input id="f-name" name="event_name" required></div>
<div><label for="f-venue">Venue *</label><input id="f-venue" name="venue" required></div>
<div><label for="f-suburb">Suburb *</label><input id="f-suburb" name="suburb" required></div>
<div><label for="f-cat">Type *</label><select id="f-cat" name="category" required>{cats}</select></div>
<div><label for="f-price">Price from (AUD pp)</label><input id="f-price" name="price_from" inputmode="decimal" placeholder="e.g. 249"></div>
<div><label for="f-time">Times</label><input id="f-time" name="times" placeholder="e.g. 7pm – 1am"></div>
<div><label for="f-fw">Fireworks view</label><select id="f-fw" name="fireworks"><option>Both 8:30pm &amp; midnight</option><option>Midnight only</option><option>Early show only</option><option>Partial / nearby</option><option>No view</option></select></div>
<div><label for="f-age">Age</label><select id="f-age" name="age"><option>18+</option><option>All ages</option><option>Family-friendly</option></select></div>
<div class="full"><label for="f-url">Booking URL *</label><input id="f-url" name="booking_url" type="url" required placeholder="https://"></div>
<div class="full"><label for="f-desc">Description &amp; inclusions *</label><textarea id="f-desc" name="description" required placeholder="What makes your night special? Food, drinks, DJs, views…"></textarea></div>
<div><label for="f-contact">Contact name *</label><input id="f-contact" name="contact_name" required></div>
<div><label for="f-email">Email *</label><input id="f-email" name="email" type="email" required></div>
<div><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel"></div>
<div><label for="f-abn">Business / ABN</label><input id="f-abn" name="business"></div>
<input type="hidden" name="_subject" value="New NYE in Perth listing request (${p})">
<input type="hidden" name="_template" value="table"><input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">
<div class="full"><button class="btn btn-primary" type="submit">{submit_label}</button>
<p class="form-status muted" aria-live="polite" style="margin:12px 0 0"></p></div>
</form>
</div></section>
<section><div class="wrap"><div class="section-head"><h2>Listing FAQ</h2></div><div class="faq">{faq_html(faq)}</div></div></section>"""
    service = {
        "@context": "https://schema.org", "@type": "Service", "name": f"NYE {Y} event listing",
        "provider": {"@type": "Organization", "name": CONFIG["site_name"], "url": URL + "/"},
        "areaServed": "Perth, WA",
        "offers": {"@type": "Offer", "price": p, "priceCurrency": "AUD", "url": URL + "/list-your-event/"},
    }
    return layout(
        "/list-your-event/",
        f"List Your New Year's Eve Event in Perth – ${p} | NYE in Perth",
        f"Promote your Perth New Year's Eve {Y} party, dinner or cruise. ${p} flat fee, no commission: a dedicated SEO event page, directory placement and a direct booking link.",
        body, schema=[service, faq_schema(faq), breadcrumbs(("Home", "/"), ("List your event", "/list-your-event/"))],
    )


def page_404():
    body = f"""<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}<div class="wrap">
<h1>This page fizzled out</h1><p class="lead">The page you're after isn't here, but the fireworks still are.</p>{countdown()}
<div class="cta-row"><a class="btn btn-primary" href="/">Back to all NYE events</a></div></div></section>"""
    return layout("/404.html", "Page not found | NYE in Perth", "Page not found.", body).replace(
        'content="index,follow', 'content="noindex,follow')


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#07061a"/><g stroke-linecap="round" stroke-width="4"><path d="M32 32 32 8" stroke="#ffc94d"/><path d="M32 32 53 20" stroke="#ff4fa3"/><path d="M32 32 53 44" stroke="#8b5cff"/><path d="M32 32 32 56" stroke="#41e3ff"/><path d="M32 32 11 44" stroke="#ffc94d"/><path d="M32 32 11 20" stroke="#ff4fa3"/></g><circle cx="32" cy="32" r="5" fill="#fff"/></svg>"""

OG_HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700&family=Playfair+Display:wght@800&display=swap" rel="stylesheet">
<style>body{{margin:0;width:1200px;height:630px;background:radial-gradient(ellipse at 50% 120%,#2a1a6b,transparent 60%),radial-gradient(ellipse at 85% 0%,#3a0f4d,transparent 55%),#07061a;color:#fff;font-family:Inter,sans-serif;position:relative;overflow:hidden}}
.t{{position:absolute;left:70px;top:90px;right:70px}}h1{{font-family:'Playfair Display',serif;font-size:96px;margin:0;line-height:1}}
.g{{background:linear-gradient(120deg,#ffc94d,#ff4fa3 50%,#8b5cff);-webkit-background-clip:text;color:transparent}}
p{{font-size:34px;color:#cfc9ff;margin:24px 0 0}}.b{{display:inline-block;margin-top:30px;padding:12px 26px;border-radius:99px;background:linear-gradient(120deg,#ffc94d,#ff4fa3);color:#14062b;font-weight:700;font-size:26px}}
.s{{position:absolute;bottom:0;left:0;width:100%}}.dot{{position:absolute;border-radius:50%}}</style></head><body>
<div class="t"><h1>NYE <span class="g">in Perth</span></h1><p>Fireworks · Cruises · Dinners · Parties<br>New Year's Eve {Y} on the Swan River</p><span class="b">Countdown to {NY} →</span></div>
{SKYLINE.replace('class="skyline"', 'class="s"')}
<script>for(let k=0;k<4;k++){{const cx=830+k*95,cy=90+(k%2)*110,c=['#ffc94d','#ff4fa3','#8b5cff','#41e3ff'][k];for(let i=0;i<48;i++){{const a=i/48*6.283,r=30+Math.random()*40,d=document.createElement('div');d.className='dot';d.style.cssText=`left:${{cx+Math.cos(a)*r}}px;top:${{cy+Math.sin(a)*r}}px;width:4px;height:4px;background:${{c}};box-shadow:0 0 8px ${{c}}`;document.body.appendChild(d)}}}}</script>
</body></html>"""


def build():
    if OUT.exists():
        og_keep = (OUT / "og.png").read_bytes() if (OUT / "og.png").exists() else None
        shutil.rmtree(OUT)
    else:
        og_keep = None
    OUT.mkdir()
    pages = {"/": page_home(), "/perth-fireworks-vantage-points/": page_vantage(),
             "/plan-your-night/": page_plan(), "/list-your-event/": page_list()}
    for c in CATEGORY_PAGES:
        pages[c["path"]] = page_category(c)
    for e in EVENTS:
        pages[f"/events/{e['slug']}/"] = page_event(e)
    for path, html in pages.items():
        f = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(html)
    (OUT / "404.html").write_text(page_404())
    shutil.copy(ROOT / "src" / "style.css", OUT / "style.css")
    shutil.copy(ROOT / "src" / "main.js", OUT / "main.js")
    (OUT / "favicon.svg").write_text(FAVICON)
    (OUT / "og.html").write_text(OG_HTML)
    if og_keep:
        (OUT / "og.png").write_bytes(og_keep)
    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /og.html\n\nSitemap: {URL}/sitemap.xml\n")
    prio = lambda p: "1.0" if p == "/" else "0.6" if p.startswith("/events/") else "0.8"
    sm = "".join(
        f"<url><loc>{URL}{p}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>{prio(p)}</priority></url>\n"
        for p in pages
    )
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    print(f"Built {len(pages)} pages into {OUT}")


if __name__ == "__main__":
    build()
