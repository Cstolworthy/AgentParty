# C# Development Workflow

Complete software development lifecycle for C# projects following .NET best practices, SOLID principles, and Test-Driven Development.

## Workflow Overview

This workflow ensures high-quality C# code through multiple quality gates and agent reviews:

1. **Requirements Analysis** → Requirements Engineer captures and validates requirements
2. **Technical Specification** → Spec Author creates detailed technical design
3. **Architecture Design** → Architect designs system following SOLID and Clean Architecture
4. **TDD Implementation** → Programmer implements with test-first approach
5. **Standards Audit** → Coding Standards Auditor verifies conventions
6. **QA Testing** → QA Engineer validates quality and test coverage
7. **Policy Gate** → Policy Gate ensures security and compliance
8. **Final Review** → Engineering Manager approves for deployment

## Stack-Specific Considerations

### C# Best Practices
- **Async/Await**: All I/O operations must be async
- **Dependency Injection**: Use built-in DI container
- **Nullable Reference Types**: Enabled by default
- **Pattern Matching**: Use modern C# features
- **Records**: Use for DTOs and value objects

### Testing Requirements
- **Unit Tests**: xUnit or NUnit with 80%+ coverage
- **Integration Tests**: Test API endpoints and data access
- **Mocking**: Use Moq or NSubstitute
- **Test Naming**: `MethodName_Scenario_ExpectedBehavior`

### Architecture Patterns
- **Clean Architecture**: Separate concerns into layers
- **CQRS**: For complex business logic
- **Repository Pattern**: For data access abstraction
- **MediatR**: For request/response handling

## Quality Gates

Each step with approvals acts as a quality gate:
- ✅ **PASS**: Proceed to next step
- ❌ **FAIL**: Return to appropriate earlier step for fixes

## Typical Usage

Suitable for:
- API development (REST, gRPC)
- Console applications
- Background services
- Microservices
- Desktop applications (WPF, WinForms)
