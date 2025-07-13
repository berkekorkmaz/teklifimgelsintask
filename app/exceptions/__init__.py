class CarRentalException(Exception):
    """Base exception for car rental application"""
    pass

class CarNotAvailableException(CarRentalException):
    """Raised when trying to rent an unavailable car"""
    pass

class UserAlreadyRentingException(CarRentalException):
    """Raised when user already has an active rental"""
    pass

class NoActiveRentalException(CarRentalException):
    """Raised when user has no active rental to return"""
    pass

class CarAlreadyRentedException(CarRentalException):
    """Raised when car is already rented by another user"""
    pass

class CarDeletionException(CarRentalException):
    """Raised when trying to delete a car with rental history"""
    pass

class InvalidCarOwnerException(CarRentalException):
    """Raised when merchant tries to modify another merchant's car"""
    pass 