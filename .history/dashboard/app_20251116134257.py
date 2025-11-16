import duckdb
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

st.set_page_config(page_title="Leadsmart – Campaign Intelligence", layout="wide")

# When app is at dashboard/app.py, data is at dashboard/data
DATA_DIR = Path(__file__).resolve().parent / "data"

# Load all data
@st.cache_data
def load_data():
    campaign_metrics = pd.read_csv(DATA_DIR / "campaign_metrics.csv")
    campaign_group = pd.read_csv(DATA_DIR / "campaign_group.csv")
    qualified_by_campaign = pd.read_csv(DATA_DIR / "qualified_by_campaign.csv")
    insights = pd.read_csv(DATA_DIR / "insights.csv")
    campaigns = pd.read_csv(DATA_DIR / "campaigns.csv")
    campaign_leads = pd.read_csv(DATA_DIR / "campaign_leads.csv")
    
    # Convert campaign_id to string/category
    campaign_metrics['campaign_id'] = 'C' + campaign_metrics['campaign_id'].astype(str)
    campaign_group['campaign_id'] = 'C' + campaign_group['campaign_id'].astype(str)
    qualified_by_campaign['campaign_id'] = 'C' + qualified_by_campaign['campaign_id'].astype(str)
    campaigns['id'] = 'C' + campaigns['id'].astype(str)

    # Compute qualified_by_campaign using provided status rules
    qualified_status = ['QUALIFIED','DONE_DEAL','MEETING_DONE']
    non_qualified_status = ['NOT_QUALIFIED','LOW_BUDGET','SPAM','WRONG_NUMBER','ALREADY_BOUGHT','RESALE_REQUEST']

    cl = campaign_leads.copy()
    cl['campaign_id'] = 'C' + cl['campaign_id'].astype(str)
    cl['lead_status'] = cl['lead_status'].astype(str).str.upper().str.strip()

    if 'phone' in cl.columns:
        cl1 = cl.drop_duplicates(subset=['campaign_id','phone'], keep='last')
    else:
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
     "📉 Campaign Trends",
     "💰 Cost & Budget Analysis",
     "🎯 Lead Quality & Efficiency"]
)

# Get unique users for filtering
users_list = sorted(data['campaigns']['user_id'].unique().astype(str))
selected_user = st.sidebar.selectbox("Filter by Business (user_id)", ["All"] + users_list)

# Filter by user
def filter_by_user(df, user_col='user_id'):
    if selected_user == "All":
        return df
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
        col1, col2, col3, col4 = st.columns(4)
        total_spend = metrics_df['spend'].sum()
        total_leads = metrics_df['num_leads'].sum()
        avg_cpl = (total_spend / total_leads) if total_leads > 0 else 0
        avg_ctr = metrics_df['ctr'].mean()
        col1.metric("💵 Total Spend", f"${total_spend:,.2f}")
        col2.metric("👥 Total Leads", f"{int(total_leads):,}")
        col3.metric("📍 Avg CPL", f"${avg_cpl:.2f}")
        col4.metric("📊 Avg CTR", f"{avg_ctr:.3f}%")
        st.markdown("---")
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            spend_data = metrics_df.nlargest(10, 'spend')[['campaign_id', 'spend']].sort_values('spend')
            fig = go.Figure()
            fig.add_trace(go.Bar(y=spend_data['campaign_id'].values, x=spend_data['spend'].values, orientation='h'))
            fig.update_layout(title="Top 10 Campaigns by Spend", xaxis_title="Spend ($)", yaxis_title="Campaign ID", height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_chart2:
            leads_data = metrics_df.nlargest(10, 'num_leads')[['campaign_id', 'num_leads']].sort_values('num_leads')
            fig = go.Figure()
            fig.add_trace(go.Bar(y=leads_data['campaign_id'].values, x=leads_data['num_leads'].values, orientation='h'))
            fig.update_layout(title="Top 10 Campaigns by Leads Generated", xaxis_title="Leads", yaxis_title="Campaign ID", height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# ===== DASHBOARD 2: CAMPAIGN PERFORMANCE =====
elif dashboard_choice == "📈 Campaign Performance":
    st.header("Campaign Performance Analysis")
    metrics_df = filter_by_user(data['campaign_metrics']).copy()
    qualified_df = filter_by_user(data['qualified_by_campaign'])
    if metrics_df.empty:
        st.info("No data available for selected business.")
    else:
        metrics_df = metrics_df.merge(qualified_df, on='campaign_id', how='left')
        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(metrics_df, x='spend', y='num_leads', size='ctr', color='cpl',
                             hover_data=['campaign_id', 'ctr', 'qualified_percentage', 'qualified_count', 'non_qualified_count', 'num_leads'],
                             title="Spend vs Leads (size=CTR, color=CPL)",
                             labels={'spend': 'Spend ($)', 'num_leads': 'Leads', 'cpl': 'CPL ($)'})
            fig.update_layout(hovermode='closest')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.box(metrics_df, y='cpl', title="CPL Distribution Across Campaigns", labels={'cpl': 'Cost Per Lead ($)'})
            st.plotly_chart(fig, use_container_width=True)
        fig = px.scatter(metrics_df.dropna(subset=['ctr', 'qualified_percentage']), x='ctr', y='qualified_percentage', size='num_leads', hover_data=['campaign_id', 'spend'], title="CTR vs Quality (% Qualified Leads)", labels={'ctr': 'CTR (%)', 'qualified_percentage': 'Qualified Leads (%)'})
        st.plotly_chart(fig, use_container_width=True)

# ===== DASHBOARD 3: CAMPAIGN TRENDS =====
elif dashboard_choice == "📉 Campaign Trends":
    st.header("Campaign Trend Analysis")
    insights_df = data['insights'].copy()
    campaigns_df = data['campaigns'][['id','user_id']].copy()
    campaigns_df['id'] = campaigns_df['id'].astype(str)
    insights_df['campaign_id'] = ('C' + insights_df['campaign_id'].astype(str)) if 'C' not in str(insights_df['campaign_id'].iloc[0]) else insights_df['campaign_id']
    insights_df['created_at'] = pd.to_datetime(insights_df['created_at'], errors='coerce')
    insights_df = insights_df.merge(campaigns_df, left_on='campaign_id', right_on='id', how='left')
    if selected_user != "All":
        insights_df = insights_df[insights_df['user_id'].astype(str) == selected_user]
    daily_insights = (insights_df.dropna(subset=['created_at'])
                      .groupby(insights_df['created_at'].dt.date)
                      .agg(spend=('spend','sum'), clicks=('clicks','sum'), impressions=('impressions','sum'), reach=('reach','sum'))
                      .reset_index().rename(columns={'created_at':'date'}))
    leads_df = data['campaign_leads'].copy()
    leads_df['added_date'] = pd.to_datetime(leads_df['added_date'], errors='coerce')
    leads_df['campaign_id'] = 'C' + leads_df['campaign_id'].astype(str)
    leads_df = leads_df.merge(campaigns_df, left_on='campaign_id', right_on='id', how='left')
    if selected_user != "All":
        leads_df = leads_df[leads_df['user_id'].astype(str) == selected_user]
    daily_leads = (leads_df.dropna(subset=['added_date']).groupby(leads_df['added_date'].dt.date).size().reset_index(name='leads'))
    trends = pd.merge(daily_insights, daily_leads, left_on='date', right_on='added_date', how='left')
    trends['leads'] = trends['leads'].fillna(0)
    trends['ctr'] = np.where(trends['impressions']>0, trends['clicks']/trends['impressions']*100, np.nan)
    trends['cpc'] = np.where(trends['clicks']>0, trends['spend']/trends['clicks'], np.nan)
    if trends.empty:
        st.info("No trend data available for the selected filters.")
    else:
        st.subheader("Daily Spend & Leads")
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=trends['date'], y=trends['spend'], name='Spend ($)', marker_color='steelblue', yaxis='y1'))
        fig1.add_trace(go.Line(x=trends['date'], y=trends['leads'], name='Leads', line=dict(color='orange', width=2), yaxis='y2'))
        fig1.update_layout(xaxis_title='Date', yaxis=dict(title='Spend ($)', side='left'), yaxis2=dict(title='Leads', overlaying='y', side='right'), legend=dict(orientation='h'), height=450)
        st.plotly_chart(fig1, use_container_width=True)

# ===== DASHBOARD 4: COST & BUDGET ANALYSIS =====
elif dashboard_choice == "💰 Cost & Budget Analysis":
    st.header("Cost & Budget Analysis")
    group_df = filter_by_user(data['campaign_group'])
    metrics_df = filter_by_user(data['campaign_metrics'])
    if group_df.empty:
        st.info("No data available for selected business.")
    else:
        analysis_df = group_df[['campaign_id', 'budget', 'daily_budget', 'num_leads']].merge(metrics_df[['campaign_id', 'spend', 'cpl', 'ctr']], on='campaign_id', how='left')
        col1, col2 = st.columns(2)
        with col1:
            budget_spend = analysis_df[['campaign_id', 'budget', 'spend']].copy()
            budget_spend['Difference'] = budget_spend['budget'] - budget_spend['spend']
            budget_spend_sorted = budget_spend.nlargest(10, 'budget')
            fig = go.Figure(data=[go.Bar(x=budget_spend_sorted['campaign_id'], y=budget_spend_sorted['budget'], name='Planned Budget'), go.Bar(x=budget_spend_sorted['campaign_id'], y=budget_spend_sorted['spend'], name='Actual Spend')])
            fig.update_layout(title="Budget vs Actual Spend (Top 10 Campaigns)", barmode='group', xaxis_title='Campaign ID', yaxis_title='Amount ($)')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            analysis_df['Budget_Utilization'] = ((analysis_df['spend'] / analysis_df['budget'] * 100).fillna(0).clip(0, 200))
            fig = px.histogram(analysis_df, x='Budget_Utilization', nbins=20, title="Distribution of Budget Utilization %", labels={'Budget_Utilization': 'Utilization (%)', 'count': 'Number of Campaigns'})
            st.plotly_chart(fig, use_container_width=True)

# ===== DASHBOARD 5: LEAD QUALITY & EFFICIENCY =====
elif dashboard_choice == "🎯 Lead Quality & Efficiency":
    st.header("Lead Quality & Conversion Efficiency")
    metrics_df = filter_by_user(data['campaign_metrics'])
    qualified_df = filter_by_user(data['qualified_by_campaign'])
    if metrics_df.empty:
        st.info("No data available for selected business.")
    else:
        quality_df = metrics_df.merge(qualified_df, on='campaign_id', how='left')
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(quality_df, x='ctr', nbins=20, title="Click-Through Rate (CTR) Distribution", labels={'ctr': 'CTR (%)', 'count': 'Number of Campaigns'})
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.histogram(quality_df.dropna(subset=['qualified_percentage']), x='qualified_percentage', nbins=20, title="Qualified Leads % Distribution", labels={'qualified_percentage': 'Qualified %', 'count': 'Number of Campaigns'})
            st.plotly_chart(fig, use_container_width=True)
        counts = quality_df[['campaign_id','qualified_count','non_qualified_count']].fillna(0)
        if not counts.empty:
            counts['total'] = counts['qualified_count'] + counts['non_qualified_count']
            top_counts = counts.sort_values('total', ascending=False).head(10)
            st.subheader("Qualified vs Non-Qualified (Top 10 Campaigns)")
            fig_counts = go.Figure()
            fig_counts.add_trace(go.Bar(y=top_counts['campaign_id'], x=top_counts['non_qualified_count'], name='Non-Qualified', orientation='h', marker_color='#d9534f'))
            fig_counts.add_trace(go.Bar(y=top_counts['campaign_id'], x=top_counts['qualified_count'], name='Qualified', orientation='h', marker_color='#5cb85c'))
            fig_counts.update_layout(barmode='stack', height=450, xaxis_title='Leads Count', yaxis_title='Campaign ID')
            st.plotly_chart(fig_counts, use_container_width=True)
