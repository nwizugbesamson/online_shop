from flask import Blueprint, redirect, render_template, request, url_for, abort
from project.models import User, Cart, Product, Review, Like
from project.forms import CartForm, ReviewForm, ProductForm
from flask_login import current_user, login_required
from project import db
from functools import wraps
import stripe
import numpy as np
import os

main = Blueprint(name="main", import_name=__name__, static_folder="static", template_folder="templates")



stripe.api_key = os.getenv('API_KEY')

base_url = "http://localhost:5000"

def create_product_list(product_dict):
    item_list = []
    for key, value in product_dict.items():
        item_dict = {
            
            "price_data":{
                "currency": "usd",
                "product_data":{
                    "name": value.name,
                    "images":[value.img_url],
                },
                "unit_amount": int(value.price * 100),

            },
            "quantity": int(key // value.price)

        }
        item_list.append(item_dict)
   
    return item_list



def get_customer_cart():
    id_products = current_user.get_cart_products()
   
    id_products = np.array(id_products)

    uniques, counts = np.unique(id_products, return_counts=True)
    uniques = list(uniques)
    counts = list(counts)
    counts = map(int, counts)
    setattr(current_user, "bill", 0.0)
    uniques = [Product.query.get(int(_id)) for _id in uniques]
    
    product_dict = {count*prod.price: prod for count, prod in zip(counts, uniques)}
    bill = 0
    for key, value in product_dict.items():
        bill += key
    setattr(current_user, "bill", bill)
   
    return product_dict

# ADMIN REQUIRED FUNCTION
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@main.route('/')
def home_page():
    page = request.args.get("page", default=1, type=int)
    products = Product.query.paginate(per_page=10, page=page)
    return render_template("index.html", products=products)




@main.route('/product/<int:product_id>', methods=['GET', 'POST'])
@main.route('/product/<int:product_id>/<action>', methods=['GET', 'POST'])
def product_page(product_id, action=None):
    form = CartForm()
    rev_form = ReviewForm()
    product = Product.query.get(product_id)
    reviews = Review.query.filter_by(product_id=product_id)
    if current_user.is_authenticated:
        if form.validate_on_submit():
            quantity = form.quantity.data
            for i in range(0, quantity):
                cart_item = Cart(
                                    user_id=current_user.id,
                                    product_id=product_id
                                )
                db.session.add(cart_item)
                db.session.commit()
            return redirect(request.referrer)
        if action == 'review':
            if rev_form.validate_on_submit():
                new_review = Review(
                    comment=rev_form.review.data,
                    user_id=current_user.id,
                    product_id=product_id
                )
                db.session.add(new_review)
                db.session.commit()
                return redirect(request.referrer)
    return render_template("single-product.html", product=product, form=form, rev_form=rev_form, reviews=reviews)



@main.route('/add_cart/<int:product_id>')
@login_required
def add_cart(product_id):
    cart_item = Cart(
        user_id=current_user.id,
        product_id=product_id
    )
    db.session.add(cart_item)
    db.session.commit()
    return redirect(request.referrer)


@main.route('/add_product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product_page():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
        )
        for key, value in form.data.items():
            if key in Product.__table__.columns:
                setattr(new_product, key, value)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('main.home_page'))
    return render_template('add-product.html', form=form)



@main.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product_page(product_id):
    form = ProductForm()
    product = Product.query.get(product_id)
    form.name.data = product.name
    form.description.data = product.description
    form.img_url.data = product.img_url
    form.price.data = product.price
    if form.validate_on_submit():
        for key, value in form.data.items():
            if key in Product.__table__.columns:
                setattr(product, key, value)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('main.home_page'))
    return render_template('add-product.html', form=form)



@main.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_product_page(product_id):
    Product.query.get(product_id).delete()
    db.session.commit()
    return redirect(url_for('main.home_page'))



@main.route('/like_action/<action>/<int:product_id>')
@login_required
def like_action(action, product_id ):
    product = Product.query.get(product_id)
    if action == "like":
        current_user.like_product(product)

    if action == "unlike":
        current_user.unlike_product(product)
       

    return redirect(request.referrer)


@main.route('/cart')
@login_required
def cart_page():
    product_dict = get_customer_cart()
    return render_template('cart.html', product_dict=product_dict)



@main.route('/item_cart_delete/<int:product_id>')
@login_required
def cart_item_delete_page(product_id):
    current_user.delete_cart_product(product_id)
    return redirect(request.referrer)


@main.route('/check_out', methods=['GET', 'POST'])
@login_required
def create_checkout_session():
 
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=create_product_list(get_customer_cart()),
            mode='payment',
            success_url=base_url + '/success',
            cancel_url=base_url + '/cancel',
        )
    except Exception as e:
        return str(e)
        
     
    return redirect(checkout_session.url, code=303)


@main.route('/success')
@login_required
def success_page():
    # code to send mail to fufill customer orders
    Cart.query.filter_by(
            user_id=current_user.id
        ).delete()
    db.session.commit()
    return render_template('success.html')


@main.route('/cancel')
@login_required
def cancel_page():
    
    return render_template('cancel.html')
