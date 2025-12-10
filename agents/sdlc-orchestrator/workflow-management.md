# Workflow Management Guide

## Workflow State Machine

### States
```
┌──────────────┐
│  initiated   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ in_progress  │──────┐
└──────┬───────┘      │
       │              │
       ▼              │ (rework)
┌──────────────┐      │
│   blocked    │◄─────┘
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  completed   │
└──────────────┘
```

### Transitions
- `initiated` → `in_progress`: Work starts
- `in_progress` → `blocked`: Waiting on something
- `blocked` → `in_progress`: Blocker resolved
- `in_progress` → `completed`: All steps done
- `in_progress` → `in_progress` (rework): Quality gate fail

## Step Transitions

### Standard Flow
```
Requirements
    ↓
Specification (PM Approval)
    ↓
Architecture (EM Approval)
    ↓
Implementation
    ↓
Standards Audit ──FAIL──→ Implementation (rework)
    ↓ PASS
QA Testing ──FAIL──→ Implementation (rework)
    ↓ PASS
Policy Gate ──FAIL──→ Implementation or Architecture (rework)
    ↓ PASS
Final Review ──FAIL──→ Appropriate step (rework)
    ↓ PASS
Complete
```

### Rework Routing

**Standards Audit FAIL**:
- Reason: Linting errors, naming issues
- Route To: Implementation
- Fix: Developer fixes standards violations

**QA Testing FAIL**:
- Reason: Tests failing, bugs found
- Route To: Implementation
- Fix: Developer fixes bugs

**Policy Gate FAIL (Security)**:
- Reason: Security vulnerabilities
- Route To: Implementation
- Fix: Developer fixes security issues

**Policy Gate FAIL (Architecture)**:
- Reason: Architectural non-compliance
- Route To: Architecture
- Fix: Architect revises design

**Final Review FAIL**:
- Reason: Quality concerns
- Route To: Determined by Engineering Manager
- Fix: Depends on issue

## Tracking Mechanisms

### Work Item States
```typescript
interface WorkItem {
  jobId: string;
  workflowId: string;
  currentStep: string;
  status: 'initiated' | 'in_progress' | 'blocked' | 'completed' | 'failed';
  startedAt: Date;
  completedAt?: Date;
  steps: StepStatus[];
  approvals: Approval[];
  blockers: Blocker[];
}

interface StepStatus {
  stepId: string;
  agent: string;
  status: 'not_started' | 'in_progress' | 'passed' | 'failed' | 'skipped';
  startedAt?: Date;
  completedAt?: Date;
  attempts: number;
  artifacts: string[];
}

interface Approval {
  step: string;
  approver: string;
  status: 'pending' | 'approved' | 'rejected';
  timestamp?: Date;
  comments?: string;
}

interface Blocker {
  id: string;
  description: string;
  blockedSince: Date;
  resolvedAt?: Date;
  impact: 'low' | 'medium' | 'high' | 'critical';
}
```

## Progress Tracking

### Completion Percentage
```typescript
function calculateProgress(workflow: WorkItem): number {
  const totalSteps = workflow.steps.length;
  const completedSteps = workflow.steps.filter(s => 
    s.status === 'passed' || s.status === 'completed'
  ).length;
  
  return (completedSteps / totalSteps) * 100;
}
```

### Time Tracking
```typescript
function getStepDuration(step: StepStatus): number {
  if (!step.startedAt || !step.completedAt) return 0;
  return step.completedAt.getTime() - step.startedAt.getTime();
}

function getCycleTime(workflow: WorkItem): number {
  if (!workflow.completedAt) return 0;
  return workflow.completedAt.getTime() - workflow.startedAt.getTime();
}
```

## Notification System

### When to Notify

**Workflow Started**:
- Notify: Job owner, team
- Message: "Work started on [Job Name]"

**Step Completed**:
- Notify: Next agent in workflow
- Message: "Ready for [Next Step]"

**Approval Needed**:
- Notify: Approver (PM, EM)
- Message: "Approval needed for [Step]"

**Quality Gate Failed**:
- Notify: Developer, Engineering Manager
- Message: "[Gate] failed, fixes needed"

**Blocked**:
- Notify: Engineering Manager, stakeholders
- Message: "Workflow blocked: [Reason]"

**Workflow Completed**:
- Notify: Job owner, team, stakeholders
- Message: "[Job Name] ready for deployment"

### Notification Template
```markdown
## Workflow Notification: [Event]

**Job**: [Job Name]
**Status**: [Status]
**Current Step**: [Step Name]
**Action Required**: [What needs to happen]

**Details**:
[Additional context]

**Next Steps**:
- [Action 1]
- [Action 2]

**Timeline**: [Expected completion or deadline]
```

## Metrics & Reporting

### Key Metrics

**Cycle Time**:
- Definition: Time from workflow start to completion
- Target: < 5 days for standard features
- Formula: `completed_at - started_at`

**Lead Time**:
- Definition: Time from request to deployment
- Target: < 7 days
- Formula: `deployed_at - requested_at`

**Rework Rate**:
- Definition: % of steps that fail quality gates
- Target: < 20%
- Formula: `failed_steps / total_steps`

**Step Duration**:
- Track average time per step
- Identify bottlenecks
- Optimize slow steps

**Quality Gate Pass Rate**:
- Standards Audit pass rate
- QA Testing pass rate
- Policy Gate pass rate
- Target: > 80% first-time pass

### Dashboard Data
```typescript
interface WorkflowMetrics {
  // Current Status
  activeWorkflows: number;
  completedToday: number;
  blockedWorkflows: number;
  
  // Performance
  avgCycleTime: number;  // hours
  avgLeadTime: number;   // hours
  reworkRate: number;    // percentage
  
  // Quality Gates
  standardsPassRate: number;
  qaPassRate: number;
  policyPassRate: number;
  
  // Bottlenecks
  slowestStep: string;
  avgStepDuration: Record<string, number>;
  
  // Trends
  completionTrend: number[];  // last 30 days
  qualityTrend: number[];     // pass rates over time
}
```

## Process Optimization

### Identify Bottlenecks
- Track step durations
- Find steps taking longest
- Analyze failure patterns
- Identify recurring issues

### Improvement Actions
- **Slow Step**: Add resources, automation
- **High Failure Rate**: Improve training, tooling
- **Frequent Rework**: Better quality checks upstream
- **Long Approval Wait**: SLA for approvals

### Continuous Improvement
- Monthly retrospectives
- Review metrics trends
- Implement improvements
- Measure impact

## Emergency Procedures

### Hotfix Process
- Skip non-critical steps
- Expedited approvals
- Parallel testing
- Quick deployment
- Post-deployment review

### Rollback Process
- Identify issue
- Stop workflow
- Revert changes
- Root cause analysis
- Resume with fixes

### Escalation Path
1. **Agent Level**: Agent resolves
2. **Orchestrator Level**: Route/reassign
3. **Manager Level**: Engineering Manager decides
4. **Executive Level**: CTO/VP involvement (rare)

## Best Practices

1. **Clear Handoffs**: Each transition well-defined
2. **Fast Feedback**: Quick quality gate results
3. **Minimal Wait**: Reduce approval delays
4. **Automate**: Automate repetitive tasks
5. **Measure**: Track and optimize metrics
6. **Communicate**: Keep stakeholders informed
7. **Learn**: Retrospectives and improvements
8. **Document**: Clear process documentation
