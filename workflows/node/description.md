# Node.js Development Workflow

Modern Node.js/TypeScript development workflow emphasizing async patterns, API design, and comprehensive testing.

## Workflow Overview

This workflow ensures production-ready Node.js applications with proper error handling, type safety, and security:

1. **Requirements Analysis** → Requirements Engineer validates business needs
2. **API Specification** → Spec Author designs RESTful API with OpenAPI
3. **Architecture Design** → Architect plans middleware and async patterns
4. **TDD Implementation** → Programmer builds with Jest/TypeScript
5. **Standards Audit** → Auditor enforces ESLint, Prettier, TypeScript rules
6. **QA Testing** → QA Engineer validates API and edge cases
7. **Security Gate** → Policy Gate checks dependencies and vulnerabilities
8. **Final Review** → Engineering Manager approves deployment

## Stack-Specific Considerations

### TypeScript Best Practices
- **Strict Mode**: Enable all strict TypeScript checks
- **Type Definitions**: Use `@types` packages
- **Interfaces over Types**: For object shapes
- **No `any`**: Avoid implicit any
- **Async/Await**: Modern promise handling

### Testing Requirements
- **Unit Tests**: Jest with 80%+ coverage
- **Integration Tests**: Supertest for API endpoints
- **Mocking**: Jest mocks for external services
- **Error Cases**: Test all error paths
- **Test Structure**: AAA (Arrange, Act, Assert)

### Node.js Patterns
- **Express/Fastify**: Modern web frameworks
- **Middleware**: Composable request handling
- **Error Handling**: Centralized error middleware
- **Validation**: Joi or Zod for input validation
- **Logging**: Winston or Pino structured logging

### Security Considerations
- **npm audit**: Check for vulnerabilities
- **Helmet.js**: Security headers
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Sanitize all inputs
- **Environment Variables**: Never commit secrets

## Quality Gates

- **Standards Gate**: ESLint, Prettier, TypeScript compiler
- **Testing Gate**: 80%+ coverage, all tests pass
- **Security Gate**: No critical vulnerabilities, dependencies up to date
- **Review Gate**: Engineering Manager approval

## Typical Usage

Perfect for:
- RESTful APIs
- GraphQL servers
- Microservices
- Real-time applications (WebSockets)
- CLI tools
- Background workers
