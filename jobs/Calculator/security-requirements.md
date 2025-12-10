# Security Requirements

Even though this is a console application:

## Input Validation
- Reject any non-math ASCII except a–z, digits, + - * / ^ = ( )
- Reject attempts to inject code or non-math symbols
- Validate variable assignment syntax (x=5)

## Execution Safety
- No dynamic code execution
- No reflection
- No external IO

## Logging
- Never log raw user input in verbose/debug mode unless explicitly requested

## Operational Safety
- Application should never crash from malformed input
