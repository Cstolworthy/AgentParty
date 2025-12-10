# Compliance Rules

## GDPR Compliance (EU)

### Data Subject Rights
1. **Right to Access**: Users can request their data
2. **Right to Rectification**: Users can correct their data
3. **Right to Erasure**: Users can request deletion
4. **Right to Portability**: Users can export their data
5. **Right to Restrict Processing**: Users can limit processing
6. **Right to Object**: Users can opt out

### Implementation Requirements
- [ ] Consent mechanism implemented
- [ ] Data export functionality
- [ ] Data deletion functionality
- [ ] Privacy policy published
- [ ] Data processing records maintained
- [ ] Data breach notification process (<72 hours)
- [ ] DPO (Data Protection Officer) if required
- [ ] Privacy by design

### Technical Measures
```typescript
// Example: GDPR-compliant user deletion
async deleteUserData(userId: string) {
  // 1. Delete or anonymize personal data
  await this.userRepo.deleteUser(userId);
  
  // 2. Delete related data
  await this.sessionsRepo.deleteByUser(userId);
  
  // 3. Log the deletion
  await this.auditLog.log({
    action: 'USER_DELETED',
    userId,
    reason: 'GDPR_RIGHT_TO_ERASURE',
    timestamp: new Date()
  });
  
  // 4. Notify dependent systems
  await this.eventBus.publish('user.deleted', { userId });
}
```

## HIPAA Compliance (US Healthcare)

### Required Safeguards

#### Administrative
- [ ] Security management process
- [ ] Assigned security responsibility
- [ ] Workforce security
- [ ] Information access management
- [ ] Security awareness training

#### Physical
- [ ] Facility access controls
- [ ] Workstation use policies
- [ ] Device and media controls

#### Technical
- [ ] Access control (unique user IDs)
- [ ] Audit controls
- [ ] Integrity controls
- [ ] Transmission security (encryption)

### PHI Protection
Protected Health Information must:
- Be encrypted at rest (AES-256)
- Be encrypted in transit (TLS 1.2+)
- Have access controls
- Have audit logging
- Be backed up securely

## PCI DSS (Payment Card Data)

### Requirements
1. **Firewall Configuration**: Protect cardholder data
2. **No Default Passwords**: Change default credentials
3. **Protect Stored Data**: Encrypt cardholder data
4. **Encrypt Transmission**: Use TLS for card data
5. **Use Anti-Virus**: Protect systems
6. **Secure Systems**: Update and patch regularly
7. **Restrict Access**: Need-to-know basis only
8. **Unique IDs**: Each user has unique ID
9. **Restrict Physical Access**: To cardholder data
10. **Track Access**: Log and monitor
11. **Test Security**: Regular security testing
12. **Security Policy**: Document and maintain

### Cardholder Data Storage
❌ **NEVER store**:
- Full magnetic stripe data
- CVV2/CVC2/CID
- PIN/PIN block

✅ **May store (encrypted)**:
- Primary Account Number (PAN)
- Cardholder name
- Expiration date
- Service code

### Best Practice: Don't Store
Use payment processors (Stripe, Square):
```typescript
// Don't store card details
const payment = await stripe.paymentIntents.create({
  amount: 1000,
  currency: 'usd',
  payment_method: paymentMethodId,
  confirm: true
});
```

## SOC 2 Compliance

### Trust Service Criteria

#### Security
- [ ] Access controls implemented
- [ ] Systems protected from unauthorized access
- [ ] Security incidents detected and addressed

#### Availability
- [ ] Systems available for operation
- [ ] Monitoring and incident response
- [ ] Business continuity and disaster recovery

#### Processing Integrity
- [ ] Processing is complete, valid, accurate
- [ ] Authorized processing only
- [ ] Timely processing

#### Confidentiality
- [ ] Confidential information protected
- [ ] Access limited to authorized users
- [ ] Confidential data disposed securely

#### Privacy
- [ ] Personal information collected per notice
- [ ] Used and retained per notice
- [ ] Disclosed per notice
- [ ] Disposed per notice
- [ ] Quality maintained
- [ ] Monitoring and enforcement

## Data Classification

### Public
- No restrictions
- Marketing materials
- Public documentation

### Internal
- Internal use only
- Business documents
- Internal communications

### Confidential
- Restricted access
- Customer data
- Financial information
- Source code

### Restricted
- Highly sensitive
- PII/PHI
- Payment card data
- Authentication credentials
- Legal documents

## Audit Logging Requirements

### What to Log
- Authentication attempts (success/failure)
- Authorization failures
- Data access (read sensitive data)
- Data modifications (create/update/delete)
- Configuration changes
- Security events
- System errors

### What NOT to Log
- Passwords
- Credit card numbers
- Social Security Numbers
- Authentication tokens
- Other sensitive PII

### Log Format
```json
{
  "timestamp": "2024-12-10T20:00:00Z",
  "level": "INFO",
  "event": "USER_LOGIN",
  "userId": "uuid",
  "ipAddress": "192.168.1.1",
  "userAgent": "Mozilla/5.0...",
  "success": true,
  "metadata": {}
}
```

### Log Retention
- **Security logs**: 1 year minimum
- **Audit logs**: Per regulatory requirements
- **Application logs**: 30-90 days
- **Debug logs**: 7-14 days

## Incident Response Plan

### Phases
1. **Preparation**: Have plan ready
2. **Identification**: Detect incident
3. **Containment**: Limit damage
4. **Eradication**: Remove threat
5. **Recovery**: Restore systems
6. **Lessons Learned**: Improve process

### Security Incident Categories
- **Critical**: Data breach, ransomware
- **High**: Unauthorized access, malware
- **Medium**: Failed intrusion attempt
- **Low**: Policy violation

### Notification Requirements
- **GDPR**: 72 hours
- **HIPAA**: 60 days
- **State Laws**: Varies by state
- **Customers**: As required by law

## Regular Security Assessments

### Required Assessments
- [ ] Quarterly vulnerability scans
- [ ] Annual penetration testing
- [ ] Quarterly dependency audits
- [ ] Annual security training
- [ ] Monthly access reviews
- [ ] Quarterly disaster recovery tests
