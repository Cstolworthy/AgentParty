# Recommended Design Patterns by Stack

## C# Patterns

### Repository Pattern
**When**: Data access abstraction needed
```csharp
public interface IUserRepository {
    Task<User> GetByIdAsync(int id);
    Task<IEnumerable<User>> GetAllAsync();
    Task AddAsync(User user);
}
```

### Unit of Work Pattern
**When**: Multiple repositories need transactional consistency
```csharp
public interface IUnitOfWork {
    IUserRepository Users { get; }
    Task<int> SaveChangesAsync();
}
```

### Mediator Pattern (MediatR)
**When**: Decoupling request handlers from controllers
```csharp
public class CreateUserCommand : IRequest<UserDto> {
    public string Email { get; set; }
}
```

### Strategy Pattern
**When**: Algorithm selection at runtime
```csharp
public interface IPaymentStrategy {
    Task ProcessPayment(decimal amount);
}
```

### Factory Pattern
**When**: Complex object creation
```csharp
public interface IUserFactory {
    User CreateUser(UserType type);
}
```

## Node.js Patterns

### Middleware Pattern
**When**: Request/response processing pipeline
```typescript
app.use(authMiddleware);
app.use(loggingMiddleware);
app.use(errorHandler);
```

### Service Layer Pattern
**When**: Business logic separation
```typescript
class UserService {
    async createUser(data: CreateUserDto): Promise<User> {
        // Business logic here
    }
}
```

### Repository Pattern
**When**: Data access abstraction
```typescript
interface IUserRepository {
    findById(id: string): Promise<User | null>;
    save(user: User): Promise<User>;
}
```

### Observer Pattern (Events)
**When**: Loose coupling of components
```typescript
eventEmitter.on('user.created', handleUserCreated);
```

### Builder Pattern
**When**: Complex query or object construction
```typescript
const query = new QueryBuilder()
    .select('*')
    .from('users')
    .where('active', true)
    .build();
```

## Angular Patterns

### Smart/Dumb Components
**When**: Always for component architecture
- **Smart**: Container components with logic, DI, state
- **Dumb**: Presentational components with @Input/@Output only

### Service Pattern
**When**: Shared logic, HTTP calls, state management
```typescript
@Injectable({ providedIn: 'root' })
export class UserService {
    getUsers(): Observable<User[]> { }
}
```

### Facade Pattern
**When**: Simplifying complex subsystems
```typescript
@Injectable()
export class CheckoutFacade {
    // Hides complexity of cart, payment, shipping services
}
```

### Observer Pattern (RxJS)
**When**: Reactive data streams
```typescript
this.data$ = this.service.getData().pipe(
    map(data => transform(data)),
    catchError(err => handleError(err))
);
```

### State Management Pattern
**When**: Complex shared state
- Use Signals (Angular 17+) for simple state
- Use NgRx for complex state machines
- Use Services with BehaviorSubject for medium complexity

## Cross-Cutting Patterns

### Dependency Injection
- **All stacks**: Primary pattern for loose coupling
- Inject interfaces/abstractions, not concrete types

### Decorator/Interceptor Pattern
- **C#**: Attribute decorators, middleware
- **Node**: Express middleware, decorators
- **Angular**: HTTP interceptors, custom decorators

### Adapter Pattern
- **When**: Integrating third-party APIs
- **Why**: Isolate external dependencies behind your interface
