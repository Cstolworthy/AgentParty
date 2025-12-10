# Engineering Manager Review Criteria

## Comprehensive Review Checklist

### 1. Quality Gates Status
- [ ] Standards Audit: PASSED
- [ ] QA Testing: PASSED
- [ ] Policy/Security Gate: PASSED
- [ ] All previous approvals obtained

### 2. Code Quality Assessment

#### Readability
- [ ] Code is self-documenting
- [ ] Meaningful variable/function names
- [ ] Consistent formatting
- [ ] Comments explain "why", not "what"
- [ ] No overly complex methods

#### Maintainability
- [ ] Follows SOLID principles
- [ ] Low coupling, high cohesion
- [ ] No code duplication
- [ ] Easy to modify and extend
- [ ] Technical debt documented if introduced

#### Best Practices
- [ ] Proper error handling
- [ ] Logging at appropriate levels
- [ ] Configuration externalized
- [ ] Dependencies managed correctly
- [ ] Async patterns used (where applicable)

### 3. Architecture Review

#### Design Alignment
- [ ] Follows agreed architecture
- [ ] Proper layer separation
- [ ] Dependencies flow correctly
- [ ] Design patterns used appropriately

#### Scalability
- [ ] Can handle growth
- [ ] Database queries optimized
- [ ] Caching strategy appropriate
- [ ] No obvious bottlenecks

#### Performance
- [ ] Meets performance requirements
- [ ] No N+1 query problems
- [ ] Efficient algorithms used
- [ ] Resource usage reasonable

### 4. Testing Evaluation

#### Coverage
- [ ] Line coverage ≥ 80%
- [ ] Branch coverage ≥ 75%
- [ ] Critical paths 100% covered
- [ ] Edge cases tested

#### Test Quality
- [ ] Tests are meaningful
- [ ] Tests follow AAA pattern
- [ ] No flaky tests
- [ ] Integration tests present
- [ ] E2E tests for critical flows

#### Test Execution
- [ ] All tests passing
- [ ] Tests run in CI/CD
- [ ] No tests skipped/ignored
- [ ] Fast execution times

### 5. Documentation Review

#### Code Documentation
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] XML docs (C#) / TSDoc (TypeScript)
- [ ] No stale comments

#### Project Documentation
- [ ] README up to date
- [ ] API documentation current
- [ ] Architecture diagrams present
- [ ] Deployment guide available
- [ ] Troubleshooting guide

### 6. Security Assessment

#### Authentication & Authorization
- [ ] Auth correctly implemented
- [ ] Authorization checks present
- [ ] Tokens properly secured
- [ ] Session management correct

#### Input Validation
- [ ] All inputs validated
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] CSRF protection present

#### Configuration
- [ ] No hardcoded secrets
- [ ] Environment-based config
- [ ] Secure defaults
- [ ] Sensitive data encrypted

### 7. Production Readiness

#### Deployment
- [ ] Deployment process documented
- [ ] Rollback plan exists
- [ ] Migration scripts tested
- [ ] Zero-downtime strategy (if needed)

#### Monitoring
- [ ] Logging configured
- [ ] Metrics/monitoring in place
- [ ] Error tracking setup
- [ ] Health checks implemented

#### Operations
- [ ] Runbooks available
- [ ] Alerting configured
- [ ] Backup strategy defined
- [ ] Disaster recovery plan

## Decision Framework

### Automatic APPROVE if:
- ✅ All quality gates passed
- ✅ Low risk changes
- ✅ Previous approvals obtained
- ✅ No concerns raised

### CONDITIONAL APPROVE if:
- ⚠️ Minor issues that don't block deployment
- ⚠️ Technical debt accepted with plan
- ⚠️ Medium risk with mitigation plan
- ⚠️ Staged rollout recommended

### Automatic REJECT if:
- ❌ Any quality gate failed
- ❌ Critical bugs present
- ❌ Security vulnerabilities
- ❌ Insufficient test coverage
- ❌ High risk without proper review

## Risk vs. Reward Analysis

When making decisions, consider:

### Business Value
- How critical is this feature?
- What's the cost of delay?
- What's the opportunity?

### Technical Risk
- How complex is the change?
- What's the blast radius?
- Can we roll back easily?
- What's the worst case?

### Quality vs. Speed
- Can we ship with minor issues?
- Is technical debt acceptable?
- Should we do staged rollout?
- Do we need feature flags?

## Example Scenarios

### Scenario 1: New Feature with Minor Issues
**Situation**: Feature complete, tests pass, minor code smell detected
**Decision**: APPROVE with follow-up ticket
**Reasoning**: Minor issues don't justify blocking, create tech debt ticket

### Scenario 2: Bug Fix with Inadequate Tests
**Situation**: Critical bug fix, no tests added
**Decision**: CONDITIONAL - Add tests first
**Reasoning**: Bug fixes without tests lead to regressions

### Scenario 3: Refactoring without Business Value
**Situation**: Large refactor, no new features, introduces risk
**Decision**: REJECT - Schedule as separate effort
**Reasoning**: Risk doesn't justify the change right now

### Scenario 4: Security Fix
**Situation**: Security vulnerability patch, fast-tracked
**Decision**: APPROVE if fix verified
**Reasoning**: Security takes priority, can refine later
