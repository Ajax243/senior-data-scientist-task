import duckdb
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

st.set_page_config(page_title="Leadsmart – Campaign Intelligence", layout="wide")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Load all data
@st.cache_data
def load_data():
    campaign_metrics = pd.read_csv(DATA_DIR / "campaign_metrics.csv")
    campaign_group = pd.read_csv(DATA_DIR / "campaign_group.csv")
    qualified_by_campaign = pd.read_csv(DATA_DIR / "qualified_by_campaign.csv")
    insights = pd.read_csv(DATA_DIR / "insights.csv")
    campaigns = pd.read_csv(DATA_DIR / "campaigns.csv")
    campaign_leads = pd.read_csv(DATA_DIR / "campaign_leads.csv")
    
    # Convert campaign_id to string/category in all dataframes to ensure it's treated as dimension
    campaign_metrics['campaign_id'] = 'C' + campaign_metrics['campaign_id'].astype(str)
    campaign_group['campaign_id'] = 'C' + campaign_group['campaign_id'].astype(str)
    qualified_by_campaign['campaign_id'] = 'C' + qualified_by_campaign['campaign_id'].astype(str)
    campaigns['id'] = 'C' + campaigns['id'].astype(str)

    # --- Compute qualified_by_campaign using provided status rules ---
    qualified_status = ['QUALIFIED','DONE_DEAL','MEETING_DONE']
    non_qualified_status = ['NOT_QUALIFIED','LOW_BUDGET','SPAM','WRONG_NUMBER','ALREADY_BOUGHT','RESALE_REQUEST']
    undetermined_status = ['UNKNOWN','NO_ANSWER','CALL_AGAIN','FOLLOW_UP','WHATSAPP','SWITCHED_OFF','HIGH INTEREST','RESALE_REQUEST']

    # Normalize campaign_leads
    cl = campaign_leads.copy()
    cl['campaign_id'] = 'C' + cl['campaign_id'].astype(str)
    # Ensure status uppercase and strip
    cl['lead_status'] = cl['lead_status'].astype(str).str.upper().str.strip()
    # Drop potential dup leads per campaign by phone if available
    if 'phone' in cl.columns:
        cl1 = cl.drop_duplicates(subset=['campaign_id','phone'], keep='last')
    else:
        # fallback: drop duplicate by campaign_id + id if phone not present
        key_cols = ['campaign_id'] + (["id"] if 'id' in cl.columns else [])
        cl1 = cl.drop_duplicates(subset=key_cols, keep='last')

    cl1['is_qualified'] = cl1['lead_status'].isin(qualified_status)
    cl1['is_non_qualified'] = cl1['lead_status'].isin(non_qualified_status)

    agg = cl1.groupby('campaign_id').agg(
        qualified_count=('is_qualified','sum'),
        non_qualified_count=('is_non_qualified','sum')
    ).reset_index()
    agg['total_considered'] = agg['qualified_count'] + agg['non_qualified_count']
    agg['qualified_percentage'] = np.where(agg['total_considered']>0,
                                           agg['qualified_count']/agg['total_considered']*100,
                                           0.0)
    agg['qualified_percentage'] = agg['qualified_percentage'].round(2)
    # Override loaded CSV with computed values to ensure consistency
    qualified_by_campaign = agg
    
    # Merge campaign_metrics with campaigns to get user_id
    campaign_metrics = campaign_metrics.merge(
        campaigns[['id', 'user_id']],
        left_on='campaign_id',
        right_on='id',
        how='left'
    )
    
    return {
        'campaign_metrics': campaign_metrics,
        'campaign_group': campaign_group,
    'qualified_by_campaign': qualified_by_campaign,
        'insights': insights,
        'campaigns': campaigns,
        'campaign_leads': campaign_leads
    }

data = load_data()

st.title("🎯 Leadsmart – Campaign Intelligence Dashboard")
st.markdown("---")

# Sidebar Navigation
dashboard_choice = st.sidebar.radio(
    "Select Dashboard",
    ["📊 Executive Summary", 
     "📈 Campaign Performance", 
     "� Campaign Trends",  # new dashboard
     "💰 Cost & Budget Analysis",
     "🎯 Lead Quality & Efficiency"]
)

# Get unique users for filtering
users_list = sorted(data['campaigns']['user_id'].unique().astype(str))
selected_user = st.sidebar.selectbox("Filter by Business (user_id)", ["All"] + users_list)

# Filter data by user
def filter_by_user(df, user_col='user_id'):
    if selected_user == "All":
        return df
    # Handle case where user_id column might not exist
    if user_col not in df.columns:
        return df
    return df[df[user_col].astype(str) == selected_user]

# ===== DASHBOARD 1: EXECUTIVE SUMMARY =====
if dashboard_choice == "📊 Executive Summary":
    st.header("Executive Summary")
    st.markdown("High-level KPIs and performance overview")
    
    metrics_df = filter_by_user(data['campaign_metrics'])
    group_df = filter_by_user(data['campaign_group'])
    
    if metrics_df.empty:
        st.info("No data available for selected business.")
    else:
        # KPI Row 1
        col1, col2, col3, col4 = st.columns(4)
        
        total_spend = metrics_df['spend'].sum()
        total_leads = metrics_df['num_leads'].sum()
        avg_cpl = (total_spend / total_leads) if total_leads > 0 else 0
        avg_ctr = metrics_df['ctr'].mean()
        
        col1.metric("💵 Total Spend", f"${total_spend:,.2f}", delta=None)
        col2.metric("👥 Total Leads", f"{int(total_leads):,}", delta=None)
        col3.metric("📍 Avg CPL", f"${avg_cpl:.2f}", delta=None)
        col4.metric("📊 Avg CTR", f"{avg_ctr:.3f}%", delta=None)
        
        # KPI Row 2
        col5, col6, col7, col8 = st.columns(4)
        
        total_budget = group_df['budget'].sum()
        num_campaigns = len(metrics_df)
        avg_budget_per_lead = (total_budget / total_leads) if total_leads > 0 else 0
        spend_vs_budget = (total_spend / total_budget * 100) if total_budget > 0 else 0
        
        col5.metric("💰 Total Budget", f"${total_budget:,.2f}", delta=None)
        col6.metric("📋 # Campaigns", f"{num_campaigns}", delta=None)
        col7.metric("💸 Budget/Lead", f"${avg_budget_per_lead:.2f}", delta=None)
        col8.metric("✅ Spend Utilization", f"{spend_vs_budget:.1f}%", delta=None)
        
        st.markdown("---")
        
        # Summary Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Spend by Campaign - Horizontal bar chart
            spend_data = metrics_df.nlargest(10, 'spend')[['campaign_id', 'spend']].sort_values('spend')
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=spend_data['campaign_id'].values,
                x=spend_data['spend'].values,
                orientation='h',
                marker=dict(color='steelblue')
            ))
            fig.update_layout(
                title="Top 10 Campaigns by Spend",
                xaxis_title="Spend ($)",
                yaxis_title="Campaign ID",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_chart2:
            # Leads by Campaign - Horizontal bar chart
            leads_data = metrics_df.nlargest(10, 'num_leads')[['campaign_id', 'num_leads']].sort_values('num_leads')
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=leads_data['campaign_id'].values,
                x=leads_data['num_leads'].values,
                orientation='h',
                marker=dict(color='lightseagreen')
            ))
            fig.update_layout(
                title="Top 10 Campaigns by Leads Generated",
                xaxis_title="Leads",
                yaxis_title="Campaign ID",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

# ===== DASHBOARD 2: CAMPAIGN PERFORMANCE =====
elif dashboard_choice == "📈 Campaign Performance":
    st.header("Campaign Performance Analysis")
    st.markdown("Detailed metrics for individual campaigns")
    
    metrics_df = filter_by_user(data['campaign_metrics']).copy()
    qualified_df = filter_by_user(data['qualified_by_campaign'])
    
    if metrics_df.empty:
        st.info("No data available for selected business.")
    else:
        # Merge with qualified leads data (includes qualified_count, non_qualified_count, total_considered, qualified_percentage)
        metrics_df = metrics_df.merge(qualified_df, on='campaign_id', how='left')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Scatter: Spend vs Leads with bubble size = CTR
            fig = px.scatter(metrics_df, 
                           x='spend', y='num_leads',
                           size='ctr',
                           color='cpl',
                           hover_data=['campaign_id', 'ctr', 'qualified_percentage', 'qualified_count', 'non_qualified_count', 'num_leads'],
                           title="Spend vs Leads (size=CTR, color=CPL)",
                           labels={'spend': 'Spend ($)', 'num_leads': 'Leads', 'cpl': 'CPL ($)'})
            fig.update_layout(hovermode='closest')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Box plot: CPL Distribution
            fig = px.box(metrics_df, y='cpl',
                        title="CPL Distribution Across Campaigns",
                        labels={'cpl': 'Cost Per Lead ($)'})
            st.plotly_chart(fig, use_container_width=True)
        
        # CTR vs Qualified Leads correlation
        fig = px.scatter(metrics_df.dropna(subset=['ctr', 'qualified_percentage']),
                        x='ctr', y='qualified_percentage',
                        size='num_leads',
                        hover_data=['campaign_id', 'spend'],
                        title="CTR vs Quality (% Qualified Leads)",
                        labels={'ctr': 'CTR (%)', 'qualified_percentage': 'Qualified Leads (%)'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Campaign Metrics Table")
        
        # Display detailed table
        display_cols = ['campaign_id', 'num_leads', 'spend', 'cpl', 'ctr', 
                       'clicks', 'impressions_ins', 'qualified_percentage',
                       'qualified_count', 'non_qualified_count', 'total_considered']
        display_cols = [c for c in display_cols if c in metrics_df.columns]
        
        display_df = metrics_df[display_cols].copy()
        display_df = display_df.round(3)
        st.dataframe(display_df.sort_values('cpl'), use_container_width=True, hide_index=True)

# ===== DASHBOARD 3: CAMPAIGN TRENDS =====
elif dashboard_choice == "� Campaign Trends":
    st.header("Campaign Trend Analysis")
    st.markdown("Time-series view of core performance metrics. All metrics aggregated daily. Use the business filter to isolate trends.")

    # Prepare insights with campaign/user mapping
    insights_df = data['insights'].copy()
    campaigns_df = data['campaigns'][['id','user_id']].copy()
    campaigns_df['id'] = campaigns_df['id'].astype(str)
    insights_df['campaign_id'] = ('C' + insights_df['campaign_id'].astype(str)) if 'C' not in str(insights_df['campaign_id'].iloc[0]) else insights_df['campaign_id']
    insights_df['created_at'] = pd.to_datetime(insights_df['created_at'], errors='coerce')
    insights_df = insights_df.merge(campaigns_df, left_on='campaign_id', right_on='id', how='left')

    # Filter by user if selected
    if selected_user != "All":
        insights_df = insights_df[insights_df['user_id'].astype(str) == selected_user]

    # Daily aggregation for spend/clicks/impressions/reach
    daily_insights = (insights_df.dropna(subset=['created_at'])
                      .groupby(insights_df['created_at'].dt.date)
                      .agg(spend=('spend','sum'),
                           clicks=('clicks','sum'),
                           impressions=('impressions','sum'),
                           reach=('reach','sum'))
                      .reset_index()
                      .rename(columns={'created_at':'date'}))

    # Leads per day (from campaign_leads)
    leads_df = data['campaign_leads'].copy()
    leads_df['added_date'] = pd.to_datetime(leads_df['added_date'], errors='coerce')
    leads_df['campaign_id'] = 'C' + leads_df['campaign_id'].astype(str)
    leads_df = leads_df.merge(campaigns_df, left_on='campaign_id', right_on='id', how='left')
    if selected_user != "All":
        leads_df = leads_df[leads_df['user_id'].astype(str) == selected_user]
    daily_leads = (leads_df.dropna(subset=['added_date'])
                   .groupby(leads_df['added_date'].dt.date)
                   .size()
                   .reset_index(name='leads'))

    # Merge spend/clicks with leads
    trends = pd.merge(daily_insights, daily_leads, left_on='date', right_on='added_date', how='left')
    trends['leads'] = trends['leads'].fillna(0)
    trends['ctr'] = np.where(trends['impressions']>0, trends['clicks']/trends['impressions']*100, np.nan)
    trends['cpc'] = np.where(trends['clicks']>0, trends['spend']/trends['clicks'], np.nan)

    if trends.empty:
        st.info("No trend data available for the selected filters.")
    else:
        # Chart 1: Spend & Leads dual-axis
        st.subheader("Daily Spend & Leads")
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=trends['date'], y=trends['spend'], name='Spend ($)', marker_color='steelblue', yaxis='y1'))
        fig1.add_trace(go.Line(x=trends['date'], y=trends['leads'], name='Leads', line=dict(color='orange', width=2), yaxis='y2'))
        fig1.update_layout(
            xaxis_title='Date',
            yaxis=dict(title='Spend ($)', side='left'),
            yaxis2=dict(title='Leads', overlaying='y', side='right'),
            legend=dict(orientation='h'),
            height=450
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2: Impressions vs Reach
        st.subheader("Daily Impressions vs Reach")
        fig2 = go.Figure()
        fig2.add_trace(go.Line(x=trends['date'], y=trends['impressions'], name='Impressions', line=dict(color='teal')))
        fig2.add_trace(go.Line(x=trends['date'], y=trends['reach'], name='Reach', line=dict(color='purple')))
        fig2.update_layout(xaxis_title='Date', yaxis_title='Count', legend=dict(orientation='h'), height=400)
        st.plotly_chart(fig2, use_container_width=True)

        # Chart 3: CPC & CTR trend
        st.subheader("Daily CPC & CTR")
        fig3 = go.Figure()
        fig3.add_trace(go.Line(x=trends['date'], y=trends['cpc'], name='CPC ($)', line=dict(color='green')))
        fig3.add_trace(go.Line(x=trends['date'], y=trends['ctr'], name='CTR (%)', line=dict(color='firebrick', dash='dash')))
        fig3.update_layout(xaxis_title='Date', yaxis_title='Value', legend=dict(orientation='h'), height=400)
        st.plotly_chart(fig3, use_container_width=True)

    # If All businesses selected show aggregate business scatter (unique metrics previously in performance tab)
    if selected_user == "All":
        st.markdown("---")
        st.subheader("Business Efficiency Overview")
        group_df = data['campaign_group'].copy()
        metrics_df = data['campaign_metrics'].copy()
        user_summary = group_df.groupby('user_id').agg(
            Num_Campaigns=('campaign_id','count'),
            Total_Leads=('num_leads','sum'),
            Total_Budget=('budget','sum'),
            Avg_Daily_Budget=('daily_budget','mean')
        ).reset_index()
        spend_by_user = metrics_df.groupby('user_id')['spend'].sum().reset_index()
        user_summary = user_summary.merge(spend_by_user, on='user_id', how='left')
        user_summary['Avg_CPL'] = np.where(user_summary['Total_Leads']>0, user_summary['spend']/user_summary['Total_Leads'], np.nan)
        # Scatter: Budget vs Leads
        fig4 = px.scatter(user_summary, x='Total_Budget', y='Total_Leads',
                          size='Num_Campaigns', color='Avg_CPL',
                          hover_data=['user_id','Avg_Daily_Budget','spend'],
                          title='Total Budget vs Total Leads (bubble size=#Campaigns, color=Avg CPL)')
        st.plotly_chart(fig4, use_container_width=True)
        st.dataframe(user_summary.round(2), use_container_width=True, hide_index=True)

# ===== DASHBOARD 4: COST & BUDGET ANALYSIS =====
elif dashboard_choice == "💰 Cost & Budget Analysis":
    st.header("Cost & Budget Analysis")
    st.markdown("Understand spending efficiency and budget utilization")
    
    group_df = filter_by_user(data['campaign_group'])
    metrics_df = filter_by_user(data['campaign_metrics'])
    
    if group_df.empty:
        st.info("No data available for selected business.")
    else:
        # Merge to get complete picture - use suffixes to handle duplicate columns
        analysis_df = group_df[['campaign_id', 'budget', 'daily_budget', 'num_leads']].merge(
            metrics_df[['campaign_id', 'spend', 'cpl', 'ctr']],
            on='campaign_id',
            how='left'
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Budget vs Spend
            budget_spend = analysis_df[['campaign_id', 'budget', 'spend']].copy()
            budget_spend['Difference'] = budget_spend['budget'] - budget_spend['spend']
            budget_spend_sorted = budget_spend.nlargest(10, 'budget')
            
            fig = go.Figure(data=[
                go.Bar(x=budget_spend_sorted['campaign_id'], y=budget_spend_sorted['budget'], name='Planned Budget'),
                go.Bar(x=budget_spend_sorted['campaign_id'], y=budget_spend_sorted['spend'], name='Actual Spend')
            ])
            fig.update_layout(title="Budget vs Actual Spend (Top 10 Campaigns)",
                            barmode='group',
                            xaxis_title='Campaign ID',
                            yaxis_title='Amount ($)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Budget Utilization %
            analysis_df['Budget_Utilization'] = (
                (analysis_df['spend'] / analysis_df['budget'] * 100)
                .fillna(0)
                .clip(0, 200)  # Cap at 200% for visualization
            )
            
            fig = px.histogram(analysis_df, x='Budget_Utilization', nbins=20,
                             title="Distribution of Budget Utilization %",
                             labels={'Budget_Utilization': 'Utilization (%)', 'count': 'Number of Campaigns'})
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Budget Per Lead vs Actual CPL
            # Merge group_df to get budget_per_lead
            analysis_with_bpl = analysis_df.merge(
                group_df[['campaign_id', 'budget_per_lead']],
                on='campaign_id',
                how='left'
            )
            analysis_clean = analysis_with_bpl.dropna(subset=['budget_per_lead', 'cpl'])
            
            if not analysis_clean.empty:
                fig = px.scatter(analysis_clean,
                               x='budget_per_lead', y='cpl',
                               size='num_leads',
                               hover_data=['campaign_id', 'num_leads'],
                               title="Expected (Budget/Lead) vs Actual CPL",
                               labels={'budget_per_lead': 'Budget per Lead ($)', 'cpl': 'Actual CPL ($)'})
                # Add diagonal reference line
                max_val = max(analysis_clean['budget_per_lead'].max(), analysis_clean['cpl'].max())
                fig.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val], 
                                        mode='lines', name='Expected=Actual',
                                        line=dict(dash='dash', color='gray')))
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # Cost efficiency: Daily Budget impact
            fig = px.scatter(analysis_df,
                           x='daily_budget', y='cpl',
                           size='num_leads',
                           color='ctr',
                           hover_data=['campaign_id', 'num_leads'],
                           title="Daily Budget Impact on CPL",
                           labels={'daily_budget': 'Daily Budget ($)', 'cpl': 'CPL ($)', 'ctr': 'CTR'})
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Cost Analysis Details")
        
        summary_stats = pd.DataFrame({
            'Metric': ['Total Budget', 'Total Spend', 'Avg Daily Budget', 'Avg CPL', 'Avg Budget per Lead'],
            'Value': [
                f"${group_df['budget'].sum():,.2f}",
                f"${analysis_df['spend'].sum():,.2f}",
                f"${group_df['daily_budget'].mean():,.2f}",
                f"${metrics_df['cpl'].mean():,.2f}",
                f"${group_df['budget_per_lead'].mean():,.2f}"
            ]
        })
        st.dataframe(summary_stats, use_container_width=True, hide_index=True)

# ===== DASHBOARD 5: LEAD QUALITY & EFFICIENCY =====
elif dashboard_choice == "🎯 Lead Quality & Efficiency":
    st.header("Lead Quality & Conversion Efficiency")
    st.markdown("Analyze lead quality metrics and campaign efficiency")
    
    metrics_df = filter_by_user(data['campaign_metrics'])
    qualified_df = filter_by_user(data['qualified_by_campaign'])
    
    if metrics_df.empty:
        st.info("No data available for selected business.")
    else:
        # Merge all data
        quality_df = metrics_df.merge(qualified_df, on='campaign_id', how='left')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CTR Distribution
            fig = px.histogram(quality_df, x='ctr', nbins=20,
                             title="Click-Through Rate (CTR) Distribution",
                             labels={'ctr': 'CTR (%)', 'count': 'Number of Campaigns'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Qualified Leads Distribution
            fig = px.histogram(quality_df.dropna(subset=['qualified_percentage']), 
                             x='qualified_percentage', nbins=20,
                             title="Qualified Leads % Distribution",
                             labels={'qualified_percentage': 'Qualified %', 'count': 'Number of Campaigns'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Qualified vs Non-Qualified by Campaign (Top 10 by total considered)
        counts = quality_df[['campaign_id','qualified_count','non_qualified_count']].fillna(0)
        if not counts.empty:
            counts['total'] = counts['qualified_count'] + counts['non_qualified_count']
            top_counts = counts.sort_values('total', ascending=False).head(10)
            st.subheader("Qualified vs Non-Qualified (Top 10 Campaigns)")
            fig_counts = go.Figure()
            fig_counts.add_trace(go.Bar(y=top_counts['campaign_id'], x=top_counts['non_qualified_count'],
                                        name='Non-Qualified', orientation='h', marker_color='#d9534f'))
            fig_counts.add_trace(go.Bar(y=top_counts['campaign_id'], x=top_counts['qualified_count'],
                                        name='Qualified', orientation='h', marker_color='#5cb85c'))
            fig_counts.update_layout(barmode='stack', height=450, xaxis_title='Leads Count', yaxis_title='Campaign ID')
            st.plotly_chart(fig_counts, use_container_width=True)

        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Efficiency Score: Combining CTR and Qualified %
            quality_df['Efficiency_Score'] = (
                (quality_df['ctr'].fillna(0) / quality_df['ctr'].max() * 50) +
                (quality_df['qualified_percentage'].fillna(0) / quality_df['qualified_percentage'].max() * 50)
            )
            
            top_efficient = quality_df.nlargest(10, 'Efficiency_Score')
            fig = px.bar(top_efficient, x='campaign_id', y='Efficiency_Score',
                        title="Top 10 Most Efficient Campaigns",
                        labels={'campaign_id': 'Campaign ID', 'Efficiency_Score': 'Efficiency Score'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # CPL vs Qualified %
            fig = px.scatter(quality_df.dropna(subset=['cpl', 'qualified_percentage']),
                           x='qualified_percentage', y='cpl',
                           size='num_leads',
                           color='ctr',
                           hover_data=['campaign_id'],
                           title="Qualified % vs CPL (color=CTR)",
                           labels={'qualified_percentage': 'Qualified Leads (%)', 'cpl': 'CPL ($)', 'ctr': 'CTR'})
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Quality Metrics Summary")
        
        col5, col6, col7, col8 = st.columns(4)
        
        avg_ctr = quality_df['ctr'].mean()
        avg_qualified = quality_df['qualified_percentage'].mean()
        campaigns_with_qualified = (quality_df['qualified_percentage'] > 0).sum()
        total_campaigns = len(quality_df)
        
        col5.metric("📊 Avg CTR", f"{avg_ctr:.3f}%")
        col6.metric("✅ Avg Qualified %", f"{avg_qualified:.1f}%")
        col7.metric("🎯 Campaigns with Qualified Leads", f"{campaigns_with_qualified}/{total_campaigns}")
        col8.metric("📈 Quality/CTR Correlation", 
                   f"{quality_df[['qualified_percentage', 'ctr']].corr().iloc[0, 1]:.2f}")
        
        st.markdown("---")
        st.subheader("Detailed Quality Analysis")
        
    display_cols = ['campaign_id', 'num_leads', 'ctr', 'qualified_percentage', 'cpl', 'spend',
            'qualified_count', 'non_qualified_count', 'total_considered']
        display_df = quality_df[display_cols].dropna(subset=['qualified_percentage']).copy()
        display_df = display_df.round(3)
        st.dataframe(display_df.sort_values('qualified_percentage', ascending=False), 
                    use_container_width=True, hide_index=True)
