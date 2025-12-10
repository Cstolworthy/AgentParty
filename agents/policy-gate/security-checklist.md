# Security Checklist

## OWASP Top 10 (2021)

### A01:2021 - Broken Access Control
- [ ] Authorization checks on all endpoints
- [ ] Resource-level access control
- [ ] No direct object references without validation
- [ ] CORS properly configured
- [ ] Rate limiting implemented

### A02:2021 - Cryptographic Failures
- [ ] HTTPS enforced in production
- [ ] Sensitive data encrypted at rest
- [ ] Strong encryption algorithms (AES-256)
- [ ] Secure key management
- [ ] TLS 1.2+ only

### A03:2021 - Injection
- [ ] Parameterized queries (no string concatenation)
- [ ] Input validation and sanitization
- [ ] ORM usage (prevents SQL injection)
- [ ] Command injection prevented
- [ ] LDAP injection prevented

### A04:2021 - Insecure Design
- [ ] Threat modeling performed
- [ ] Security requirements defined
- [ ] Secure by default
- [ ] Defense in depth
- [ ] Fail securely

### A05:2021 - Security Misconfiguration
- [ ] No default credentials
- [ ] Error messages don't leak info
- [ ] Security headers configured
- [ ] Unnecessary features disabled
- [ ] Components up to date

### A06:2021 - Vulnerable Components
- [ ] Dependencies regularly updated
- [ ] No known CVEs in dependencies
- [ ] Automated vulnerability scanning
- [ ] Software Bill of Materials (SBOM)

### A07:2021 - Identification & Authentication Failures
- [ ] Multi-factor authentication where appropriate
- [ ] Strong password policy
- [ ] Account lockout after failed attempts
- [ ] Secure session management
- [ ] No credential stuffing vulnerabilities

### A08:2021 - Software & Data Integrity Failures
- [ ] Code signing
- [ ] CI/CD pipeline security
- [ ] Unsigned/unverified updates prevented
- [ ] Serialization attacks prevented

### A09:2021 - Security Logging & Monitoring Failures
- [ ] All authentication events logged
- [ ] Security events logged
- [ ] Logs include sufficient context
- [ ] Logs protected from tampering
- [ ] Anomaly detection

### A10:2021 - Server-Side Request Forgery (SSRF)
- [ ] Validate all URLs
- [ ] Whitelist allowed domains
- [ ] Network segmentation
- [ ] No access to internal services

## Common Vulnerabilities

### SQL Injection
```csharp
// ❌ NEVER DO THIS
var query = $"SELECT * FROM Users WHERE Email = '{email}'";

// ✅ ALWAYS DO THIS
var query = "SELECT * FROM Users WHERE Email = @Email";
```

### XSS (Cross-Site Scripting)
```typescript
// ❌ Dangerous
element.innerHTML = userInput;

// ✅ Safe (Angular)
this.sanitizedContent = this.sanitizer.sanitize(SecurityContext.HTML, userInput);
```

### Hardcoded Secrets
```typescript
// ❌ NEVER
const API_KEY = "sk_live_abc123";

// ✅ ALWAYS
const API_KEY = process.env.API_KEY;
```

### Weak Password Hashing
```csharp
// ❌ NEVER
var hash = MD5.Create().ComputeHash(password);

// ✅ ALWAYS
var hash = BCrypt.HashPassword(password, workFactor: 12);
```

## Security Headers

Required headers:
```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
```

## Authentication Best Practices

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- Consider special characters
- Check against breach database (HaveIBeenPwned)

### JWT Security
- Use secure signing algorithm (HS256/RS256)
- Short expiration (15-60 minutes)
- Implement refresh tokens
- Validate signature
- Check expiration
- Verify issuer and audience

### Session Management
- Secure cookie flags (HttpOnly, Secure, SameSite)
- Session timeout
- Logout invalidates session
- One session per user (or limit concurrent)

## Data Protection

### PII (Personally Identifiable Information)
Must protect:
- Names
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- Medical information
- IP addresses

### Encryption Requirements
- **At Rest**: AES-256
- **In Transit**: TLS 1.2+
- **Database**: Encrypted columns for sensitive data
- **Backups**: Encrypted backups

### Data Retention
- Define retention policy
- Auto-delete after retention period
- Comply with GDPR "right to be forgotten"
- Secure deletion (not just marking as deleted)

## Dependency Security

### Tools to Use
- **npm audit** (Node.js)
- **dotnet list package --vulnerable** (C#)
- **OWASP Dependency-Check**
- **Snyk**
- **GitHub Dependabot**

### Actions to Take
- Run vulnerability scan before every release
- Update dependencies regularly
- Review security advisories
- Test after updates

## Penetration Testing Checklist

Before production:
- [ ] Authentication bypass attempts
- [ ] Authorization bypass attempts
- [ ] SQL injection testing
- [ ] XSS testing
- [ ] CSRF testing
- [ ] Session management testing
- [ ] API fuzzing
- [ ] Rate limiting verification
