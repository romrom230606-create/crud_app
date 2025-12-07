# Product CRUD API

## Production URL
**Live Application**: https://crud-app-2fgv.onrender.com

## Test Accounts
Use the web interface to test functionality. No special accounts required.

## How to Run Tests
# Locally
python -m pytest tests/ -v

# In CI - tests run automatically on every push

## API Endpoints
- GET / - Main page with product management UI
- GET /products - Get all products
- GET /products/<id> - Get specific product
- POST /products - Create new product
- PUT /products/<id> - Update existing product
- DELETE /products/<id> - Delete product

## Validation Rules
- name: required, 3-50 characters
- email: valid email format
- price: number > 0
- birthDate: not later than today
- code: 4-20 characters (letters, numbers, dash)

## Error Responses
The API returns structured error responses:

{
  "timestamp": "2025-01-11T10:30:00Z",
  "status": 400,
  "error": "Bad Request",
  "fieldErrors": [
    {
      "field": "email",
      "code": "INVALID_FORMAT", 
      "message": "Invalid email"
    }
  ]
}

## CI/CD Pipeline
- Automated tests run on every push to main branch
- Automatic deployment to Render after successful tests
- Test results visible in GitHub Actions

## Technology Stack
- Backend: Flask, SQLAlchemy, PostgreSQL
- Frontend: HTML, JavaScript
- Deployment: Render + GitHub Actions
- Testing: pytest 
