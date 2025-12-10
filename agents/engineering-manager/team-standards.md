# Team Standards & Expectations

## Development Standards

### Code Review Expectations
- All code reviewed before merge
- At least one approval required
- Address all comments before merging
- No direct commits to main/master
- PR size: < 500 lines (prefer smaller)

### Git Workflow
- Feature branches from main
- Branch naming: `feature/description`, `fix/description`
- Commit messages follow Conventional Commits
- Squash commits before merge
- Keep commit history clean

### Testing Philosophy
- Test-Driven Development (TDD) encouraged
- Tests written alongside code
- Tests must pass before merge
- Coverage gates enforced
- Integration tests for APIs

## Quality Expectations

### Minimal Quality Bar
Every PR must:
- ✅ Build successfully
- ✅ Pass all tests
- ✅ Pass linting
- ✅ Have 80%+ coverage
- ✅ Be reviewed and approved
- ✅ Update documentation

### Code Excellence
Strive for:
- **Clarity**: Code is easy to understand
- **Simplicity**: Simplest solution that works
- **Consistency**: Follows team patterns
- **Testability**: Easy to test
- **Maintainability**: Easy to change

## Technical Debt Management

### When Technical Debt is Acceptable
- Time-to-market is critical
- Temporary solution with clear plan to address
- Isolated to non-critical area
- Documented and tracked

### Technical Debt Process
1. Document the debt in code comments
2. Create a tracked ticket
3. Add to technical debt backlog
4. Review quarterly
5. Prioritize paydown

### Red Flags
- Accumulating debt without plan
- Critical paths with debt
- Security-related debt
- Performance-critical debt

## Performance Standards

### Response Times (p95)
| Endpoint Type | Target |
|--------------|--------|
| Simple GET | < 100ms |
| Complex GET | < 200ms |
| POST/PUT | < 300ms |
| Batch operations | < 1s |

### Resource Usage
- Memory: Stable, no leaks
- CPU: < 70% under normal load
- Database: Connection pooling enabled
- Caching: Used appropriately

### Scalability
- Stateless services
- Horizontal scaling supported
- No single points of failure
- Graceful degradation

## Security Standards

### Authentication
- JWT for APIs
- Secure cookie storage
- Token rotation
- Multi-factor when appropriate

### Authorization
- Role-based access control (RBAC)
- Principle of least privilege
- Resource-level permissions
- API-level authorization checks

### Data Protection
- Encrypt sensitive data at rest
- HTTPS in production
- Secure password hashing (bcrypt)
- No secrets in code

## Documentation Standards

### Code Documentation
- Public APIs fully documented
- Complex logic explained
- Examples provided
- Kept up to date

### Project Documentation
- README with setup instructions
- Architecture documentation
- API documentation (OpenAPI/Swagger)
- Deployment guide
- Troubleshooting guide

## Communication Standards

### Daily Communication
- Stand-ups: Share progress, blockers
- Slack: Quick questions, updates
- PRs: Technical discussions
- Issues: Bug reports, feature requests

### Design Discussions
- Architecture Decision Records (ADRs)
- Design docs for major features
- Team review before implementation
- Consider alternatives

### Incident Response
- Document in runbook
- Post-mortem for outages
- Share learnings
- Update processes

## Continuous Improvement

### Retrospectives
- Every sprint/milestone
- Celebrate wins
- Identify improvements
- Action items tracked

### Learning & Growth
- Pair programming encouraged
- Code reviews as teaching moments
- Tech talks and knowledge sharing
- Conference attendance supported

### Metrics We Track
- Deployment frequency
- Lead time for changes
- Time to restore service
- Change failure rate
- Test coverage
- Code quality scores

## Engineering Values

1. **Quality First**: Ship quality code, not quick code
2. **Test Everything**: If it's not tested, it's broken
3. **Automate Relentlessly**: Automate repetitive tasks
4. **Measure Continuously**: Data-driven decisions
5. **Collaborate Openly**: Share knowledge, help teammates
6. **Fail Fast**: Detect issues early, fix quickly
7. **Document Generously**: Code should explain itself
8. **Refactor Ruthlessly**: Improve code constantly
9. **Secure by Default**: Security is everyone's job
10. **Customer Focus**: Build what users need

## When to Escalate

Escalate to Engineering Manager when:
- Blocked for > 1 day
- Unclear requirements
- Technical disagreements
- Security concerns
- Performance issues
- Timeline at risk
- Need architectural guidance
- Cross-team dependencies
