from flask import Blueprint,session,request,jsonify,current_app
from app.extensions import db,bcrypt
from app.models import User_JWT,Project,User,TokenBlocklist
from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required,get_jwt_identity, get_jwt, current_user 
from .schemas import UserSchema,ProjectSchema

api_bp=Blueprint('api', __name__)


##################---------------------Primo approccio alle api, qui nessuna necessità di JWT e non protetti----------------------##################
@api_bp.post('/api/register')
def register():
    data = request.get_json()

    new_user=User_JWT(
        userjwt_username= data.get('username'),
    ) #su new_user passiamo anche i metodi dell'oggetto User_JWT

    new_user.set_password(password= data.get('password'))

    new_user.save()

    return jsonify({'message':'User created'})

@api_bp.post('/api/login')
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User_JWT.query.filter_by(userjwt_username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Credenziali non valide"}), 401

    access_token = create_access_token(identity=user.userjwt_username)
    refresh_token = create_refresh_token(identity=user.userjwt_username)

    return jsonify({
        "message": "Login effettuato",
        "tokens": {
            "access": access_token,
            "refresh": refresh_token
        }
    }), 200
##################---------------------Primo approccio alle api, qui nessuna necessità di JWT e non protetti----------------------##################

###############################----------- Da qui End point decorati con jwt required-----------###############################



@api_bp.get('/api/logout')
@jwt_required()
def logout():
    jwt = get_jwt()
    jti = jwt["jti"]
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()
    return jsonify(msg="Logout successful")

@api_bp.post('/api/refresh')
@jwt_required(refresh=True)  
def refresh_access_token():
    current_user = get_jwt_identity()  # prendi l'identità dal refresh token
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access": new_access_token}), 200

@api_bp.post('/api/get_project_name')
@jwt_required()
def get_project_name():
    data = request.get_json()
    project_id = data.get('project_id')

    if not project_id or not isinstance(project_id, int):
        return jsonify({"error": "Project ID mancante o non valido"}), 400

    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return jsonify({"error": "Progetto non trovato"}), 404

    return jsonify({"Nome Progetto": project.project_name})

@api_bp.post('/api/get_project_description')
@jwt_required
def get_project_description():
    
    data = request.get_json()
    project_id=data.get('project_id')

    if not project_id:
        return jsonify({"Errore":"Progetto non trovato"}), 404
    
    project=Project.query.filter_by(project_id,project_id).first()

    if not project:
        return jsonify({"Errore":"Descrizione non trovata"}), 404
    
    return jsonify({"Descrizione del progetto":project.project_description})

########------#########------#######------Da qui utiliziamo istruioni di jwt come claims=get_jwt()---------########------#########------#######------
@api_bp.get('/api/all/pagination')
@jwt_required()
def get_all_jwt_users():
    claims=get_jwt()
    if claims.get('is_staff')==True:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=3, type=int)

        users_jwt = User_JWT.query.paginate(page=page, per_page=per_page)

        result = UserSchema(many=True).dump(users_jwt.items)

        return jsonify({
            "users": result
        }), 200
    
    return jsonify({'message':'You are not allowed to access'}),401

@api_bp.get('/api/jwt_claims')
@jwt_required()
def jwt_claims():
    claims=get_jwt()

    return jsonify({'message':'ok','claims':claims})

@api_bp.get('/api/whoiam')
@jwt_required()
def whoiam():

    return jsonify({'user_details':{'username':current_user.userjwt_username}})

########------#########------#######------Da qui utiliziamo istruioni di jwt come claims=get_jwt()---------########------#########------#######------


#######------------Api personalizzata per trovare progetto con data di update a partire da vaole Json----------######
@api_bp.post('/api/find_from_data')
def find_from_data():
    data = request.get_json()

    # Ricavo e valido la data
    date_str = data.get('date_from')
    if not date_str:
        return jsonify({'message': 'Please insert a correct date'}), 400

    try:
        date_from = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Ricavo parametri di paginazione (es. /api/find_from_data?page=1&per_page=5)
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=5, type=int)

    # Filtro i progetti con date >= quella inserita
    projects_query = Project.query.filter(Project.project_updated >= date_from).order_by(Project.project_updated.desc())

    # Paginazione
    paginated_projects = projects_query.paginate(page=page, per_page=per_page, error_out=False)

    # Serializzazione
    result = ProjectSchema(many=True).dump(paginated_projects.items)

    return jsonify({
        'projects': result,
        'total': paginated_projects.total,
        'page': paginated_projects.page,
        'pages': paginated_projects.pages
    })
#######------------Api personalizzata per trovare progetto con data di update a partire da vaole Json----------######


