# Feature Prioritization Guide

## Prioritization Frameworks

### RICE Score

**R**each × **I**mpact × **C**onfidence / **E**ffort

#### Reach
How many users will this impact per time period?
- Measure: Users per month/quarter

#### Impact
How much will this impact users?
- 3 = Massive impact
- 2 = High impact
- 1 = Medium impact
- 0.5 = Low impact
- 0.25 = Minimal impact

#### Confidence
How confident are we in our estimates?
- 100% = High confidence (data-backed)
- 80% = Medium confidence (some data)
- 50% = Low confidence (hypothesis)

#### Effort
How much work is required?
- Person-months or story points

#### Example
```
Feature: Password Reset
- Reach: 1000 users/month
- Impact: 2 (high - critical for user access)
- Confidence: 100% (we know users need this)
- Effort: 2 person-weeks (0.5 person-months)

RICE Score = (1000 × 2 × 1.0) / 0.5 = 4000
```

### MoSCoW Method

#### Must Have
- Critical for launch
- Legal/compliance requirement
- Blocks core functionality
- High risk if not included

#### Should Have
- Important but not critical
- Can work around temporarily
- High value-to-effort ratio
- User expectations

#### Could Have
- Nice to have
- Low priority enhancement
- Improves user experience
- Minimal impact if excluded

#### Won't Have (This Time)
- Out of scope
- Future consideration
- Low value proposition
- High effort/complexity

### Value vs. Effort Matrix

```
        High Value
           |
Should  |  Must
Have    |  Have
--------+--------
Won't   |  Could
Have    |  Have
           |
        Low Effort
```

## Decision-Making Factors

### Strategic Alignment
- Supports company vision
- Aligns with product strategy
- Fits market positioning
- Competitive necessity

### User Impact
- Number of users affected
- Frequency of use
- Severity of pain point
- User segment importance

### Business Value
- Revenue generation
- Cost reduction
- Market differentiation
- Strategic advantage

### Technical Considerations
- Implementation complexity
- Technical dependencies
- Technical debt impact
- Platform constraints

### Resource Constraints
- Team capacity
- Skill requirements
- Timeline requirements
- Budget limitations

## Trade-off Analysis

### Feature Trade-offs

When choosing between features:

#### Example: Feature A vs. Feature B

| Criteria | Feature A | Feature B |
|----------|-----------|-----------|
| Users Impacted | 10,000 | 2,000 |
| Development Time | 4 weeks | 1 week |
| Revenue Impact | $50k/year | $10k/year |
| Strategic Value | Medium | High |
| Technical Risk | Low | High |
| Dependencies | None | Requires Feature C |

**Decision**: Feature A (higher overall value despite longer timeline)

### Scope Reduction Strategies

When timeline is constrained:

#### Phase 1 (MVP)
- Core functionality only
- Happy path implementation
- Basic error handling
- Manual processes acceptable

#### Phase 2 (Enhanced)
- Edge cases
- Advanced features
- Automation
- Optimizations

#### Phase 3 (Complete)
- Nice-to-have features
- Performance tuning
- Polish and refinement

## Stakeholder Management

### Stakeholder Matrix

```
        High Influence
             |
Manage    |  Partner
Closely   |  Closely
----------+----------
Monitor   |  Keep
         |  Informed
             |
        Low Interest
```

### Communication Strategies

#### Manage Closely (High Power, High Interest)
- Regular updates
- Involve in decisions
- Seek approval
- Address concerns quickly

#### Partner Closely (High Power, Low Interest)
- Keep satisfied
- Leverage expertise
- Minimal time commitment
- Quarterly reviews

#### Keep Informed (Low Power, High Interest)
- Regular status updates
- Feedback welcome
- No decision authority
- Advocates/champions

#### Monitor (Low Power, Low Interest)
- Minimal communication
- Broadcast updates
- No active involvement

## Feature Request Evaluation

### Template for New Requests

```markdown
## Feature Request: [Name]

### Requestor
- Who: [Name, role]
- When: [Date]
- Context: [Why now?]

### Problem Statement
- Current situation
- Pain points
- Impact if not solved

### Proposed Solution
- High-level approach
- Expected outcome
- Success criteria

### Business Case
- Users affected: [number]
- Revenue impact: [amount]
- Strategic value: [High/Medium/Low]
- Urgency: [When needed?]

### Initial Assessment
- Effort estimate: [T-shirt size]
- Technical feasibility: [High/Medium/Low]
- Dependencies: [List]
- Risks: [List]

### Priority Recommendation
- [P0/P1/P2/P3]
- Rationale: [Why?]
- Timeline: [Proposed quarter]
```

## Roadmap Planning

### Quarterly Planning

#### Q1 Focus Areas
- Theme: [e.g., "User Growth"]
- Goals: [Specific, measurable]
- Key Features: [Top 3-5]
- Success Metrics: [How measured]

#### Backlog Grooming

**Weekly**:
- Review new requests
- Update priorities
- Refine upcoming stories
- Remove outdated items

**Monthly**:
- Reassess roadmap
- Adjust priorities
- Stakeholder alignment
- Capacity planning

## Saying "No" Gracefully

### When to Say No
- Doesn't align with strategy
- Low value-to-effort ratio
- Technical constraints
- Resource limitations
- Not the right time

### How to Say No
1. **Acknowledge**: "I understand this is important to you"
2. **Explain**: "Here's why we can't do this now"
3. **Alternative**: "Here's what we can do instead"
4. **Future**: "Let's revisit in Q3"

### Template Response
```
Thank you for the suggestion! I appreciate you thinking about how to improve [product].

After evaluating this against our current priorities and roadmap, we've decided not to pursue this right now because [reason: strategic fit, resources, timing].

However, we are planning to [alternative solution or future consideration]. This will [similar benefit] and fits better with our current focus on [strategic theme].

Let's keep this on our radar and revisit in [timeframe] when we have [resources/data/prerequisite].
```
