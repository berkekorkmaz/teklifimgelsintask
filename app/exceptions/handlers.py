from flask import jsonify
from app.exceptions import (
    CarRentalException, CarNotAvailableException, UserAlreadyRentingException,
    NoActiveRentalException, CarAlreadyRentedException, CarDeletionException,
    InvalidCarOwnerException
)

def register_error_handlers(app):
    """Register custom error handlers for the Flask app"""
    
    @app.errorhandler(CarNotAvailableException)
    def handle_car_not_available(error):
        return jsonify({'message': str(error)}), 400
    
    @app.errorhandler(UserAlreadyRentingException)
    def handle_user_already_renting(error):
        return jsonify({'message': str(error)}), 400
    
    @app.errorhandler(NoActiveRentalException)
    def handle_no_active_rental(error):
        return jsonify({'message': str(error)}), 400
    
    @app.errorhandler(CarAlreadyRentedException)
    def handle_car_already_rented(error):
        return jsonify({'message': str(error)}), 400
    
    @app.errorhandler(CarDeletionException)
    def handle_car_deletion_error(error):
        return jsonify({'message': str(error)}), 400
    
    @app.errorhandler(InvalidCarOwnerException)
    def handle_invalid_car_owner(error):
        return jsonify({'message': str(error)}), 403
    
    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return jsonify({'message': str(error)}), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({'message': 'Internal server error'}), 500 