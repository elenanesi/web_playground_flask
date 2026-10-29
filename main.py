# local version
from flask import Flask, render_template, session, redirect, url_for, request, jsonify, make_response, g, Response, abort
import os
import random
import json
from datetime import datetime, date, timedelta, timezone
from flask import jsonify, abort, session
import copy 

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
        {'item_id': 1, 'item_name': 'T-Shirt', 'item_category': 'clothing', 'price': 20, 'quantity': 1, 'description': 'Cotton t-shirt.', 'image': '👕'},
        {'item_id': 2, 'item_name': 'Jeans', 'item_category': 'clothing', 'price': 40, 'quantity': 1, 'description': 'Denim jeans.', 'image': '👖'},
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

category_icons = {
    'electronics': '💻',
    'clothing': '👕',
    'home': '🏠',
    'beauty': '💄',
    'sports': '⚽',
}


categories = products.keys()

# GA4 MEASUREMENT ID, needed to create cookies for simulation of returning users
GA_MEASUREMENT_ID = "0MD7HEDQ3S";
# name of the file where client_ids are stored for simulation purposes
filename = 'client_ids.json'
# max number of client_ids that can be saved in the file
ids_max = 1000

ga_cookie_name = "_ga_"+GA_MEASUREMENT_ID;
client_ids = []

def load_client_ids(filename):
    # Load client IDs from JSON file if it exists.
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

# Add a function to save the client IDs to the file when they're written after a request
def save_client_ids(client_ids, filename):
    with open(filename, 'w') as f:
        json.dump(client_ids, f)

@app.before_request
def returning_user_setup():
    # the following cookie is set everytime consent.js loads (every page)
    cookie_banner = request.cookies.get('cookie_banner_loaded')
    print("Hello Ele, I'm returning_user_setup")
    # If request is an actual page request and this is the first page
    if request.endpoint != 'static' and cookie_banner is None:
        # decide if user is going to be new or returning   
        is_returning_user = random.random() < 0.4  # 40% chance
        print("User returning is: ", is_returning_user)
        client_id = None

        if is_returning_user:
            print("-- DEBUG returning_user_setup")
            # if returning user, then get old ids from file and pick one to setup as a cookie
            # (hence simulating a returning user)
            client_ids = load_client_ids(filename)
            if client_ids:
                client_id = random.choice(client_ids)
                if client_id:     
                    # make client_id available under window 
                    # so analytics.js can use it to set a cookie before GA library loads
                    g.client_id = client_id

@app.route('/user_saved')
def new_user_setup():
    # used to populate client_ids.json
    print("-- DEBUG new_user_setup")
    # get the ga cookies
    response = make_response('', 204)
    ga_cookie = request.cookies.get('_ga') 
    ga_MID_cookie = request.cookies.get(ga_cookie_name)
    
    # if they exist, load client ids and check its length
    if ga_cookie and ga_MID_cookie:
        client_ids = load_client_ids(filename)
        # if length is OK, push values in the file
        if len(client_ids) < ids_max:
            data_value = {'_ga': ga_cookie, ga_cookie_name: ga_MID_cookie}
            # if data_value is not empty and not already existing, write the new ID in the list
            if data_value and not any(data_value == existing for existing in client_ids):
                client_ids.append(data_value)
                save_client_ids(client_ids, filename)  # Use the save function which handles file operation
                
                # Setting the 'user_saved' cookie to prevent re-execution
                # domain = request.host
                # response.set_cookie('user_saved', "1", max_age=31536000, path='/', domain=domain)  # Set for 1 year
                response.set_cookie('user_saved', "1", max_age=31536000, path='/')
                return response  # No content response

    return response  # No content response

@app.route('/')
def home():
    return render_template('home.html', categories=categories, category_icons=category_icons)

@app.route('/category/<category>/')
def show_category(category):
    if category not in categories:
        abort(404)
    return render_template('category.html', category=category, products=products[category], category_icons=category_icons)

@app.route('/<category>/<product_name>/')
def product_detail(category, product_name):
    if category not in categories:
        abort(404)
    product_list = products[category]
    product = next((item for item in product_list if item["item_name"] == product_name), None)
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
    
    if 'cart' not in session:
        session['cart'] = []
    
    # Create a copy of the product to work with
    aux = product.copy()  # This creates a shallow copy of the product dictionary
    
    # Initialize quantity for the copy if adding to cart for the first time
    aux['quantity'] = 1  # Set quantity to 1 for the new item

    # Check if the product is already in the cart
    found = False
    for cart_item in session['cart']:
        if cart_item['item_id'] == aux["item_id"]:  # Assuming item_id is unique and exists
            cart_item['quantity'] += 1
            found = True
            break
    
    if not found:
        session['cart'].append(aux)  # Append the copy, not the original
    
    session.modified = True
    return jsonify({'status': 'success', 'message': 'Product added to cart'})



@app.route('/empty_cart')
def empty_cart():
    if 'cart' not in session:
        return redirect(url_for('show_cart'))
    else:
        session['cart'] = []
        session.modified = True
        return redirect(url_for('show_cart'))

@app.route('/cart')
def show_cart():
    cart_items = session.get('cart', [])
    total_price = 0
    for cart_item in cart_items:
        product = next(item for category, items in products.items() for item in items if item["item_name"] == cart_item['item_name'])

        total_price += product['price'] * cart_item['quantity']
    
    return render_template('cart.html', cart=cart_items, total_price=total_price)


@app.route('/checkout', methods=['POST'])
def checkout():
    # Ensure the cart is treated as a dictionary here as well
    cart_items = session.pop('cart', {})
    session['purchased_items'] = cart_items  # Directly assign the dictionary
    return redirect(url_for('thank_you'))


@app.route('/thank-you')
def thank_you():
    purchased_items = session.pop('purchased_items', [])
    total_price = 0
    for purchase_item in purchased_items:
        product = next(item for category, items in products.items() for item in items if item["item_name"] == purchase_item['item_name'])

        total_price += product['price'] * purchase_item['quantity']
    return render_template('thank_you.html', purchased_items=purchased_items, total_price=total_price)

@app.route('/sitemap.xml')
# NOTE: change "localhost:8080 in the sitemap.xml file under /templates with your own domain"
def sitemap():
    return Response(render_template('sitemap.xml'), mimetype='application/xml')

@app.route('/sitemap-products.xml')
# NOTE: change "localhost:8080 in the code below with your own domain"
def sitemap_products():
    product_urls = []
    for category, items in products.items():
        for item in items:
            product_urls.append(f"http://localhost:8080/{category}/{item['item_name']}/")
    return Response(render_template('sitemap_products.xml', products=product_urls), mimetype='application/xml')

@app.route('/sitemap-product-categories.xml')
# NOTE: change "localhost:8080 in the code below with your own domain"
def sitemap_product_categories():
    category_urls = [f"http://localhost:8080/category/{category}/" for category in categories]
    return Response(render_template('sitemap_product_categories.xml', categories=category_urls), mimetype='application/xml')

@app.route('/sitemap-others.xml')
# NOTE: change "localhost:8080 in the code below with your own domain"
# NOTE: change others with the other URLs you want to include there"
def sitemap_others():
    others = [
        'http://localhost:8080/'
    ]
    return Response(render_template('sitemap_others.xml', others=others), mimetype='application/xml')

if __name__ == "__main__":
    # This is used when running locally only. 
    app.run(host="127.0.0.1", port=8080, debug=True)
