from flask import Blueprint, request, jsonify, g
from app import db
from app.models import User, Car, Rental
from app.auth import login_required
from app.services import CarService, RentalService, UserService
from app.exceptions import (
    CarNotAvailableException, UserAlreadyRentingException,
    NoActiveRentalException, CarAlreadyRentedException,
    CarDeletionException, InvalidCarOwnerException
)
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('api', __name__)

@bp.route('/')
def index():
    return jsonify({"message": "Car Rental API is running."})

# --- Authentication ---

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    
    if not username or not password or not role:
        return jsonify({'message': 'Username, password, and role are required'}), 400
    
    if role not in ['merchant', 'user']:
        return jsonify({'message': 'Role must be either "merchant" or "user"'}), 400
    
    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    # Create new user
    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        role=role
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': user.id,
        'username': user.username,
        'role': user.role
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid username or password'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'user_id': user.id,
        'username': user.username,
        'role': user.role
    })

# --- Car Management ---

@bp.route('/cars', methods=['POST'])
@login_required(role='merchant')
def add_car():
    try:
        data = request.get_json()
        car = CarService.create_car(g.current_user.id, data)
        
        return jsonify({
            'message': 'Car added successfully',
            'car_id': car.id,
            'brand': car.brand,
            'model': car.model,
            'year': car.year,
            'daily_rate': float(car.daily_rate),
            'available': car.available
        }), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400

@bp.route('/cars', methods=['GET'])
def list_cars():
    # Get query parameters for filtering and pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build filters
    filters = {}
    for field in ['brand', 'model', 'year', 'available']:
        value = request.args.get(field)
        if value is not None:
            if field == 'available':
                filters[field] = value.lower() == 'true'
            elif field == 'year':
                filters[field] = int(value)
            else:
                filters[field] = value
    
    try:
        result = CarService.get_cars(filters, page, per_page)
        
        return jsonify({
            'cars': [
                {
                    'id': car.id,
                    'brand': car.brand,
                    'model': car.model,
                    'year': car.year,
                    'available': car.available,
                    'daily_rate': float(car.daily_rate),
                    'merchant_id': car.merchant_id
                } for car in result['cars']
            ],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        })
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@bp.route('/cars/<int:car_id>', methods=['GET'])
def get_car(car_id):
    car = Car.query.get_or_404(car_id)
    return jsonify({
        'id': car.id,
        'brand': car.brand,
        'model': car.model,
        'year': car.year,
        'available': car.available,
        'daily_rate': float(car.daily_rate),
        'merchant_id': car.merchant_id
    })

@bp.route('/cars/<int:car_id>', methods=['PUT'])
@login_required(role='merchant')
def update_car(car_id):
    try:
        data = request.get_json()
        car = CarService.update_car(car_id, g.current_user.id, data)
        
        return jsonify({
            'message': 'Car updated successfully',
            'car_id': car.id,
            'brand': car.brand,
            'model': car.model,
            'year': car.year,
            'daily_rate': float(car.daily_rate),
            'available': car.available
        })
    except (ValueError, InvalidCarOwnerException) as e:
        return jsonify({'message': str(e)}), 400

@bp.route('/cars/<int:car_id>', methods=['DELETE'])
@login_required(role='merchant')
def delete_car(car_id):
    try:
        CarService.delete_car(car_id, g.current_user.id)
        return jsonify({'message': 'Car deleted successfully'})
    except (CarNotAvailableException, CarDeletionException, InvalidCarOwnerException) as e:
        return jsonify({'message': str(e)}), 400

# --- Rental System ---

@bp.route('/rentals', methods=['POST'])
@login_required(role='user')
def rent_car():
    try:
        data = request.get_json()
        car_id = data.get('car_id')
        
        if not car_id:
            return jsonify({'message': 'Car ID is required'}), 400
        
        rental = RentalService.rent_car(g.current_user.id, car_id)
        
        return jsonify({
            'message': 'Car rented successfully',
            'rental_id': rental.id,
            'car_id': rental.car_id,
            'daily_rate': float(rental.daily_rate),
            'rented_at': rental.rented_at.isoformat()
        }), 201
    except (CarNotAvailableException, UserAlreadyRentingException, CarAlreadyRentedException) as e:
        return jsonify({'message': str(e)}), 400

@bp.route('/rentals/return', methods=['POST'])
@login_required(role='user')
def return_car():
    try:
        rental = RentalService.return_car(g.current_user.id)
        
        return jsonify({
            'message': 'Car returned successfully',
            'rental_id': rental.id,
            'total_fee': float(rental.total_fee),
            'duration_hours': rental.get_duration_hours(),
            'duration_days': rental.get_duration_days(),
            'returned_at': rental.returned_at.isoformat()
        })
    except NoActiveRentalException as e:
        return jsonify({'message': str(e)}), 400

@bp.route('/rentals', methods=['GET'])
@login_required(role='user')
def list_rentals():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    try:
        result = RentalService.get_user_rental_history(g.current_user.id, page, per_page)
        
        return jsonify({
            'rentals': result['rentals'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        })
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@bp.route('/rentals/active', methods=['GET'])
@login_required(role='user')
def get_active_rental():
    """Get user's current active rental"""
    rental = g.current_user.get_active_rental()
    
    if not rental:
        return jsonify({'message': 'No active rental found'}), 404
    
    return jsonify(rental.to_dict())

# --- Rental History ---

@bp.route('/rentals/history', methods=['GET'])
@login_required(role='user')
def get_rental_history():
    """Get detailed rental history for user"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    try:
        result = RentalService.get_user_rental_history(g.current_user.id, page, per_page)
        
        return jsonify({
            'rentals': result['rentals'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        })
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@bp.route('/cars/<int:car_id>/rentals', methods=['GET'])
@login_required(role='merchant')
def get_car_rental_history(car_id):
    """Get rental history for a specific car (merchant only)"""
    car = Car.query.get_or_404(car_id)
    
    if car.merchant_id != g.current_user.id:
        return jsonify({'message': 'Forbidden: Not your car'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    try:
        result = RentalService.get_car_rental_history(car_id, page, per_page)
        
        return jsonify({
            'car_id': car_id,
            'car_info': {
                'brand': car.brand,
                'model': car.model,
                'year': car.year
            },
            'rentals': result['rentals'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        })
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# --- User Statistics ---

@bp.route('/users/stats', methods=['GET'])
@login_required()
def get_user_stats():
    """Get user statistics and rental summary"""
    try:
        stats = UserService.get_user_stats(g.current_user.id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# --- Pricing Information ---

@bp.route('/cars/<int:car_id>/pricing', methods=['GET'])
def get_car_pricing(car_id):
    """Get pricing information for a car"""
    car = Car.query.get_or_404(car_id)
    
    return jsonify({
        'car_id': car.id,
        'brand': car.brand,
        'model': car.model,
        'year': car.year,
        'daily_rate': float(car.daily_rate),
        'available': car.available,
        'pricing_info': {
            'daily_rate': float(car.daily_rate),
            'hourly_rate': float(car.daily_rate / 24),
            'weekly_rate': float(car.daily_rate * 7),
            'monthly_rate': float(car.daily_rate * 30)
        }
    })

def register_routes(app):
    app.register_blueprint(bp) 