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

### High-Level Data Flow

```
                    ┌─────────────────────────────────────┐
                    │      EXTERNAL DATA SOURCES          │
                    │                                     │
                    │  ┌──────────┐    ┌──────────┐     │
                    │  │ Facebook │    │   CRM    │     │
                    │  │ Ads API  │    │  System  │     │
                    │  └─────┬────┘    └────┬─────┘     │
                    └────────┼──────────────┼───────────┘
                             │              │
                             │              │
                   ┌─────────▼──────────────▼──────────┐
                   │    DATA INGESTION LAYER           │
                   │  (AWS Lambda Functions)           │
                   │                                    │
                   │  ┌────────────────────────────┐   │
                   │  │ Facebook Connector         │   │
                   │  │ - Runs every 4 hours       │   │
                   │  │ - Rate limit management    │   │
                   │  │ - OAuth token refresh      │   │
                   │  └────────────────────────────┘   │
                   │                                    │
                   │  ┌────────────────────────────┐   │
                   │  │ CRM Webhook Listener       │   │
                   │  │ - Real-time updates        │   │
                   │  │ - Lead status changes      │   │
                   │  └────────────────────────────┘   │
                   └────────────┬───────────────────────┘
                                │
                                │ Write raw data
                                ▼
                   ┌────────────────────────────────────┐
                   │       DATA STORAGE LAYER           │
                   │                                    │
                   │  ┌──────────────┐  ┌───────────┐  │
                   │  │ PostgreSQL   │  │    S3     │  │
                   │  │   (RDS)      │  │  Bucket   │  │
                   │  │              │  │           │  │
                   │  │ • campaigns  │  │ • Raw CSVs│  │
                   │  │ • metrics    │  │ • Backups │  │
                   │  │ • scores     │  │ • Archives│  │
                   │  └──────┬───────┘  └───────────┘  │
                   └─────────┼──────────────────────────┘
                             │
                             │ Read campaign data
                             ▼
                   ┌────────────────────────────────────┐
                   │    SCORING ENGINE (CORE LOGIC)     │
                   │       AWS Lambda Function          │
                   │                                    │
                   │  ┌────────────────────────────┐   │
                   │  │ 1. Load campaign data      │   │
                   │  │ 2. Calculate 5 dimensions: │   │
                   │  │    • Cost Efficiency       │   │
                   │  │    • Lead Quality          │   │
                   │  │    • Volume                │   │
                   │  │    • Trends                │   │
                   │  │    • Engagement            │   │
                   │  │ 3. Generate recommendation │   │
                   │  │ 4. Store results           │   │
                   │  └────────────────────────────┘   │
                   │                                    │
                   │  Triggered: Every 6 hours (cron)   │
                   └────────────┬───────────────────────┘
                                │
                                │ Publish results
                                ▼
                   ┌────────────────────────────────────┐
                   │      DELIVERY & PRESENTATION       │
                   │                                    │
                   │  ┌──────────┐  ┌──────────────┐   │
                   │  │  Email   │  │  Dashboard   │   │
                   │  │  Alerts  │  │  (Streamlit) │   │
                   │  │  (SES)   │  │  on ECS      │   │
                   │  └──────────┘  └──────────────┘   │
                   │                                    │
                   │  ┌──────────────────────────┐     │
                   │  │    REST API              │     │
                   │  │    (API Gateway +        │     │
                   │  │    Lambda/FastAPI)       │     │
                   │  │                          │     │
                   │  │  GET /scores             │     │
                   │  │  GET /recommendations    │     │
                   │  └──────────────────────────┘     │
                   └────────────────────────────────────┘
```

---

## 2. AWS Service Mapping

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS CLOUD                            │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                     VPC (Virtual Private Cloud)        │  │
│  │                                                        │  │
│  │  ┌──────────────────┐      ┌──────────────────┐      │  │
│  │  │  Private Subnet  │      │  Public Subnet   │      │  │
│  │  │                  │      │                  │      │  │
│  │  │  ┌────────────┐  │      │  ┌────────────┐ │      │  │
│  │  │  │    RDS     │  │      │  │    ALB     │ │      │  │
│  │  │  │ PostgreSQL │  │      │  │ (Dashboard)│ │      │  │
│  │  │  └────────────┘  │      │  └────────────┘ │      │  │
│  │  │                  │      │                  │      │  │
│  │  │  ┌────────────┐  │      │  ┌────────────┐ │      │  │
│  │  │  │   Lambda   │  │      │  │  NAT GW    │ │      │  │
│  │  │  │  (in VPC)  │  │      │  └────────────┘ │      │  │
│  │  │  └────────────┘  │      │                  │      │  │
│  │  └──────────────────┘      └──────────────────┘      │  │
│  │                                                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │   Lambda         │      │   S3 Bucket      │            │
│  │   (outside VPC)  │      │   - Raw data     │            │
│  │   - API Gateway  │      │   - Backups      │            │
│  │   - Facebook API │      │   - Archives     │            │
│  └──────────────────┘      └──────────────────┘            │
│                                                              │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  EventBridge     │      │   SES (Email)    │            │
│  │  (Scheduler)     │      │   - Alerts       │            │
│  │  - Cron triggers │      │   - Reports      │            │
│  └──────────────────┘      └──────────────────┘            │
│                                                              │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  Secrets Manager │      │   CloudWatch     │            │
│  │  - API keys      │      │   - Logs         │            │
│  │  - DB credentials│      │   - Metrics      │            │
│  └──────────────────┘      └──────────────────┘            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Data Pipeline Flow (Detailed)

### Facebook API Ingestion Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: EventBridge Trigger (Cron: 0 */4 * * *)             │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Lambda - Facebook Connector                          │
│                                                               │
│  def handler(event, context):                                │
│      # 1. Get OAuth token from Secrets Manager               │
│      token = get_secret('facebook-api-token')                │
│                                                               │
│      # 2. Fetch campaign data (last 7 days)                  │
│      campaigns = facebook_api.get_campaigns(                 │
│          since='2025-11-08',                                 │
│          fields=['id', 'name', 'budget', 'status']           │
│      )                                                        │
│                                                               │
│      # 3. Fetch metrics (insights)                           │
│      for campaign in campaigns:                              │
│          insights = facebook_api.get_insights(               │
│              campaign_id=campaign['id'],                     │
│              fields=['impressions', 'clicks', 'spend']       │
│          )                                                    │
│          campaign['metrics'] = insights                      │
│                                                               │
│      # 4. Save raw data to S3 (audit trail)                  │
│      s3.put_object(                                          │
│          Bucket='leadsmart-raw-data',                        │
│          Key=f'facebook/{date}/campaigns.json',              │
│          Body=json.dumps(campaigns)                          │
│      )                                                        │
│                                                               │
│      # 5. Insert into RDS (staging table)                    │
│      db.insert('staging_campaigns', campaigns)               │
│                                                               │
│      # 6. Data quality checks                                │
│      validation_errors = validate_data(campaigns)            │
│      if validation_errors:                                   │
│          send_alert('Data quality issues', validation_errors)│
│                                                               │
│      # 7. Promote to production table                        │
│      db.execute('''                                          │
│          INSERT INTO campaigns                               │
│          SELECT * FROM staging_campaigns                     │
│          ON CONFLICT (campaign_id) DO UPDATE ...             │
│      ''')                                                     │
│                                                               │
│      return {'statusCode': 200, 'campaigns_processed': len} │
└──────────────┬───────────────────────────────────────────────┘
               │
               │ On success: Publish to SNS topic
               │ On failure: Send to DLQ, retry 3x
               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: CloudWatch Logs & Metrics                            │
│                                                               │
│  • Log: "Processed 1,234 campaigns in 45 seconds"           │
│  • Metric: facebook_api_calls = 67                           │
│  • Metric: campaigns_updated = 1,234                         │
└───────────────────────────────────────────────────────────────┘
```

---

## 4. Scoring Engine Flow (Detailed)

```
┌──────────────────────────────────────────────────────────────┐
│ INPUT: Trigger (EventBridge cron or manual invoke)           │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Load Data from RDS                                   │
│                                                               │
│  SELECT                                                       │
│      c.campaign_id,                                          │
│      c.campaign_name,                                        │
│      c.daily_budget,                                         │
│      m.impressions,                                          │
│      m.clicks,                                               │
│      m.spend,                                                │
│      m.ctr,                                                  │
│      COUNT(l.lead_id) as total_leads,                        │
│      SUM(CASE WHEN l.status = 'qualified' THEN 1 ELSE 0 END) │
│          as qualified_leads                                  │
│  FROM campaigns c                                            │
│  LEFT JOIN campaign_metrics m ON c.campaign_id = m.campaign_id│
│  LEFT JOIN campaign_leads l ON c.campaign_id = l.campaign_id│
│  WHERE m.date >= NOW() - INTERVAL '30 days'                 │
│  GROUP BY c.campaign_id                                      │
│                                                               │
│  Result: DataFrame with 5,000 campaigns                      │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Calculate Scores (5 Dimensions)                      │
│                                                               │
│  for campaign in campaigns:                                  │
│      # Dimension 1: Cost Efficiency (0-25 points)            │
│      cpql = campaign['spend'] / campaign['qualified_leads']  │
│      cost_score = calculate_cost_score(cpql)                 │
│                                                               │
│      # Dimension 2: Lead Quality (0-25 points)               │
│      qual_rate = campaign['qualified_leads'] / total_leads   │
│      quality_score = calculate_quality_score(qual_rate)      │
│                                                               │
│      # Dimension 3: Volume (0-20 points)                     │
│      volume_score = calculate_volume_score(qualified_leads)  │
│                                                               │
│      # Dimension 4: Trends (0-20 points)                     │
│      trend_score = calculate_trend_score(campaign)           │
│                                                               │
│      # Dimension 5: Engagement (0-10 points)                 │
│      engagement_score = calculate_engagement_score(ctr)      │
│                                                               │
│      # Total Score                                           │
│      total_score = sum([cost, quality, volume, trend, eng])  │
│                                                               │
│      # Recommendation Logic                                  │
│      if total_score >= 80:                                   │
│          recommendation = 'INCREASE_BUDGET'                  │
│      elif total_score >= 60:                                 │
│          recommendation = 'CONTINUE_OPTIMIZE'                │
│      elif total_score >= 40:                                 │
│          recommendation = 'TEST_CHANGES'                     │
│      elif total_score >= 20:                                 │
│          recommendation = 'REDUCE_BUDGET'                    │
│      else:                                                   │
│          recommendation = 'PAUSE_CAMPAIGN'                   │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Save Results to Database                             │
│                                                               │
│  INSERT INTO campaign_scores (                               │
│      campaign_id, date, total_score,                         │
│      cost_efficiency_score, lead_quality_score,              │
│      volume_score, trend_score, engagement_score,            │
│      recommendation, recommendation_details                  │
│  ) VALUES (...)                                              │
│  ON CONFLICT (campaign_id, date)                             │
│  DO UPDATE SET ...                                           │
│                                                               │
│  -- Also insert into score_history for trend analysis        │
│  INSERT INTO score_history (                                 │
│      campaign_id, date, total_score, recommendation          │
│  ) VALUES (...)                                              │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 4: Trigger Downstream Actions                           │
│                                                               │
│  • Publish to SNS topic: 'campaign-scores-updated'           │
│  • Email Lambda subscribes to SNS, sends alerts              │
│  • Dashboard reads from RDS (no action needed)               │
│  • CloudWatch logs: "Scored 5,000 campaigns in 3.2 minutes" │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│ OUTPUT: Campaign scores stored, alerts triggered             │
└───────────────────────────────────────────────────────────────┘
```

---

## 5. Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  INTERNET (Public Access)                    │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ HTTPS (TLS 1.2+)
               ▼
┌─────────────────────────────────────────────────────────────┐
│ AWS WAF (Web Application Firewall) - Optional Phase 2       │
│  • Rate limiting (100 req/min per IP)                        │
│  • SQL injection protection                                  │
│  • XSS protection                                            │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ CloudFront (CDN) - Optional for dashboard static assets     │
│  • SSL certificate (ACM)                                     │
│  • DDOS protection (AWS Shield)                              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ Application Load Balancer (ALB)                              │
│  • HTTPS listener (port 443)                                 │
│  • SSL certificate (ACM)                                     │
│  • Health checks (every 30 sec)                              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ AWS Cognito (Authentication)                                 │
│  • User pool (email + password)                              │
│  • JWT tokens (1 hour expiry)                                │
│  • MFA (optional, SMS or TOTP)                               │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ Authorized requests only
               ▼
┌─────────────────────────────────────────────────────────────┐
│ Application Layer (ECS Fargate + Lambda)                     │
│  • IAM roles (principle of least privilege)                  │
│  • Security groups (restrict inbound to ALB only)            │
│  • Environment variables (encrypted at rest)                 │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ TLS connection
               ▼
┌─────────────────────────────────────────────────────────────┐
│ RDS PostgreSQL (Private Subnet)                              │
│  • Encryption at rest (AES-256)                              │
│  • SSL connections enforced                                  │
│  • Security group (port 5432 from app only)                  │
│  • No public IP address                                      │
│  • Master user password in Secrets Manager                   │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ Audit & Monitoring                                           │
│  • CloudTrail (all API calls logged)                         │
│  • CloudWatch Logs (application logs)                        │
│  • VPC Flow Logs (network traffic)                           │
│  • AWS Config (compliance checks)                            │
└──────────────────────────────────────────────────────────────┘
```

### IAM Roles & Policies

```
┌─────────────────────────────────────────────────────────────┐
│ Lambda Execution Role: "scoring-engine-lambda-role"          │
│                                                               │
│  Permissions:                                                 │
│  • logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents│
│  • rds:DescribeDBInstances (read-only)                       │
│  • secretsmanager:GetSecretValue (specific secrets only)     │
│  • s3:PutObject (leadsmart-raw-data bucket only)             │
│  • sns:Publish (campaign-scores-updated topic only)          │
│  • ec2:CreateNetworkInterface (for VPC access)               │
│                                                               │
│  Trust Policy:                                                │
│  {                                                            │
│    "Principal": {"Service": "lambda.amazonaws.com"},         │
│    "Action": "sts:AssumeRole"                                │
│  }                                                            │
└───────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ ECS Task Role: "dashboard-ecs-task-role"                     │
│                                                               │
│  Permissions:                                                 │
│  • logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents│
│  • rds:DescribeDBInstances (read-only)                       │
│  • secretsmanager:GetSecretValue (DB credentials only)       │
│  • s3:GetObject (dashboard-assets bucket only)               │
│                                                               │
│  Trust Policy:                                                │
│  {                                                            │
│    "Principal": {"Service": "ecs-tasks.amazonaws.com"},      │
│    "Action": "sts:AssumeRole"                                │
│  }                                                            │
└───────────────────────────────────────────────────────────────┘
```

---

## 6. Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                                                               │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐           │
│  │  Lambda   │    │    ECS    │    │    API    │           │
│  │ Functions │    │  Fargate  │    │  Gateway  │           │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘           │
│        │                 │                 │                 │
│        │ Emit logs       │ Emit logs       │ Emit logs       │
│        │ & metrics       │ & metrics       │ & metrics       │
│        └─────────────────┴─────────────────┘                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    CloudWatch Logs                           │
│  • Log Group: /aws/lambda/scoring-engine                     │
│  • Log Group: /ecs/dashboard                                 │
│  • Log Group: /aws/apigateway/leadsmart                      │
│                                                               │
│  Retention: 30 days                                          │
│  Insights queries: Cost analysis, error rate, slow queries   │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                 CloudWatch Metrics                           │
│                                                               │
│  Custom Metrics:                                              │
│  • CampaignsScored (count)                                   │
│  • ScoringDuration (milliseconds)                            │
│  • FacebookAPICalls (count)                                  │
│  • DataQualityErrors (count)                                 │
│                                                               │
│  AWS Metrics:                                                 │
│  • Lambda: Invocations, Errors, Duration, Throttles          │
│  • RDS: CPUUtilization, DatabaseConnections, ReadLatency     │
│  • ECS: CPUUtilization, MemoryUtilization                    │
│  • API Gateway: Count, Latency, 4XXError, 5XXError          │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│               CloudWatch Alarms                              │
│                                                               │
│  Critical:                                                    │
│  • Lambda error rate >5% for 5 minutes → PagerDuty           │
│  • RDS CPU >90% for 10 minutes → PagerDuty                   │
│  • Data pipeline failed 3x → PagerDuty                       │
│                                                               │
│  High:                                                        │
│  • API latency p95 >1000ms for 5 minutes → Slack            │
│  • Email bounce rate >10% → Slack                            │
│                                                               │
│  Medium:                                                      │
│  • Daily AWS spend >$50 → Email                              │
│  • Data quality errors >20% → Email                          │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│            Sentry (Error Tracking)                           │
│                                                               │
│  • Real-time error alerts                                    │
│  • Full stack traces                                         │
│  • Error grouping & deduplication                            │
│  • Release tracking (which deployment caused errors?)        │
│                                                               │
│  Integration: Python SDK in Lambda & ECS                     │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│              Alerting Destinations                           │
│                                                               │
│  • PagerDuty (critical alerts, wake up on-call)              │
│  • Slack #leadsmart-alerts (high/medium alerts)              │
│  • Email (daily digest, weekly reports)                      │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Disaster Recovery Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRIMARY REGION (us-east-1)                │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Lambda     │    │   RDS        │    │     S3       │  │
│  │  Functions   │    │  PostgreSQL  │    │   Bucket     │  │
│  │              │    │              │    │              │  │
│  │ • Scoring    │    │ • campaigns  │    │ • Raw data   │  │
│  │ • Ingestion  │    │ • metrics    │    │ • Backups    │  │
│  │ • API        │    │ • scores     │    │              │  │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘  │
│                              │                    │          │
└──────────────────────────────┼────────────────────┼──────────┘
                               │                    │
                               │ Auto backup        │ Replication
                               │ every 6 hours      │
                               ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                BACKUP & ARCHIVE STORAGE                      │
│                                                               │
│  ┌──────────────────────────────────────────────┐           │
│  │ RDS Automated Backups (us-east-1)            │           │
│  │ • Daily snapshots (7-day retention)          │           │
│  │ • Point-in-time recovery (5-minute RPO)      │           │
│  │ • Can restore to any time in last 7 days    │           │
│  └──────────────────────────────────────────────┘           │
│                                                               │
│  ┌──────────────────────────────────────────────┐           │
│  │ S3 Cross-Region Replication (us-east-1 → us-west-2)│     │
│  │ • Replicates all raw data & backups          │           │
│  │ • Versioning enabled (30-day retention)      │           │
│  │ • Can restore from us-west-2 if us-east-1 down│         │
│  └──────────────────────────────────────────────┘           │
│                                                               │
│  ┌──────────────────────────────────────────────┐           │
│  │ S3 Glacier (Long-term archive)               │           │
│  │ • Data older than 90 days moved to Glacier   │           │
│  │ • 1-year retention                            │           │
│  │ • Retrieval time: 1-5 hours                  │           │
│  └──────────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────┘
```

### Recovery Procedures

```
Scenario 1: Database Corruption
├── Detection: Data quality check fails, invalid data in production table
├── Impact: Users see incorrect scores
├── RTO: 4 hours
├── RPO: 24 hours
└── Procedure:
    1. Identify corruption timestamp (check CloudWatch logs)
    2. Find last good snapshot (before corruption)
    3. Restore RDS from snapshot:
       aws rds restore-db-instance-from-db-snapshot \
         --db-instance-identifier leadsmart-restored \
         --db-snapshot-identifier rds:leadsmart-2025-11-14-06-00
    4. Update DNS to point to restored instance (or update app config)
    5. Re-run scoring for missing period (between snapshot and now)
    6. Verify data integrity with validation queries
    7. Cut over to restored instance

Scenario 2: Lambda Function Bug (Producing Incorrect Scores)
├── Detection: Sentry alert, user reports, or validation test failure
├── Impact: Incorrect recommendations sent to users
├── RTO: 5 minutes
├── RPO: 0 (no data loss)
└── Procedure:
    1. Identify bad deployment (check GitHub commit, Sentry release)
    2. Rollback Lambda to previous version:
       aws lambda update-alias --function-name scoring-engine-prod \
         --name production --function-version 42
    3. Verify rollback with smoke test (invoke Lambda manually)
    4. Re-score affected campaigns (query scores from bad deployment period)
    5. Send corrected recommendations to users
    6. Post-mortem: What caused the bug? Add test case to prevent recurrence

Scenario 3: Region Outage (us-east-1 Unavailable)
├── Detection: All services in us-east-1 returning errors
├── Impact: Complete service outage
├── RTO: 8 hours (if DR environment pre-provisioned in us-west-2)
├── RPO: 24 hours
└── Procedure:
    1. Confirm region-wide outage (AWS Service Health Dashboard)
    2. Activate DR plan (page DevOps lead)
    3. Restore RDS from latest snapshot to us-west-2:
       aws rds restore-db-instance-from-db-snapshot \
         --db-instance-identifier leadsmart-prod-usw2 \
         --db-snapshot-identifier rds:leadsmart-latest \
         --region us-west-2
    4. Deploy Lambda functions to us-west-2 (Terraform apply -var region=us-west-2)
    5. Update DNS (Route53) to point to us-west-2 load balancer
    6. Verify all services operational in us-west-2
    7. Communicate to users (service restored, may have stale data from last 24h)
    8. Once us-east-1 recovers, migrate back (reverse procedure)
```

---

## 8. Cost Breakdown Visualization

```
Monthly Cost Breakdown (MVP - $90/month)
┌────────────────────────────────────────────────────────┐
│                                                         │
│  RDS (db.t4g.micro)        ████████████  $13  (14%)    │
│  ECS Fargate (Dashboard)   ███████████████  $15  (17%) │
│  Sentry (SaaS)             ████████████████████  $26  (29%)│
│  Lambda (Scoring)          ████  $4  (4%)               │
│  Lambda (Ingestion)        ███  $3  (3%)                │
│  S3 Storage                ██████  $6  (7%)             │
│  CloudWatch Logs           ███  $3  (3%)                │
│  Secrets Manager           ██  $2  (2%)                 │
│  Other (SES, API GW, etc.) ████  $3  (3%)               │
│  Contingency               ███████████  $15  (17%)      │
│                                                         │
│  TOTAL: $90/month                                       │
└────────────────────────────────────────────────────────┘

Monthly Cost Breakdown (Scale - $461/month at 100 clients)
┌────────────────────────────────────────────────────────┐
│                                                         │
│  Sentry (Team plan)        ████████  $80  (17%)        │
│  Lambda (Scoring)          ████████████  $80  (17%)    │
│  Contingency               ███████████  $75  (16%)     │
│  S3 Storage                ████████  $60  (13%)        │
│  RDS (db.t4g.small)        ████████  $35  (8%)         │
│  Lambda (Ingestion)        ████████  $30  (7%)         │
│  ECS Fargate (Dashboard)   ████████  $30  (7%)         │
│  CloudWatch Logs           ██████  $25  (5%)           │
│  ElastiCache Redis         ████  $12  (3%)             │
│  SES (Email)               ████  $10  (2%)             │
│  Other                     █████  $24  (5%)            │
│                                                         │
│  TOTAL: $461/month                                      │
└────────────────────────────────────────────────────────┘
```

---

## 9. Deployment Pipeline (CI/CD)

```
┌─────────────────────────────────────────────────────────────┐
│                 Developer Workflow                           │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Developer commits code to feature branch                  │
│    git checkout -b feature/add-trend-scoring                 │
│    git commit -m "Add trend scoring logic"                   │
│    git push origin feature/add-trend-scoring                 │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. GitHub Actions: Run Tests (on push to any branch)         │
│                                                               │
│    jobs:                                                      │
│      test:                                                    │
│        runs-on: ubuntu-latest                                │
│        steps:                                                 │
│          - name: Run unit tests                              │
│            run: pytest tests/unit/ --cov=src                 │
│          - name: Run linting                                 │
│            run: flake8 src/ tests/                           │
│          - name: Run type checking                           │
│            run: mypy src/                                    │
│                                                               │
│    Result: ✅ All checks passed OR ❌ Tests failed           │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ If tests pass
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Developer creates Pull Request (PR)                       │
│    Title: "Add trend scoring logic"                          │
│    Reviewers: Data team lead, DevOps engineer                │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ After review approval
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Merge PR to `develop` branch                              │
│    Triggers: GitHub Actions workflow "deploy-staging"        │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. GitHub Actions: Deploy to Staging                         │
│                                                               │
│    jobs:                                                      │
│      deploy-staging:                                          │
│        runs-on: ubuntu-latest                                │
│        steps:                                                 │
│          - name: Build Docker image                          │
│            run: docker build -t scoring-engine:${{ sha }} .  │
│          - name: Push to ECR                                 │
│            run: docker push ecr.aws/.../scoring-engine:$sha  │
│          - name: Deploy Lambda (Terraform)                   │
│            run: |                                            │
│              cd infrastructure                               │
│              terraform workspace select staging              │
│              terraform apply -var image_tag=$sha -auto-approve│
│          - name: Run smoke tests                             │
│            run: pytest tests/smoke/ --env=staging            │
│                                                               │
│    Result: Staging environment updated with new code         │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ After 48-hour soak test
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Promote to Production                                     │
│    git checkout main                                         │
│    git merge develop --no-ff                                 │
│    git tag -a v1.2.0 -m "Release v1.2.0: Add trend scoring" │
│    git push origin main --tags                               │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. GitHub Actions: Deploy to Production (tag trigger)        │
│                                                               │
│    jobs:                                                      │
│      deploy-production:                                       │
│        runs-on: ubuntu-latest                                │
│        environment: production  # Requires manual approval   │
│        steps:                                                 │
│          - name: Wait for approval (manual gate)             │
│            uses: trstringer/manual-approval@v1               │
│          - name: Deploy to production (blue-green)           │
│            run: |                                            │
│              # Deploy to 'green' environment                 │
│              terraform apply -var env=production-green       │
│              # Run smoke tests on green                      │
│              pytest tests/smoke/ --env=production-green      │
│              # If tests pass, switch traffic to green        │
│              aws lambda update-alias --function-name scoring \│
│                --name production --routing-config \         │
│                AdditionalVersionWeights={green=0.1}          │
│              # Monitor for 30 minutes                        │
│              sleep 1800                                      │
│              # If no errors, route 100% to green            │
│              aws lambda update-alias ... \                   │
│                --routing-config AdditionalVersionWeights={}  │
│                                                               │
│    Result: Production updated, with automatic rollback on error│
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. Post-Deployment Verification                              │
│    • CloudWatch dashboard: Check for error spikes            │
│    • Sentry: Monitor new error reports                       │
│    • User feedback: Any complaints in Slack?                 │
│    • Validation test: Run scoring on known dataset, verify   │
└──────────────────────────────────────────────────────────────┘
```

---

## Summary

This architecture document provides visual representations of:
1. **High-level system architecture** - How components interact
2. **AWS service mapping** - Which AWS services are used where
3. **Data pipeline flow** - Step-by-step data ingestion & scoring
4. **Security architecture** - Layers of defense (WAF, IAM, encryption)
5. **Monitoring architecture** - Logs, metrics, alerts flow
6. **Disaster recovery** - Backup strategies & recovery procedures
7. **Cost breakdown** - Where money is spent (MVP vs Scale)
8. **CI/CD pipeline** - Code to production deployment flow

**Recommended Diagramming Tools:**
- **draw.io** (free, web-based) - For flowcharts and architecture diagrams
- **Lucidchart** (free tier available) - Collaborative diagramming
- **Excalidraw** (free, open-source) - Hand-drawn style diagrams
- **CloudCraft** (AWS-specific) - 3D AWS architecture diagrams
- **Mermaid** (markdown-based) - Version-controlled diagrams in code

For the actual assessment, I recommend creating visual diagrams using one of these tools and exporting as PNG/PDF to accompany the written production plan.
