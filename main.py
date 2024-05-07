from flask import Flask, render_template, session, redirect, url_for, request, jsonify, make_response
import os
import random
import json
from datetime import datetime, date, timedelta, timezone

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'a_default_secret_key')

products = {
    'electronics': [
        {'item_id': 1, 'item_name': 'Laptop', 'item_category': 'electronics', 'price': 800, 'quantity': 0, 'description': 'High-performance laptop.', 'image': 'url_to_image'},
        {'item_id': 2, 'item_name': 'Smartphone', 'item_category': 'electronics', 'price': 500, 'quantity': 0, 'description': 'Latest model smartphone.', 'image': 'url_to_image'},
    ],
    'clothing': [
        {'item_id': 1, 'item_name': 'T-Shirt', 'item_category': 'clothing', 'price': 20, 'quantity': 0, 'description': 'Cotton t-shirt.', 'image': 'url_to_image'},
        {'item_id': 2, 'item_name': 'Jeans', 'item_category': 'clothing', 'price': 40, 'quantity': 0, 'description': 'Denim jeans.', 'image': 'url_to_image'},
    ]
}


categories = products.keys()

# GA4 MEASUREMENT ID, needed to create cookies for simulation of returning users
GA_MEASUREMENT_ID = "1L1YW7SZFP";
# name of the file where client_ids are stored for simulation purposes
filename = 'client_ids.json'
# max number of client_ids that can be saved in the file
ids_max = 1000

ga_cookie_name = "_ga_"+GA_MEASUREMENT_ID;
client_ids = []

def load_client_ids():
    # Load client IDs from JSON file if it exists.
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

# Add a function to save the client IDs to the file when they're written after a request
def save_client_ids(client_ids):
    with open(filename, 'w') as f:
        json.dump(client_ids, f)

@app.before_request
def returning_user_setup():
    # the following cookie is set everytime consent.js loads (every page)
    cookie_banner = request.cookies.get('cookie_banner_loaded')
    # If request is an actual page request and this is the first page
    if request.endpoint != 'static' and cookie_banner is None:
        # decide if user is going to be new or returning   
        is_returning_user = random.random() < 0.5  # 50% chance
        client_id = None

        if is_returning_user:
            # if returning user, then get old ids from file and pick one to setup as a cookie
            # (hence simulating a returning user)
            client_ids = load_client_ids()
            if len(client_ids) > 0:
                client_id = random.choice(client_ids)

        if client_id:
            # if returning user and everything above went OK, set the cookies
            response = make_response(redirect(request.path))
            expiration_time = datetime.now(tz=timezone.utc) + timedelta(days=365)
            expiration = expiration_time.strftime('%a, %d-%b-%Y %H:%M:%S GMT')
            domain = request.host  # Extracts domain
            response.set_cookie('_ga', client_id["_ga"], expires=expiration, path='/', domain=domain)
            response.set_cookie(ga_cookie_name, client_id[ga_cookie_name], expires=expiration, path='/', domain=domain)
            response.set_cookie('cookie_consent', "111", expires=expiration, domain=domain)
            print(f"----- DEBUG- returning user branch: {client_id[ga_cookie_name]}")
            return response

@app.route('/user_saved')
def new_user_setup():
    print("-- DEBUG new_user_setup")
    # get the ga cookies
    response = make_response('', 204)
    ga_cookie = request.cookies.get('_ga') 
    ga_MID_cookie = request.cookies.get(ga_cookie_name)
    
    # if they exist, load client ids and check its length
    if ga_cookie and ga_MID_cookie:
        client_ids = load_client_ids()
        # if length is OK, push values in the file
        if len(client_ids) < ids_max:
            data_value = {'_ga': ga_cookie, ga_cookie_name: ga_MID_cookie}
            # if data_value is not empty and not already existing, write the new ID in the list
            if data_value and not any(data_value == existing for existing in client_ids):
                client_ids.append(data_value)
                save_client_ids(client_ids)  # Use the save function which handles file operation
                
                # Setting the 'user_saved' cookie to prevent re-execution
                # domain = request.host
                # response.set_cookie('user_saved', "1", max_age=31536000, path='/', domain=domain)  # Set for 1 year
                response.set_cookie('user_saved', "1", max_age=31536000, path='/')
                return response  # No content response

    return response  # No content response

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
    product_list = products[category]
    product = next((item for item in product_list if item["item_name"] == product_name), None)
    if product is None:
        abort(404)
    return render_template('product_detail.html', product=product, category=category)

from flask import jsonify, abort, session
import copy  # Import the copy module if you need deep copy

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


if __name__ == "__main__":
    # This is used when running locally only. 
    app.run(host="127.0.0.1", port=8080, debug=True)