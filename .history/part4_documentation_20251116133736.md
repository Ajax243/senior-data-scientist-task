# Copied from `part4/part4_documentation.md`

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

... (truncated; see part4/part4_documentation.md for full content)
