# QuickBite Express - Interactive Dashboard

## 🎯 Overview

This interactive Streamlit dashboard transforms the comprehensive crisis analysis into an engaging visual story for QuickBite Express leadership. It provides actionable insights across 6 key areas:

1. **Executive Summary** - High-level crisis impact overview
2. **Business Health** - Detailed financial and operational metrics
3. **Customer Analytics** - Segmentation, loyalty, and churn analysis
4. **Operational Performance** - SLA compliance, ratings, and sentiment
5. **Restaurant Insights** - Partner performance and cuisine trends
6. **Recovery Roadmap** - Prioritized action plan with timeline

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- All analysis notebooks completed and CSV exports generated

### Installation

1. **Install required packages:**

```bash
pip install -r requirements_dashboard.txt
```

Or install individually:
```bash
pip install streamlit pandas numpy plotly
```

### Running the Dashboard

1. **Make sure you're in the project directory:**

```bash
cd /home/parambrata-ghosh/Development/Personal/Projects/Food_Delivery_Startup
```

2. **Launch the dashboard:**

```bash
streamlit run dashboard.py
```

3. **Access the dashboard:**

The dashboard will automatically open in your default browser at `http://localhost:8501`

If it doesn't open automatically, navigate to the URL shown in the terminal.

## 📊 Dashboard Features

### Page 1: Executive Summary
- **Key Metrics Cards**: Orders, Revenue, Customers, Ratings
- **Trend Visualizations**: Monthly orders and revenue trends
- **Crisis Timeline**: Visual marker showing June 2025 crisis event
- **Impact Summary**: Quick overview of business decline

### Page 2: Business Health Deep Dive
- **Revenue Analysis**: Component breakdown and waterfall chart
- **Order Trends**: Monthly orders with cancellation rate overlay
- **Geographic Impact**: City-wise performance analysis
- **Detailed Tables**: Monthly performance metrics

### Page 3: Customer Analytics
- **RFM Segmentation**: Interactive treemap of customer segments
- **Loyalty Analysis**: High-value customer identification
- **Churn Analysis**: Churned loyal customers breakdown
- **Acquisition Channels**: Performance by marketing channel

### Page 4: Operational Performance
- **SLA Compliance**: Trend analysis and target comparison
- **Delivery Metrics**: Actual vs expected time tracking
- **Rating Trends**: Monthly average rating evolution
- **Sentiment Analysis**: Positive/negative/neutral breakdown
- **Review Insights**: Most common words in customer reviews

### Page 5: Restaurant Insights
- **Restaurant Performance**: Distribution and top decliners
- **Cuisine Analysis**: Performance by cuisine type
- **Performance Matrix**: Volume vs change scatter plot
- **Detailed Tables**: Restaurant-level metrics

### Page 6: Recovery Roadmap
- **Priority Matrix**: Impact vs Effort visualization
- **Action Plans**: Immediate, short-term, and medium-term initiatives
- **Timeline Gantt**: Implementation schedule
- **Investment Summary**: Budget allocation across initiatives
- **KPI Targets**: Recovery metrics to track

## 🎨 Interactive Features

### Filters (Sidebar)
- **Time Period**: Filter by Pre-Crisis, Crisis, or All Periods
- **Cities**: Multi-select city filter (when applicable)

### Visualizations
- **Hover Details**: Hover over charts for detailed information
- **Zoom & Pan**: Interactive chart exploration
- **Export**: Download charts as PNG images (camera icon)

## 📁 Required Data Files

The dashboard expects the following CSV files in the `output/` directory:

**Business Metrics:**
- `monthly_orders.csv`
- `monthly_revenue.csv`
- `monthly_cancellations.csv`

**Customer Metrics:**
- `customer_rfm_segments.csv`
- `high_value_customers.csv`
- `churned_loyal_customers.csv`
- `acquisition_channel_performance.csv`

**Geographic:**
- `city_order_impact.csv`

**Operational:**
- `monthly_sla_compliance.csv`
- `monthly_ratings.csv`
- `sentiment_analysis.csv`
- `review_word_frequency.csv`

**Restaurant:**
- `restaurant_performance.csv`
- `cuisine_performance.csv`

**Raw Data (from input/RPC_18_Datasets/):**
- `fact_orders.csv`
- `fact_delivery_performance.csv`
- `fact_ratings.csv`
- `dim_restaurant.csv`
- `dim_customer.csv`

## 🎯 Usage Tips

### For Executives
1. Start with **Executive Summary** for high-level overview
2. Jump to **Recovery Roadmap** for action items
3. Use filters to focus on specific time periods or cities

### For Analysts
1. Explore **Business Health** for detailed metrics
2. Dive into **Customer Analytics** for segmentation insights
3. Review **Operational Performance** for quality metrics

### For Strategy Teams
1. Study **Restaurant Insights** for partner performance
2. Analyze **Recovery Roadmap** priority matrix
3. Use timeline gantt for planning

## 🛠️ Customization

### Branding
Update brand colors in the CSS section (lines 25-40 in dashboard.py):
```python
.section-header {
    border-bottom: 3px solid #ff6b6b;  # Change to your brand color
}
```

### Metrics
Add or modify KPIs in the `calculate_key_metrics()` function (lines 90-170).

### Visualizations
All charts use Plotly - easily customizable:
- Colors: `marker_color` parameter
- Layout: `fig.update_layout()` method
- Interactivity: Built-in by default

## 🐛 Troubleshooting

### Dashboard Won't Start
```bash
# Check Streamlit installation
streamlit --version

# Reinstall if needed
pip install --upgrade streamlit
```

### Data Loading Errors
- Verify all CSV files exist in `output/` and `input/RPC_18_Datasets/`
- Check file paths in `load_data()` function
- Ensure notebooks were run completely

### Chart Not Displaying
- Check browser console for JavaScript errors
- Try a different browser (Chrome recommended)
- Clear browser cache

### Performance Issues
- Dashboard caching is enabled (@st.cache_data)
- Restart dashboard if data changes: Ctrl+C then rerun

## 📈 Performance Optimization

The dashboard uses Streamlit's caching:
- `@st.cache_data` for data loading
- `@st.cache_data` for metric calculations

To clear cache:
1. Press 'C' in the dashboard
2. Select "Clear cache"
3. Or restart the dashboard

## 🌐 Deployment Options

### Local Network Access
```bash
streamlit run dashboard.py --server.address=0.0.0.0
```
Access from other devices: `http://YOUR_IP:8501`

### Streamlit Cloud (Free)
1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect repository and deploy

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements_dashboard.txt .
RUN pip install -r requirements_dashboard.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "dashboard.py"]
```

## 📝 Additional Notes

### Data Refresh
- Re-run analysis notebooks to update CSV files
- Dashboard auto-refreshes when files change (if running)
- Or use "Rerun" button in dashboard

### Mobile View
- Dashboard is responsive
- Best viewed on tablet or desktop
- Some charts may require horizontal scrolling on mobile

### Export Options
- **Charts**: Click camera icon to download PNG
- **Tables**: Copy-paste directly from dashboard
- **Full Report**: Use browser print to PDF

## 🤝 Support

For issues or questions:
1. Check this README
2. Review error messages in terminal
3. Verify all data files are present and valid
4. Check Streamlit documentation: [docs.streamlit.io](https://docs.streamlit.io)

## 📄 License

This dashboard is part of the QuickBite Express Crisis Analysis project.

---

**Dashboard Version:** 1.0  
**Last Updated:** October 2025  
**Analysis Period:** January - September 2025  
**Crisis Event:** June 2025
