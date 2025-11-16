# Architecture Diagrams - Strategic Decision System

## 1. System Architecture Overview

### High-Level Data Flow

```mermaid
graph TB
    subgraph External["External Data Sources"]
        FB[Facebook Ads API]
        CRM[CRM System]
        CSV[Manual CSV Uploads]
    end
    
    subgraph EC2["EC2 Instance - t3.medium"]
        direction TB
        Cron[Cron Jobs<br/>Scheduler]
        Fetch[fetch_facebook_data.py<br/>Every 4 hours]
        Score[score_campaigns.py<br/>Every 6 hours]
        DB[(PostgreSQL 15<br/>Local Database)]
        FastAPI[FastAPI Server<br/>Port 8000]
        Nginx[Nginx<br/>Reverse Proxy]
    end
    
    subgraph AWS["AWS Services"]
        S3[S3 Bucket<br/>Backups + Raw Data]
        CW[CloudWatch<br/>Logs + Metrics]
        SES[SES<br/>Email Service]
    end
    
    subgraph External2["External Monitoring"]
        Sentry[Sentry<br/>Error Tracking]
    end
    
    FB -->|API Calls| Fetch
    CRM -->|Webhooks| FastAPI
    CSV -->|Upload| FastAPI
    
    Cron -->|Trigger| Fetch
    Cron -->|Trigger| Score
    
    Fetch -->|Insert Data| DB
    Score -->|Read/Write| DB
    FastAPI -->|Query| DB
    
    Fetch -->|Backup| S3
    Score -->|Archive| S3
    
    Score -->|Send Alerts| SES
    
    Nginx -->|Reverse Proxy| FastAPI
    
    EC2 -->|Push Logs| CW
    EC2 -->|Send Errors| Sentry
    
    style EC2 fill:#e1f5ff
    style AWS fill:#fff4e6
    style External fill:#f3e5f5
    style External2 fill:#fce4ec
```

---

## 2. Deployment Timeline

```mermaid
gantt
    title Production Deployment Roadmap (4 Weeks)
    dateFormat YYYY-MM-DD
    
    section Week 1: Infrastructure
    Launch EC2 Instance                :done, w1a, 2025-11-18, 2d
    Install PostgreSQL + Python        :done, w1b, after w1a, 2d
    Configure Nginx + SSL              :done, w1c, after w1b, 1d
    
    section Week 2: Core Engine
    Port Scoring Code                  :active, w2a, 2025-11-25, 3d
    Facebook API Connector             :active, w2b, after w2a, 2d
    Setup Cron Jobs                    :w2c, after w2b, 2d
    
    section Week 3: API & UI
    Build FastAPI Endpoints            :w3a, 2025-12-02, 3d
    Create Dashboard Templates         :w3b, after w3a, 2d
    Email Alert System                 :w3c, after w3b, 2d
    
    section Week 4: Production Ready
    CloudWatch Integration             :w4a, 2025-12-09, 2d
    Security Hardening                 :w4b, after w4a, 2d
    Load Testing                       :w4c, after w4b, 1d
    Documentation                      :w4d, after w4c, 2d
```

---

## 3. Data Pipeline Flow

```mermaid
sequenceDiagram
    participant Cron as Cron Scheduler
    participant Fetch as fetch_facebook_data.py
    participant FB as Facebook API
    participant DB as PostgreSQL
    participant S3 as S3 Backup
    participant Score as score_campaigns.py
    participant Email as AWS SES
    
    Note over Cron: Every 4 hours
    Cron->>Fetch: Trigger ingestion
    Fetch->>FB: GET /campaigns<br/>GET /insights
    FB-->>Fetch: JSON data
    Fetch->>DB: INSERT campaigns<br/>INSERT metrics
    Fetch->>S3: Upload raw JSON
    
    Note over Cron: Every 6 hours
    Cron->>Score: Trigger scoring
    Score->>DB: SELECT campaigns<br/>(last 30 days)
    Score->>Score: Calculate scores<br/>5 dimensions
    Score->>DB: INSERT campaign_scores
    Score->>Email: Send high-priority alerts
    Score->>S3: Backup scored data
```

---

## 4. Facebook API Error Handling

```mermaid
graph TD
    A[API Call] --> B{HTTP Status?}
    B -->|200 OK| C[Parse JSON]
    B -->|429 Rate Limit| D[Sleep 60s]
    B -->|401 Unauthorized| E[Refresh Token]
    B -->|500 Server Error| F[Retry 3x]
    B -->|Other Error| G[Log to Sentry]
    
    C --> H[Validate Data]
    D --> A
    E --> A
    F --> A
    G --> I[Send Email Alert]
    
    H --> J{Valid?}
    J -->|Yes| K[Save to DB]
    J -->|No| L[Log Warning]
    
    style A fill:#2196f3
    style K fill:#4caf50
    style I fill:#f44336
```

---

## 5. Scoring Engine Logic

```mermaid
graph LR
    subgraph Input
        Data[(Campaign Data<br/>Last 30 Days)]
    end
    
    subgraph Scoring["Score Calculation"]
        Cost[Cost Efficiency<br/>0-25 points]
        Quality[Lead Quality<br/>0-25 points]
        Volume[Volume<br/>0-20 points]
        Trend[Trends<br/>0-20 points]
        Engage[Engagement<br/>0-10 points]
    end
    
    subgraph Output
        Total[Total Score<br/>0-100]
        Rec[Recommendation]
    end
    
    Data --> Cost
    Data --> Quality
    Data --> Volume
    Data --> Trend
    Data --> Engage
    
    Cost --> Total
    Quality --> Total
    Volume --> Total
    Trend --> Total
    Engage --> Total
    
    Total --> Rec
    
    Rec -->|80-100| Inc[INCREASE_BUDGET]
    Rec -->|60-79| Cont[CONTINUE_OPTIMIZE]
    Rec -->|40-59| Test[TEST_CHANGES]
    Rec -->|20-39| Red[REDUCE_BUDGET]
    Rec -->|0-19| Pause[PAUSE_CAMPAIGN]
    
    style Total fill:#ff9800
    style Inc fill:#4caf50
    style Pause fill:#f44336
```

---

## 6. Monitoring Architecture

```mermaid
graph TB
    subgraph EC2["EC2 Instance"]
        App[Application]
        Nginx[Nginx]
        PG[(PostgreSQL)]
    end
    
    subgraph CloudWatch["AWS CloudWatch"]
        Logs[CloudWatch Logs]
        Metrics[CloudWatch Metrics]
        Alarms[CloudWatch Alarms]
    end
    
    subgraph External["External"]
        Sentry[Sentry<br/>Error Tracking]
    end
    
    subgraph Alerts["Alert Channels"]
        Email[📧 Email]
        Slack[💬 Slack]
        SMS[📱 SMS]
    end
    
    App -->|Logs| Logs
    Nginx -->|Access Logs| Logs
    PG -->|Query Logs| Logs
    
    App -->|Custom Metrics| Metrics
    EC2 -->|System Metrics| Metrics
    
    App -->|Errors| Sentry
    
    Metrics --> Alarms
    Logs --> Alarms
    
    Alarms -->|Critical| SMS
    Alarms -->|High| Slack
    Alarms -->|Medium| Email
    Sentry -->|Errors| Slack
    
    style EC2 fill:#2196f3
    style CloudWatch fill:#ff9800
    style Sentry fill:#9c27b0
```

---

## 7. Alert Severity Levels

```mermaid
graph TB
    subgraph Critical["🔴 CRITICAL - Immediate Response"]
        C1[EC2 Instance Down]
        C2[Database Unreachable]
        C3[Error Rate >10%]
        C4[Disk >95% Full]
    end
    
    subgraph High["🟠 HIGH - 1 Hour Response"]
        H1[CPU >85% for 15min]
        H2[Disk >85% Full]
        H3[Pipeline Failed 2x]
        H4[API Latency >1000ms]
    end
    
    subgraph Medium["🟡 MEDIUM - Daily Review"]
        M1[Data Quality Issues]
        M2[Cost Spike 50%]
        M3[API Latency >800ms]
    end
    
    subgraph Low["🟢 LOW - Weekly Digest"]
        L1[Slow Queries 5-10s]
        L2[Unused Campaigns]
        L3[Stale Data]
    end
    
    Critical -->|SMS + Email| Response1[Immediate Action]
    High -->|Slack + Email| Response2[1 Hour Response]
    Medium -->|Email| Response3[Daily Review]
    Low -->|Email Digest| Response4[Weekly Review]
    
    style Critical fill:#f44336
    style High fill:#ff9800
    style Medium fill:#ffc107
    style Low fill:#4caf50
```

---

## 8. Security Architecture

```mermaid
graph TB
    Internet[🌐 Internet]
    
    subgraph WAF["Optional: CloudFlare WAF"]
        CF[DDoS Protection<br/>Rate Limiting]
    end
    
    subgraph EC2["EC2 Instance"]
        SG[Security Group<br/>Ports: 22, 80, 443]
        UFW[UFW Firewall]
        Nginx[Nginx<br/>SSL/TLS 1.2+<br/>Rate Limit: 100/min]
        FastAPI[FastAPI<br/>JWT Authentication]
        PG[(PostgreSQL<br/>Localhost Only)]
    end
    
    subgraph Secrets["Secrets Management"]
        SM[AWS Secrets Manager]
        ENV[Environment Variables]
    end
    
    subgraph Encryption["Encryption"]
        EBS[EBS Encryption<br/>AES-256]
        SSL[Let's Encrypt SSL]
        S3E[S3 SSE Encryption]
    end
    
    Internet --> CF
    CF --> SG
    SG --> UFW
    UFW --> Nginx
    Nginx --> FastAPI
    FastAPI --> PG
    
    SM -.->|Sync at Boot| ENV
    ENV -.->|Used by| FastAPI
    
    EC2 -.->|Uses| EBS
    Nginx -.->|Uses| SSL
    
    style WAF fill:#9c27b0
    style EC2 fill:#2196f3
    style Secrets fill:#ff9800
    style Encryption fill:#4caf50
```

---

## 9. FastAPI Architecture

```mermaid
graph LR
    subgraph Clients["API Clients"]
        Browser[🖥️ Web Browser]
        Mobile[📱 Mobile App]
        Script[🐍 Python Script]
    end
    
    subgraph Nginx["Nginx (Port 443)"]
        SSL[SSL Termination]
        RL[Rate Limiting]
    end
    
    subgraph FastAPI["FastAPI (Port 8000)"]
        Auth[JWT Middleware]
        Validate[Pydantic Validation]
        Routes[API Routes]
    end
    
    subgraph Endpoints["Endpoints"]
        E1[GET /health]
        E2[GET /api/campaigns]
        E3[GET /api/recommendations]
        E4[POST /api/webhooks/crm]
    end
    
    subgraph DB["Database"]
        PG[(PostgreSQL)]
    end
    
    Browser --> Nginx
    Mobile --> Nginx
    Script --> Nginx
    
    Nginx --> SSL
    SSL --> RL
    RL --> FastAPI
    
    FastAPI --> Auth
    Auth --> Validate
    Validate --> Routes
    
    Routes --> E1
    Routes --> E2
    Routes --> E3
    Routes --> E4
    
    E2 --> PG
    E3 --> PG
    E4 --> PG
    
    style Nginx fill:#4caf50
    style FastAPI fill:#2196f3
    style DB fill:#ff9800
```

---

## 10. Cost Breakdown (MVP)

```mermaid
pie title Monthly Cost Breakdown - MVP ($83)
    "EC2 t3.medium (24/7)" : 30
    "Sentry SaaS" : 26
    "EBS 50GB" : 5
    "S3 Storage" : 6
    "CloudWatch" : 6
    "Other AWS Services" : 6
    "Contingency" : 4
```

### Cost Scaling Path

```mermaid
graph LR
    A[MVP<br/>$83/mo<br/>10 clients] --> B{Growing?}
    B -->|Yes| C[Scale<br/>$355/mo<br/>100 clients]
    B -->|No| A
    
    C --> D{Need HA?}
    D -->|Yes| E[Multi-Instance<br/>$800/mo<br/>Load Balancer]
    D -->|No| C
    
    A -.->|Upgrade| F[Buy Reserved<br/>Instance<br/>Save 40%]
    C -.->|Upgrade| F
    
    style A fill:#4caf50
    style C fill:#ff9800
    style E fill:#f44336
```

---

## 11. Disaster Recovery Flow

```mermaid
graph TB
    subgraph Production["Production System"]
        EC2[EC2 Instance]
        PG[(PostgreSQL)]
    end
    
    subgraph Backups["Backup Strategy"]
        Daily[Daily DB Backup<br/>pg_dump → S3<br/>7-day retention]
        Snap[Weekly EBS Snapshot<br/>4-week retention]
        Code[Git Repository<br/>GitHub]
    end
    
    subgraph Recovery["Recovery Scenarios"]
        R1[Database Corruption<br/>RTO: 2 hours<br/>RPO: 24 hours]
        R2[EC2 Failure<br/>RTO: 4 hours<br/>RPO: 24 hours]
        R3[Region Outage<br/>RTO: 8 hours<br/>RPO: 24 hours]
    end
    
    PG -->|Cron: 2 AM daily| Daily
    EC2 -->|Weekly| Snap
    EC2 -.->|Code in| Code
    
    Daily -.->|Restore from| R1
    Snap -.->|Launch new EC2| R2
    Daily -.->|Cross-region| R3
    
    R1 --> Restore1[Restore DB<br/>from S3]
    R2 --> Restore2[Launch new EC2<br/>Restore from snapshot]
    R3 --> Restore3[Deploy to<br/>us-west-2]
    
    style Production fill:#2196f3
    style Backups fill:#4caf50
    style Recovery fill:#ff9800
```

---

## 12. Data Quality Pipeline

```mermaid
graph LR
    Raw[Raw Data<br/>from API] --> Schema{Schema<br/>Valid?}
    
    Schema -->|No| Error1[❌ Log Error<br/>Send Alert]
    Schema -->|Yes| Complete{Required<br/>Fields?}
    
    Complete -->|No| Flag1[⚠️ Flag as<br/>Incomplete]
    Complete -->|Yes| Range{Values<br/>Reasonable?}
    
    Range -->|No| Flag2[⚠️ Flag as<br/>Outlier]
    Range -->|Yes| Accept[✅ Accept Data]
    
    Flag1 --> DB[(Insert to DB)]
    Flag2 --> DB
    Accept --> DB
    
    style Raw fill:#2196f3
    style Error1 fill:#f44336
    style Flag1 fill:#ff9800
    style Flag2 fill:#ff9800
    style Accept fill:#4caf50
```

---

## 13. Operational Runbook - Issue Resolution

```mermaid
graph TD
    Issue[🚨 Issue Detected] --> Type{Issue Type?}
    
    Type -->|Pipeline Failure| PF[Check Logs]
    Type -->|High CPU| CPU[Check Processes]
    Type -->|API Errors| API[Check Sentry]
    Type -->|Disk Full| Disk[Clean Logs]
    
    PF --> PF1{Error Type?}
    PF1 -->|API Rate Limit| PF2[Wait 60min<br/>Retry]
    PF1 -->|Auth Error| PF3[Refresh Token]
    PF1 -->|Other| PF4[Manual Fix]
    
    CPU --> CPU1{Which Process?}
    CPU1 -->|PostgreSQL| CPU2[Optimize Queries]
    CPU1 -->|Python| CPU3[Check Scoring Job]
    CPU1 -->|Other| CPU4[Kill Process]
    
    API --> API1{Error Rate?}
    API1 -->|>10%| API2[Rollback Code]
    API1 -->|<10%| API3[Monitor]
    
    Disk --> Disk1[Delete Old Logs]
    Disk1 --> Disk2[Expand EBS Volume]
    
    style Issue fill:#f44336
    style PF2 fill:#4caf50
    style API2 fill:#ff9800
```

---

## Summary

These diagrams provide a comprehensive visual representation of:
1. **System Architecture** - Single EC2 with all components
2. **Data Pipeline** - Facebook API → PostgreSQL → Scoring → Outputs
3. **Monitoring** - CloudWatch + Sentry + Alerting
4. **Security** - Multiple layers of protection
5. **FastAPI** - Modern API architecture
6. **Cost Optimization** - Scaling path from MVP to production
7. **Disaster Recovery** - Backup and restore procedures
8. **Operations** - Issue resolution workflows

All diagrams use **Mermaid** syntax for easy rendering in GitHub, GitLab, Notion, and other Markdown-compatible platforms.


