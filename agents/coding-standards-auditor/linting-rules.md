# Linting Rules and Configuration

## C# Linting (.editorconfig)

```ini
# EditorConfig is awesome: https://EditorConfig.org

root = true

[*.cs]
indent_style = space
indent_size = 4
end_of_line = crlf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

# Naming Conventions
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.severity = warning
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.symbols = interface
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.style = begins_with_i

dotnet_naming_style.begins_with_i.required_prefix = I
dotnet_naming_style.begins_with_i.capitalization = pascal_case

# Private fields with underscore
dotnet_naming_rule.private_fields_with_underscore.severity = warning
dotnet_naming_rule.private_fields_with_underscore.symbols = private_fields
dotnet_naming_rule.private_fields_with_underscore.style = underscore_camel_case

dotnet_naming_style.underscore_camel_case.required_prefix = _
dotnet_naming_style.underscore_camel_case.capitalization = camel_case

# Async methods must have Async suffix
dotnet_naming_rule.async_methods_must_end_with_async.severity = warning
dotnet_naming_rule.async_methods_must_end_with_async.symbols = async_methods
dotnet_naming_rule.async_methods_must_end_with_async.style = ends_with_async

# Code Style
csharp_prefer_braces = true:warning
csharp_prefer_simple_using_statement = true:suggestion
csharp_prefer_static_local_function = true:suggestion
csharp_style_namespace_declarations = file_scoped:warning

# Nullable Reference Types
dotnet_diagnostic.CS8602.severity = error # Possible null reference
dotnet_diagnostic.CS8603.severity = error # Possible null return
dotnet_diagnostic.CS8604.severity = error # Possible null argument

# Code Quality
dotnet_diagnostic.CA1031.severity = warning # Do not catch general exception types
dotnet_diagnostic.CA1303.severity = none # Do not pass literals as localized parameters
dotnet_diagnostic.CA1822.severity = suggestion # Mark members as static
```

## Node.js ESLint Configuration

```json
{
  "parser": "@typescript-eslint/parser",
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking",
    "prettier"
  ],
  "plugins": ["@typescript-eslint"],
  "parserOptions": {
    "ecmaVersion": 2022,
    "sourceType": "module",
    "project": "./tsconfig.json"
  },
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-unused-vars": ["error", {
      "argsIgnorePattern": "^_"
    }],
    "@typescript-eslint/no-floating-promises": "error",
    "@typescript-eslint/await-thenable": "error",
    "no-console": "warn",
    "no-debugger": "error",
    "prefer-const": "error",
    "no-var": "error",
    "eqeqeq": ["error", "always"],
    "curly": ["error", "all"],
    "no-return-await": "off",
    "@typescript-eslint/return-await": ["error", "in-try-catch"],
    "max-len": ["warn", { "code": 120 }],
    "complexity": ["warn", 10],
    "max-lines-per-function": ["warn", 50]
  }
}
```

## Prettier Configuration

```json
{
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

## Angular ESLint Configuration

```json
{
  "root": true,
  "overrides": [
    {
      "files": ["*.ts"],
      "extends": [
        "eslint:recommended",
        "plugin:@typescript-eslint/recommended",
        "plugin:@angular-eslint/recommended",
        "plugin:@angular-eslint/template/process-inline-templates"
      ],
      "rules": {
        "@angular-eslint/directive-selector": [
          "error",
          { "type": "attribute", "prefix": "app", "style": "camelCase" }
        ],
        "@angular-eslint/component-selector": [
          "error",
          { "type": "element", "prefix": "app", "style": "kebab-case" }
        ],
        "@angular-eslint/no-output-on-prefix": "error",
        "@angular-eslint/use-lifecycle-interface": "error",
        "@angular-eslint/use-pipe-transform-interface": "error",
        "@typescript-eslint/no-explicit-any": "error",
        "@typescript-eslint/explicit-function-return-type": "warn",
        "@typescript-eslint/no-unused-vars": ["error", {
          "argsIgnorePattern": "^_"
        }]
      }
    },
    {
      "files": ["*.html"],
      "extends": [
        "plugin:@angular-eslint/template/recommended",
        "plugin:@angular-eslint/template/accessibility"
      ],
      "rules": {
        "@angular-eslint/template/no-call-expression": "error",
        "@angular-eslint/template/use-track-by-function": "error"
      }
    }
  ]
}
```

## TypeScript Configuration (Strict)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  }
}
```

## SonarQube Rules (All Stacks)

### Critical Issues (Must Fix)
- **Bugs**: Code that will definitely fail
- **Vulnerabilities**: Security issues
- **Code Smells (Blocker)**: Critical maintainability issues

### Major Issues (Should Fix)
- **Complexity**: Methods too complex
- **Duplications**: Copy-pasted code
- **Test Coverage**: Below threshold

### Common SonarQube Rules

**Cognitive Complexity**:
- Threshold: 15 per method
- Measures how hard code is to understand

**Cyclomatic Complexity**:
- Threshold: 10 per method
- Measures number of paths through code

**Code Duplication**:
- Threshold: 3% of total code
- Identifies copy-pasted blocks

**Test Coverage**:
- Threshold: 80% line coverage
- Measures % of code covered by tests

## Git Hooks (Husky + Lint-Staged)

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
    }
  },
  "lint-staged": {
    "*.{ts,js}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.cs": [
      "dotnet format"
    ]
  }
}
```

## Commit Message Rules (Conventional Commits)

Format: `type(scope): subject`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (not code style)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(auth): add password reset functionality
fix(api): handle null values in user endpoint
docs(readme): update installation instructions
refactor(service): extract user validation logic
test(auth): add tests for login flow
```
