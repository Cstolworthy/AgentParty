# Code Review Guide

## Review Process

### 1. Initial Scan
- [ ] Code compiles/builds without errors
- [ ] All tests pass
- [ ] Linting passes with zero warnings
- [ ] No obvious security issues

### 2. Detailed Review
- [ ] Logic correctness
- [ ] Edge cases handled
- [ ] Error handling present
- [ ] Performance considerations
- [ ] Code readability

### 3. Standards Check
- [ ] Naming conventions followed
- [ ] Documentation present
- [ ] Code organization logical
- [ ] Consistent style

## What to Look For

### Logic Issues
❌ **Off-by-one errors**:
```csharp
// Wrong
for (int i = 0; i <= array.Length; i++) // OutOfBoundsException

// Correct
for (int i = 0; i < array.Length; i++)
```

❌ **Null reference bugs**:
```csharp
// Wrong
var email = user.Email.ToLower(); // NullReferenceException if Email is null

// Correct
var email = user.Email?.ToLower() ?? string.Empty;
```

❌ **Race conditions**:
```typescript
// Wrong
let counter = 0;
async function increment() {
  const current = counter;
  await delay(100);
  counter = current + 1; // Lost updates!
}

// Correct
let counter = 0;
const lock = new Mutex();
async function increment() {
  await lock.acquire();
  counter++;
  lock.release();
}
```

### Performance Issues

❌ **N+1 Query Problem**:
```csharp
// Wrong
var users = await _context.Users.ToListAsync();
foreach (var user in users) {
    user.Posts = await _context.Posts
        .Where(p => p.UserId == user.Id)
        .ToListAsync(); // N+1 queries!
}

// Correct
var users = await _context.Users
    .Include(u => u.Posts) // Single query with join
    .ToListAsync();
```

❌ **Inefficient Loops**:
```typescript
// Wrong
for (let i = 0; i < array.length; i++) { // Recalculates length every iteration
    // ...
}

// Correct
const len = array.length;
for (let i = 0; i < len; i++) {
    // ...
}

// Better
for (const item of array) {
    // ...
}
```

### Security Issues

❌ **SQL Injection**:
```csharp
// NEVER DO THIS
var query = $"SELECT * FROM Users WHERE Email = '{email}'";

// Always use parameters
var query = "SELECT * FROM Users WHERE Email = @Email";
```

❌ **Hardcoded Secrets**:
```typescript
// NEVER DO THIS
const API_KEY = "sk_live_abc123def456";

// Use environment variables
const API_KEY = process.env.API_KEY;
```

❌ **XSS Vulnerability**:
```typescript
// Wrong (Angular)
this.innerHTML = userInput; // XSS vulnerability!

// Correct
this.sanitizedHTML = this.sanitizer.sanitize(SecurityContext.HTML, userInput);
```

### Memory Leaks

❌ **Angular Subscription Leak**:
```typescript
// Wrong
export class Component {
  ngOnInit() {
    this.service.getData().subscribe(data => {
      this.data = data; // Never unsubscribed!
    });
  }
}

// Correct - Option 1: Async pipe
<div>{{ data$ | async }}</div>

// Correct - Option 2: Unsubscribe
export class Component implements OnDestroy {
  private destroy$ = new Subject<void>();
  
  ngOnInit() {
    this.service.getData()
      .pipe(takeUntil(this.destroy$))
      .subscribe(data => this.data = data);
  }
  
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

❌ **Event Listener Leak**:
```typescript
// Wrong
document.addEventListener('click', handleClick);
// Never removed!

// Correct
useEffect(() => {
  document.addEventListener('click', handleClick);
  return () => document.removeEventListener('click', handleClick);
}, []);
```

## Code Readability

### Good Practices

✅ **Meaningful Names**:
```csharp
// Bad
var d = DateTime.Now.AddDays(30);

// Good
var expirationDate = DateTime.Now.AddDays(30);
```

✅ **Small Functions**:
```typescript
// Bad - 100 line function doing everything

// Good - Multiple focused functions
function validateUser(user: User): boolean { }
function hashPassword(password: string): string { }
function saveToDatabase(user: User): Promise<void> { }
```

✅ **Guard Clauses**:
```csharp
// Bad - Nested ifs
public async Task<User> GetUser(Guid id) {
    if (id != Guid.Empty) {
        var user = await _repository.FindAsync(id);
        if (user != null) {
            if (user.IsActive) {
                return user;
            }
        }
    }
    return null;
}

// Good - Guard clauses
public async Task<User> GetUser(Guid id) {
    if (id == Guid.Empty) return null;
    
    var user = await _repository.FindAsync(id);
    if (user == null) return null;
    if (!user.IsActive) return null;
    
    return user;
}
```

✅ **Extract Complex Conditions**:
```typescript
// Bad
if (user.age >= 18 && user.hasAcceptedTerms && !user.isBanned && user.emailVerified) {
    // ...
}

// Good
const isEligibleUser = user.age >= 18 
    && user.hasAcceptedTerms 
    && !user.isBanned 
    && user.emailVerified;

if (isEligibleUser) {
    // ...
}
```

## Review Feedback Template

### For PASS with Minor Issues

```markdown
## Code Review: PASS ✅

### Summary
Code meets standards with minor suggestions for improvement.

### Minor Issues (Optional Improvements)
- Line 42: Consider extracting this condition to a named variable for readability
- Line 67: This method could be simplified using LINQ `.Where().Select()`

### Positive Observations
- Good test coverage (85%)
- Clear naming conventions
- Proper error handling

**Status**: APPROVED - Proceed to QA Testing
```

### For FAIL with Issues

```markdown
## Code Review: FAIL ❌

### Critical Issues (Must Fix)
1. **Security**: Hardcoded API key on line 23
   - Fix: Move to environment variable
   - File: `src/services/api.service.ts:23`

2. **Memory Leak**: Unsubscribed observable on line 56
   - Fix: Use async pipe or unsubscribe in ngOnDestroy
   - File: `src/components/user-list.component.ts:56`

3. **Linting**: 12 ESLint errors
   - Run: `npm run lint:fix`

### Standards Violations
- Missing TSDoc comments on exported functions
- Inconsistent naming (mixing camelCase and snake_case)
- Test coverage below 80% (current: 65%)

**Status**: REJECTED - Fix issues and resubmit
**Return To**: Implementation step
```

## Auto-Fix Scripts

### C#
```bash
# Format code
dotnet format

# Run analyzers
dotnet build /p:TreatWarningsAsErrors=true
```

### Node.js
```bash
# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Run all checks
npm run lint && npm test
```

### Angular
```bash
# Fix linting
ng lint --fix

# Format code
npm run format

# Run tests with coverage
ng test --code-coverage
```

## Review Checklist Summary

Before approving code:
- [ ] All tests pass
- [ ] Linting passes (zero warnings)
- [ ] Code coverage ≥ 80%
- [ ] No security vulnerabilities
- [ ] No performance red flags
- [ ] Naming conventions followed
- [ ] Documentation present
- [ ] No code smells
- [ ] Error handling consistent
- [ ] Memory leaks prevented
