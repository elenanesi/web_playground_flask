# Fairy Codemother Shop 🧚

A pretend online shop for safely testing analytics: GA4 ecommerce events, Google Tag Manager, cookie
consent (Consent Mode v2) and returning users. Nothing is real: no products, no payments, no customer data.

> Coding agents: read [AGENTS.md](AGENTS.md).

## See the website

The site runs on Google Cloud Run and is **private**: opening the URL directly gives a 403 "Forbidden" page.
To view it:

1. Sign in once: `gcloud auth login` (with an account that has invoker access to the service).
2. Start the proxy and leave it running:

   ```bash
   gcloud run services proxy <SERVICE> --region <REGION> --project <PROJECT> --port 9090
   ```
   The first time, say yes if it asks to install `cloud-run-proxy`. Ask the owner for the actual values.
3. Open http://localhost:9090. Stop the proxy with Ctrl+C.

## Use it for analytics testing

- Browse: home → category → product → **Add to Cart** → cart → **Proceed to Checkout** → thank-you page.
- Each step pushes a GA4 ecommerce event to the dataLayer (view_item_list, select_item, view_item,
  add_to_cart, begin_checkout, purchase). Check them in GTM Preview or with `dataLayer` in the browser console.
- The cookie banner offers **Allow All / Allow Selection / Deny All** and updates Consent Mode.
- **Returning users:** visitors who click Allow All get their GA ids saved. Some later first visits reuse
  them, so GA sees returning users.
- To use your own tags, change `GTM_ID` and `GA_MEASUREMENT_ID` in `static/analytics.js`, and
  `GA_MEASUREMENT_ID` in `main.py` too.

## User ID

- If the first-party cookie `fc_user_id` is set (opaque ID like `FC000123`), every page pushes
  `{user_id: <value>}` to the dataLayer before GTM loads; if absent, nothing is pushed.
- Manual GTM step: in GTM-WZ4DNGJW, add a Data Layer Variable named `user_id` and map it to the `user_id`
  field in the Google tag's (GA4 config tag's) configuration settings. Without this step, nothing reaches GA4.

## Scrapers and bots

Scripts can't use the proxy's `localhost` address cleanly (GA would record `localhost`). Instead, send a
Google identity token on requests to the shop:

```
Authorization: Bearer <output of: gcloud auth print-identity-token>
```

Tokens last about one hour. In Playwright, add the header only for the shop's address, so GA requests stay untouched.

## Why it isn't public, and why we don't use IAP

- **Not public:** the organization's Google Cloud policies don't allow anonymous access to Cloud Run services.
  We respect that rather than working around it, and the proxy plus tokens cover what we need.
- **No IAP (Google login screen in front of the site):** it would let people open the URL in a browser, but it
  changes how scripts must authenticate (they'd need an IAP-specific token or a service account). The proxy
  is simpler and keeps the scraper setup as it is.

## Run it on your own computer

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

Then open http://localhost:8080. The returning-user feature needs Google Cloud access; without it everything
else still works.

## Deploy changes

- The live site is deployed to Cloud Run from source (`Procfile` + `requirements.txt`). `app.yaml` is a
  legacy App Engine config and is not used.
- The project, region, service, bucket and exact deploy command live in `.local/deploy.md`, which is
  gitignored. Do not copy them into the repo.
- Required env vars: `SECRET_KEY` and `BUCKET_NAME`. They are kept from the previous deploy, so a redeploy
  doesn't need to pass them again.
- `SECRET_KEY` must stay the same across deploys/instances, otherwise every visitor's cart is emptied.
- The Cloud Run service account needs `roles/storage.objectAdmin` on the bucket.
