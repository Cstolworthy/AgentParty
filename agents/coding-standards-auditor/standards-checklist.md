# Coding Standards Checklist

## General Standards (All Stacks)

### Naming Conventions
- [ ] Consistent naming convention used throughout
- [ ] Names are descriptive and meaningful
- [ ] Abbreviations avoided (unless industry standard)
- [ ] No single-letter variables (except loop counters)
- [ ] Boolean variables use is/has/can prefixes

### Code Organization
- [ ] One class/component per file
- [ ] Related files grouped in appropriate folders
- [ ] File names match class/component names
- [ ] Imports organized and grouped logically
- [ ] No unused imports

### Documentation
- [ ] All public APIs documented
- [ ] Complex logic explained with comments
- [ ] No commented-out code
- [ ] README files present and up-to-date
- [ ] Inline comments explain WHY, not WHAT

### Code Quality
- [ ] Methods are focused and single-purpose
- [ ] Classes have single responsibility
- [ ] No duplicate code
- [ ] No magic numbers (use named constants)
- [ ] Error messages are clear and actionable

### Testing
- [ ] All business logic has unit tests
- [ ] Test coverage meets 80% minimum
- [ ] Tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Test names clearly describe scenario
- [ ] Edge cases are tested

## C#-Specific Standards

### Naming
- [ ] PascalCase for: Classes, Methods, Properties, Events
- [ ] camelCase with underscore for: Private fields (`_userName`)
- [ ] camelCase for: Local variables, Parameters
- [ ] ALL_CAPS for: Constants
- [ ] `IInterface` for: Interface names
- [ ] `Async` suffix for async methods

### Code Structure
- [ ] Using statements at top of file
- [ ] Namespace matches folder structure
- [ ] Properties before methods
- [ ] Public members before private
- [ ] Constructors first, then methods
- [ ] One class per file

### Language Features
- [ ] Nullable reference types enabled
- [ ] Expression-bodied members when appropriate
- [ ] String interpolation used (`$"{var}"` not `"" + var`)
- [ ] `var` used when type is obvious
- [ ] LINQ used for collections
- [ ] `async/await` for I/O operations

### Documentation
- [ ] XML docs on all public members
- [ ] `<summary>` tag present
- [ ] `<param>` tags for parameters
- [ ] `<returns>` tag for return values
- [ ] `<exception>` tags for thrown exceptions

### StyleCop Rules
```
SA1309: Field names must not begin with underscore (allow _camelCase)
SA1101: Prefix local calls with this (disable)
SA1200: Using directives must be ordered
SA1309: Field names must follow conventions
SA1600: Elements must be documented
```

## Node.js/TypeScript Standards

### Naming
- [ ] camelCase for: Variables, functions, methods
- [ ] PascalCase for: Classes, interfaces, types, enums
- [ ] SCREAMING_SNAKE_CASE for: Constants
- [ ] kebab-case for: File names
- [ ] No abbreviations in names

### Code Structure
- [ ] Imports at top of file
- [ ] External imports before internal
- [ ] One export per file (default export)
- [ ] Interfaces before classes
- [ ] Public methods before private

### TypeScript
- [ ] Strict mode enabled
- [ ] No `any` type usage
- [ ] Explicit return types on functions
- [ ] Interfaces for object shapes
- [ ] Enums for fixed sets of values
- [ ] Type guards for runtime checks

### Async Patterns
- [ ] Always use async/await (no callbacks)
- [ ] Promise.all() for parallel operations
- [ ] Proper error handling (try/catch)
- [ ] No blocking synchronous operations
- [ ] Async functions return promises

### ESLint Rules
```json
{
  "no-console": "warn",
  "no-unused-vars": "error",
  "@typescript-eslint/no-explicit-any": "error",
  "@typescript-eslint/explicit-function-return-type": "warn",
  "prefer-const": "error",
  "no-var": "error"
}
```

### Documentation
- [ ] TSDoc comments on exported functions
- [ ] `@param` tags for parameters
- [ ] `@returns` tag for return values
- [ ] `@throws` tag for exceptions
- [ ] README with usage examples

## Angular Standards

### Naming
- [ ] `*.component.ts` for components
- [ ] `*.service.ts` for services
- [ ] `*.directive.ts` for directives
- [ ] `*.pipe.ts` for pipes
- [ ] `*.module.ts` for modules
- [ ] Kebab-case for selectors

### Component Structure
- [ ] Smart/Dumb pattern enforced
- [ ] `@Input()` for data down
- [ ] `@Output()` for events up
- [ ] No business logic in templates
- [ ] OnPush change detection for dumb components
- [ ] Standalone components preferred (Angular 14+)

### Subscriptions
- [ ] Use `async` pipe in templates
- [ ] Manual subscriptions unsubscribed in `ngOnDestroy`
- [ ] Use `takeUntil` pattern for cleanup
- [ ] No memory leaks

### RxJS
- [ ] Prefer operators over imperative code
- [ ] Use `pipe()` for chaining operators
- [ ] `shareReplay()` for shared streams
- [ ] `catchError()` for error handling
- [ ] `finalize()` for cleanup

### Templates
- [ ] No complex logic in templates
- [ ] Use trackBy with *ngFor
- [ ] Avoid calling functions in templates
- [ ] Use async pipe for observables
- [ ] Accessibility attributes present

### Angular ESLint Rules
```json
{
  "@angular-eslint/component-selector": [
    "error",
    { "type": "element", "prefix": "app", "style": "kebab-case" }
  ],
  "@angular-eslint/directive-selector": [
    "error",
    { "type": "attribute", "prefix": "app", "style": "camelCase" }
  ],
  "@angular-eslint/no-output-on-prefix": "error"
}
```

## Security Checklist

### All Stacks
- [ ] No hardcoded secrets or API keys
- [ ] No sensitive data in logs
- [ ] Input validation on all user inputs
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (sanitize output)
- [ ] HTTPS enforced in production

### C#
- [ ] Secrets in User Secrets (dev) or Azure Key Vault (prod)
- [ ] Use `IConfiguration` for settings
- [ ] SQL parameters, never string concatenation
- [ ] Identity framework for authentication

### Node.js
- [ ] Environment variables for secrets
- [ ] Use `.env` files (not committed)
- [ ] Helmet.js for security headers
- [ ] Rate limiting on sensitive endpoints
- [ ] CORS configured properly

### Angular
- [ ] No secrets in frontend code
- [ ] Sanitize user-generated HTML
- [ ] Use DomSanitizer when needed
- [ ] HTTP interceptors for auth headers
- [ ] CSP headers configured

## Performance Checklist

### C#
- [ ] Async/await used for I/O
- [ ] LINQ queries optimized
- [ ] Database queries use proper indexes
- [ ] Connection pooling enabled
- [ ] Caching used appropriately

### Node.js
- [ ] Async operations don't block event loop
- [ ] Database queries use indexes
- [ ] Response compression enabled
- [ ] Static assets cached
- [ ] Connection pooling for databases

### Angular
- [ ] OnPush change detection used
- [ ] Lazy loading for routes
- [ ] trackBy used with *ngFor
- [ ] Images optimized (NgOptimizedImage)
- [ ] Bundle size monitored
- [ ] Production build optimized
