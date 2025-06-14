from flask import Blueprint,session,request,redirect,url_for,render_template,flash,current_app, abort,current_app
from flask_login import login_user,login_required,logout_user,current_user
from app.extensions import db,bcrypt
from app.models import User, Project
from flask_login import LoginManager
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
import os
import uuid

from app.models import User, Project
from app.forms.csrf_form import FormCSRF

auth_bp= Blueprint('auth', __name__)

@auth_bp.route('/signin', methods=['GET','POST'])
def signin():
    if request.method=='GET':
        return render_template('signin.html')
    
    elif request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')

        if not username or not password:
            flash('In campi devono essere compilati')
            return redirect(url_for('auth.signin'))  
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user=User(user_username=username, user_password=hashed_password)

        db.session.add(user)
        db.session.commit()

        flash('Registrazione riuscita')

        return redirect(url_for('auth.signin'))


@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    
    elif request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')

        if not username or not password:
            flash('In campi devono essere compilati')
            return redirect(url_for('auth.login'))  
        
        

        user = User.query.filter_by(user_username=username).first()
        if user and bcrypt.check_password_hash(user.user_password, password):
            login_user(user)
            flash('Login Riuscito!!!')
            return redirect(url_for('auth.user_main'))
        else:
            flash('Login Fallito')
            return redirect(url_for('auth.login'))
    
@auth_bp.route('/logout', methods=['GET','POST'])
def logout():
    logout_user()
    flash('Logout effettuato')
    return redirect(url_for('main.home')) 

@auth_bp.route('/user_main')
@login_required
def user_main():
    user_id=current_user

    user=User.query.filter_by(user_id=current_user.get_id()).first()

    return render_template('user_main.html', user=user)

@auth_bp.route('/my_projects')
@login_required
def my_projects():
    user_id=current_user

    projects=Project.query.filter_by(user_id=current_user.get_id()).all()
    user=User.query.filter_by(user_id=current_user.get_id()).first()
    return render_template('my_projects.html',projects=projects,user=user)


@auth_bp.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if project.user_id != current_user.user_id:
        abort(403)

    if request.method == 'POST':
        project.project_name = request.form.get('name')
        project.project_category = request.form.get('category')
        project.project_description = request.form.get('description')

        # Se cliccato il bottone "Elimina immagine"
        if 'delete_image' in request.form and project.project_img:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], project.project_img)
            if os.path.exists(image_path):
                os.remove(image_path)
            project.project_img = None

        project.project_updated = datetime.now(timezone.utc)
        db.session.commit()
        flash('Progetto aggiornato con successo')
        return redirect(url_for('auth.my_projects'))

    return render_template('edit_project.html', project=project)

@auth_bp.route('/add_project', methods=['GET', 'POST'])
@login_required
def add_project():
    user = User.query.filter_by(user_id=current_user.get_id()).first()

    if request.method == 'GET':
        return render_template('add_project.html', user=user)

    elif request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description')
        image_file = request.files.get('immagine')

        image_filename = None

        if image_file and image_file.filename != '':
            # Estrai nome e estensione originali
            original_filename = secure_filename(image_file.filename)
            ext = os.path.splitext(original_filename)[1]  # es. ".png"
            
            # Genera un nome unico usando uuid4
            unique_filename = f"{uuid.uuid4().hex}{ext}"

            # Percorso cartella upload configurata in app.config['UPLOAD_FOLDER']
            upload_folder = current_app.config.get('UPLOAD_FOLDER')

            # Assicurati che la cartella esista
            os.makedirs(upload_folder, exist_ok=True)

            # Salva il file nel percorso completo
            image_path = os.path.join(upload_folder, unique_filename)
            image_file.save(image_path)

            image_filename = unique_filename

        project = Project(
            project_name=name,
            project_category=category,
            project_description=description,
            project_img=image_filename,
            user_id=user.user_id,
            project_created=datetime.now(timezone.utc),
            project_updated=datetime.now(timezone.utc)
        )

        db.session.add(project)
        db.session.commit()

        flash('Progetto aggiunto con successo')
        return render_template('user_main.html', user=user)
    

@auth_bp.route('/delete_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)

    # Verifica che l'utente sia il proprietario del progetto
    if project.user_id != current_user.user_id:
        abort(403)

    # Elimina il file immagine, se presente
    if project.project_img:
        img_path = os.path.join(current_app.root_path, 'static', 'uploads', project.project_img)
        if os.path.exists(img_path):
            os.remove(img_path)

    db.session.delete(project)
    db.session.commit()

    flash('Progetto eliminato con successo.')
    return redirect(url_for('auth.my_projects'))




  
from app.forms.csrf_form import FormCSRF       
@auth_bp.route('/CSRF', methods=['GET','POST'])
def CSRF():
    form=FormCSRF()
    if form.validate_on_submit():
        nome=form.nome.data
        return f'Ciao {nome}'
    return render_template('CSRF.html', form=form)



