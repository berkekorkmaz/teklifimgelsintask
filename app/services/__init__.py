from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app import db
from app.models import User, Car, Rental
from app.exceptions import (
    CarNotAvailableException, UserAlreadyRentingException, 
    NoActiveRentalException, CarAlreadyRentedException,
    CarDeletionException, InvalidCarOwnerException
)
from app.utils import validate_car_data, calculate_rental_fee

class CarService:
    """Service for car-related business logic"""
    
    @staticmethod
    def create_car(merchant_id: int, car_data: Dict[str, Any]) -> Car:
        """Create a new car for a merchant"""
        validated_data = validate_car_data(car_data)
        validated_data['merchant_id'] = merchant_id
        
        car = Car(**validated_data)
        db.session.add(car)
        db.session.commit()
        return car
    
    @staticmethod
    def update_car(car_id: int, merchant_id: int, car_data: Dict[str, Any]) -> Car:
        """Update car details (merchant only)"""
        car = Car.query.get_or_404(car_id)
        
        if car.merchant_id != merchant_id:
            raise InvalidCarOwnerException("You can only update your own cars")
        
        validated_data = validate_car_data(car_data)
        
        for field, value in validated_data.items():
            setattr(car, field, value)
        
        db.session.commit()
        return car
    
    @staticmethod
    def delete_car(car_id: int, merchant_id: int) -> bool:
        """Delete a car (merchant only)"""
        car = Car.query.get_or_404(car_id)
        
        if car.merchant_id != merchant_id:
            raise InvalidCarOwnerException("You can only delete your own cars")
        
        if not car.available:
            raise CarNotAvailableException("Cannot delete a car that is not available")
        
        # Check for rental history
        if Rental.query.filter_by(car_id=car.id).first():
            raise CarDeletionException("Cannot delete a car with rental history")
        
        db.session.delete(car)
        db.session.commit()
        return True
    
    @staticmethod
    def get_cars(filters: Optional[Dict[str, Any]] = None, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get cars with optional filtering and pagination"""
        query = Car.query
        
        if filters:
            for field, value in filters.items():
                if value is not None and value != '':
                    if hasattr(Car, field):
                        query = query.filter(getattr(Car, field) == value)
        
        total = query.count()
        cars = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'cars': cars,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }

class RentalService:
    """Service for rental-related business logic"""
    
    @staticmethod
    def rent_car(user_id: int, car_id: int) -> Rental:
        """Rent a car for a user"""
        car = Car.query.get_or_404(car_id)
        
        if not car.is_available():
            raise CarNotAvailableException("Car is not available for rent")
        
        # Check if user already has an active rental
        active_rental = Rental.query.filter_by(user_id=user_id, returned_at=None).first()
        if active_rental:
            raise UserAlreadyRentingException("You already have an active rental")
        
        # Check if car is already rented
        active_car_rental = Rental.query.filter_by(car_id=car_id, returned_at=None).first()
        if active_car_rental:
            raise CarAlreadyRentedException("Car is already rented by another user")
        
        # Create rental
        rental = Rental(
            user_id=user_id,
            car_id=car_id,
            daily_rate=car.daily_rate
        )
        
        # Update car availability
        car.available = False
        
        db.session.add(rental)
        db.session.commit()
        
        return rental
    
    @staticmethod
    def return_car(user_id: int) -> Rental:
        """Return a car for a user"""
        rental = Rental.query.filter_by(user_id=user_id, returned_at=None).first()
        
        if not rental:
            raise NoActiveRentalException("No active rental found")
        
        # Calculate fee
        rental.returned_at = datetime.utcnow()
        rental.total_fee = rental.calculate_fee()
        
        # Update car availability
        rental.car.available = True
        
        db.session.commit()
        
        return rental
    
    @staticmethod
    def get_user_rental_history(user_id: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get rental history for a user"""
        query = Rental.query.filter_by(user_id=user_id).order_by(Rental.rented_at.desc())
        
        total = query.count()
        rentals = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'rentals': [rental.to_dict() for rental in rentals],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def get_car_rental_history(car_id: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get rental history for a car"""
        query = Rental.query.filter_by(car_id=car_id).order_by(Rental.rented_at.desc())
        
        total = query.count()
        rentals = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'rentals': [rental.to_dict() for rental in rentals],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }

class UserService:
    """Service for user-related business logic"""
    
    @staticmethod
    def get_user_stats(user_id: int) -> Dict[str, Any]:
        """Get statistics for a user"""
        user = User.query.get_or_404(user_id)
        
        # Get rental statistics
        total_rentals = Rental.query.filter_by(user_id=user_id).count()
        active_rentals = Rental.query.filter_by(user_id=user_id, returned_at=None).count()
        completed_rentals = total_rentals - active_rentals
        
        # Calculate total spent
        total_spent = db.session.query(db.func.sum(Rental.total_fee))\
            .filter(Rental.user_id == user_id, Rental.total_fee.isnot(None))\
            .scalar() or Decimal('0.00')
        
        return {
            'user_id': user_id,
            'username': user.username,
            'role': user.role,
            'total_rentals': total_rentals,
            'active_rentals': active_rentals,
            'completed_rentals': completed_rentals,
            'total_spent': float(total_spent)
        } 