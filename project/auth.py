from project import db
from flask import Blueprint, render_template, flash, redirect, url_for
from project.forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from project.models import User

auth = Blueprint(name="auth", import_name=__name__, static_folder="static", template_folder="templates")


@auth.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User()
        setattr(new_user, "bill", 0.00)
        for key, value in form.data.items():
            if key.lower() == "password":
                value = generate_password_hash(password=form.password.data, method="pbkdf2:sha256", salt_length=12)
            if key in User.__table__.columns:
                setattr(new_user, key, value)
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("main.home_page"))
        except IntegrityError:
            flash("Email already Exists Login instead", category="error")
            return redirect(url_for("auth.login_page"))
    return render_template("register.html", form=form)


@auth.route("/login", methods=["POST", "GET"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("main.home_page"))
            else:
                flash("password is incorrect", category="error")
        else:
            flash("user does not exist check email entered", category="error")
            return redirect(url_for("auth.login_page"))
    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout_page():
    logout_user()
    return redirect(url_for("main.home_page"))
