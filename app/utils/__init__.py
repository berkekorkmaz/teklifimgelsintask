from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

def validate_car_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean car data"""
    validated = {}
    
    if 'brand' in data:
        validated['brand'] = str(data['brand']).strip()
        if not validated['brand']:
            raise ValueError("Brand cannot be empty")
    
    if 'model' in data:
        validated['model'] = str(data['model']).strip()
        if not validated['model']:
            raise ValueError("Model cannot be empty")
    
    if 'year' in data:
        try:
            year = int(data['year'])
            if year < 1900 or year > datetime.now().year + 1:
                raise ValueError("Invalid year")
            validated['year'] = year
        except (ValueError, TypeError):
            raise ValueError("Year must be a valid integer")
    
    if 'daily_rate' in data:
        try:
            rate = Decimal(str(data['daily_rate']))
            if rate <= 0:
                raise ValueError("Daily rate must be positive")
            validated['daily_rate'] = rate
        except (ValueError, TypeError):
            raise ValueError("Daily rate must be a valid number")
    
    if 'available' in data:
        validated['available'] = bool(data['available'])
    
    return validated

def format_currency(amount: Decimal) -> str:
    """Format decimal amount as currency string"""
    return f"${amount:.2f}"

def calculate_rental_fee(daily_rate: Decimal, duration_hours: float) -> Decimal:
    """Calculate rental fee based on duration and daily rate"""
    if duration_hours <= 0:
        return Decimal('0.00')
    
    # Convert hours to days (minimum 1 day)
    days = max(1, duration_hours / 24)
    fee = Decimal(str(days)) * daily_rate
    return fee.quantize(Decimal('0.01'))

def paginate_query(query, page: int = 1, per_page: int = 10):
    """Apply pagination to a query"""
    offset = (page - 1) * per_page
    return query.offset(offset).limit(per_page)

def build_filter_query(base_query, filters: Dict[str, Any]):
    """Apply filters to a base query"""
    query = base_query
    
    for field, value in filters.items():
        if value is not None and value != '':
            if hasattr(query.model, field):
                query = query.filter(getattr(query.model, field) == value)
    
    return query 