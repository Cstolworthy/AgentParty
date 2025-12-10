# Technical Specifications

## Technology Stack
- C# 12
- .NET 8 console app

## Architecture
- Lexer → Parser → AST → Evaluator/Simplifier
- Variable Table for user-defined values

## Data Structures
### AST Nodes
- ConstantNode
- VariableNode
- BinaryOperationNode
- UnaryOperationNode

## Simplification Engine
- Combine like terms
- Flatten associative operators
- Remove zero terms

## Testing Framework
- xUnit
- 100% of logic covered via TDD loop
