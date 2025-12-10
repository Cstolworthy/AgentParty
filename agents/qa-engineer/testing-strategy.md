# Testing Strategy

## Test Pyramid

```
      /\
     /  \     E2E Tests (10%)
    /____\    
   /      \   Integration Tests (20%)
  /________\  
 /          \ Unit Tests (70%)
/____________\
```

### Unit Tests (70%)
- Fast, isolated, mock dependencies
- Test business logic thoroughly
- Target: 80%+ coverage

### Integration Tests (20%)
- Test component interactions
- Use test database
- Verify data flows

### E2E Tests (10%)
- Test critical user journeys
- Slower but comprehensive
- Focus on happy paths

## Test Coverage Goals

### Minimum Requirements
- **Overall Coverage**: 80%
- **Branch Coverage**: 75%
- **Critical Paths**: 100%

### What to Test
✅ **Always Test**:
- Business logic
- Data validation
- Error handling
- Edge cases
- Security features
- API endpoints
- Database operations

❌ **Don't Test**:
- Third-party libraries
- Framework code
- Simple getters/setters
- Configuration files

## C# Testing Strategy

### Unit Test Example (xUnit)
```csharp
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _mockRepo;
    private readonly UserService _service;
    
    public UserServiceTests()
    {
        _mockRepo = new Mock<IUserRepository>();
        _service = new UserService(_mockRepo.Object);
    }
    
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
        _mockRepo.Verify(r => r.AddAsync(It.IsAny<User>()), Times.Once);
    }
    
    [Theory]
    [InlineData("")] // Empty email
    [InlineData("invalid")] // Invalid format
    [InlineData(null)] // Null email
    public async Task CreateUser_InvalidEmail_ThrowsException(string email)
    {
        // Arrange
        var dto = new CreateUserDto { Email = email };
        
        // Act & Assert
        await Assert.ThrowsAsync<ValidationException>(
            () => _service.CreateUserAsync(dto)
        );
    }
}
```

### Integration Test Example
```csharp
public class UserApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    
    public UserApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }
    
    [Fact]
    public async Task CreateUser_ValidInput_Returns201()
    {
        // Arrange
        var request = new { email = "test@example.com", password = "Pass123!", name = "Test" };
        
        // Act
        var response = await _client.PostAsJsonAsync("/api/users", request);
        
        // Assert
        response.EnsureSuccessStatusCode();
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
    }
}
```

## Node.js Testing Strategy

### Unit Test Example (Jest)
```typescript
describe('UserService', () => {
  let service: UserService;
  let mockRepo: jest.Mocked<IUserRepository>;
  
  beforeEach(() => {
    mockRepo = {
      findByEmail: jest.fn(),
      save: jest.fn()
    } as any;
    service = new UserService(mockRepo);
  });
  
  describe('createUser', () => {
    it('should create user with valid input', async () => {
      // Arrange
      const dto = { email: 'test@example.com', password: 'Pass123!', name: 'Test' };
      mockRepo.save.mockResolvedValue({ id: '123', ...dto });
      
      // Act
      const result = await service.createUser(dto);
      
      // Assert
      expect(result).toBeDefined();
      expect(result.email).toBe(dto.email);
      expect(mockRepo.save).toHaveBeenCalledTimes(1);
    });
    
    it('should throw error for duplicate email', async () => {
      // Arrange
      mockRepo.findByEmail.mockResolvedValue({ id: '1', email: 'test@example.com' });
      
      // Act & Assert
      await expect(service.createUser({ email: 'test@example.com' }))
        .rejects.toThrow('Email already exists');
    });
  });
});
```

### API Integration Test (Supertest)
```typescript
describe('POST /api/users', () => {
  it('should create user and return 201', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', password: 'Pass123!', name: 'Test' })
      .expect(201);
    
    expect(response.body).toHaveProperty('id');
    expect(response.body.email).toBe('test@example.com');
  });
  
  it('should return 400 for invalid email', async () => {
    await request(app)
      .post('/api/users')
      .send({ email: 'invalid', password: 'Pass123!', name: 'Test' })
      .expect(400);
  });
});
```

## Angular Testing Strategy

### Component Test Example
```typescript
describe('UserListComponent', () => {
  let component: UserListComponent;
  let fixture: ComponentFixture<UserListComponent>;
  let mockService: jasmine.SpyObj<UserService>;
  
  beforeEach(() => {
    mockService = jasmine.createSpyObj('UserService', ['getUsers']);
    
    TestBed.configureTestingModule({
      declarations: [UserListComponent],
      providers: [{ provide: UserService, useValue: mockService }]
    });
    
    fixture = TestBed.createComponent(UserListComponent);
    component = fixture.componentInstance;
  });
  
  it('should display users', () => {
    // Arrange
    const users = [{ id: '1', name: 'Test User' }];
    mockService.getUsers.and.returnValue(of(users));
    
    // Act
    fixture.detectChanges();
    
    // Assert
    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('.user-name').textContent).toContain('Test User');
  });
  
  it('should handle error', () => {
    // Arrange
    mockService.getUsers.and.returnValue(throwError(() => new Error('API Error')));
    
    // Act
    fixture.detectChanges();
    
    // Assert
    expect(component.error).toBe('Failed to load users');
  });
});
```

### E2E Test Example (Cypress)
```typescript
describe('User Registration', () => {
  it('should allow user to register', () => {
    cy.visit('/register');
    cy.get('[data-testid="email"]').type('test@example.com');
    cy.get('[data-testid="password"]').type('SecurePass123!');
    cy.get('[data-testid="name"]').type('Test User');
    cy.get('[data-testid="submit"]').click();
    
    cy.url().should('include', '/login');
    cy.contains('Registration successful').should('be.visible');
  });
  
  it('should show validation errors', () => {
    cy.visit('/register');
    cy.get('[data-testid="submit"]').click();
    
    cy.contains('Email is required').should('be.visible');
    cy.contains('Password is required').should('be.visible');
  });
});
```

## Performance Testing

### Load Testing (k6)
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 20 }, // Ramp up
    { duration: '1m', target: 20 },  // Stay at 20 users
    { duration: '30s', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
  },
};

export default function () {
  const res = http.get('http://localhost:8000/api/users');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

## Accessibility Testing (Angular)

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

it('should have no accessibility violations', async () => {
  const { container } = render(UserListComponent);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## Test Data Management

### Use Test Fixtures
```typescript
// fixtures/users.ts
export const validUser = {
  email: 'test@example.com',
  password: 'SecurePass123!',
  name: 'Test User'
};

export const invalidUsers = {
  emptyEmail: { ...validUser, email: '' },
  invalidEmail: { ...validUser, email: 'invalid' },
  shortPassword: { ...validUser, password: '123' }
};
```

### Database Seeding
```typescript
beforeEach(async () => {
  await database.clear();
  await database.seed([
    { id: '1', email: 'user1@example.com', name: 'User 1' },
    { id: '2', email: 'user2@example.com', name: 'User 2' }
  ]);
});
```

## Continuous Testing

### Run Tests on Every Commit
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: npm test
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```
