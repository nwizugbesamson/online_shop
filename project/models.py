from enum import unique
from sqlalchemy import ForeignKey
from project import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship



class User(UserMixin, db.Model):

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    bill = db.Column(db.Float, unique=False, nullable=False)
    reviews = relationship("Review", back_populates="user") 

    liked = db.relationship(
        "Like", 
        foreign_keys="Like.user_id",
        backref="user"   
    )

    def like_product(self, product):
        if not self.has_liked_product(product):
            like = Like(
                user_id = self.id,
                product_id = product.id
            )
            db.session.add(like)
            db.session.commit()

    
    def unlike_product(self, product):
        if self.has_liked_product(product):
            Like.query.filter_by(
                user_id = self.id,
                product_id = product.id 
            ).delete()
            db.session.commit()


    def has_liked_product(self, product):
        return Like.query.filter_by(
            user_id = self.id,
            product_id = product.id
        ).count() > 0


    user_cart = db.relationship(
        "Cart",
        foreign_keys="Cart.user_id",
        backref="user"
    )

    def get_cart_products(self):
        cart_products = Cart.query.filter_by(
            user_id=self.id
        )
        if cart_products:
            cart_products = [prod.product_id for prod in cart_products ]
        return cart_products

    def delete_cart_product(self, product_id):
        Cart.query.filter_by(
            user_id=self.id,
            product_id=product_id
        ).delete()



class Product(db.Model):

    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(150), unique=True, nullable=False)
    img_url = db.Column(db.String(400), unique=False, nullable=False)
    price = db.Column(db.Float, unique=False, nullable=False)
    description = db.Column(db.String(600), unique=False, nullable=False)
    
    likes = relationship("Like", back_populates="product")
    reviews = relationship("Review", back_populates="product")

   



class Cart(db.Model):

    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))






class Review(db.Model):

    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    comment = db.Column(db.String(400), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")



class Like(db.Model):

    __tablename__ = "like"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))

    product = relationship("Product", back_populates="likes")
    # user = relationship("User")