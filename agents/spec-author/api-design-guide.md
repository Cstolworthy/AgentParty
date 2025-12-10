# API Design Guide

## REST API Best Practices

### Resource Naming
✅ **Good**:
- `/api/users` (plural nouns)
- `/api/users/{id}` (specific resource)
- `/api/users/{id}/posts` (nested resources)

❌ **Bad**:
- `/api/getUsers` (verbs in URL)
- `/api/user` (singular)
- `/api/users/posts` (unclear relationship)

### HTTP Verbs

| Verb | Purpose | Example |
|------|---------|---------|
| GET | Retrieve resource(s) | `GET /api/users` |
| POST | Create new resource | `POST /api/users` |
| PUT | Full update (replace) | `PUT /api/users/{id}` |
| PATCH | Partial update | `PATCH /api/users/{id}` |
| DELETE | Remove resource | `DELETE /api/users/{id}` |

### Status Codes

**Success**:
- 200 OK - GET, PUT, PATCH successful
- 201 Created - POST successful
- 204 No Content - DELETE successful

**Client Errors**:
- 400 Bad Request - Invalid input
- 401 Unauthorized - Auth required
- 403 Forbidden - No permission
- 404 Not Found - Resource doesn't exist
- 409 Conflict - Duplicate resource
- 422 Unprocessable Entity - Business rule violation

**Server Errors**:
- 500 Internal Server Error - Unexpected error
- 503 Service Unavailable - System down

### Pagination

Always paginate large collections:

**Request**:
```
GET /api/users?page=2&pageSize=20&sortBy=createdAt&sortOrder=desc
```

**Response**:
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "pageSize": 20,
    "totalItems": 150,
    "totalPages": 8,
    "hasNext": true,
    "hasPrevious": true
  }
}
```

### Filtering

Use query parameters for filtering:
```
GET /api/users?status=active&role=admin&createdAfter=2024-01-01
```

### Searching

Use `q` parameter for full-text search:
```
GET /api/users?q=john&fields=name,email
```

### Versioning

Include version in URL:
```
/api/v1/users
/api/v2/users
```

### Response Format

**Success**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "createdAt": "2024-12-10T20:00:00Z"
}
```

**Error**:
```json
{
  "error": "Validation failed",
  "message": "The email field is required",
  "details": {
    "email": ["Email is required"],
    "password": ["Password must be at least 8 characters"]
  },
  "timestamp": "2024-12-10T20:00:00Z",
  "path": "/api/users",
  "requestId": "uuid"
}
```

## C#-Specific Patterns

### Controller Pattern
```csharp
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _service;
    
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<UserDto>), 200)]
    public async Task<ActionResult<IEnumerable<UserDto>>> GetAll()
    {
        var users = await _service.GetAllAsync();
        return Ok(users);
    }
    
    [HttpPost]
    [ProducesResponseType(typeof(UserDto), 201)]
    [ProducesResponseType(400)]
    public async Task<ActionResult<UserDto>> Create(CreateUserDto dto)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);
            
        var user = await _service.CreateAsync(dto);
        return CreatedAtAction(nameof(GetById), new { id = user.Id }, user);
    }
}
```

### DTO Pattern
```csharp
// Request DTO
public class CreateUserDto
{
    [Required]
    [EmailAddress]
    public string Email { get; set; }
    
    [Required]
    [MinLength(8)]
    public string Password { get; set; }
    
    [Required]
    [MaxLength(100)]
    public string Name { get; set; }
}

// Response DTO
public class UserResponseDto
{
    public Guid Id { get; set; }
    public string Email { get; set; }
    public string Name { get; set; }
    public DateTime CreatedAt { get; set; }
}
```

## Node-Specific Patterns

### Express Controller
```typescript
import { Request, Response, NextFunction } from 'express';

export class UserController {
  constructor(private userService: UserService) {}
  
  async getAll(req: Request, res: Response, next: NextFunction) {
    try {
      const users = await this.userService.getAll();
      res.json(users);
    } catch (error) {
      next(error);
    }
  }
  
  async create(req: Request, res: Response, next: NextFunction) {
    try {
      const dto = CreateUserSchema.parse(req.body);
      const user = await this.userService.create(dto);
      res.status(201).json(user);
    } catch (error) {
      next(error);
    }
  }
}
```

### Middleware for Validation
```typescript
export const validateRequest = (schema: z.ZodSchema) => {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      schema.parse(req.body);
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          error: 'Validation failed',
          details: error.errors
        });
      } else {
        next(error);
      }
    }
  };
};
```

### Error Handler Middleware
```typescript
export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  console.error(err.stack);
  
  if (err instanceof ValidationError) {
    return res.status(400).json({
      error: err.message,
      details: err.details
    });
  }
  
  res.status(500).json({
    error: 'Internal server error',
    message: err.message
  });
};
```

## Angular-Specific Patterns

### HTTP Service
```typescript
@Injectable({ providedIn: 'root' })
export class UserService {
  private apiUrl = '/api/users';
  
  constructor(private http: HttpClient) {}
  
  getAll(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl).pipe(
      catchError(this.handleError)
    );
  }
  
  create(user: CreateUserRequest): Observable<User> {
    return this.http.post<User>(this.apiUrl, user).pipe(
      catchError(this.handleError)
    );
  }
  
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      errorMessage = `Server returned code ${error.status}: ${error.message}`;
    }
    
    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
```

### HTTP Interceptor
```typescript
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = localStorage.getItem('token');
    
    if (token) {
      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }
    
    return next.handle(req);
  }
}
```

## Authentication Patterns

### JWT Authentication Flow

1. **Login**:
```
POST /api/auth/login
Body: { email, password }
Response: { accessToken, refreshToken }
```

2. **Protected Request**:
```
GET /api/users/me
Headers: Authorization: Bearer {accessToken}
```

3. **Refresh Token**:
```
POST /api/auth/refresh
Body: { refreshToken }
Response: { accessToken }
```

### Security Headers

Always include:
```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```
