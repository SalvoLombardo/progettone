# app/models.py
from app.extensions import db
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

class Project(db.Model):
    __tablename__='projects'
    project_id=db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(150), nullable=False)
    project_category = db.Column(db.String(150), nullable=False)
    project_description=db.Column(db.String(150))
    project_created = db.Column(db.DateTime)
    project_updated = db.Column(db.DateTime)
    project_img=db.Column(db.String(255))
    user_id = db.Column(db.Integer,db.ForeignKey('users.user_id', ondelete='CASCADE'),nullable=False)

    def get_id(self):
        return str(self.user_id)
     
class User(db.Model, UserMixin):
    
    __tablename__='users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.String(150), unique=True, nullable=False)
    user_password = db.Column(db.String(256), nullable=False)
    user_admin=db.Column(db.Boolean, nullable=False, default=False)
    user_description = db.Column(db.String(256))
    user_goals=db.Column(db.String(256))
    


    def get_id(self):
        return str(self.user_id)
    
class User_JWT(db.Model):
    __tablename__='users_jwt'
    userjwt_id=db.Column(db.Integer, primary_key=True)
    userjwt_username = db.Column(db.String(150), unique=True, nullable=False)
    userjwt_password = db.Column(db.String(256), nullable=False)
    

    def __repr__(self):
        return f'User: {self.userjwt_username}'
    
    def set_password(self, password):
        self.userjwt_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.userjwt_password, password)
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_id(self):
        return str(self.userjwt_id)
    
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)  # JWT ID univoco del token
    created_at = db.Column(db.DateTime, default=datetime.utcnow)




