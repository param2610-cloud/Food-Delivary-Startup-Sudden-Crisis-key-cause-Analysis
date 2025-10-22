"""
QuickBite Express - Crisis Analysis Dashboard
Interactive Streamlit Dashboard for Business Intelligence
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="QuickBite Express - Crisis Analysis",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .positive-change {
        color: #28a745;
    }
    .negative-change {
        color: #dc3545;
    }
    .section-header {
        border-bottom: 3px solid #ff6b6b;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Data loading function with caching
@st.cache_data
def load_data():
    """Load all analysis datasets"""
    data_dir = Path('input/RPC_18_Datasets')
    output_dir = Path('output')
    
    data = {}
    
    # Load raw data
    try:
        data['orders'] = pd.read_csv(data_dir / 'fact_orders.csv')
        data['orders']['order_timestamp'] = pd.to_datetime(data['orders']['order_timestamp'])
        data['orders']['month'] = data['orders']['order_timestamp'].dt.month
        data['orders']['year'] = data['orders']['order_timestamp'].dt.year
        data['orders']['month_period'] = data['orders']['order_timestamp'].dt.to_period('M').astype(str)
        
        data['delivery'] = pd.read_csv(data_dir / 'fact_delivery_performance.csv')
        data['ratings'] = pd.read_csv(data_dir / 'fact_ratings.csv')
        data['restaurant'] = pd.read_csv(data_dir / 'dim_restaurant.csv')
        data['customer'] = pd.read_csv(data_dir / 'dim_customer.csv')
        
        # Load analysis outputs
        data['monthly_orders'] = pd.read_csv(output_dir / 'monthly_orders.csv')
        data['monthly_revenue'] = pd.read_csv(output_dir / 'monthly_revenue.csv')
        data['monthly_cancellations'] = pd.read_csv(output_dir / 'monthly_cancellations.csv')
        data['city_impact'] = pd.read_csv(output_dir / 'city_order_impact.csv')
        data['customer_segments'] = pd.read_csv(output_dir / 'customer_rfm_segments.csv')
        data['high_value_customers'] = pd.read_csv(output_dir / 'high_value_customers.csv')
        data['churned_customers'] = pd.read_csv(output_dir / 'churned_loyal_customers.csv')
        data['acquisition_channels'] = pd.read_csv(output_dir / 'acquisition_channel_performance.csv')
        data['sla_compliance'] = pd.read_csv(output_dir / 'monthly_sla_compliance.csv')
        data['monthly_ratings_trend'] = pd.read_csv(output_dir / 'monthly_ratings.csv')
        data['restaurant_performance'] = pd.read_csv(output_dir / 'restaurant_performance.csv')
        data['cuisine_performance'] = pd.read_csv(output_dir / 'cuisine_performance.csv')
        data['sentiment'] = pd.read_csv(output_dir / 'sentiment_analysis.csv')
        data['word_frequency'] = pd.read_csv(output_dir / 'review_word_frequency.csv')
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None
    
    return data

# Calculate key metrics
@st.cache_data
def calculate_key_metrics(data):
    """Calculate key business metrics"""
    orders = data['orders']
    
    # Pre-crisis (Jan-May 2025)
    pre_crisis = orders[(orders['year'] == 2025) & (orders['month'].between(1, 5))]
    # Crisis (Jun-Sep 2025)
    crisis = orders[(orders['year'] == 2025) & (orders['month'].between(6, 9))]
    
    metrics = {}
    
    # Order metrics
    metrics['pre_crisis_orders'] = len(pre_crisis[pre_crisis['is_cancelled'] == 'N'])
    metrics['crisis_orders'] = len(crisis[crisis['is_cancelled'] == 'N'])
    metrics['order_change_pct'] = ((metrics['crisis_orders'] - metrics['pre_crisis_orders']) / 
                                    metrics['pre_crisis_orders'] * 100)
    
    # Revenue metrics
    metrics['pre_crisis_revenue'] = pre_crisis[pre_crisis['is_cancelled'] == 'N']['total_amount'].sum()
    metrics['crisis_revenue'] = crisis[crisis['is_cancelled'] == 'N']['total_amount'].sum()
    metrics['revenue_change_pct'] = ((metrics['crisis_revenue'] - metrics['pre_crisis_revenue']) / 
                                      metrics['pre_crisis_revenue'] * 100)
    
    # Customer metrics
    metrics['pre_crisis_customers'] = pre_crisis['customer_id'].nunique()
    metrics['crisis_customers'] = crisis['customer_id'].nunique()
    metrics['customer_change_pct'] = ((metrics['crisis_customers'] - metrics['pre_crisis_customers']) / 
                                       metrics['pre_crisis_customers'] * 100)
    
    # Cancellation rate
    metrics['pre_crisis_cancel_rate'] = (pre_crisis['is_cancelled'] == 'Y').sum() / len(pre_crisis) * 100
    metrics['crisis_cancel_rate'] = (crisis['is_cancelled'] == 'Y').sum() / len(crisis) * 100
    
    # SLA and ratings
    if 'sla_compliance' in data:
        pre_sla = data['sla_compliance'][data['sla_compliance']['month_period'].isin(['2025-01', '2025-02', '2025-03', '2025-04', '2025-05'])]
        crisis_sla = data['sla_compliance'][data['sla_compliance']['month_period'].isin(['2025-06', '2025-07', '2025-08', '2025-09'])]
        metrics['pre_crisis_sla'] = pre_sla['compliance_rate'].mean()
        metrics['crisis_sla'] = crisis_sla['compliance_rate'].mean()
    
    if 'ratings' in data:
        ratings = data['ratings'].dropna()
        ratings['review_timestamp'] = pd.to_datetime(ratings['review_timestamp'], format='%d-%m-%Y %H:%M')
        ratings['month'] = ratings['review_timestamp'].dt.month
        ratings['year'] = ratings['review_timestamp'].dt.year
        
        pre_ratings = ratings[(ratings['year'] == 2025) & (ratings['month'].between(1, 5))]
        crisis_ratings = ratings[(ratings['year'] == 2025) & (ratings['month'].between(6, 9))]
        
        metrics['pre_crisis_rating'] = pre_ratings['rating'].mean()
        metrics['crisis_rating'] = crisis_ratings['rating'].mean()
    
    return metrics

def format_metric_change(value, is_percentage=True, inverse=False):
    """Format metric change with color"""
    if is_percentage:
        formatted = f"{value:+.1f}%"
    else:
        formatted = f"{value:+.2f}"
    
    # Inverse means negative is good (like cancellation rate)
    if inverse:
        color = "positive-change" if value < 0 else "negative-change"
    else:
        color = "positive-change" if value > 0 else "negative-change"
    
    return f'<span class="{color}">{formatted}</span>'

# Main Dashboard Function
def main():
    # Load data
    data = load_data()
    
    if data is None:
        st.error("Failed to load data. Please check data files.")
        return
    
    # Calculate metrics
    metrics = calculate_key_metrics(data)
    
    # Sidebar navigation
    st.sidebar.title("🍔 QuickBite Express")
    st.sidebar.markdown("### Crisis Analysis Dashboard")
    
    page = st.sidebar.radio(
        "Navigate to:",
        ["📊 Executive Summary", 
         "💰 Business Health", 
         "👥 Customer Analytics", 
         "⚙️ Operational Performance",
         "🏪 Restaurant Insights",
         "🎯 Recovery Roadmap"]
    )
    
    # Filters
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filters")
    
    # Time period filter
    time_filter = st.sidebar.selectbox(
        "Time Period",
        ["All Periods", "Pre-Crisis (Jan-May)", "Crisis (Jun-Sep)"]
    )
    
    # City filter
    available_cities = sorted(data['customer']['city'].unique())
    city_filter = st.sidebar.multiselect(
        "Cities",
        available_cities,
        default=[]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Analysis Period:** Jan - Sep 2025")
    st.sidebar.markdown("**Crisis Event:** June 2025")
    st.sidebar.markdown("**Last Updated:** October 2025")
    
    # Route to selected page
    if page == "📊 Executive Summary":
        show_executive_summary(data, metrics)
    elif page == "💰 Business Health":
        show_business_health(data, metrics, time_filter, city_filter)
    elif page == "👥 Customer Analytics":
        show_customer_analytics(data, metrics, time_filter, city_filter)
    elif page == "⚙️ Operational Performance":
        show_operational_performance(data, metrics, time_filter)
    elif page == "🏪 Restaurant Insights":
        show_restaurant_insights(data, metrics)
    elif page == "🎯 Recovery Roadmap":
        show_recovery_roadmap(data, metrics)

# Page 1: Executive Summary
def show_executive_summary(data, metrics):
    st.title("📊 Executive Summary")
    st.markdown("### Crisis Impact Overview - QuickBite Express")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Orders (Crisis)",
            f"{metrics['crisis_orders']:,}",
            delta=f"{metrics['order_change_pct']:.1f}%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Revenue (Crisis)",
            f"₹{metrics['crisis_revenue']/1_000_000:.2f}M",
            delta=f"{metrics['revenue_change_pct']:.1f}%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "Active Customers",
            f"{metrics['crisis_customers']:,}",
            delta=f"{metrics['customer_change_pct']:.1f}%",
            delta_color="normal"
        )
    
    with col4:
        if 'crisis_rating' in metrics:
            rating_change = metrics['crisis_rating'] - metrics['pre_crisis_rating']
            st.metric(
                "Avg Rating",
                f"{metrics['crisis_rating']:.2f}/5",
                delta=f"{rating_change:+.2f}",
                delta_color="normal"
            )
    
    st.markdown("---")
    
    # Main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Monthly Order Trend")
        monthly_data = data['monthly_orders'].copy()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_data['month_period'],
            y=monthly_data['orders'],
            mode='lines+markers',
            name='Orders',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8)
        ))
        
        # Add crisis marker
        fig.add_vline(x=4.5, line_dash="dash", line_color="red", 
                      annotation_text="Crisis Start", annotation_position="top")
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Number of Orders",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Monthly Revenue Trend")
        revenue_data = data['monthly_revenue'].copy()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=revenue_data['month_period'],
            y=revenue_data['total_amount'] / 1_000_000,
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_vline(x=4.5, line_dash="dash", line_color="red",
                      annotation_text="Crisis Start", annotation_position="top")
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue (₹ Millions)",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Crisis impact summary
    st.markdown("---")
    st.markdown("### 🚨 Crisis Impact Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Business Decline")
        st.markdown(f"""
        - **Orders:** {metrics['order_change_pct']:.1f}% decline
        - **Revenue:** {metrics['revenue_change_pct']:.1f}% decline
        - **Customers:** {metrics['customer_change_pct']:.1f}% decline
        """)
    
    with col2:
        st.markdown("#### Operational Issues")
        if 'crisis_sla' in metrics:
            sla_change = metrics['crisis_sla'] - metrics['pre_crisis_sla']
            st.markdown(f"""
            - **SLA Compliance:** {sla_change:+.1f}pp
            - **Cancellation Rate:** {metrics['crisis_cancel_rate']:.1f}%
            - **Rating Drop:** {metrics['crisis_rating'] - metrics['pre_crisis_rating']:+.2f}
            """)
    
    with col3:
        st.markdown("#### Key Concerns")
        st.markdown("""
        - 🔴 High customer churn rate
        - 🔴 Delivery performance decline
        - 🔴 Negative sentiment surge
        - 🟡 Restaurant partner attrition
        """)
    
    # Quick insights
    st.markdown("---")
    st.markdown("### 💡 Quick Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.info("""
        **Most Critical Areas:**
        1. Customer retention (significant churn in loyal segments)
        2. Service quality (SLA violations increased)
        3. Geographic concentration (top cities heavily impacted)
        """)
    
    with insights_col2:
        st.success("""
        **Recovery Opportunities:**
        1. Re-engage churned high-value customers
        2. Focus on high-performing cities
        3. Improve delivery partner management
        """)

# Page 2: Business Health
def show_business_health(data, metrics, time_filter, city_filter):
    st.title("💰 Business Health Deep Dive")
    
    # Revenue breakdown
    st.markdown("### Revenue Analysis")
    
    revenue_data = data['monthly_revenue'].copy()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Monthly Revenue Components', 'Revenue Waterfall'),
        specs=[[{"type": "bar"}, {"type": "waterfall"}]]
    )
    
    # Stacked bar chart
    fig.add_trace(
        go.Bar(name='Subtotal', x=revenue_data['month_period'], y=revenue_data['subtotal_amount']/1000000),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='Delivery Fee', x=revenue_data['month_period'], y=revenue_data['delivery_fee']/1000000),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='Discount', x=revenue_data['month_period'], y=-revenue_data['discount_amount']/1000000),
        row=1, col=1
    )
    
    # Waterfall chart
    waterfall_data = [
        ('Pre-Crisis', metrics['pre_crisis_revenue']/1000000),
        ('Crisis Impact', (metrics['crisis_revenue'] - metrics['pre_crisis_revenue'])/1000000),
        ('Crisis Period', metrics['crisis_revenue']/1000000)
    ]
    
    fig.add_trace(
        go.Waterfall(
            x=[d[0] for d in waterfall_data],
            y=[d[1] for d in waterfall_data],
            measure=['absolute', 'relative', 'total']
        ),
        row=1, col=2
    )
    
    fig.update_layout(height=500, showlegend=True, barmode='relative')
    fig.update_yaxes(title_text="Revenue (₹M)", row=1, col=1)
    fig.update_yaxes(title_text="Revenue (₹M)", row=1, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Order analysis
    st.markdown("---")
    st.markdown("### Order Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly orders with cancellation overlay
        monthly_data = data['monthly_orders'].copy()
        cancel_data = data['monthly_cancellations'].copy()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=monthly_data['month_period'],
                y=monthly_data['orders'],
                name='Total Orders',
                marker_color='skyblue'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=cancel_data['month_period'],
                y=cancel_data['cancellation_rate'],
                name='Cancellation Rate',
                mode='lines+markers',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ),
            secondary_y=True
        )
        
        fig.update_xaxes(title_text="Month")
        fig.update_yaxes(title_text="Number of Orders", secondary_y=False)
        fig.update_yaxes(title_text="Cancellation Rate (%)", secondary_y=True)
        fig.update_layout(height=400, title="Orders vs Cancellation Rate")
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Order status distribution
        orders = data['orders']
        status_counts = orders['is_cancelled'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=['Completed', 'Cancelled'],
            values=[status_counts.get('N', 0), status_counts.get('Y', 0)],
            hole=.4,
            marker_colors=['#2ecc71', '#e74c3c']
        )])
        
        fig.update_layout(
            height=400,
            title="Order Status Distribution"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Geographic impact
    st.markdown("---")
    st.markdown("### Geographic Impact Analysis")
    
    city_data = data['city_impact'].copy()
    city_data = city_data.sort_values('order_change_pct').head(10)
    
    fig = go.Figure(go.Bar(
        x=city_data['order_change_pct'],
        y=city_data['city'],
        orientation='h',
        marker_color=['red' if x < 0 else 'green' for x in city_data['order_change_pct']],
        text=city_data['order_change_pct'].apply(lambda x: f"{x:.1f}%"),
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Top 10 Most Affected Cities (Order Change %)",
        xaxis_title="Order Change (%)",
        yaxis_title="City",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed metrics table
    st.markdown("---")
    st.markdown("### Monthly Performance Details")
    
    monthly_summary = revenue_data[['month_period', 'total_amount', 'subtotal_amount', 
                                     'delivery_fee', 'discount_amount']].copy()
    monthly_summary['total_amount'] = monthly_summary['total_amount'].apply(lambda x: f"₹{x/1000000:.2f}M")
    monthly_summary['subtotal_amount'] = monthly_summary['subtotal_amount'].apply(lambda x: f"₹{x/1000000:.2f}M")
    monthly_summary['delivery_fee'] = monthly_summary['delivery_fee'].apply(lambda x: f"₹{x/1000:.0f}K")
    monthly_summary['discount_amount'] = monthly_summary['discount_amount'].apply(lambda x: f"₹{x/1000:.0f}K")
    
    monthly_summary.columns = ['Month', 'Total Revenue', 'Subtotal', 'Delivery Fee', 'Discount']
    
    st.dataframe(monthly_summary, use_container_width=True, hide_index=True)

# Page 3: Customer Analytics
def show_customer_analytics(data, metrics, time_filter, city_filter):
    st.title("👥 Customer Analytics")
    
    # RFM Segmentation
    st.markdown("### Customer Segmentation (RFM Analysis)")
    
    segment_data = data['customer_segments'].copy()
    segment_counts = segment_data['segment'].value_counts()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Treemap visualization
        fig = go.Figure(go.Treemap(
            labels=segment_counts.index,
            parents=[""] * len(segment_counts),
            values=segment_counts.values,
            textinfo="label+value+percent parent",
            marker=dict(
                colors=['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#95a5a6', '#9b59b6'],
                line=dict(width=2)
            )
        ))
        
        fig.update_layout(height=500, title="Customer Segment Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Segment Breakdown")
        for segment, count in segment_counts.items():
            pct = (count / segment_counts.sum()) * 100
            st.metric(segment, f"{count:,}", f"{pct:.1f}%")
    
    # Loyalty analysis
    st.markdown("---")
    st.markdown("### Customer Loyalty Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # High-value customers
        st.markdown("#### High-Value Customer Spending")
        hvc_data = data['high_value_customers'].copy()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hvc_data['customer_id'].head(15).astype(str),
            y=hvc_data['total_spending'].head(15),
            marker_color='gold',
            text=hvc_data['total_spending'].head(15).apply(lambda x: f"₹{x:.0f}"),
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Top 15 High-Value Customers",
            xaxis_title="Customer ID",
            yaxis_title="Total Spending (₹)",
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Churned customers
        st.markdown("#### Churned Loyal Customers")
        churned_data = data['churned_customers'].copy()
        
        st.metric("Total Churned Loyal Customers", f"{len(churned_data):,}")
        st.metric("Avg Orders Before Churn", f"{churned_data['order_count'].mean():.1f}")
        st.metric("Estimated Lost Revenue", f"₹{churned_data['total_spending'].sum()/1000:.0f}K")
        
        # Churn by segment
        if 'segment' in churned_data.columns:
            churn_by_segment = churned_data['segment'].value_counts()
            
            fig = go.Figure(data=[go.Pie(
                labels=churn_by_segment.index,
                values=churn_by_segment.values,
                hole=.3
            )])
            
            fig.update_layout(height=300, title="Churned Customers by Segment")
            st.plotly_chart(fig, use_container_width=True)
    
    # Acquisition channels
    st.markdown("---")
    st.markdown("### Acquisition Channel Performance")
    
    channel_data = data['acquisition_channels'].copy()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Pre-Crisis',
        x=channel_data['acquisition_channel'],
        y=channel_data['pre_crisis_orders'],
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name='Crisis',
        x=channel_data['acquisition_channel'],
        y=channel_data['crisis_orders'],
        marker_color='coral'
    ))
    
    fig.update_layout(
        title="Customer Orders by Acquisition Channel",
        xaxis_title="Channel",
        yaxis_title="Number of Orders",
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Channel change metrics
    col1, col2, col3, col4 = st.columns(4)
    
    for idx, row in channel_data.iterrows():
        with [col1, col2, col3, col4][idx % 4]:
            change_pct = row['order_change_pct']
            st.metric(
                row['acquisition_channel'],
                f"{row['crisis_orders']:,}",
                f"{change_pct:.1f}%"
            )
    
    # Customer insights
    st.markdown("---")
    st.markdown("### 💡 Key Customer Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.warning("""
        **At-Risk Segments:**
        - Champions: Need immediate re-engagement
        - Loyal Customers: Showing signs of reduced activity
        - At-Risk: Require win-back campaigns
        """)
    
    with col2:
        st.info("""
        **Recommendations:**
        - Personalized offers for churned high-value customers
        - Channel-specific retention campaigns
        - Geographic targeting for recovery
        """)

# Page 4: Operational Performance
def show_operational_performance(data, metrics, time_filter):
    st.title("⚙️ Operational Performance")
    
    # SLA Compliance
    st.markdown("### Delivery SLA Compliance")
    
    sla_data = data['sla_compliance'].copy()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'pre_crisis_sla' in metrics:
            st.metric(
                "Pre-Crisis SLA",
                f"{metrics['pre_crisis_sla']:.1f}%",
                help="Average SLA compliance Jan-May 2025"
            )
    
    with col2:
        if 'crisis_sla' in metrics:
            sla_change = metrics['crisis_sla'] - metrics['pre_crisis_sla']
            st.metric(
                "Crisis SLA",
                f"{metrics['crisis_sla']:.1f}%",
                f"{sla_change:+.1f}pp",
                delta_color="normal"
            )
    
    with col3:
        target_sla = 90.0
        current_sla = metrics.get('crisis_sla', 0)
        gap = current_sla - target_sla
        st.metric(
            "Gap to Target (90%)",
            f"{gap:+.1f}pp",
            delta_color="inverse"
        )
    
    # SLA trend
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=sla_data['month_period'],
            y=sla_data['compliance_rate'],
            mode='lines+markers',
            name='Compliance Rate',
            line=dict(color='green', width=3),
            marker=dict(size=10)
        ))
        
        fig.add_hline(y=90, line_dash="dash", line_color="orange", 
                      annotation_text="Target 90%")
        fig.add_vline(x=4.5, line_dash="dash", line_color="red",
                      annotation_text="Crisis Start")
        
        fig.update_layout(
            title="Monthly SLA Compliance Rate",
            xaxis_title="Month",
            yaxis_title="Compliance Rate (%)",
            height=400,
            yaxis_range=[0, 100]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Actual vs Expected delivery time
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=sla_data['month_period'],
            y=sla_data['avg_actual_time'],
            mode='lines+markers',
            name='Actual Time',
            line=dict(color='red', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=sla_data['month_period'],
            y=sla_data['avg_expected_time'],
            mode='lines+markers',
            name='Expected Time',
            line=dict(color='blue', width=2, dash='dash')
        ))
        
        fig.add_vline(x=4.5, line_dash="dash", line_color="red",
                      annotation_text="Crisis Start")
        
        fig.update_layout(
            title="Average Delivery Time: Actual vs Expected",
            xaxis_title="Month",
            yaxis_title="Time (minutes)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Ratings analysis
    st.markdown("---")
    st.markdown("### Customer Ratings & Sentiment")
    
    ratings_data = data['monthly_ratings_trend'].copy()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rating trend
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=ratings_data['month_period'],
            y=ratings_data['avg_rating'],
            mode='lines+markers',
            name='Average Rating',
            line=dict(color='gold', width=3),
            marker=dict(size=10),
            fill='tonexty'
        ))
        
        fig.add_hline(y=4.0, line_dash="dash", line_color="green",
                      annotation_text="Target 4.0")
        fig.add_vline(x=4.5, line_dash="dash", line_color="red",
                      annotation_text="Crisis Start")
        
        fig.update_layout(
            title="Monthly Average Rating Trend",
            xaxis_title="Month",
            yaxis_title="Rating (out of 5)",
            height=400,
            yaxis_range=[0, 5]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Rating volume
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=ratings_data['month_period'],
            y=ratings_data['count'],
            marker_color='coral',
            text=ratings_data['count'],
            textposition='auto'
        ))
        
        fig.add_vline(x=4.5, line_dash="dash", line_color="red",
                      annotation_text="Crisis Start")
        
        fig.update_layout(
            title="Monthly Rating Volume",
            xaxis_title="Month",
            yaxis_title="Number of Ratings",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment analysis
    st.markdown("---")
    st.markdown("### Sentiment Analysis")
    
    sentiment_data = data['sentiment'].copy()
    
    def categorize_sentiment(rating):
        if rating >= 4:
            return 'Positive'
        elif rating == 3:
            return 'Neutral'
        else:
            return 'Negative'
    
    sentiment_data['sentiment'] = sentiment_data['rating'].apply(categorize_sentiment)
    sentiment_counts = sentiment_data['sentiment'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment pie chart
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            marker_colors=['#2ecc71', '#f39c12', '#e74c3c'],
            hole=.4
        )])
        
        fig.update_layout(
            title="Overall Sentiment Distribution",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top words in reviews
        word_data = data['word_frequency'].head(15).copy()
        
        fig = go.Figure(go.Bar(
            x=word_data['frequency'],
            y=word_data['word'],
            orientation='h',
            marker_color='steelblue',
            text=word_data['frequency'],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Top 15 Words in Reviews",
            xaxis_title="Frequency",
            yaxis_title="Word",
            height=400
        )
        fig.update_yaxes(autorange="reversed")
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance summary
    st.markdown("---")
    st.markdown("### 📋 Performance Summary")
    
    summary_data = sla_data[['month_period', 'compliance_rate', 'avg_actual_time', 
                               'avg_expected_time', 'avg_delay']].copy()
    summary_data.columns = ['Month', 'SLA Compliance (%)', 'Avg Actual Time (min)', 
                            'Avg Expected Time (min)', 'Avg Delay (min)']
    
    # Format numbers
    summary_data['SLA Compliance (%)'] = summary_data['SLA Compliance (%)'].apply(lambda x: f"{x:.1f}%")
    summary_data['Avg Actual Time (min)'] = summary_data['Avg Actual Time (min)'].apply(lambda x: f"{x:.1f}")
    summary_data['Avg Expected Time (min)'] = summary_data['Avg Expected Time (min)'].apply(lambda x: f"{x:.1f}")
    summary_data['Avg Delay (min)'] = summary_data['Avg Delay (min)'].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(summary_data, use_container_width=True, hide_index=True)

# Page 5: Restaurant Insights
def show_restaurant_insights(data, metrics):
    st.title("🏪 Restaurant & Partner Insights")
    
    # Restaurant performance
    st.markdown("### Restaurant Performance Analysis")
    
    restaurant_data = data['restaurant_performance'].copy()
    restaurant_data = restaurant_data[restaurant_data['pre_crisis_orders'] >= 10]  # Filter significant restaurants
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Restaurants Analyzed", f"{len(restaurant_data):,}")
    
    with col2:
        declining = (restaurant_data['order_change_pct'] < -20).sum()
        st.metric("Severely Declining (>20%)", f"{declining:,}")
    
    with col3:
        avg_change = restaurant_data['order_change_pct'].mean()
        st.metric("Avg Order Change", f"{avg_change:.1f}%")
    
    # Restaurant decline distribution
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=restaurant_data['order_change_pct'],
            nbinsx=30,
            marker_color='steelblue',
            opacity=0.7
        ))
        
        fig.add_vline(x=0, line_dash="dash", line_color="red", 
                      annotation_text="No Change")
        
        fig.update_layout(
            title="Restaurant Order Change Distribution",
            xaxis_title="Order Change (%)",
            yaxis_title="Number of Restaurants",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top declining restaurants
        top_declining = restaurant_data.nsmallest(15, 'order_change_pct')
        
        fig = go.Figure(go.Bar(
            x=top_declining['order_change_pct'],
            y=top_declining.index.astype(str),
            orientation='h',
            marker_color='red',
            text=top_declining['order_change_pct'].apply(lambda x: f"{x:.1f}%"),
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Top 15 Declining Restaurants",
            xaxis_title="Order Change (%)",
            yaxis_title="Restaurant ID",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Cuisine performance
    st.markdown("---")
    st.markdown("### Cuisine Type Performance")
    
    cuisine_data = data['cuisine_performance'].copy()
    
    fig = go.Figure()
    
    colors = ['red' if x < 0 else 'green' for x in cuisine_data['change_pct']]
    
    fig.add_trace(go.Bar(
        x=cuisine_data['change_pct'],
        y=cuisine_data.index,
        orientation='h',
        marker_color=colors,
        text=cuisine_data['change_pct'].apply(lambda x: f"{x:.1f}%"),
        textposition='auto'
    ))
    
    fig.add_vline(x=0, line_dash="solid", line_color="black", line_width=1)
    
    fig.update_layout(
        title="Cuisine Type Performance: Pre-Crisis vs Crisis",
        xaxis_title="Order Change (%)",
        yaxis_title="Cuisine Type",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Cuisine insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📉 Most Affected Cuisines")
        worst_cuisines = cuisine_data.nsmallest(3, 'change_pct')
        for idx, (cuisine, row) in enumerate(worst_cuisines.iterrows(), 1):
            st.markdown(f"{idx}. **{cuisine}**: {row['change_pct']:.1f}% decline")
    
    with col2:
        st.markdown("#### 📈 Best Performing Cuisines")
        best_cuisines = cuisine_data.nlargest(3, 'change_pct')
        for idx, (cuisine, row) in enumerate(best_cuisines.iterrows(), 1):
            st.markdown(f"{idx}. **{cuisine}**: {row['change_pct']:+.1f}%")
    
    # Restaurant scatter plot
    st.markdown("---")
    st.markdown("### Restaurant Performance Matrix")
    
    # Merge with ratings if available
    restaurant_detail = restaurant_data.copy()
    
    fig = px.scatter(
        restaurant_detail,
        x='pre_crisis_orders',
        y='order_change_pct',
        size='pre_crisis_revenue',
        color='order_change_pct',
        color_continuous_scale=['red', 'yellow', 'green'],
        hover_data=['crisis_orders', 'crisis_revenue'],
        labels={
            'pre_crisis_orders': 'Pre-Crisis Orders',
            'order_change_pct': 'Order Change (%)',
            'pre_crisis_revenue': 'Pre-Crisis Revenue'
        }
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title="Restaurant Performance: Volume vs Change",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.markdown("---")
    st.markdown("### Detailed Restaurant Performance")
    
    display_cols = ['pre_crisis_orders', 'crisis_orders', 'order_change_pct', 
                    'pre_crisis_revenue', 'crisis_revenue', 'revenue_change_pct']
    
    restaurant_table = restaurant_detail[display_cols].copy()
    restaurant_table = restaurant_table.sort_values('order_change_pct').head(20)
    
    restaurant_table.columns = ['Pre Orders', 'Crisis Orders', 'Order Change %',
                                  'Pre Revenue', 'Crisis Revenue', 'Revenue Change %']
    
    # Format currency
    restaurant_table['Pre Revenue'] = restaurant_table['Pre Revenue'].apply(lambda x: f"₹{x:,.0f}")
    restaurant_table['Crisis Revenue'] = restaurant_table['Crisis Revenue'].apply(lambda x: f"₹{x:,.0f}")
    restaurant_table['Order Change %'] = restaurant_table['Order Change %'].apply(lambda x: f"{x:.1f}%")
    restaurant_table['Revenue Change %'] = restaurant_table['Revenue Change %'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(restaurant_table, use_container_width=True)

# Page 6: Recovery Roadmap
def show_recovery_roadmap(data, metrics):
    st.title("🎯 Recovery Roadmap")
    
    st.markdown("""
    ### Strategic Recovery Plan for QuickBite Express
    Based on comprehensive data analysis, here are prioritized recommendations for business recovery.
    """)
    
    # Priority matrix
    st.markdown("---")
    st.markdown("### Recovery Priority Matrix")
    
    priorities = pd.DataFrame({
        'Initiative': [
            'Re-engage Churned Champions',
            'Improve Delivery SLA',
            'Geographic Expansion Recovery',
            'Restaurant Partner Support',
            'Brand Reputation Management',
            'Customer Service Enhancement',
            'Loyalty Program Revamp',
            'Pricing Strategy Review'
        ],
        'Impact': [9, 10, 7, 6, 8, 7, 6, 5],
        'Effort': [3, 8, 6, 5, 4, 6, 7, 8],
        'Priority': ['High', 'High', 'Medium', 'Medium', 'High', 'Medium', 'Low', 'Low'],
        'Timeline': ['Immediate', '1-2 Months', '2-3 Months', '1-2 Months', 'Immediate', 
                     '1-2 Months', '3-6 Months', '3-6 Months']
    })
    
    # Priority scatter plot
    fig = px.scatter(
        priorities,
        x='Effort',
        y='Impact',
        size=[30]*len(priorities),
        color='Priority',
        color_discrete_map={'High': '#2ecc71', 'Medium': '#f39c12', 'Low': '#e74c3c'},
        text='Initiative',
        hover_data=['Timeline']
    )
    
    fig.update_traces(textposition='top center', textfont_size=9)
    
    fig.update_layout(
        title="Impact vs Effort Matrix",
        xaxis_title="Implementation Effort (1-10)",
        yaxis_title="Business Impact (1-10)",
        height=500,
        xaxis_range=[0, 11],
        yaxis_range=[0, 11]
    )
    
    # Add quadrant lines
    fig.add_hline(y=5.5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=5.5, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=2.5, y=9, text="Quick Wins", showarrow=False, font=dict(size=14, color="green"))
    fig.add_annotation(x=8, y=9, text="Major Projects", showarrow=False, font=dict(size=14, color="orange"))
    fig.add_annotation(x=2.5, y=2, text="Fill-ins", showarrow=False, font=dict(size=14, color="gray"))
    fig.add_annotation(x=8, y=2, text="Avoid", showarrow=False, font=dict(size=14, color="red"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed recommendations
    st.markdown("---")
    st.markdown("### 🎯 Detailed Action Plans")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔥 Immediate Actions",
        "📅 Short-term (1-2 Months)",
        "📈 Medium-term (3-6 Months)",
        "💡 Key Insights"
    ])
    
    with tab1:
        st.markdown("#### Immediate Priority Actions (Week 1-4)")
        
        st.success("""
        **1. Re-engage Churned High-Value Customers**
        - **Target:** {} churned loyal customers
        - **Action:** Personalized outreach with exclusive offers
        - **Expected Impact:** 20-30% reactivation rate
        - **Budget:** ₹500K for incentives
        """.format(len(data['churned_customers'])))
        
        st.success("""
        **2. Brand Reputation Crisis Management**
        - **Action:** Social media response campaign
        - **Action:** Proactive customer communication
        - **Action:** Influencer partnerships for positive coverage
        - **Expected Impact:** Improve sentiment by 15-20%
        """)
        
        st.success("""
        **3. Emergency Delivery Performance Fixes**
        - **Action:** Increase delivery partner incentives
        - **Action:** Route optimization implementation
        - **Action:** Real-time monitoring dashboard
        - **Target:** Improve SLA compliance to 85%+
        """)
    
    with tab2:
        st.markdown("#### Short-term Recovery Plan (1-2 Months)")
        
        st.info("""
        **1. Geographic Recovery Focus**
        - **Target Cities:** {} most affected cities
        - **Action:** City-specific promotional campaigns
        - **Action:** Local partnership initiatives
        - **Budget:** ₹2M allocated by city performance
        """.format(len(data['city_impact'].head(5))))
        
        st.info("""
        **2. Restaurant Partner Support Program**
        - **Action:** Revenue guarantee for top partners
        - **Action:** Marketing co-investment program
        - **Action:** Performance coaching and support
        - **Target:** Reduce partner attrition by 50%
        """)
        
        st.info("""
        **3. Customer Service Enhancement**
        - **Action:** Expand support team by 30%
        - **Action:** Implement AI chatbot for common issues
        - **Action:** Proactive issue resolution system
        - **Target:** Reduce complaint resolution time by 40%
        """)
    
    with tab3:
        st.markdown("#### Medium-term Strategic Initiatives (3-6 Months)")
        
        st.warning("""
        **1. Loyalty Program 2.0**
        - **Action:** Tiered benefits redesign
        - **Action:** Gamification elements
        - **Action:** Partnership rewards network
        - **Expected Impact:** 25% increase in repeat orders
        """)
        
        st.warning("""
        **2. Operational Excellence Program**
        - **Action:** Delivery partner training academy
        - **Action:** Technology infrastructure upgrade
        - **Action:** Predictive demand forecasting
        - **Target:** Achieve 95%+ SLA compliance
        """)
        
        st.warning("""
        **3. Market Expansion & Diversification**
        - **Action:** New cuisine categories
        - **Action:** Cloud kitchen partnerships
        - **Action:** Grocery/convenience delivery pilot
        - **Expected Impact:** 15% new revenue streams
        """)
    
    with tab4:
        st.markdown("#### 💡 Key Strategic Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Critical Success Factors")
            st.markdown("""
            - **Speed of Response:** First 30 days critical
            - **Customer Trust:** Must rebuild through actions, not words
            - **Operational Excellence:** Delivery performance is table stakes
            - **Partner Ecosystem:** Restaurant success = Our success
            - **Data-Driven:** Monitor recovery metrics weekly
            """)
        
        with col2:
            st.markdown("##### Risk Mitigation")
            st.markdown("""
            - **Competition:** Aggressive acquisition campaigns expected
            - **Churn Acceleration:** Without intervention, could lose 40%+ customers
            - **Partner Exodus:** Critical to retain top restaurant partners
            - **Funding:** May need additional capital for recovery
            - **Timeline:** 6-9 months for full recovery
            """)
    
    # Recovery metrics dashboard
    st.markdown("---")
    st.markdown("### 📊 Recovery KPIs to Track")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Weekly Orders Target", "15K+", help="Goal for end of Month 1")
    
    with col2:
        st.metric("SLA Compliance Target", "90%+", help="Goal for end of Month 3")
    
    with col3:
        st.metric("Customer Rating Target", "4.0+", help="Goal for end of Month 2")
    
    with col4:
        st.metric("Churn Reduction Target", "-50%", help="Vs current crisis rate")
    
    # Timeline gantt chart
    st.markdown("---")
    st.markdown("### 📅 Implementation Timeline")
    
    timeline_data = [
        dict(Task="Customer Re-engagement", Start='2025-10-01', Finish='2025-10-31', Priority='High'),
        dict(Task="Brand Reputation", Start='2025-10-01', Finish='2025-11-15', Priority='High'),
        dict(Task="Delivery Performance", Start='2025-10-01', Finish='2025-12-31', Priority='High'),
        dict(Task="Geographic Recovery", Start='2025-10-15', Finish='2025-12-31', Priority='Medium'),
        dict(Task="Partner Support", Start='2025-11-01', Finish='2026-01-31', Priority='Medium'),
        dict(Task="Service Enhancement", Start='2025-11-01', Finish='2026-01-31', Priority='Medium'),
        dict(Task="Loyalty Program", Start='2026-01-01', Finish='2026-04-30', Priority='Low'),
        dict(Task="Market Expansion", Start='2026-02-01', Finish='2026-06-30', Priority='Low'),
    ]
    
    fig = px.timeline(
        timeline_data,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Priority",
        color_discrete_map={'High': '#2ecc71', 'Medium': '#f39c12', 'Low': '#e74c3c'}
    )
    
    fig.update_layout(
        title="Recovery Initiative Timeline",
        height=400,
        xaxis_title="Timeline"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Investment summary
    st.markdown("---")
    st.markdown("### 💰 Investment Summary")
    
    investment_data = pd.DataFrame({
        'Category': [
            'Customer Incentives',
            'Marketing & PR',
            'Technology Upgrades',
            'Partner Support',
            'Operations Enhancement',
            'Total'
        ],
        'Budget (₹M)': [2.5, 3.0, 1.5, 2.0, 1.0, 10.0],
        'Expected ROI': ['250%', '200%', '150%', '180%', '220%', '200%']
    })
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=investment_data['Budget (₹M)'][:-1],
            y=investment_data['Category'][:-1],
            orientation='h',
            marker_color='teal',
            text=investment_data['Budget (₹M)'][:-1].apply(lambda x: f"₹{x}M"),
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Recovery Investment Allocation",
            xaxis_title="Investment (₹ Millions)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Budget Breakdown")
        st.dataframe(investment_data, hide_index=True, use_container_width=True)
    
    # Final call to action
    st.markdown("---")
    st.success("""
    ### ✅ Next Steps
    
    1. **Leadership Approval:** Present this roadmap to executive team
    2. **Resource Allocation:** Secure budget and team assignments
    3. **Quick Wins:** Launch immediate actions within 7 days
    4. **Dashboard Setup:** Weekly recovery metrics monitoring
    5. **Stakeholder Communication:** Regular updates to all stakeholders
    
    **Recovery is achievable with focused execution and data-driven decision making.**
    """)

# Run the dashboard
if __name__ == "__main__":
    main()
