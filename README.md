# Car Rental API

A comprehensive REST API for a car rental platform built with Flask, PostgreSQL, and Docker. This application allows merchants to manage their car listings and users to rent cars with pricing and rental history tracking.

## 🚀 Features

### Core Features
- **User Authentication & Authorization**: Register and login with role-based access (merchant/user)
- **Car Management**: CRUD operations for car listings with pricing
- **Rental System**: Rent and return cars with fee calculation
- **Rental History**: Track rental history for users and cars
- **Pricing Logic**: Automatic fee calculation based on rental duration
- **Statistics**: User rental statistics and spending tracking

### Technical Features
- **RESTful API**: Clean, well-documented endpoints
- **Database ORM**: SQLAlchemy for all database operations
- **Docker Support**: Containerized application with PostgreSQL
- **Error Handling**: Comprehensive error responses and validation
- **Pagination**: Support for paginated results
- **Filtering**: Advanced filtering for car listings

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Basic Auth
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Postman Collection

## 📋 Prerequisites

- Docker and Docker Compose
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd car-rental-api
```

### 2. Start the Application
```bash
docker-compose up -d
```

### 3. Initialize Database
```bash
docker-compose exec web flask db upgrade
```

### 4. Access the API
The API will be available at: `http://localhost:5020`

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /register
Content-Type: application/json

{
    "username": "user1",
    "password": "password123",
    "role": "user"
}
```

#### Login
```http
POST /login
Content-Type: application/json

{
    "username": "user1",
    "password": "password123"
}
```

### Car Management Endpoints

#### Add Car (Merchant Only)
```http
POST /cars
Authorization: Basic <merchant_credentials>
Content-Type: application/json

{
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2022,
    "daily_rate": 75.00
}
```

#### List Cars (Public)
```http
GET /cars?brand=Toyota&available=true&page=1&per_page=10
```

#### Get Car Details
```http
GET /cars/{car_id}
```

#### Update Car (Merchant Only)
```http
PUT /cars/{car_id}
Authorization: Basic <merchant_credentials>
Content-Type: application/json

{
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2023,
    "daily_rate": 80.00,
    "available": true
}
```

#### Delete Car (Merchant Only)
```http
DELETE /cars/{car_id}
Authorization: Basic <merchant_credentials>
```

#### Get Car Pricing
```http
GET /cars/{car_id}/pricing
```

### Rental System Endpoints

#### Rent Car (User Only)
```http
POST /rentals
Authorization: Basic <user_credentials>
Content-Type: application/json

{
    "car_id": 1
}
```

#### Return Car (User Only)
```http
POST /rentals/return
Authorization: Basic <user_credentials>
```

#### List User Rentals
```http
GET /rentals?page=1&per_page=10
Authorization: Basic <user_credentials>
```

#### Get Rental History
```http
GET /rentals/history?page=1&per_page=10
Authorization: Basic <user_credentials>
```

#### Get Active Rental
```http
GET /rentals/active
Authorization: Basic <user_credentials>
```

#### Get Car Rental History (Merchant Only)
```http
GET /cars/{car_id}/rentals?page=1&per_page=10
Authorization: Basic <merchant_credentials>
```

### User Statistics

#### Get User Stats
```http
GET /users/stats
Authorization: Basic <user_credentials>
```

## 📊 Response Examples

### Car Creation Response
```json
{
    "message": "Car added successfully",
    "car_id": 1,
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2022,
    "daily_rate": 75.0,
    "available": true
}
```

### Rental Response
```json
{
    "message": "Car rented successfully",
    "rental_id": 1,
    "car_id": 1,
    "daily_rate": 75.0,
    "rented_at": "2024-06-13T12:00:00.000Z"
}
```

### Return Response
```json
{
    "message": "Car returned successfully",
    "rental_id": 1,
    "total_fee": 75.0,
    "duration_hours": 25.0,
    "duration_days": 2.0,
    "returned_at": "2024-06-14T13:00:00.000Z"
}
```

### User Statistics Response
```json
{
    "user_id": 1,
    "username": "user1",
    "role": "user",
    "total_rentals": 2,
    "active_rentals": 0,
    "completed_rentals": 2,
    "total_spent": 150.0
}
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: Development environment
- `FLASK_APP`: Flask application entry point

### Database Configuration
- **Host**: `db` (Docker service)
- **Port**: `5432`
- **Database**: `car_rental`
- **User**: `postgres`
- **Password**: `postgres`

## 🧪 Testing

### Using Postman
1. Import the provided `Car_Rental_API.postman_collection.json`
2. Set up environment variables:
   - `base_url`: `http://localhost:5020`
   - `merchant_username`: `merchant1`
   - `merchant_password`: `merchantpass`
   - `user_username`: `user1`
   - `user_password`: `userpass`

### Using curl
```bash
# Register a merchant
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"merchant1","password":"pass","role":"merchant"}' \
  http://localhost:5020/register

# Add a car
curl -X POST -u merchant1:pass -H "Content-Type: application/json" \
  -d '{"brand":"Toyota","model":"Corolla","year":2022,"daily_rate":75.00}' \
  http://localhost:5020/cars

# Rent a car
curl -X POST -u user1:pass -H "Content-Type: application/json" \
  -d '{"car_id":1}' \
  http://localhost:5020/rentals
```

## 📁 Project Structure

```
car-rental-api/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes.py            # API endpoints
│   ├── auth.py              # Authentication logic
│   ├── config.py            # Configuration
│   ├── services/            # Business logic layer
│   ├── utils/               # Utility functions
│   └── exceptions/          # Custom exceptions
├── docker-compose.yml       # Docker services
├── Dockerfile              # Application container
├── requirements.txt         # Python dependencies
├── Car_Rental_API.postman_collection.json  # API documentation
└── README.md               # This file
```

## 🔒 Security Features

- **Role-based Access Control**: Merchants can only manage their own cars
- **Authentication Required**: All sensitive endpoints require authentication
- **Input Validation**: Comprehensive validation for all inputs
- **Error Handling**: Secure error responses without information leakage

## 🚀 Deployment

### Local Development
```bash
docker-compose up -d
```