# Console Interaction Contract

Even though this is not an HTTP API, we define structured IO:

## Input Format Examples
```
2x - x
x = 5
2(x + 3)
(2x + 3y) - (x - y)
```

## Output Format
```
x
Assigned x = 5
2x + 6
x + 4y
```

## Error Output
```
Error: Invalid expression
Error: Unknown variable 'q'
Error: Division by zero
```
