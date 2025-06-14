# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # oppure il nome della tua route di login

db = SQLAlchemy()
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3



from flask_jwt_extended import JWTManager
jwt = JWTManager()


from flask_wtf.csrf import CSRFProtect
csrf=CSRFProtect()


@event.listens_for(Engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):  # Verifica che sia SQLite
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

        
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()


