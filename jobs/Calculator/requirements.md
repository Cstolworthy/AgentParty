# Functional Requirements

## Core Expression Handling
- Support + - * / operations
- Support parentheses
- Support implicit multiplication (2x, 3(x+1))
- Support symbolic variables (a–z)
- Support numeric evaluation when variables are defined

## Simplification Rules
- Reduce like terms (2x - x → x)
- Combine constants (2 + 3 → 5)
- Disallow multi-character variables (future extension)

## REPL Requirements
- User enters expression
- Output displays simplified or evaluated result
- Support assignments (x=5)

## Error Handling
- Detect malformed expressions
- Detect unsupported characters
- Detect division by zero on evaluated expressions
