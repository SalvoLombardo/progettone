from flask import Blueprint, render_template , session, redirect,url_for
from flask_login import login_user,login_required,logout_user,current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')

