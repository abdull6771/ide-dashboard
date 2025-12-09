"""
Advanced Visualizations for Research Dashboard
Publication-quality charts for academic analysis
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st

def create_correlation_heatmap(df):
    """Create correlation heatmap for PLCT dimensions and other metrics"""
    st.subheader("🔥 Correlation Matrix: PLCT Dimensions & Investment")
    st.caption("Statistical relationships between key variables (Pearson correlation)")
    
    # Select numeric columns for correlation
    numeric_cols = [
        'plct_customer_experience_score',
        'plct_people_empowerment_score',
        'plct_operational_efficiency_score',
        'plct_new_business_models_score',
        'plct_total_score',
        'disclosure_quality_total_score'
    ]
    
    # Filter to existing columns
    available_cols = [col for col in numeric_cols if col in df.columns]
    
    if len(available_cols) < 2:
        st.info("Insufficient numeric data for correlation analysis")
        return
    
    # Calculate correlation matrix
    corr_df = df[available_cols].corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=[col.replace('plct_', '').replace('_score', '').replace('_', ' ').title() for col in corr_df.columns],
        y=[col.replace('plct_', '').replace('_score', '').replace('_', ' ').title() for col in corr_df.index],
        colorscale='RdBu',
        zmid=0,
        text=corr_df.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Correlation Matrix",
        height=500,
        xaxis={'side': 'bottom'},
        yaxis={'autorange': 'reversed'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretation guide
    with st.expander("📖 How to Interpret Correlations"):
        st.markdown("""
        **Correlation Coefficient (r):**
        - **+1.0**: Perfect positive correlation
        - **+0.7 to +1.0**: Strong positive correlation
        - **+0.3 to +0.7**: Moderate positive correlation
        - **-0.3 to +0.3**: Weak or no correlation
        - **-0.3 to -0.7**: Moderate negative correlation
        - **-0.7 to -1.0**: Strong negative correlation
        - **-1.0**: Perfect negative correlation
        
        **Research Use**: Identify relationships between transformation dimensions for hypothesis testing.
        """)

def create_scatter_matrix(df):
    """Create scatter plot matrix for multivariate analysis"""
    st.subheader("📊 Scatter Plot Matrix: Multivariate Analysis")
    st.caption("Pairwise relationships between PLCT dimensions")
    
    dimensions = [
        'plct_customer_experience_score',
        'plct_people_empowerment_score',
        'plct_operational_efficiency_score',
        'plct_new_business_models_score'
    ]
    
    # Filter to existing columns
    available_dims = [dim for dim in dimensions if dim in df.columns]
    
    if len(available_dims) < 2:
        st.info("Insufficient dimensional data for scatter matrix")
        return
    
    # Create scatter matrix
    fig = px.scatter_matrix(
        df[available_dims],
        dimensions=available_dims,
        labels={col: col.replace('plct_', '').replace('_score', '').replace('_', ' ').title() 
                for col in available_dims},
        title="PLCT Dimensions Scatter Matrix"
    )
    
    fig.update_traces(diagonal_visible=False, showupperhalf=False)
    fig.update_layout(height=700)
    
    st.plotly_chart(fig, use_container_width=True)

def create_box_plot_comparison(df):
    """Create box plots for distribution comparison across categories"""
    st.subheader("📦 Distribution Analysis: PLCT Scores by Category")
    st.caption("Compare score distributions across sectors, maturity levels, or innovation types")
    
    col1, col2 = st.columns(2)
    
    with col1:
        group_by = st.selectbox(
            "Group by:",
            ['company_sector', 'digital_maturity_level', 'innovation_level', 'strategic_priority'],
            key='box_groupby'
        )
    
    with col2:
        metric = st.selectbox(
            "Metric:",
            ['plct_total_score', 'plct_customer_experience_score', 
             'plct_operational_efficiency_score', 'disclosure_quality_total_score'],
            key='box_metric'
        )
    
    if group_by not in df.columns or metric not in df.columns:
        st.info(f"Selected columns not available in dataset")
        return
    
    # Filter out nulls
    plot_df = df[[group_by, metric]].dropna()
    
    if plot_df.empty:
        st.info("No data available for selected combination")
        return
    
    # Create box plot
    fig = px.box(
        plot_df,
        x=group_by,
        y=metric,
        color=group_by,
        points="outliers",
        labels={
            metric: metric.replace('_', ' ').title(),
            group_by: group_by.replace('_', ' ').title()
        }
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        xaxis={'tickangle': 45}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistical summary
    with st.expander("📊 Statistical Summary by Group"):
        summary_stats = plot_df.groupby(group_by)[metric].describe()
        st.dataframe(summary_stats, use_container_width=True)

def create_sunburst_chart(df):
    """Create hierarchical sunburst chart for sector->company->initiative drill-down"""
    st.subheader("☀️ Hierarchical View: Sector → Company → Initiative Type")
    st.caption("Interactive drill-down visualization of data structure")
    
    required_cols = ['company_sector', 'company_name', 'ide_category']
    if not all(col in df.columns for col in required_cols):
        st.info("Required columns not available for sunburst chart")
        return
    
    # Create hierarchical dataframe
    sunburst_df = df.groupby(['company_sector', 'company_name', 'ide_category']).size().reset_index(name='count')
    
    fig = px.sunburst(
        sunburst_df,
        path=['company_sector', 'company_name', 'ide_category'],
        values='count',
        color='count',
        color_continuous_scale='Viridis',
        title='Hierarchical Distribution of Digital Initiatives'
    )
    
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

def create_treemap_investment(df):
    """Create treemap for investment distribution"""
    st.subheader("🗺️ Investment Treemap: Sector and Company Allocation")
    st.caption("Proportional view of disclosed investment amounts")
    
    if 'investment_amount' not in df.columns:
        st.info("Investment data not available")
        return
    
    # Extract numeric investment values
    def extract_investment(text):
        if pd.isna(text) or text == '':
            return 0
        text = str(text).lower()
        try:
            if 'million' in text:
                num = float(''.join(c for c in text.split('million')[0] if c.isdigit() or c == '.'))
                return num * 1_000_000
            elif 'billion' in text:
                num = float(''.join(c for c in text.split('billion')[0] if c.isdigit() or c == '.'))
                return num * 1_000_000_000
            else:
                return 0
        except:
            return 0
    
    df['investment_numeric'] = df['investment_amount'].apply(extract_investment)
    
    # Filter to non-zero investments
    investment_df = df[df['investment_numeric'] > 0].copy()
    
    if investment_df.empty:
        st.info("No quantifiable investment data available")
        return
    
    # Aggregate by sector and company
    treemap_df = investment_df.groupby(['company_sector', 'company_name'])['investment_numeric'].sum().reset_index()
    
    fig = px.treemap(
        treemap_df,
        path=['company_sector', 'company_name'],
        values='investment_numeric',
        color='investment_numeric',
        color_continuous_scale='Greens',
        title='Investment Distribution by Sector and Company (RM)'
    )
    
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

def create_radar_chart(df):
    """Create radar chart for PLCT dimension comparison"""
    st.subheader("🎯 PLCT Radar Chart: Dimensional Profile Comparison")
    st.caption("Compare average PLCT profiles across sectors or maturity levels")
    
    group_by = st.selectbox(
        "Compare by:",
        ['company_sector', 'digital_maturity_level', 'innovation_level'],
        key='radar_groupby'
    )
    
    if group_by not in df.columns:
        st.info(f"{group_by} not available in dataset")
        return
    
    dimensions = [
        'plct_customer_experience_score',
        'plct_people_empowerment_score',
        'plct_operational_efficiency_score',
        'plct_new_business_models_score'
    ]
    
    if not all(dim in df.columns for dim in dimensions):
        st.info("PLCT dimension scores not available")
        return
    
    # Calculate averages by group
    radar_data = df.groupby(group_by)[dimensions].mean().reset_index()
    
    # Limit to top 5 groups
    top_groups = df[group_by].value_counts().head(5).index
    radar_data = radar_data[radar_data[group_by].isin(top_groups)]
    
    fig = go.Figure()
    
    dim_labels = ['Customer Experience', 'People Empowerment', 
                  'Operational Efficiency', 'New Business Models']
    
    for idx, row in radar_data.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row[dim] for dim in dimensions],
            theta=dim_labels,
            fill='toself',
            name=row[group_by]
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=500,
        title=f'PLCT Profile Comparison by {group_by.replace("_", " ").title()}'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_timeline_evolution(df):
    """Create stacked area chart showing evolution of initiative types over time"""
    st.subheader("📈 Temporal Evolution: Initiative Categories Over Time")
    st.caption("Stacked area chart showing trends in digital transformation focus areas")
    
    if 'report_year' not in df.columns or 'ide_category' not in df.columns:
        st.info("Timeline data not available")
        return
    
    # Create year x category counts
    timeline_df = df.groupby(['report_year', 'ide_category']).size().reset_index(name='count')
    
    # Pivot for stacked area
    pivot_df = timeline_df.pivot(index='report_year', columns='ide_category', values='count').fillna(0)
    
    fig = go.Figure()
    
    for category in pivot_df.columns:
        fig.add_trace(go.Scatter(
            x=pivot_df.index,
            y=pivot_df[category],
            mode='lines',
            stackgroup='one',
            name=category,
            hovertemplate='%{y} initiatives<extra></extra>'
        ))
    
    fig.update_layout(
        height=500,
        xaxis_title='Year',
        yaxis_title='Number of Initiatives',
        hovermode='x unified',
        title='Evolution of Initiative Categories'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_bubble_chart(df):
    """Create bubble chart for multi-dimensional comparison"""
    st.subheader("💭 Bubble Chart: Multi-Dimensional Analysis")
    st.caption("Three-variable comparison with bubble size representing fourth variable")
    
    col1, col2, col3, col4 = st.columns(4)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    with col1:
        x_axis = st.selectbox("X-axis:", numeric_cols, index=0, key='bubble_x')
    with col2:
        y_axis = st.selectbox("Y-axis:", numeric_cols, index=1 if len(numeric_cols) > 1 else 0, key='bubble_y')
    with col3:
        size_var = st.selectbox("Bubble Size:", numeric_cols, index=2 if len(numeric_cols) > 2 else 0, key='bubble_size')
    with col4:
        color_var = st.selectbox("Color by:", 
                                 ['company_sector', 'digital_maturity_level', 'innovation_level'],
                                 key='bubble_color')
    
    if x_axis not in df.columns or y_axis not in df.columns or size_var not in df.columns:
        st.info("Selected variables not available")
        return
    
    plot_df = df[[x_axis, y_axis, size_var, color_var]].dropna()
    
    if plot_df.empty:
        st.info("No data available for selected combination")
        return
    
    fig = px.scatter(
        plot_df,
        x=x_axis,
        y=y_axis,
        size=size_var,
        color=color_var,
        hover_data=[color_var],
        labels={
            x_axis: x_axis.replace('_', ' ').title(),
            y_axis: y_axis.replace('_', ' ').title(),
            size_var: size_var.replace('_', ' ').title()
        },
        title=f'{y_axis.replace("_", " ").title()} vs {x_axis.replace("_", " ").title()}'
    )
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def create_violin_plot(df):
    """Create violin plots showing distribution density"""
    st.subheader("🎻 Violin Plot: Score Distribution Density")
    st.caption("Detailed view of score distributions with probability density")
    
    metric = st.selectbox(
        "Select metric for distribution analysis:",
        ['plct_total_score', 'plct_customer_experience_score', 
         'disclosure_quality_total_score'],
        key='violin_metric'
    )
    
    group_by = st.selectbox(
        "Group by:",
        ['company_sector', 'digital_maturity_level', 'innovation_level'],
        key='violin_groupby'
    )
    
    if metric not in df.columns or group_by not in df.columns:
        st.info("Selected columns not available")
        return
    
    plot_df = df[[metric, group_by]].dropna()
    
    fig = px.violin(
        plot_df,
        y=metric,
        x=group_by,
        color=group_by,
        box=True,
        points="outliers",
        labels={
            metric: metric.replace('_', ' ').title(),
            group_by: group_by.replace('_', ' ').title()
        }
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        xaxis={'tickangle': 45}
    )
    
    st.plotly_chart(fig, use_container_width=True)
