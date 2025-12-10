# Architectural Anti-Patterns to Reject

## Critical Anti-Patterns (Always FAIL)

### God Object / God Class
**Problem**: Single class does everything
**C# Example**: `UserManager` that handles auth, DB, email, logging, validation
**Fix**: Split into focused services

### Circular Dependencies
**Problem**: A depends on B, B depends on A
**Fix**: Extract shared logic to new module, use dependency inversion

### Tight Coupling
**Problem**: Classes directly instantiate dependencies
**Fix**: Use dependency injection, depend on abstractions

### Anemic Domain Model
**Problem**: Domain models with no behavior, only getters/setters
**C# Example**: Models are just DTOs, all logic in services
**Fix**: Put business logic in domain models where appropriate

### Big Ball of Mud
**Problem**: No clear architecture, everything depends on everything
**Fix**: Define clear layers with dependency rules

## C# Anti-Patterns

### Static Cling
**Problem**: Overuse of static classes/methods
**Why bad**: Untestable, global state
**Fix**: Use instance methods with DI

### Service Locator
**Problem**: Calling `ServiceLocator.Get<IService>()` instead of constructor injection
**Fix**: Use constructor injection everywhere

### Repository Returning IQueryable
**Problem**: `IQueryable<T> GetAll()` leaks persistence concerns
**Fix**: Return `IEnumerable<T>` or specific query methods

### Fat Controllers
**Problem**: Business logic in ASP.NET controllers
**Fix**: Move logic to services, controllers should be thin

## Node.js Anti-Patterns

### Callback Hell
**Problem**: Deeply nested callbacks
**Fix**: Use async/await, Promises

### Synchronous I/O
**Problem**: Using `fs.readFileSync` in production
**Fix**: Use async versions (`fs.promises`)

### Not Handling Promise Rejections
**Problem**: Unhandled promise rejections crash the app
**Fix**: Always handle errors with `.catch()` or try/catch

### Massive Route Files
**Problem**: All routes in `app.js` with inline handlers
**Fix**: Separate routes, controllers, services

### Global Variables for State
**Problem**: Using global vars for request state
**Fix**: Use request-scoped variables, middleware, context

## Angular Anti-Patterns

### Logic in Templates
**Problem**: Complex expressions in `*.html` templates
**Fix**: Move logic to component class methods

### Imperative DOM Manipulation
**Problem**: Using `document.querySelector`, `nativeElement` everywhere
**Fix**: Use Angular directives, data binding, ViewChild sparingly

### Huge Smart Components
**Problem**: 1000+ line component doing everything
**Fix**: Break into smaller smart/dumb components

### Not Unsubscribing
**Problem**: Memory leaks from open subscriptions
**Fix**: Use `async` pipe, `takeUntil`, or unsubscribe in `ngOnDestroy`

### Tightly Coupled to HTTP Details
**Problem**: Components directly calling HttpClient
**Fix**: Use services, abstract HTTP concerns

### Any Type Everywhere
**Problem**: `data: any` throughout codebase
**Fix**: Use proper TypeScript types

## Database Anti-Patterns

### N+1 Query Problem
**Problem**: Loading 1 parent + N children in separate queries
**Fix**: Use eager loading, joins, or batching

### No Connection Pooling
**Problem**: Opening new connection per request
**Fix**: Use connection pooling

### Missing Indexes
**Problem**: Slow queries on large tables
**Fix**: Add indexes on frequently queried columns

### Storing JSON as String
**Problem**: Serializing JSON to varchar instead of JSON column type
**Fix**: Use native JSON column types when available

## When to FAIL Architecture Review

Immediately reject if you see:
- ❌ No dependency injection
- ❌ Business logic in controllers/routes
- ❌ Circular dependencies
- ❌ Global mutable state
- ❌ God objects/classes
- ❌ No separation between layers
- ❌ Direct database access from presentation layer
- ❌ Synchronous I/O in Node.js
- ❌ Memory leaks (Angular subscriptions)
- ❌ Hardcoded configuration values
