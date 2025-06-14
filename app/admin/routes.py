from flask import Blueprint,session,request,redirect,url_for,render_template,flash
from flask_login import login_user,login_required,logout_user,current_user
from app.extensions import db,bcrypt
from app.models import User, Project
from flask_login import LoginManager
from app.utils.decorators import admin_required


admin_bp=Blueprint('admin', __name__)



@admin_bp.route('/login_admin', methods=['GET','POST'])
def login_admin():
    if request.method=='GET':
        return render_template('login_admin.html')
    
    elif request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')

        if not username or not password:
            flash('In campi devono essere compilati')
            return redirect(url_for('admin.login_admin'))  
        
        

        user = User.query.filter_by(user_username=username).first()
        if user and user.user_admin and bcrypt.check_password_hash(user.user_password, password):
            login_user(user)
            flash('Login Riuscito!!!')
            return redirect(url_for('admin.admin_main'))
        else:
            flash('Login Fallito')
            return redirect(url_for('admin.login_admin'))

       
@admin_bp.route('/logout', methods=['GET','POST'])
def logout():
    logout_user()
    flash('Logout effettuato')
    return redirect(url_for('main.home')) 


@admin_bp.route('/admin_main')
@admin_required
def admin_main():
    user_id=current_user

    user=User.query.filter_by(user_id=current_user.get_id()).first()

    return render_template('admin_main.html', user=user)

@admin_bp.route('/view_all_users')
def view_all_users():
    users = User.query.filter_by(user_admin=False).all()

    return render_template('view_all_users.html', users=users)


@admin_bp.route('/delete_user/<int:user_id>', methods=['GET','POST'])
def delete_user(user_id):
    user=User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('admin.view_all_users'))

