from flask_restx import Namespace, Resource, fields
from flask import request
from Backend.models import User
from Backend.extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from datetime import timedelta

api = Namespace('auth', description='Authentication')

signup_model = api.model('SignUp', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'username': fields.String(required=True),
    'password': fields.String(required=True),
    'confirm_password': fields.String(required=True),
    'role': fields.String(required=False, default='senior_citizen'),
    'profile_picture': fields.String(required=False),
    'relation': fields.String(required=False),
})

login_model = api.model('Login', {
    'username': fields.String(required=True),
    'password': fields.String(required=True),
})

@api.route('/signup')
class Signup(Resource):
    @api.expect(signup_model)
    def post(self):
        data = request.get_json() or {}

        # List of required fields
        required_fields = ['first_name', 'last_name', 'username', 'password', 'confirm_password']

        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return {
                'message': f"Missing required fields: {', '.join(missing)}"
            }, 400

        if data['password'] != data['confirm_password']:
            return {'message': 'Passwords do not match'}, 400

        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username already exists'}, 400

        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data['username'],
            role=data.get('role', 'senior_citizen'),
            profile_picture=data.get('profile_picture'),
            relation=data.get('relation')
        )

        user.set_password(data['password'])
        try:
            db.session.add(user)
            db.session.commit()
            return {'message': 'User registered successfully'}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to register user: {str(e)}'}, 500

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        data = request.get_json() or {}

        # Check required fields explicitly
        if not data.get('username') or not data.get('password'):
            return {'message': 'Missing username or password'}, 400

        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(days=1),
                additional_claims={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'role': user.role
                }
            )
            return {
                'access_token': access_token,
                'user_id': user.id,
                'role': user.role
            }, 200

        return {'message': 'Invalid credentials'}, 401
    
@api.route('/protected')
class Protected(Resource):
    @jwt_required()
    def get(self):
        """Protected route"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        return {'message': f'Hello {user.first_name}!'}