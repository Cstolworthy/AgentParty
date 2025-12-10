# Requirements Validation Criteria

## Completeness Checklist

Every requirement must answer:
- ✅ **Who**: Which user/role is affected?
- ✅ **What**: What must the system do?
- ✅ **When**: Under what conditions?
- ✅ **Where**: In which part of the system?
- ✅ **Why**: What's the business value?
- ✅ **How**: What's the expected behavior?

## SMART Requirements

Requirements should be:
- **Specific**: Precise, not vague
- **Measurable**: Quantifiable or verifiable
- **Achievable**: Technically feasible
- **Relevant**: Aligned with business goals
- **Time-bound**: Clear deadlines when applicable

## Edge Cases to Always Consider

### Input Validation
- Empty input
- Null values
- Invalid format
- Extremely long input
- Special characters
- SQL injection attempts

### Boundary Conditions
- Minimum values
- Maximum values
- Zero values
- Negative values
- Overflow scenarios

### Error Scenarios
- Network failures
- Database unavailable
- External API failures
- Permission denied
- Resource exhaustion

### Concurrency
- Multiple users editing same data
- Race conditions
- Deadlock scenarios

## Non-Functional Requirements Template

### Performance
```
- Response time: < 200ms for 95% of requests
- Throughput: Support 1000 concurrent users
- Database: Query execution < 100ms
```

### Security
```
- Authentication: JWT with 24-hour expiration
- Authorization: Role-based access control
- Data: Encrypt sensitive data at rest
- Transport: HTTPS only
```

### Usability
```
- Accessibility: WCAG 2.1 AA compliance (Angular)
- Mobile: Responsive design, mobile-first
- Error Messages: Clear, actionable guidance
```

### Reliability
```
- Uptime: 99.9% availability
- Recovery: Automatic retry with exponential backoff
- Backup: Daily database backups
```

## Red Flags to Reject

❌ **Vague Requirements**:
- "The system should be fast"
- "Users should have a good experience"
- "It should work well"

**Fix**: Make them measurable
- "API responses < 200ms"
- "Task completion rate > 90%"
- "Zero critical bugs in production"

❌ **Untestable Requirements**:
- "The UI should be beautiful"
- "Code should be elegant"

**Fix**: Define objective criteria
- "Pass WCAG 2.1 AA accessibility audit"
- "Pass automated linting with zero warnings"

❌ **Missing Edge Cases**:
- "Users can submit forms"

**Fix**: Define error scenarios
- "Display validation errors if required fields empty"
- "Show error message if network request fails"
- "Prevent duplicate submissions"
