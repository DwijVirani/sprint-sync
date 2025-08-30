# JWT Authentication Middleware Documentation

## Overview

The JWT Authentication Middleware provides secure token-based authentication for the SprintSync API using PyJWT. It automatically validates JWT tokens and sets user context for protected routes.

## Features

- 🔐 **JWT Token Validation**: Decodes and validates JWT tokens using PyJWT
- 🛡️ **Route Protection**: Configurable path-based authentication
- 👤 **User Context**: Sets authenticated user data in request state
- 🚫 **Flexible Exclusions**: Easy configuration of public routes
- 📝 **Comprehensive Logging**: Detailed authentication logging
- 🔧 **FastAPI Dependencies**: Ready-to-use dependency functions

## Configuration

### Environment Variables

Add to your `.env` file:

```env
AUTH_SECRET_KEY=your_super_secret_jwt_key_change_in_production_12345
ENVIRONMENT=development
```

### Middleware Setup

The middleware is automatically configured in `app/main.py`:

```python
from app.middleware.authorization import JWTAuthMiddleware

app.add_middleware(JWTAuthMiddleware)
```

## Protected Routes Configuration

By default, these paths require authentication:

- `/api/v1/users`
- `/api/v1/tasks` 
- `/api/v1/projects`
- `/api/v1/ai-suggestions`

These paths are excluded (public):

- `/health-check`
- `/docs`
- `/redoc`
- `/openapi.json`
- `/api/v1/auth/login`
- `/api/v1/auth/register`
- `/api/v1/auth/refresh`

## Usage Examples

### 1. Login and Get Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@sprintsync.com",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "1",
    "email": "admin@sprintsync.com", 
    "name": "Admin User",
    "is_admin": true
  }
}
```

### 2. Access Protected Route

```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 3. Using FastAPI Dependencies

```python
from fastapi import APIRouter, Depends
from app.middleware.authorization import require_auth, require_admin

router = APIRouter()

@router.get("/protected")
async def protected_route(user: dict = Depends(require_auth)):
    return {"message": f"Hello {user['email']}!"}

@router.delete("/admin/users/{user_id}")
async def delete_user(user_id: int, admin: dict = Depends(require_admin)):
    # Only admins can access this endpoint
    pass
```

### 4. Manual User Context Access

```python
from fastapi import Request
from app.middleware.authorization import get_current_user

@router.get("/manual-auth")
async def manual_auth(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"user": user}
```

## Available Dependencies

### `require_auth(request: Request)`
- Raises HTTPException if user is not authenticated
- Returns user data if authenticated

### `require_admin(request: Request)`  
- Requires authentication AND admin privileges
- Returns admin user data

### `get_current_user(request: Request)`
- Returns user data or None (doesn't raise exception)
- For optional authentication

### `get_current_user_id(request: Request)`
- Returns user ID string or None
- Quick access to user ID

## JWT Token Structure

The middleware expects JWT tokens with this structure:

```json
{
  "user_id": "123",
  "email": "user@example.com",
  "name": "User Name",
  "is_admin": false,
  "exp": 1693574400,
  "iat": 1693488000
}
```

## Demo Credentials

For testing purposes, these credentials are available:

**Admin User:**
- Email: `admin@sprintsync.com`
- Password: `admin123`

**Regular User:**
- Email: `user@sprintsync.com` 
- Password: `user123`

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Missing authorization token",
  "code": "AUTH_001"
}
```

### 403 Forbidden (Admin Required)
```json
{
  "detail": "Admin privileges required"
}
```

## Testing the Middleware

### 1. Test Public Route (No Auth Required)
```bash
curl http://localhost:8000/api/v1/auth/public
```

### 2. Test Protected Route (Auth Required)
```bash
# Without token (should fail)
curl http://localhost:8000/api/v1/auth/protected

# With token (should succeed)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/auth/protected
```

### 3. Test Admin Route
```bash
# Login as admin first, then:
curl -H "Authorization: Bearer ADMIN_TOKEN" \
     http://localhost:8000/api/v1/auth/admin-only
```

## Customization

### Custom Protected Paths

```python
app.add_middleware(
    JWTAuthMiddleware,
    protected_paths=[
        "/api/v1/custom",
        "/admin"
    ],
    excluded_paths=[
        "/public",
        "/health"
    ]
)
```

### Custom Secret Key

```python
app.add_middleware(
    JWTAuthMiddleware,
    secret_key="your_custom_secret_key",
    algorithm="HS256"
)
```

## Security Best Practices

1. **Strong Secret Key**: Use a cryptographically strong secret key
2. **Environment Variables**: Never hardcode secrets in source code  
3. **Token Expiration**: Set appropriate token expiration times
4. **HTTPS Only**: Use HTTPS in production
5. **Rotate Keys**: Regularly rotate JWT secret keys
6. **Validate Claims**: Always validate required JWT claims

## Troubleshooting

### Common Issues

1. **"Missing authorization token"**: Add `Authorization: Bearer <token>` header
2. **"Invalid or expired token"**: Check token format and expiration
3. **"Admin privileges required"**: Ensure user has `is_admin: true` in token
4. **Path not protected**: Check if path matches `protected_paths` configuration

### Debug Logging

Enable debug logging to see authentication details:

```python
import logging
logging.getLogger("sprintsync.auth_middleware").setLevel(logging.DEBUG)
```
