# Test Cases Library

## User Registration Test Cases

### TC-001: Valid Registration
**Objective**: Verify user can register with valid data
**Priority**: High
**Prerequisites**: None

**Steps**:
1. Navigate to /register
2. Enter valid email: test@example.com
3. Enter valid password: SecurePass123!
4. Enter name: Test User
5. Click Submit

**Expected Result**:
- User created in database
- Confirmation email sent
- Redirected to login page
- Success message displayed

**Test Data**:
```json
{
  "email": "test@example.com",
  "password": "SecurePass123!",
  "name": "Test User"
}
```

### TC-002: Duplicate Email
**Objective**: Verify system rejects duplicate email
**Priority**: High
**Prerequisites**: User with test@example.com exists

**Steps**:
1. Navigate to /register
2. Enter existing email: test@example.com
3. Enter password: Pass123!
4. Click Submit

**Expected Result**:
- Registration fails
- Error: "Email already registered"
- Status code: 400

### TC-003: Invalid Email Format
**Objective**: Verify email validation
**Priority**: Medium
**Test Data**:
| Email | Expected Result |
|-------|----------------|
| invalid | "Invalid email format" |
| @example.com | "Invalid email format" |
| test@ | "Invalid email format" |
| "" | "Email is required" |

### TC-004: Weak Password
**Objective**: Verify password strength requirements
**Priority**: High
**Test Data**:
| Password | Expected Result |
|----------|----------------|
| "123" | "Password must be at least 8 characters" |
| "password" | "Password must contain uppercase" |
| "PASSWORD" | "Password must contain lowercase" |
| "Password" | "Password must contain number" |

## User Login Test Cases

### TC-010: Successful Login
**Objective**: Verify user can log in
**Priority**: Critical
**Steps**:
1. Navigate to /login
2. Enter email: test@example.com
3. Enter password: SecurePass123!
4. Click Login

**Expected Result**:
- JWT token returned
- Redirected to dashboard
- Token stored in localStorage

### TC-011: Invalid Credentials
**Objective**: Verify login fails with wrong password
**Priority**: High
**Expected Result**:
- Login fails
- Error: "Invalid credentials"
- Status code: 401
- No token returned

### TC-012: Rate Limiting
**Objective**: Verify rate limiting on login
**Priority**: High
**Steps**:
1. Attempt login with wrong password 6 times

**Expected Result**:
- First 5 attempts: "Invalid credentials"
- 6th attempt: "Too many login attempts. Try again in 15 minutes"
- Status code: 429

### TC-013: Account Lockout
**Objective**: Verify account locks after failed attempts
**Priority**: High
**Expected Result**:
- After 5 failed attempts: Account locked for 30 minutes
- Error: "Account locked. Try again later"

## API Endpoint Test Cases

### TC-100: GET /api/users (List Users)
**Authorization**: Required (JWT)
**Test Cases**:

| Scenario | Input | Expected Output | Status Code |
|----------|-------|----------------|-------------|
| No auth | - | "Authentication required" | 401 |
| Valid auth | - | List of users | 200 |
| Pagination | ?page=2&pageSize=20 | Page 2 results | 200 |
| Invalid page | ?page=-1 | "Invalid page number" | 400 |

### TC-101: GET /api/users/:id (Get User)
**Test Cases**:
| Scenario | Input | Expected Output | Status Code |
|----------|-------|----------------|-------------|
| Valid ID | existing-uuid | User object | 200 |
| Invalid ID | invalid-uuid | "User not found" | 404 |
| Malformed ID | "abc" | "Invalid ID format" | 400 |

### TC-102: POST /api/users (Create User)
**Test Cases**:
| Scenario | Input | Expected Output | Status Code |
|----------|-------|----------------|-------------|
| Valid | Valid user data | Created user | 201 |
| Duplicate email | Existing email | "Email exists" | 409 |
| Missing field | No email | Validation error | 400 |
| Invalid format | Bad email | Validation error | 400 |

### TC-103: PUT /api/users/:id (Update User)
**Test Cases**:
| Scenario | Input | Expected Output | Status Code |
|----------|-------|----------------|-------------|
| Valid update | Valid data | Updated user | 200 |
| Not found | Invalid ID | "User not found" | 404 |
| Unauthorized | Different user | "Forbidden" | 403 |

### TC-104: DELETE /api/users/:id (Delete User)
**Test Cases**:
| Scenario | Input | Expected Output | Status Code |
|----------|-------|----------------|-------------|
| Valid delete | Valid ID | Success | 204 |
| Not found | Invalid ID | "User not found" | 404 |
| Unauthorized | Different user | "Forbidden" | 403 |

## Edge Cases & Boundary Tests

### TC-200: Maximum Input Length
**Objective**: Verify max length validation
| Field | Max Length | Test Input | Expected Result |
|-------|-----------|------------|----------------|
| Email | 255 | 256 chars | "Email too long" |
| Name | 100 | 101 chars | "Name too long" |
| Password | 128 | 129 chars | "Password too long" |

### TC-201: Special Characters
**Objective**: Verify special character handling
**Test Data**:
```javascript
const specialChars = `!@#$%^&*()_+-={}[]|:;"'<>,.?/`;
// Test in name, email, etc.
```

### TC-202: SQL Injection Attempts
**Objective**: Verify SQL injection prevention
**Test Data**:
```sql
-- Attempt 1
' OR '1'='1

-- Attempt 2
'; DROP TABLE users; --

-- Attempt 3
<script>alert('XSS')</script>
```
**Expected Result**: All rejected or sanitized

### TC-203: Unicode Characters
**Objective**: Verify Unicode support
**Test Data**:
```
Name: "José García 日本語"
Expected: Stored and retrieved correctly
```

### TC-204: Concurrent Requests
**Objective**: Verify system handles concurrent operations
**Steps**:
1. Send 100 concurrent POST requests
2. Verify all processed correctly
3. Check for race conditions

**Expected Result**:
- All requests processed
- No duplicate IDs created
- No data corruption

## Performance Test Cases

### TC-300: Response Time
**Objective**: Verify API response times
| Endpoint | Max Response Time (p95) |
|----------|------------------------|
| GET /api/users | 200ms |
| POST /api/users | 300ms |
| GET /api/users/:id | 100ms |

### TC-301: Load Test
**Objective**: Verify system under load
**Scenario**:
- 100 concurrent users
- Duration: 5 minutes
- Operations: CRUD operations

**Success Criteria**:
- Response time < 500ms (p95)
- Error rate < 1%
- No memory leaks
- CPU usage < 80%

### TC-302: Stress Test
**Objective**: Find breaking point
**Scenario**:
- Gradually increase load
- Monitor system resources
- Identify failure point

**Metrics to Track**:
- Requests per second
- Response times
- Error rates
- Resource utilization

## Security Test Cases

### TC-400: Authentication Bypass
**Objective**: Verify auth cannot be bypassed
**Attempts**:
1. Access protected endpoint without token
2. Use expired token
3. Use modified token
4. Use another user's token

**Expected Result**: All attempts rejected with 401

### TC-401: Authorization Check
**Objective**: Verify users can only access their data
**Steps**:
1. User A creates resource
2. User B attempts to access/modify User A's resource

**Expected Result**: Denied with 403 Forbidden

### TC-402: XSS Prevention
**Objective**: Verify XSS attacks blocked
**Test Data**:
```html
<script>alert('XSS')</script>
<img src=x onerror="alert('XSS')">
```
**Expected Result**: Sanitized or escaped

### TC-403: CSRF Prevention
**Objective**: Verify CSRF protection
**Steps**:
1. Attempt state-changing operation from external site

**Expected Result**: Rejected (CSRF token validation)

## Regression Test Suite

Must pass before every release:
- [ ] All critical test cases (TC-010, TC-100-104)
- [ ] Authentication flow
- [ ] User CRUD operations
- [ ] Input validation
- [ ] Error handling
- [ ] Performance benchmarks
- [ ] Security tests
