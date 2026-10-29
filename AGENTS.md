# AGENTS.md

Canonical instructions for any coding agent working in this repo (Claude, Codex, Gemini, Copilot, etc.).
`CLAUDE.md` only points here. Update this file, not tool-specific copies.

## What this is

**Fairy Codemother Shop**: a fake ecommerce site where people (SMEs, trainees) can safely test analytics code:
GA4 ecommerce events, GTM, Consent Mode v2, and a simulation of returning users.

**Keep it VERY SIMPLE.** It's a sandbox, not a product. Don't add frameworks, build steps, databases, logins
or JS bundlers. Use plain Flask, Jinja templates, one CSS file and vanilla JS.

## Layout

| Path | Purpose |
|------|---------|
| `main.py` | The whole Flask app: product catalog (in-memory dict), cart (Flask session), checkout, sitemaps, returning-user simulation |
| `templates/base.html` | Shared layout: header, footer, **cookie banner**, script loading order |
| `templates/*.html` | Pages extend `base.html`. `cart.html` is titled "Checkout" (it fires `begin_checkout`) |
| `static/analytics.js` | GTM loader, consent default/update, dataLayer ecommerce pushes, returning-user cookies |
| `static/consent_update.js` | Re-applies stored consent on each page load and shows/hides the banner |
| `static/FairyStyleSheet.css` | All styling. No external fonts or CDNs (see below) |
| `static/*_policy.html` | Static privacy and cookie policy pages |
| `Procfile`, `.python-version` | Cloud Run buildpack config (gunicorn, Python 3.13) |
| `app.yaml` | Legacy App Engine config. **Not used**; deployment is Cloud Run |

## Analytics contract: don't break it

The site exists for analytics testing, so these are a public interface. Change them only on purpose and say so:

- **URL paths.** `analytics.js` picks the page type from the path with regexes: `/`, `/category/<cat>/`,
  `/<cat>/<product>/`, `/cart`, `/thank-you`.
- **Page `<title>`s**: Home, category name, product name, Checkout, Thank you.
- **Script order** in `base.html`: `analytics_items` / `analytics_value` / `window.clientId` are defined
  (via `{% block head_data %}`) **before** `analytics.js` loads.
- **DOM hooks**: `#cookie-banner`, `.cookie-banner`, `#analyticsToggle`, `#marketingToggle`, the banner
  `onclick` handlers, `#cart-count`. Link/button classes `next`, `cart`, `your-cart` and `checkout` may be
  used as GTM click triggers.
- **dataLayer events**: view_item_list, select_item, view_item, add_to_cart, begin_checkout, purchase (EUR).
- **`item_id`s are unique across categories.** The cart dedupes on `item_id`.
- **No third-party requests before consent.** Don't add Google Fonts, CDNs or external images. Use emoji
  or inline SVG for product images.

Known quirks the owner hasn't decided to change: `view_item` sends a hardcoded `value: 7.77`, and
`analytics.js` also sets a legacy `_ga_0MD7HEDQ3S` cookie. Ask before "fixing" them.

## Returning-user simulation

- On a browser's **first page view** (no `cookie_banner_loaded` and no `_ga` cookie), 40% of visitors get a
  previously saved GA client id. It's exposed as `window.clientId`, and `analytics.js` writes the `_ga*`
  cookies before GTM loads.
- After a visitor clicks **Allow All**, `/user_saved` stores their `_ga` and `_ga_<MEASUREMENT_ID>` cookies
  (max 1000 entries).
- The storage is `client_ids.json` in the GCS bucket named by `$BUCKET_NAME`. GCS errors are logged and
  swallowed, so pages never 500 because of storage.
- The GA4 measurement id is hardcoded in **both** `main.py` and `static/analytics.js`. Keep them in sync.

## Run locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python main.py          # http://localhost:8080
```

Without GCP credentials the returning-user feature just logs warnings. Everything else works.

## Deployment (Cloud Run)

The live site runs on Cloud Run, deployed from source. The project, region, service, bucket, runtime service
account and exact deploy command are in `.local/deploy.md`, which is gitignored (and listed in
`.gcloudignore`). Do not copy any of them into a tracked file: the GitHub repo is public.

- **Env vars:** `SECRET_KEY` (keeps carts stable across instances) and `BUCKET_NAME`.
- **Runtime service account** needs `roles/storage.objectAdmin` on the bucket.
- **Sizing:** scales to zero, max 2 instances, 512Mi. gunicorn runs with 1 worker and 8 threads. At 256Mi with
  2 workers it crash-looped.
- **Redeploy:** existing env vars are kept, so don't pass a new `SECRET_KEY` (that empties every cart).

### Access model (deliberate)

The service is **private**. Org policies (`constraints/run.managed.requireInvokerIam` plus domain-restricted
sharing) block `allUsers` and `--no-invoker-iam-check`. **Don't try to work around them.** That includes
moving the app to App Engine or another product to get public access.

- **Humans** view it through `gcloud run services proxy` on a local port (exact command in `.local/deploy.md`),
  then open the localhost address.
- **Scripts and scrapers** send `Authorization: Bearer $(gcloud auth print-identity-token)`. In Playwright,
  add the header only for the shop's host via `context.route()`, never to GTM or GA requests.
- **IAP was considered and rejected.** It would change the scraper's token requirements (it would need an
  IAP-specific token or a service account) for little gain. Don't enable it unless the owner asks.

## Working conventions

- Match the existing style: short functions, sparse comments, no type-hint or docstring sweeps.
- After changing templates or JS, click through home → category → product → add 2 different products →
  cart → checkout → thank-you, and check the dataLayer events in the browser console.
- Don't commit or deploy unless asked.
