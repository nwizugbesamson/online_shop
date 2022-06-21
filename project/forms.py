from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired




class RegisterForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()], render_kw={"placeholder": "Username"})
    email = EmailField(label='Email', validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField(label='Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField(label="Register")


# CREATE LOGIN FORM
class LoginForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField(label='Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField(label="Login")


# CREATE PRODUCT FORM
class ProductForm(FlaskForm):
    name = StringField(label="Product Name", validators=[DataRequired()], render_kw={"placeholder": "Product Name"})
    img_url = StringField(label="Img_url", validators=[DataRequired()], render_kw={"placeholder": "Product Img url"})
    price = FloatField(label="Price", validators=[DataRequired()], render_kw={"placeholder": "Product Description"})
    description = TextAreaField(label="Description", validators=[DataRequired()], render_kw={"placeholder": "Product Description"})
    submit = SubmitField(label="Add", validators=[DataRequired()])


# ADD PRODUCT TO CART
class CartForm(FlaskForm):
    quantity = IntegerField(label="quantity", validators=[DataRequired()], render_kw={"placeholder": "Quantity"})
    submit = SubmitField(label="Add", validators=[DataRequired()])



# REVIEW FORM
class ReviewForm(FlaskForm):
    review = TextAreaField(label="Review", validators=[DataRequired()], render_kw={"placeholder": "review"})
    submit = SubmitField(label="Submit now", validators=[DataRequired()])