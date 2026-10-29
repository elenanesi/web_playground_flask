from flask import Flask, render_template, session, redirect, url_for, request, jsonify, make_response, g, Response, abort
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import random
import json
from google.cloud import storage


app = Flask(__name__)
# Must be stable across workers/instances, otherwise the session (cart) gets lost
app.secret_key = os.environ.get('SECRET_KEY', 'local-dev-only-secret')
# Cloud Run sits behind a proxy: trust X-Forwarded-* so url_for(_external=True) emits https
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# item_id must be unique across categories: the cart dedupes on it
products = {
    'electronics': [
        {'item_id': 1, 'item_name': 'Laptop', 'item_category': 'electronics', 'price': 800, 'quantity': 1, 'description': 'High-performance laptop.', 'image': '💻'},
        {'item_id': 2, 'item_name': 'Smartphone', 'item_category': 'electronics', 'price': 500, 'quantity': 1, 'description': 'Latest model smartphone.', 'image': '📱'},
        {'item_id': 3, 'item_name': 'Earbuds', 'item_category': 'electronics', 'price': 45, 'quantity': 1, 'description': 'Wireless earbuds with charging case.', 'image': '🎧'},
        {'item_id': 4, 'item_name': 'Charger', 'item_category': 'electronics', 'price': 18, 'quantity': 1, 'description': 'Fast USB-C wall charger.', 'image': '🔌'},
        {'item_id': 5, 'item_name': 'Monitor', 'item_category': 'electronics', 'price': 240, 'quantity': 1, 'description': '27-inch full HD monitor.', 'image': '🖥️'},
        {'item_id': 6, 'item_name': 'Tablet', 'item_category': 'electronics', 'price': 55, 'quantity': 1, 'description': 'Compact tablet for reading and browsing.', 'image': '📲'},
    ],
    'clothing': [
        {'item_id': 25, 'item_name': 'TShirt', 'item_category': 'clothing', 'price': 20, 'quantity': 1, 'description': 'Cotton t-shirt.', 'image': '👕'},
        {'item_id': 26, 'item_name': 'Jeans', 'item_category': 'clothing', 'price': 40, 'quantity': 1, 'description': 'Denim jeans.', 'image': '👖'},
        {'item_id': 7, 'item_name': 'Socks', 'item_category': 'clothing', 'price': 6, 'quantity': 1, 'description': 'Soft cotton socks.', 'image': '🧦'},
        {'item_id': 8, 'item_name': 'Jacket', 'item_category': 'clothing', 'price': 95, 'quantity': 1, 'description': 'Water-resistant everyday jacket.', 'image': '🧥'},
        {'item_id': 9, 'item_name': 'Sneakers', 'item_category': 'clothing', 'price': 120, 'quantity': 1, 'description': 'Lightweight running sneakers.', 'image': '👟'},
        {'item_id': 10, 'item_name': 'Watch', 'item_category': 'clothing', 'price': 900, 'quantity': 1, 'description': 'Stainless steel luxury watch.', 'image': '⌚'},
    ],
    'home': [
        {'item_id': 11, 'item_name': 'Mug', 'item_category': 'home', 'price': 8, 'quantity': 1, 'description': 'Ceramic coffee mug.', 'image': '☕'},
        {'item_id': 12, 'item_name': 'Towel', 'item_category': 'home', 'price': 14, 'quantity': 1, 'description': 'Absorbent bath towel.', 'image': '🛁'},
        {'item_id': 13, 'item_name': 'Blender', 'item_category': 'home', 'price': 55, 'quantity': 1, 'description': 'Countertop blender for smoothies.', 'image': '🥤'},
        {'item_id': 14, 'item_name': 'Lamp', 'item_category': 'home', 'price': 38, 'quantity': 1, 'description': 'Warm-light desk lamp.', 'image': '💡'},
        {'item_id': 15, 'item_name': 'Sofa', 'item_category': 'home', 'price': 1200, 'quantity': 1, 'description': 'Three-seater fabric sofa.', 'image': '🛋️'},
    ],
    'beauty': [
        {'item_id': 16, 'item_name': 'Lipstick', 'item_category': 'beauty', 'price': 12, 'quantity': 1, 'description': 'Long-lasting matte lipstick.', 'image': '💄'},
        {'item_id': 17, 'item_name': 'Shampoo', 'item_category': 'beauty', 'price': 9, 'quantity': 1, 'description': 'Gentle daily shampoo.', 'image': '🧴'},
        {'item_id': 18, 'item_name': 'Perfume', 'item_category': 'beauty', 'price': 85, 'quantity': 1, 'description': 'Floral eau de parfum.', 'image': '🌸'},
        {'item_id': 19, 'item_name': 'SkinSerum', 'item_category': 'beauty', 'price': 150, 'quantity': 1, 'description': 'Hydrating vitamin C face serum.', 'image': '💧'},
    ],
    'sports': [
        {'item_id': 20, 'item_name': 'YogaMat', 'item_category': 'sports', 'price': 25, 'quantity': 1, 'description': 'Non-slip yoga mat.', 'image': '🧘'},
        {'item_id': 21, 'item_name': 'Dumbbell', 'item_category': 'sports', 'price': 35, 'quantity': 1, 'description': 'Adjustable hand dumbbell.', 'image': '🏋️'},
        {'item_id': 22, 'item_name': 'Cleats', 'item_category': 'sports', 'price': 60, 'quantity': 1, 'description': 'Football cleats for firm ground.', 'image': '⚽'},
        {'item_id': 23, 'item_name': 'Treadmill', 'item_category': 'sports', 'price': 280, 'quantity': 1, 'description': 'Foldable home treadmill.', 'image': '🏃'},
        {'item_id': 24, 'item_name': 'Bicycle', 'item_category': 'sports', 'price': 550, 'quantity': 1, 'description': 'Aluminium city bicycle.', 'image': '🚲'},
    ],
}

categories = products.keys()
category_icons = {
    'electronics': '💻',
    'clothing': '👕',
    'home': '🏠',
    'beauty': '💄',
    'sports': '⚽',
}

# GA4 MEASUREMENT ID, needed to create cookies for simulation of returning users
GA_MEASUREMENT_ID = "1L1YW7SZFP"
# GCS location where client_ids are stored for simulation purposes
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'returning_user_simulation')
BLOB_NAME = 'client_ids.json'
# max number of client_ids that can be saved in the file
ids_max = 1000
# share of first-time visitors that get turned into a "returning" user
RETURNING_USER_RATE = 0.4
# pages where the returning user simulation can kick in
PAGE_ENDPOINTS = {'home', 'show_category', 'product_detail', 'show_cart', 'thank_you'}

ga_cookie_name = "_ga_" + GA_MEASUREMENT_ID


def _blob():
    return storage.Client().bucket(BUCKET_NAME).blob(BLOB_NAME)

def load_client_ids():
    # Never break the page if GCS is unreachable: just simulate no returning users
    try:
        blob = _blob()
        if blob.exists():
            return json.loads(blob.download_as_bytes())
    except Exception as e:
        app.logger.warning("Could not load client ids: %s", e)
    return []

def save_client_ids(client_ids):
    try:
        _blob().upload_from_string(json.dumps(client_ids), content_type="application/json")
    except Exception as e:
        app.logger.warning("Could not save client ids: %s", e)


@app.before_request
def returning_user_setup():
    # Decide once per browser (on its first page view) whether to simulate a returning user.
    # Skip visitors that already have a real GA cookie, so we don't overwrite their identity.
    if (request.endpoint not in PAGE_ENDPOINTS
            or request.cookies.get('cookie_banner_loaded')
            or request.cookies.get('_ga')):
        return
    g.first_page_view = True
    if random.random() < RETURNING_USER_RATE:
        client_ids = load_client_ids()
        if client_ids:
            # exposed as window.clientId, so analytics.js sets the GA cookies before GTM loads
            g.client_id = random.choice(client_ids)

@app.after_request
def mark_visitor_seen(response):
    if g.get('first_page_view'):
        response.set_cookie('cookie_banner_loaded', '1', max_age=31536000, path='/')
    return response

@app.route('/user_saved')
def new_user_setup():
    # used to populate client_ids.json with the GA cookies of consenting visitors
    response = make_response('', 204)
    ga_cookie = request.cookies.get('_ga')
    ga_MID_cookie = request.cookies.get(ga_cookie_name)

    if ga_cookie and ga_MID_cookie:
        client_ids = load_client_ids()
        if len(client_ids) < ids_max:
            data_value = {'_ga': ga_cookie, ga_cookie_name: ga_MID_cookie}
            if data_value not in client_ids:
                client_ids.append(data_value)
                save_client_ids(client_ids)
                # Setting the 'user_saved' cookie to prevent re-execution
                response.set_cookie('user_saved', "1", max_age=31536000, path='/')

    return response

@app.route('/')
def home():
    return render_template('home.html', categories=categories)

@app.route('/category/<category>/')
def show_category(category):
    if category not in categories:
        abort(404)
    return render_template('category.html', category=category, products=products[category])

@app.route('/<category>/<product_name>/')
def product_detail(category, product_name):
    if category not in categories:
        abort(404)
    product = next((item for item in products[category] if item["item_name"] == product_name), None)
    if product is None:
        abort(404)
    return render_template('product_detail.html', product=product, category=category)

@app.route('/add_to_cart/<category>/<product_name>', methods=['POST'])
def add_to_cart(category, product_name):
    if category not in categories:
        return jsonify({'status': 'error', 'message': 'Category not found'}), 404
    product = next((item for item in products[category] if item["item_name"] == product_name), None)
    if product is None:
        return jsonify({'status': 'error', 'message': 'Product not found'}), 404

    cart = session.setdefault('cart', [])
    for cart_item in cart:
        if cart_item['item_id'] == product['item_id']:
            cart_item['quantity'] += 1
            break
    else:
        cart.append({**product, 'quantity': 1})

    session.modified = True
    return jsonify({'status': 'success', 'message': 'Product added to cart', 'cart_count': cart_count(cart)})

def cart_total(items):
    return sum(item['price'] * item['quantity'] for item in items)

def cart_count(items):
    return sum(item['quantity'] for item in items)

@app.context_processor
def inject_globals():
    # used by the shared header in base.html
    return {'cart_count': cart_count(session.get('cart', [])), 'nav_categories': categories, 'category_icons': category_icons}

@app.route('/empty_cart')
def empty_cart():
    session['cart'] = []
    return redirect(url_for('show_cart'))

@app.route('/cart')
def show_cart():
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart=cart_items, total_price=cart_total(cart_items))

@app.route('/checkout', methods=['POST'])
def checkout():
    session['purchased_items'] = session.pop('cart', [])
    return redirect(url_for('thank_you'))

@app.route('/thank-you')
def thank_you():
    purchased_items = session.pop('purchased_items', [])
    return render_template('thank_you.html', purchased_items=purchased_items, total_price=cart_total(purchased_items))

@app.route('/sitemap.xml')
def sitemap():
    return Response(render_template('sitemap.xml'), mimetype='application/xml')

@app.route('/sitemap-products.xml')
def sitemap_products():
    product_urls = [url_for('product_detail', category=category, product_name=item['item_name'], _external=True)
                    for category, items in products.items() for item in items]
    return Response(render_template('sitemap_products.xml', products=product_urls), mimetype='application/xml')

@app.route('/sitemap-product-categories.xml')
def sitemap_product_categories():
    category_urls = [url_for('show_category', category=category, _external=True) for category in categories]
    return Response(render_template('sitemap_product_categories.xml', categories=category_urls), mimetype='application/xml')

@app.route('/sitemap-others.xml')
# NOTE: add here any other URLs you want to include
def sitemap_others():
    others = [url_for('home', _external=True)]
    return Response(render_template('sitemap_others.xml', others=others), mimetype='application/xml')

if __name__ == "__main__":
    # This is used when running locally only.
    app.run(host="127.0.0.1", port=int(os.environ.get('PORT', 8080)), debug=True)
