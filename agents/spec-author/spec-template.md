# Technical Specification Template

## 1. System Overview

### Purpose
[What this feature/system does]

### Scope
[What's included and excluded]

### Technology Stack
- **C#**: .NET 8, Entity Framework Core 8, xUnit
- **Node**: TypeScript, Express/Fastify, Jest, Prisma
- **Angular**: Angular 17+, RxJS, Signals, Jasmine/Karma

## 2. Component Architecture

### C# Example
```
Controllers/
  ├── UserController.cs
  ├── AuthController.cs
Services/
  ├── IUserService.cs
  ├── UserService.cs
Repositories/
  ├── IUserRepository.cs
  ├── UserRepository.cs
Models/
  ├── User.cs
  ├── DTOs/
      ├── CreateUserDto.cs
      ├── UserResponseDto.cs
```

### Node Example
```
routes/
  ├── user.routes.ts
  ├── auth.routes.ts
controllers/
  ├── user.controller.ts
  ├── auth.controller.ts
services/
  ├── user.service.ts
  ├── auth.service.ts
models/
  ├── user.model.ts
  ├── interfaces/
      ├── IUser.ts
      ├── ICreateUser.ts
```

### Angular Example
```
features/
  ├── user/
      ├── components/
          ├── user-list/
          ├── user-detail/
      ├── services/
          ├── user.service.ts
      ├── models/
          ├── user.model.ts
      ├── state/
          ├── user.signals.ts
```

## 3. Data Models

### Entity: User (C#)
```csharp
public class User
{
    public Guid Id { get; set; }
    public string Email { get; set; } = string.Empty;
    public string PasswordHash { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public bool IsActive { get; set; } = true;
    
    // Navigation properties
    public ICollection<Session> Sessions { get; set; }
}

// EF Core Configuration
public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.HasKey(u => u.Id);
        builder.Property(u => u.Email).IsRequired().HasMaxLength(255);
        builder.HasIndex(u => u.Email).IsUnique();
        builder.Property(u => u.Name).IsRequired().HasMaxLength(100);
    }
}
```

### Model: User (Node/TypeScript)
```typescript
// Prisma Schema
model User {
  id           String    @id @default(uuid())
  email        String    @unique
  passwordHash String
  name         String
  createdAt    DateTime  @default(now())
  updatedAt    DateTime  @updatedAt
  isActive     Boolean   @default(true)
  
  sessions Session[]
  
  @@index([email])
}

// TypeScript Interface
export interface IUser {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
}

export interface ICreateUser {
  email: string;
  password: string;
  name: string;
}
```

### Model: User (Angular)
```typescript
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
}

export interface CreateUserRequest {
  email: string;
  password: string;
  name: string;
}

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  createdAt: string;
}
```

## 4. API Specifications

### Endpoint: Create User

**HTTP Method**: POST
**Path**: `/api/users`
**Authentication**: Not required (registration)

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Validation Rules**:
- email: Required, valid email format, unique
- password: Required, min 8 chars, 1 upper, 1 lower, 1 number
- name: Required, max 100 characters

**Success Response (201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "createdAt": "2024-12-10T20:00:00Z"
}
```

**Error Responses**:

400 Bad Request - Validation Error:
```json
{
  "error": "Validation failed",
  "details": {
    "email": ["Email is already registered"],
    "password": ["Password must contain at least one uppercase letter"]
  }
}
```

500 Internal Server Error:
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## 5. Business Logic

### Service Layer (C#)
```csharp
public interface IUserService
{
    Task<UserResponseDto> CreateUserAsync(CreateUserDto dto);
    Task<UserResponseDto?> GetUserByIdAsync(Guid id);
    Task<IEnumerable<UserResponseDto>> GetAllUsersAsync();
    Task<bool> DeleteUserAsync(Guid id);
}

public class UserService : IUserService
{
    private readonly IUserRepository _repository;
    private readonly IPasswordHasher _hasher;
    
    public UserService(IUserRepository repository, IPasswordHasher hasher)
    {
        _repository = repository;
        _hasher = hasher;
    }
    
    public async Task<UserResponseDto> CreateUserAsync(CreateUserDto dto)
    {
        // 1. Validate email uniqueness
        if (await _repository.EmailExistsAsync(dto.Email))
            throw new ValidationException("Email already registered");
        
        // 2. Hash password
        var passwordHash = _hasher.Hash(dto.Password);
        
        // 3. Create entity
        var user = new User
        {
            Email = dto.Email,
            PasswordHash = passwordHash,
            Name = dto.Name,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        
        // 4. Save to database
        await _repository.AddAsync(user);
        
        // 5. Return response DTO
        return new UserResponseDto
        {
            Id = user.Id,
            Email = user.Email,
            Name = user.Name,
            CreatedAt = user.CreatedAt
        };
    }
}
```

## 6. Validation

### C# with FluentValidation
```csharp
public class CreateUserDtoValidator : AbstractValidator<CreateUserDto>
{
    public CreateUserDtoValidator()
    {
        RuleFor(x => x.Email)
            .NotEmpty()
            .EmailAddress()
            .MaximumLength(255);
            
        RuleFor(x => x.Password)
            .NotEmpty()
            .MinimumLength(8)
            .Matches(@"[A-Z]").WithMessage("Must contain uppercase")
            .Matches(@"[a-z]").WithMessage("Must contain lowercase")
            .Matches(@"[0-9]").WithMessage("Must contain number");
            
        RuleFor(x => x.Name)
            .NotEmpty()
            .MaximumLength(100);
    }
}
```

### Node with Zod
```typescript
import { z } from 'zod';

export const CreateUserSchema = z.object({
  email: z.string().email().max(255),
  password: z.string()
    .min(8)
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/[a-z]/, 'Must contain lowercase')
    .regex(/[0-9]/, 'Must contain number'),
  name: z.string().min(1).max(100)
});

export type CreateUserRequest = z.infer<typeof CreateUserSchema>;
```

## 7. Error Handling

### Error Categories
- **400 Bad Request**: Invalid input/validation errors
- **401 Unauthorized**: Missing/invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Duplicate resource
- **422 Unprocessable Entity**: Business logic violation
- **500 Internal Server Error**: Unexpected errors

### Error Response Format
```json
{
  "error": "Error category",
  "message": "Human-readable description",
  "details": {
    "field": ["Validation error messages"]
  },
  "timestamp": "2024-12-10T20:00:00Z",
  "path": "/api/users",
  "requestId": "uuid"
}
```

## 8. Performance Considerations

### Database Optimization
- Add index on `email` (unique)
- Add index on `createdAt` for sorting
- Use connection pooling (min: 5, max: 20)
- Implement pagination (default: 20 items per page)

### Caching Strategy
- Cache user profiles for 5 minutes
- Invalidate on user update
- Use Redis for distributed caching

### Rate Limiting
- Registration: 3 attempts per hour per IP
- Login: 5 attempts per 15 minutes per IP
- API calls: 1000 requests per hour per user

## 9. Security

### Authentication
- Use JWT with 24-hour expiration
- Refresh tokens with 30-day expiration
- Implement token rotation

### Authorization
- Role-based access control (RBAC)
- Roles: admin, user, guest

### Input Sanitization
- Validate all inputs against schema
- Escape HTML in user-generated content
- Use parameterized queries (prevent SQL injection)

### Password Security
- Hash with bcrypt (cost factor 12)
- Never log passwords
- Enforce password complexity

## 10. Testing Requirements

### Unit Tests
- Test all service methods
- Test validation rules
- Test error scenarios
- Target: 80%+ code coverage

### Integration Tests
- Test API endpoints end-to-end
- Test database operations
- Test authentication flow

### Test Data
```csharp
// C# xUnit
public class UserServiceTests
{
    [Fact]
    public async Task CreateUser_ValidInput_ReturnsUser()
    {
        // Arrange
        var dto = new CreateUserDto
        {
            Email = "test@example.com",
            Password = "SecurePass123!",
            Name = "Test User"
        };
        
        // Act
        var result = await _service.CreateUserAsync(dto);
        
        // Assert
        Assert.NotNull(result);
        Assert.Equal(dto.Email, result.Email);
    }
}
```
