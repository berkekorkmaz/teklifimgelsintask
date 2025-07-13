from datetime import datetime, timedelta
from app import db
from decimal import Decimal

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'merchant' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cars = db.relationship('Car', backref='merchant', lazy=True, cascade='all, delete-orphan')
    rentals = db.relationship('Rental', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_active_rental(self):
        """Get user's current active rental"""
        return Rental.query.filter_by(user_id=self.id, returned_at=None).first()
    
    def get_rental_history(self, limit=None):
        """Get user's rental history with optional limit"""
        query = Rental.query.filter_by(user_id=self.id).order_by(Rental.rented_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    brand = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Boolean, default=True)
    daily_rate = db.Column(db.Numeric(10, 2), default=50.00)  # Price per day
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rentals = db.relationship('Rental', backref='car', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Car {self.brand} {self.model}>'
    
    def is_available(self):
        """Check if car is currently available"""
        return self.available and not self.get_active_rental()
    
    def get_active_rental(self):
        """Get current active rental for this car"""
        return Rental.query.filter_by(car_id=self.id, returned_at=None).first()
    
    def get_rental_history(self, limit=None):
        """Get rental history for this car"""
        query = Rental.query.filter_by(car_id=self.id).order_by(Rental.rented_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    rented_at = db.Column(db.DateTime, default=datetime.utcnow)
    returned_at = db.Column(db.DateTime, nullable=True)
    total_fee = db.Column(db.Numeric(10, 2), nullable=True)  # Calculated fee
    daily_rate = db.Column(db.Numeric(10, 2), nullable=False)  # Rate at time of rental

    def __repr__(self):
        return f'<Rental User:{self.user_id} Car:{self.car_id}>'
    
    def is_active(self):
        """Check if rental is currently active"""
        return self.returned_at is None
    
    def get_duration_hours(self):
        """Get rental duration in hours"""
        if not self.returned_at:
            return None
        duration = self.returned_at - self.rented_at
        return duration.total_seconds() / 3600
    
    def get_duration_days(self):
        """Get rental duration in days (rounded up)"""
        if not self.returned_at:
            return None
        duration = self.returned_at - self.rented_at
        return max(1, (duration.total_seconds() / 86400))  # Minimum 1 day
    
    def calculate_fee(self):
        """Calculate rental fee based on duration and daily rate"""
        if not self.returned_at:
            return None
        
        days = self.get_duration_days()
        fee = Decimal(str(days)) * self.daily_rate
        return fee.quantize(Decimal('0.01'))  # Round to 2 decimal places
    
    def to_dict(self):
        """Convert rental to dictionary for API responses"""
        return {
            'id': self.id,
            'car_id': self.car_id,
            'car_brand': self.car.brand,
            'car_model': self.car.model,
            'rented_at': self.rented_at.isoformat(),
            'returned_at': self.returned_at.isoformat() if self.returned_at else None,
            'total_fee': float(self.total_fee) if self.total_fee else None,
            'daily_rate': float(self.daily_rate),
            'duration_hours': self.get_duration_hours(),
            'duration_days': self.get_duration_days(),
            'is_active': self.is_active()
        } 