# Part 4: Strategic Decision System Documentation

## Executive Summary

The Strategic Decision System is a quantitative model that evaluates campaign performance across five dimensions and provides actionable recommendations on whether to continue, scale, or stop each campaign. The system scores campaigns on a 0-100 scale and generates specific actions: increase budget, continue with optimization, monitor closely, reduce budget, or pause immediately.

## System Overview

### Objective
Help businesses make data-driven decisions about which marketing campaigns to continue funding and which to stop, preventing capital burn on underperforming campaigns while identifying opportunities to scale winners.

### Methodology
The system uses a multi-dimensional scoring approach that evaluates campaigns across five key areas:

1. **Cost Efficiency (0-25 points)** - Evaluates cost per qualified lead relative to target benchmarks
2. **Lead Quality (0-25 points)** - Measures qualification rate and lead-to-customer potential
3. **Volume Adequacy (0-20 points)** - Ensures statistical significance for confident decision-making
4. **Performance Trends (0-20 points)** - Analyzes trajectory (improving vs declining)
5. **Engagement Quality (0-10 points)** - Measures click-through and conversion rates

**Total Score: 0-100 points**

## Scoring Model Details

### 1. Cost Efficiency Score (0-25 points)

Evaluates the cost per qualified lead (CPQL) against target benchmarks.

**Scoring Logic:**
- 25 points: CPQL ≤ $50 (50% of target)
- 20 points: CPQL ≤ $100 (at target)
- 15 points: CPQL ≤ $150 (50% above target)
- 10 points: CPQL ≤ $200 (2x target)
- 5 points: CPQL ≤ $300 (3x target)
- 0 points: CPQL > $300 (unacceptable)

**Rationale:** Cost efficiency is paramount. A campaign that costs 3x the target to acquire a qualified lead is burning capital and should score very low, regardless of other factors.

### 2. Lead Quality Score (0-25 points)

Measures the percentage of leads that become qualified.

**Scoring Logic:**
- 25 points: Qualification rate ≥ 22.5% (1.5x target)
- 20 points: Qualification rate ≥ 15% (at target)
- 15 points: Qualification rate ≥ 10.5% (70% of target)
- 10 points: Qualification rate ≥ 6% (40% of target)
- 5 points: Qualification rate > 0%
- 0 points: No qualified leads

**Rationale:** High qualification rates indicate excellent targeting and lead quality. Even with moderate volume, campaigns with 20%+ qualification deserve high scores.

### 3. Volume Score (0-20 points)

Ensures sufficient data for confident decision-making.

**Scoring Logic:**
- 20 points: ≥20 qualified leads (high confidence)
- 15 points: ≥10 qualified leads (good confidence)
- 10 points: ≥5 qualified leads (minimum confidence)
- 5 points: ≥20 total leads but no conversions
- 0 points: Insufficient data

**Rationale:** Statistical significance matters. We need sufficient sample size to make confident decisions about stopping or scaling campaigns.

### 4. Trend Score (0-20 points)

Analyzes whether performance is improving or declining.

**Scoring Logic:**
- Start at 10 points (neutral for new campaigns)
- +5 points: CTR improving significantly (>0.5% gain)
- +3 points: CTR improving moderately
- -5 points: CTR declining significantly (>0.5% loss)
- -3 points: CTR declining moderately
- +5 points: Cost per conversion improving significantly (>$20 reduction)
- +3 points: Cost per conversion improving moderately
- -5 points: Cost per conversion worsening significantly (>$20 increase)
- -3 points: Cost per conversion worsening moderately

**Rationale:** Trends matter more than point-in-time snapshots. A campaign with mediocre current performance but strong upward trajectory may be worth continuing, while a declining high performer may need attention.

### 5. Engagement Score (0-10 points)

Measures audience engagement through CTR and conversion rate.

**Scoring Logic (CTR):**
- 6 points: CTR ≥ 3% (3x minimum)
- 4 points: CTR ≥ 2% (2x minimum)
- 2 points: CTR ≥ 1% (at minimum)
- 0 points: CTR < 1%

**Scoring Logic (Conversion Rate):**
- 4 points: Conversion rate ≥ 5%
- 2 points: Conversion rate ≥ 2%
- 1 point: Conversion rate > 0%
- 0 points: No conversions

**Rationale:** Engagement metrics indicate creative quality and audience fit. Poor engagement suggests fundamental issues with messaging or targeting.

## Decision Framework

### Action Thresholds

| Score Range | Action | Rationale |
|-------------|--------|-----------|
| 80-100 | **INCREASE_BUDGET** | Excellent performance across all dimensions. Scale by 30-50% |
| 60-79 | **CONTINUE_OPTIMIZE** | Solid performance. Continue while testing improvements |
| 40-59 | **TEST_CHANGES** or **MONITOR_CLOSELY** | Concerning performance. Test significant changes to creative/targeting. If insufficient data, monitor for 2 more weeks |
| 20-39 | **REDUCE_BUDGET** | Poor performance. Cut budget by 50% while attempting fixes |
| 0-19 | **PAUSE_CAMPAIGN** | Critical underperformance. Immediate pause required |

### Special Cases

1. **New Campaigns (< 2 weeks, < 20 leads)**: Automatically receive neutral trend score (10 points) and "MONITOR_CLOSELY" recommendation even if scoring in poor range, to allow learning period

2. **High Spend Underperformers**: Campaigns spending $1000+/day with scores < 40 are flagged as "URGENT" priority for immediate review

3. **Declining Winners**: Campaigns that previously scored 70+ but now score 50-69 with negative trends are flagged for "DIAGNOSTIC REVIEW" before cutting budget

## Delivery Mechanism

### Daily Automated Reports

**Morning Campaign Alert Email** (sent at 8 AM):
- Subject: "Campaign Performance Alert: X campaigns need immediate attention"
- Red Section: Campaigns to pause (critical underperformers)
- Yellow Section: Campaigns to reduce budget (poor performers)
- Green Section: Campaigns to scale (high performers)
- Each section includes campaign name, platform, current spend, score, and specific recommendation

**Weekly Strategic Review** (sent Friday):
- Comprehensive dashboard with:
  - Portfolio performance trends
  - Budget reallocation recommendations
  - A/B test results for concerning campaigns
  - Month-over-month improvement tracking

### Interactive Dashboard

**Real-time Dashboard Features:**
1. **Campaign Scorecard**: Live view of all campaigns with color-coded scores
2. **Drill-down Analysis**: Click any campaign to see detailed breakdown
3. **What-If Calculator**: Model impact of budget changes
4. **Alert Center**: Prioritized action items with one-click approval
5. **Historical Trends**: Track how campaign scores change over time

**Access Levels:**
- **Marketing Managers**: View all reports, export data, access recommendations
- **Campaign Operators**: View assigned campaigns, see recommended actions
- **Finance/Leadership**: Portfolio overview, budget impact summaries

### API Integration

For businesses using marketing automation platforms:
- **Real-time API**: Query campaign scores and recommendations programmatically
- **Webhook Alerts**: Push notifications when campaigns cross critical thresholds
- **Budget Automation**: Optional auto-adjust budgets based on scores (with approval workflow)

### Mobile App

**Push Notifications:**
- "Campaign XYZ is underperforming. Pause recommended."
- "Campaign ABC scored 85! Consider increasing budget."
- Daily summary of campaigns requiring attention

## Key Assumptions

### Financial Assumptions

1. **Target CPQL = $100**
   - Assumption: Qualified leads convert to customers at a rate that makes $100/lead profitable
   - **NEEDS VALIDATION**: Actual conversion rate from qualified lead to closed deal
   - **NEEDS VALIDATION**: Average commission/profit per closed deal

2. **Acceptable Cost Ranges**
   - Excellent: ≤$50 per qualified lead
   - Good: $50-100 per qualified lead
   - Acceptable: $100-150 per qualified lead
   - Poor: $150-300 per qualified lead
   - Unacceptable: >$300 per qualified lead

### Performance Assumptions

3. **Target Qualification Rate = 15%**
   - Assumption: Real estate lead generation typically sees 10-20% qualification rates
   - **NEEDS VALIDATION**: Historical qualification rates by lead source
   - **NEEDS VALIDATION**: Definition of "qualified" (MQL vs SQL)

4. **Minimum Sample Size = 5 qualified leads**
   - Assumption: Need at least 5 conversions for statistically meaningful decisions
   - Based on: Power analysis for proportion tests at 80% confidence
   - **NEEDS VALIDATION**: Business tolerance for uncertainty in decision-making

5. **Target CTR = 1%**
   - Assumption: Industry standard for paid search/social
   - Varies by: Platform (LinkedIn higher, display lower)
   - **NEEDS VALIDATION**: Historical CTR benchmarks by platform

### Operational Assumptions

6. **Campaign Maturity Period = 14 days**
   - New campaigns get 2 weeks before harsh judgments
   - Assumption: Learning algorithms need time to optimize
   - **NEEDS VALIDATION**: Actual platform optimization timeline

7. **Equal Value Leads**
   - Current model treats all qualified leads as equal value
   - Reality: Commercial deals likely worth more than residential
   - **NEEDS IMPROVEMENT**: Weight by actual deal value when available

8. **No Strategic Premium**
   - Current model is purely performance-based
   - Reality: Some campaigns may have brand/awareness value beyond leads
   - **NEEDS INPUT**: Which campaigns have strategic importance?

## Critical Questions for Stakeholders

### Business Model Validation

1. **What is the conversion rate from qualified lead to closed deal?**
   - Needed to validate the $100 CPQL target
   - Should vary by lead source and quality

2. **What is the average revenue/profit per closed deal?**
   - Needed to calculate acceptable customer acquisition cost
   - May differ significantly by property type

3. **What is the acceptable payback period?**
   - Can we spend more upfront if leads convert over 6-12 months?
   - Or do we need immediate ROI?

### Strategic Priorities

4. **Are there campaigns running for non-lead objectives?**
   - Brand awareness campaigns shouldn't be judged on CPQL
   - Need to identify and score differently

5. **How aggressive should we be with new campaigns?**
   - Current model gives 2 weeks grace period
   - Is this too long? Too short?

6. **Are there seasonal considerations?**
   - Real estate may have high/low seasons
   - Should targets adjust by season?

### Operational Constraints

7. **How quickly can budget changes be implemented?**
   - Can we pause daily? Weekly?
   - Platform-dependent answer

8. **Are there minimum spend commitments?**
   - Contracts may prevent immediate pausing
   - Need to flag these campaigns

9. **What is the team's capacity for A/B testing?**
   - Model recommends testing on concerning campaigns
   - How many simultaneous tests can be managed?

10. **Should we incorporate lead lifecycle value?**
    - Some leads may take months to convert
    - Should we track beyond immediate qualification?

## Model Refinements Roadmap

### Phase 1: Enhanced (Next 30 days)

1. **Platform-Specific Benchmarks**
   - Different CPQL targets for Google vs Facebook vs LinkedIn
   - Platform performance varies significantly

2. **Objective-Based Scoring**
   - Separate scoring for awareness vs conversion campaigns
   - Not everything should be judged on leads

3. **Budget Impact Visualization**
   - Show projected impact of following recommendations
   - "If you pause these 5 campaigns, you'll save $X and lose Y leads"

### Phase 2: Predictive (60-90 days)

4. **Early Warning System**
   - Detect campaigns trending downward before they fully fail
   - "This campaign scored 65 today but is declining fast"

5. **Seasonal Adjustment**
   - Learn seasonal patterns and adjust expectations
   - Q4 vs Q1 may have different norms

6. **Lifetime Value Integration**
   - Track leads through to closed deals
   - Score based on actual revenue, not just qualification

### Phase 3: Autonomous (90+ days)

7. **Auto-Optimization**
   - Automatically pause critically underperforming campaigns
   - Auto-increase budget on consistent winners
   - Always with approval workflow option

8. **Portfolio Optimization**
   - Not just scoring individual campaigns
   - Optimize total budget allocation across all campaigns
   - "Move $5K from campaign A to campaign B for 20% more leads"

9. **Competitive Intelligence**
   - Incorporate competitor spending and market share data
   - "Campaign X is underperforming but competitors are also struggling in this segment"

## Technical Implementation

### Data Requirements

**Input Data:**
- Campaign metadata (ID, name, platform, objective, dates)
- Daily metrics (impressions, clicks, cost, conversions)
- Lead-level data (lead ID, campaign source, qualification status, timestamp)
- Lead status changes (lifecycle tracking)

**Data Frequency:**
- Real-time for critical alerts (pause recommendations)
- Daily batch for comprehensive scoring
- Weekly for trend analysis and strategic reports

**Data Quality Requirements:**
- UTM tracking on all campaigns
- Consistent lead attribution methodology
- Qualified lead definition standardized across team

### Calculation Pipeline

1. **Daily ETL** (runs at 2 AM)
   - Pull previous day's metrics from ad platforms
   - Update lead qualification status from CRM
   - Calculate derived metrics (CTR, CPL, CPQL, etc.)

2. **Scoring Engine** (runs at 6 AM)
   - Apply scoring model to all active campaigns
   - Calculate component scores and total scores
   - Generate action recommendations
   - Flag high-priority items

3. **Alert Generation** (runs at 7 AM)
   - Create prioritized action lists
   - Generate email content with personalized recommendations
   - Send push notifications for critical items

4. **Dashboard Refresh** (continuous)
   - Real-time dashboard updated every 15 minutes
   - Historical trends recalculated daily
   - Executive summaries updated weekly

### System Architecture

**Components:**
1. Data ingestion layer (API connections to Google Ads, Facebook, LinkedIn, CRM)
2. Data warehouse (PostgreSQL or Snowflake)
3. Scoring engine (Python service)
4. Reporting service (automated emails, dashboard API)
5. User interface (React dashboard, mobile app)

**Technology Stack:**
- **Backend**: Python (scikit-learn for scoring, pandas for data manipulation)
- **Database**: PostgreSQL (for <100GB) or Snowflake (for larger scale)
- **API**: FastAPI for real-time queries
- **Frontend**: React dashboard with Plotly visualizations
- **Orchestration**: Airflow for daily batch jobs
- **Monitoring**: Datadog for system health, Sentry for error tracking

## Success Metrics for the System Itself

How do we know if the Strategic Decision System is working?

### Performance Metrics

1. **Portfolio CPQL Improvement**
   - Target: 20% reduction in average CPQL within 90 days
   - Measured: Monthly average CPQL across all campaigns

2. **Capital Efficiency**
   - Target: 15% reduction in total spend on campaigns scoring <40
   - Measured: Month-over-month change in low-performer spend

3. **Winner Scaling**
   - Target: 30% increase in budget allocated to campaigns scoring 80+
   - Measured: Share of budget going to high performers

### Adoption Metrics

4. **Recommendation Follow-Through**
   - Target: 80% of "pause" recommendations actioned within 48 hours
   - Measured: Time-to-action for critical alerts

5. **Dashboard Engagement**
   - Target: 90% of marketing team logs in at least 3x per week
   - Measured: Active user count, session duration

6. **Decision Speed**
   - Target: Reduce time from campaign failure to pause from 14 days to 3 days
   - Measured: Average lag between score dropping below 20 and campaign pause

## Appendix: Mathematical Details

### Cost Efficiency Score Formula

```
score = f(CPQL, target_CPQL)

where:
  if CPQL ≤ target * 0.5:
    score = 25
  elif CPQL ≤ target:
    score = 25 - 5 * ((CPQL - target*0.5) / (target*0.5))
  elif CPQL ≤ target * 1.5:
    score = 20 - 5 * ((CPQL - target) / (target*0.5))
  ... (continues for each tier)
```

### Trend Score Calculation

```
recent_performance = mean(metrics[last_7_days])
early_performance = mean(metrics[first_7_days])

ctr_trend = recent_ctr - early_ctr
cost_trend = early_cost_per_conversion - recent_cost_per_conversion

trend_score = 10  # baseline
if ctr_trend > 0.005: trend_score += 5
elif ctr_trend > 0: trend_score += 3
elif ctr_trend < -0.005: trend_score -= 5
elif ctr_trend < 0: trend_score -= 3

# Similar logic for cost_trend
```

### Statistical Significance Testing

For campaigns with few conversions, we use Wilson score interval for proportions:

```
qualified_rate_ci = wilson_score_interval(
    successes=qualified_leads,
    trials=total_leads,
    confidence=0.80
)

# Reduce quality score if confidence interval is wide
uncertainty_penalty = min(5, (ci_upper - ci_lower) * 100)
quality_score = base_score - uncertainty_penalty
```

---

**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Author:** Muhammad Osama  
**Review Cycle:** Monthly (or after major model changes)
