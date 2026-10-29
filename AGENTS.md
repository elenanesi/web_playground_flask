# AGENTS.md

## Analytics contract

**Page-type detection** (`static/analytics.js`, tested on the URL path in this order, first match wins):

1. `/^\/$/` → home
2. `/cart/` → checkout
3. `/thank/` → purchase
4. `/\/category/` → product list
5. `/\/\w+\/\w+(\/)?/` → product detail (`/<category>/<item_name>/`)

**Naming rule:** category and product names become URL path segments, so they must be single tokens (`[A-Za-z0-9_]+`, no spaces or hyphens) and must never contain `cart`, `thank` or `category` (any case).

**`products` dict** (`main.py`): `{category: [ {item_id, item_name, item_category, price, quantity, description, image}, ... ]}`

- `item_id` must be globally unique across the whole dict, not just per category.
- `image` is a single emoji character, never a URL (no cross-host image loads).
- Every category needs a matching entry in `category_icons`.

**`fc_user_id` cookie:** first-party cookie set by the external simulator, with opaque values like `FC000123` (never emails or PII). Read client-side only. When set, every page pushes `{user_id: <value>}` to `dataLayer` before GTM loads; when absent, nothing is pushed (never an empty string or `"null"`).

## Redeploy

Runs on Google App Engine (`app.yaml`). Redeploy with:

```
gcloud app deploy
```
