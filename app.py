import sys
import json
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import Form
from models import db_init, Vegetable, User, Order, OrderDetails, Apartment, Category, Stock, Testimonial, Role, UserRoles
import maya
from shortid import ShortId
from flask_login import LoginManager, UserMixin, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_user import roles_required, UserManager, current_user
from flask_babelex import Babel

app = Flask(__name__)
db = db_init(app)
app.secret_key = 'abcd1234567890'
date = maya.now().add(days=3).slang_date()
babel = Babel(app)
sid = ShortId()
login_manager = LoginManager()
login_manager.init_app(app)
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

admin = Admin(app, name='NimbleBuy Admin', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Order, db.session))
admin.add_view(ModelView(OrderDetails, db.session))
admin.add_view(ModelView(Vegetable, db.session))
admin.add_view(ModelView(Apartment, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Stock, db.session))
admin.add_view(ModelView(Testimonial, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(UserRoles, db.session))


user_manager = UserManager(app, db, User)

class MuModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def mergeDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items())+ list(dict2.items))

# LOGIN / REGISTER ------------------------------------------------------------------------------------------------------

# GET Login page route
@app.route('/login', methods=['GET'])
def login_page():
    if 'user' not in session:
        return render_template('login.html')
    else : return redirect(url_for('about_page'))

# POST Lofin user route
@app.route('/login', methods=['POST'])
def login():
    data = request.form.to_dict()
    try:
        user = User.query.filter_by(email=data['email']).first()
        print(user.format())
        if user.password == data['password']:
            session['user'] = user.format()
            return redirect(url_for('index'))
    except Exception as e:
        print(f'Error ==> {e}')
        return render_template('login.html')

# POST Register new user route
@app.route('/register', methods=['POST'])
def login_register():
    data = request.form.to_dict()
    apt_name = data['apt_name']
    apt = Apartment.query.filter(Apartment.name.ilike(f'%{apt_name}%')).first()
    user = User(email=data['email'], apt=data['apt'], fname=data['name'], phone=data['phone'], password=data['password'], apartment=apt)
    user.insert()
    if 'apt' in data:
        session['user'] = user.format()
        return redirect(url_for('about_page'))
    else: return redirect(url_for('login_page', data='Please Fill Everything'))

# Logout user route
@app.route('/logout')
def logout_user():
    if 'user' in session:
        session.pop('apt', None)
        session.pop('user', None)
        session.pop('cart_items', None)
        return redirect(url_for('about_page'))
    else: return redirect(url_for('login_page'))

# -----------------------------------------------------------------------------------------------------------------------
    

# HOME / ABOUT ------------------------------------------------------------------------

# Home route
@app.route('/')
def index():
    if "user" in session:
        response = [item.format() for item in Vegetable.query.all()]
        return render_template('shop.html', vegetables=response, date=date)
    else: return redirect(url_for('login_page'))

# Endpoint to get all vegetables as JSON
@app.route('/vegetables', methods=['GET'])
def get_veggies():
    response = [item.format() for item in Vegetable.query.all()]

    return jsonify(response)

# About page route
@app.route('/about')
def about_page():
    return render_template('about.html', date=date)

# -----------------------------------------------------------------------------

# CART / CHECKOUT --------------------------------------------------------------------------

# GET Cart Route
@app.route('/cart', methods=['GET'])
def checkout():
    if 'user' in session:
        if 'cart_items' in session:
            subtotal = 0
            for product in session['cart_items']:
                subtotal += float(product['price']) * float(product['qty'])
            return render_template('checkout.html', subtotal=subtotal)
        else: return redirect(request.referrer)
    else: return redirect(url_for('login_page'))

# POST Add to Cart
@app.route('/cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    try:
        if 'user' in session:
            veg = Vegetable.query.get(product_id).format()
            veg['qty'] = 1
            new_item = [veg]
            if 'cart_items' in session:
                if product_id in session['cart_items']:
                    print('Item already in cart!')
                else:
                    session['cart_items'] = mergeDicts(session['cart_items'], new_item)
                    return redirect(request.referrer)
            else:
                session['cart_items'] = new_item
                return redirect(request.referrer)
    except Exception as e:
        print(f'Error ==> {e}')
    finally:
        return redirect(request.referrer)

# POST Delete Cart Item
@app.route('/cart/delete/<int:product_id>', methods=['POST'])
def delete_item_in_cart(product_id):
    if 'user' not in session and 'cart_item' not in session and len(session['cart_items'] <=0):
        return redirect(url_for('get_veggies'))
    try:
        session.modified = True
        arr = session['cart_items']
        arr[:] = [d for d in arr if d.get('id') != product_id]
        session['cart_items'] = arr
        return redirect(url_for('checkout'))

    except Exception as e:
        return redirect(url_for('checkout'))
        print(f'Error ==> {e}')

# UPDATE Cart Item
@app.route('/updatecart/<int:product_id>')
def update_cart(product_id):
    if 'cart_items' not in session and len(session['cart_items']) <= 0:
        return redirect(url_for('checkout'))
    else:
        qty = request.args.get('qty')
        try:
            session.modified = True
            for item in session['cart_items']:
                if item['id'] == product_id:
                    item['qty'] = qty
                    flash('Item was updated')
                    return redirect(url_for('checkout'))
        except Exception as e:
            print(f'Error ==> {e}')
            return redirect(url_for('checkout'))

# POST Create the order
@app.route('/create-order', methods=['POST'])
def create_order():
    try:
        subtotal = 0
        for product in session['cart_items']:
            subtotal += float(product['price']) * float(product['qty'])
        session['subtotal'] = subtotal
        customer = User.query.get(int(session['user']['id']))
        order = Order(customer=customer, order_number=sid.generate(), order_date=date, order_total=subtotal)
        order.insert()
        for product in session['cart_items']:
            ordered_item = Vegetable.query.get(int(product['id']))
            order_details = OrderDetails(ordered_item=ordered_item, order=order, price=product['price'], qty=product['qty'], total=subtotal)
            order_details.insert()
        session.pop('cart_items', None)
        return redirect(url_for('order_confirm', isOrderSuccess=True))

    except Exception as e:
        print(f'Error ==> {e}')
        return 'Failed'

# Order Confirmation page route
@app.route('/confirmation')
def order_confirm():
    if 'user' in session:
        if 'subtotal' in session:
            return render_template('confirmation.html')
        else : return redirect(request.referrer)

#  ----------------------------------------------------------------------------------------------------------------------------------------------

# ADMIN -----------------------------------------------------------------------------------------------------------------------------------------

def import_db():
    import data
    for item in data.data:
        veg = Vegetable(category_id=item['category_id'], image=item['image'], k_name=item['k_name'], name=item['name'], onSale=bool(item['onSale']), price=item['price'], unit=item['unit'])
        veg.insert()

def get_stock():
    try:
        inventory = [{**(item.format()), **({ 'stock' : 0 })} for item in Vegetable.query.all()]
        order_details = OrderDetails.query.all()
        items_ordered = [detail.format() for detail in order_details]
        for product in inventory:
            for item in items_ordered:
                if product['id'] == item['product_id']:
                    product['stock'] = product.get('stock') + float(item['qty'])
        return inventory
    except Exception as e:
        print(f'Error ==> {e}')
        return 'Nothing'

@app.route('/stock')
# @roles_required('Admin')
def getInventory():
    try:
        inventory = [{**(item.format()), **({ 'stock' : 0 })} for item in Vegetable.query.all()]
        order_details = OrderDetails.query.all()
        items_ordered = [detail.format() for detail in order_details]
        for product in inventory:
            for item in items_ordered:
                if product['id'] == item['product_id']:
                    product['stock'] = product.get('stock') + float(item['qty'])
        return jsonify(inventory)
    except Exception as e:
        print(f'Error ==> {e}')
        return 'Nothing'

# GET Admin page route
@app.route('/admin_orders')
# @roles_required('Admin')
def sample_route():
    response = []
    try:
        users = User.query.all()
        for user in users:
            orders = user.orders
            if len(orders) > 0:
                order_details = [order.order_details for order in orders]
                items_ordered = [{**(detail.format()), **(Vegetable.query.get(detail.product_id).format())} for detail in order_details[0]]
                response.append({
                    'customer': {**(user.format()), **(user.apartment.format())},
                    'order': [order.format() for order in user.orders],
                    'order_details': items_ordered,
                    'order_total': items_ordered[0].get('total', 0)
                })
            else: continue
        return render_template('admin_orders.html', data=response, stock=get_stock())
        # return jsonify(response)

    except Exception as e:
        print(f'error ==> {e}')
        return 'Nothing'
    
# -----------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run()
