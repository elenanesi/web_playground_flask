from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import os


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
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)