# Auth Utils

## Purpose
Authentication and authorization utilities for Nexus services.

## Features
- JWT token validation
- API key management
- Role-based access control (RBAC)
- Request signature verification
- Rate limiting helpers

## Usage
```javascript
const { AuthUtils } = require('@nexus/auth-utils');

const auth = new AuthUtils();

// Validate JWT token
const isValid = await auth.validateJWT(token);

// Check permissions
const hasAccess = auth.checkPermission(user, 'service:title:write');

// Verify API key
const validKey = await auth.verifyApiKey(apiKey);
```

## API
- `validateJWT(token)`: Validate JWT token
- `verifyApiKey(key)`: Verify API key
- `checkPermission(user, permission)`: Check user permission
- `generateApiKey()`: Generate new API key
- `rateLimit(identifier)`: Check rate limit