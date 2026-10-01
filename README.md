# NYE in Perth

An independent guide to Perth New Year's Eve: a live countdown, an events directory with filters, fireworks vantage points, a planning guide, and a paid **List your event** page ($599).

## How it works

- `data/events.json`: every listing (name, venue, suburb, area, categories, price, inclusions, booking URL, `featured`).
- `src/style.css`, `src/main.js`: the design, the countdown, the fireworks animation, the directory filters and the listing form.
- `build.py`: generates the full static site into `docs/`.

```bash
python3 build.py                     # rebuild docs/
cd docs && python3 -m http.server    # preview at http://localhost:8000
```

`build.py` generates:

- Home page: countdown, filterable directory, timeline, vantage points and FAQ
- Category landing pages: dinners, cruises, parties and family
- Fireworks vantage points page
- Planning guide: times, transport, road closures and accessibility
- List-your-event page with the $599 offer and an intake form
- One SEO page per event, with `Event` schema
- `sitemap.xml`, `robots.txt`, `404.html` and the OG image

## Before going live: edit `CONFIG` in `build.py`

| Key | What to set |
| --- | --- |
| `site_url` | `https://nyeinperth.com` (used for canonical URLs, the sitemap and OG tags) |
| `contact_email` | `aj@metatapdigital.com`: the inbox for listing requests |
| `form_endpoint` | `https://formsubmit.co/ajax/aj@metatapdigital.com`: emails each listing request to that inbox |
| `payment_link` | A Stripe Payment Link for $599 AUD. After the form saves, the buyer is redirected here with their email prefilled |

The first submission triggers a one-time FormSubmit activation email to `aj@metatapdigital.com`. Click the link in it, and every request after that arrives as a formatted email. Until `payment_link` is set, submitters see a thank-you message and you send them an invoice.

## Adding a paid listing

Add an entry to `data/events.json`. Set `"featured": true` if you want it pinned to the top with a badge. Then run `python3 build.py` and deploy.

## Deploying (Vercel)

`vercel.json` tells Vercel to serve the pre-built `docs/` folder. No build step runs, so always run `python3 build.py` and commit `docs/` before pushing.

1. On vercel.com, choose **Add New → Project**, import `adwordsmanagergc-wq/nyeinperth` and click **Deploy**. No settings need changing.
2. Under **Project → Settings → Domains**, add `nyeinperth.com` and `www.nyeinperth.com`, then set the DNS records Vercel shows at your registrar (usually an A record `76.76.21.21` for the apex and a CNAME `cname.vercel-dns.com` for `www`). `vercel.json` already redirects `www` to the apex.
3. Every push to the production branch redeploys the site automatically.

After launch, submit `https://nyeinperth.com/sitemap.xml` in Google Search Console.

To regenerate `og.png`, open `docs/og.html` at 1200×630 and screenshot it.
