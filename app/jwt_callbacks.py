from flask import jsonify
from .models import User, User_JWT, TokenBlocklist
from .extensions import db, jwt  # usa il tuo jwt importato in extensions

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "message": "Token scaduto. Effettua nuovamente il login.",
        "error": "token_expired"
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "message": "Token non valido. Firma non verificata o token corrotto.",
        "error": "invalid_token"
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "message": "Token mancante o malformato nell'header Authorization.",
        "error": "authorization_header"
    }), 401

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_data):
    jti = jwt_data["jti"]
    token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()
    return token is not None

@jwt.additional_claims_loader
def make_additional_claims(identity):
    if identity == "Chichi":
        return {"is_staff": True}
    return {"is_staff": False}

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_headers, jwt_data):
    identity_user = jwt_data['sub']
    return User_JWT.query.filter_by(userjwt_username=identity_user).one_or_none()