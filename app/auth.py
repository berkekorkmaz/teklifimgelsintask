from functools import wraps
from flask import request, jsonify, g
from werkzeug.security import check_password_hash
from app.models import User
from app import db

# Basic Auth implementation

def authenticate():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return None
    user = User.query.filter_by(username=auth.username).first()
    if user and check_password_hash(user.password_hash, auth.password):
        return user
    return None

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = authenticate()
            if not user:
                return jsonify({'message': 'Authentication required'}), 401
            if role and user.role != role:
                return jsonify({'message': 'Forbidden: Insufficient role'}), 403
            g.current_user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator 