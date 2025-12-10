"""
IDE Digital Transformation Dashboard - Complete Dash/Plotly Version
Full-featured dashboard with all analytics from Streamlit version
"""

import os
from datetime import datetime
import pymysql
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import json
import base64
import io

# Load environment variables
load_dotenv()

# Database connection
def get_db_connection():
    """Create database connection"""
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        cursorclass=pymysql.cursors.DictCursor
    )

# ==================== DATA FETCHING FUNCTIONS ====================

def fetch_all_data():
    """Fetch complete dataset for analysis"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                i.*,
                c.company_name,
                c.company_sector,
                c.year_mentioned as report_year,
                c.report_type,
                c.technology_used,
                c.digital_maturity_level,
                c.strategic_priority,
                c.digital_investment
            FROM initiatives i
            LEFT JOIN companies c ON i.company_id = c.id
        """)
        data = cursor.fetchall()
        return pd.DataFrame(data)
    finally:
        conn.close()

def fetch_initiatives(limit=100, search='', sector='', category=''):
    """Fetch initiatives with filters - for Data Explorer tab"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT 
                i.id,
                c.company_name,
                i.initiative as initiative_name,
                i.category,
                c.technology_used as technology,
                c.year_mentioned as year_announced,
                c.digital_maturity_level,
                i.innovation_level
            FROM initiatives i
            LEFT JOIN companies c ON i.company_id = c.id
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (i.initiative LIKE %s OR c.company_name LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        if sector:
            query += " AND c.company_sector = %s"
            params.append(sector)
        
        if category:
            query += " AND i.category = %s"
            params.append(category)
        
        query += f" ORDER BY c.year_mentioned DESC LIMIT {limit}"
        
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()

def fetch_metrics():
    """Fetch dashboard KPIs"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(DISTINCT id) as count FROM initiatives")
        total_initiatives = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(DISTINCT id) as count FROM companies")
        total_companies = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(DISTINCT company_sector) as count FROM companies WHERE company_sector IS NOT NULL")
        total_sectors = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(DISTINCT category) as count FROM initiatives WHERE category IS NOT NULL")
        total_categories = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(DISTINCT technology_used) as count 
            FROM companies 
            WHERE technology_used IS NOT NULL AND technology_used != ''
        """)
        total_technologies = cursor.fetchone()['count']
        
        return {
            'initiatives': total_initiatives,
            'companies': total_companies,
            'sectors': total_sectors,
            'categories': total_categories,
            'technologies': total_technologies
        }
    finally:
        conn.close()

def fetch_quick_insights():
    """Fetch data for quick insights section"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Top company
        cursor.execute("""
            SELECT c.company_name, COUNT(i.id) as count
            FROM companies c
            LEFT JOIN initiatives i ON c.id = i.company_id
            GROUP BY c.company_name
            ORDER BY count DESC
            LIMIT 1
        """)
        top_company = cursor.fetchone()
        
        # Top sector
        cursor.execute("""
            SELECT c.company_sector, COUNT(i.id) as count
            FROM companies c
            LEFT JOIN initiatives i ON c.id = i.company_id
            WHERE c.company_sector IS NOT NULL
            GROUP BY c.company_sector
            ORDER BY count DESC
            LIMIT 1
        """)
        top_sector = cursor.fetchone()
        
        # Top category
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM initiatives
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
            LIMIT 1
        """)
        top_category = cursor.fetchone()
        
        # Peak year
        cursor.execute("""
            SELECT c.year_mentioned, COUNT(i.id) as count
            FROM companies c
            LEFT JOIN initiatives i ON c.id = i.company_id
            WHERE c.year_mentioned IS NOT NULL
            GROUP BY c.year_mentioned
            ORDER BY count DESC
            LIMIT 1
        """)
        peak_year = cursor.fetchone()
        
        # Transformational count
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM initiatives
            WHERE innovation_level = 'Transformational'
        """)
        transformational = cursor.fetchone()
        
        return {
            'top_company': top_company['company_name'] if top_company else 'N/A',
            'top_company_count': top_company['count'] if top_company else 0,
            'top_sector': top_sector['company_sector'] if top_sector else 'N/A',
            'top_sector_count': top_sector['count'] if top_sector else 0,
            'top_category': top_category['category'] if top_category else 'N/A',
            'top_category_count': top_category['count'] if top_category else 0,
            'peak_year': peak_year['year_mentioned'] if peak_year else 'N/A',
            'peak_year_count': peak_year['count'] if peak_year else 0,
            'transformational_count': transformational['count'] if transformational else 0
        }
    finally:
        conn.close()

def fetch_plct_data():
    """Fetch PLCT Framework scoring data"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                i.plct_customer_experience_score,
                i.plct_people_empowerment_score,
                i.plct_operational_efficiency_score,
                i.plct_new_business_models_score,
                i.plct_total_score,
                i.plct_dominant_dimension,
                i.plct_investor_weighted_score,
                i.plct_policy_weighted_score,
                i.plct_strategic_weighted_score,
                i.disclosure_quality_total_score,
                i.disclosure_quality_tier,
                c.company_name,
                c.company_sector
            FROM initiatives i
            LEFT JOIN companies c ON i.company_id = c.id
            WHERE i.plct_total_score IS NOT NULL
        """)
        return pd.DataFrame(cursor.fetchall())
    finally:
        conn.close()

def fetch_companies_list():
    """Fetch list of all companies"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT company_name FROM companies ORDER BY company_name")
        return [row['company_name'] for row in cursor.fetchall()]
    finally:
        conn.close()

def fetch_company_data(company_name):
    """Fetch all data for a specific company"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                i.*,
                c.company_name,
                c.company_sector,
                c.year_mentioned,
                c.digital_maturity_level
            FROM initiatives i
            LEFT JOIN companies c ON i.company_id = c.id
            WHERE c.company_name = %s
        """, (company_name,))
        return pd.DataFrame(cursor.fetchall())
    finally:
        conn.close()

# ==================== VISUALIZATION FUNCTIONS ====================

def create_sector_chart(df):
    """Create sector distribution chart"""
    sector_count = df.groupby('company_sector').size().reset_index(name='count')
    sector_count = sector_count.sort_values('count', ascending=True)
    
    fig = px.bar(
        sector_count,
        x='count',
        y='company_sector',
        orientation='h',
        labels={'count': 'Number of Initiatives', 'company_sector': 'Sector'},
        color='count',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_yearly_trend_chart(df):
    """Create yearly trend line chart"""
    yearly = df.groupby('report_year').size().reset_index(name='count')
    yearly = yearly.sort_values('report_year')
    
    fig = px.line(
        yearly,
        x='report_year',
        y='count',
        labels={'report_year': 'Year', 'count': 'Number of Initiatives'},
        markers=True
    )
    fig.update_traces(line_color='#667eea', line_width=3, marker=dict(size=8))
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    return fig

def create_maturity_chart(df):
    """Create digital maturity distribution chart"""
    maturity = df['digital_maturity_level'].value_counts().reset_index()
    maturity.columns = ['level', 'count']
    
    fig = px.pie(
        maturity,
        values='count',
        names='level',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

def create_innovation_chart(df):
    """Create innovation level distribution chart"""
    innovation = df['innovation_level'].value_counts().reset_index()
    innovation.columns = ['level', 'count']
    
    fig = px.bar(
        innovation,
        x='level',
        y='count',
        labels={'level': 'Innovation Level', 'count': 'Number of Initiatives'},
        color='count',
        color_continuous_scale='Plasma'
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_category_treemap(df):
    """Create category treemap"""
    category = df['category'].value_counts().reset_index()
    category.columns = ['category', 'count']
    
    fig = px.treemap(
        category,
        path=['category'],
        values='count',
        color='count',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=600, margin=dict(l=0, r=0, t=20, b=0))
    return fig

def create_plct_radar_chart(plct_df):
    """Create radar chart for average PLCT scores"""
    avg_scores = {
        'Customer Experience': plct_df['plct_customer_experience_score'].mean(),
        'People Empowerment': plct_df['plct_people_empowerment_score'].mean(),
        'Operational Efficiency': plct_df['plct_operational_efficiency_score'].mean(),
        'New Business Models': plct_df['plct_new_business_models_score'].mean()
    }
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(avg_scores.values()),
        theta=list(avg_scores.keys()),
        fill='toself',
        name='Average Scores'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

def create_correlation_heatmap(plct_df):
    """Create correlation heatmap for PLCT dimensions"""
    numeric_cols = [
        'plct_customer_experience_score',
        'plct_people_empowerment_score',
        'plct_operational_efficiency_score',
        'plct_new_business_models_score',
        'plct_total_score',
        'disclosure_quality_total_score'
    ]
    
    available_cols = [col for col in numeric_cols if col in plct_df.columns]
    if len(available_cols) < 2:
        return go.Figure()
    
    corr_df = plct_df[available_cols].corr()
    
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
        height=500,
        margin=dict(l=100, r=50, t=50, b=100)
    )
    return fig

def create_scatter_matrix(plct_df):
    """Create scatter matrix for PLCT dimensions"""
    cols = [
        'plct_customer_experience_score',
        'plct_people_empowerment_score',
        'plct_operational_efficiency_score',
        'plct_new_business_models_score'
    ]
    
    available_cols = [col for col in cols if col in plct_df.columns]
    if len(available_cols) < 2:
        return go.Figure()
    
    fig = px.scatter_matrix(
        plct_df,
        dimensions=available_cols,
        color='plct_total_score',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=700, margin=dict(l=0, r=0, t=40, b=0))
    return fig

def create_sunburst_chart(df):
    """Create sunburst chart for sector-category hierarchy"""
    sector_cat = df.groupby(['company_sector', 'category']).size().reset_index(name='count')
    
    fig = px.sunburst(
        sector_cat,
        path=['company_sector', 'category'],
        values='count',
        color='count',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=600, margin=dict(l=0, r=0, t=20, b=0))
    return fig

def create_box_plot_comparison(plct_df):
    """Create box plot comparing PLCT scores by sector"""
    fig = go.Figure()
    
    dimensions = [
        ('plct_customer_experience_score', 'Customer Experience'),
        ('plct_people_empowerment_score', 'People Empowerment'),
        ('plct_operational_efficiency_score', 'Operational Efficiency'),
        ('plct_new_business_models_score', 'New Business Models')
    ]
    
    for col, name in dimensions:
        if col in plct_df.columns:
            fig.add_trace(go.Box(y=plct_df[col], name=name))
    
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        yaxis_title="Score"
    )
    return fig

def create_comparison_charts(df_a, df_b, company_a, company_b):
    """Create comparison charts for two companies"""
    # Category comparison
    cat_a = df_a['category'].value_counts().head(10)
    cat_b = df_b['category'].value_counts().head(10)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=cat_a.index, y=cat_a.values, name=company_a))
    fig.add_trace(go.Bar(x=cat_b.index, y=cat_b.values, name=company_b))
    
    fig.update_layout(
        barmode='group',
        height=400,
        xaxis_tickangle=-45,
        margin=dict(l=0, r=0, t=40, b=100)
    )
    return fig

# Initialize Dash app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)
app.title = "IDE Digital Transformation Dashboard"
server = app.server

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --primary-color: #667eea;
                --secondary-color: #764ba2;
                --accent-color: #f093fb;
                --text-dark: #1a202c;
                --text-light: #718096;
                --bg-light: #f7fafc;
                --border-radius: 12px;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
            }
            
            .dashboard-header {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                padding: 2rem;
                margin-bottom: 2rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .header-title {
                color: white;
                font-size: 2rem;
                font-weight: 700;
                margin: 0;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            
            .header-subtitle {
                color: rgba(255, 255, 255, 0.9);
                font-size: 1rem;
                margin-top: 0.5rem;
            }
            
            .metric-card {
                background: white;
                border-radius: var(--border-radius);
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
            }
            
            .metric-value {
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0.5rem 0;
            }
            
            .metric-label {
                color: var(--text-light);
                font-size: 0.875rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 600;
            }
            
            .metric-icon {
                font-size: 2rem;
                color: var(--primary-color);
                opacity: 0.8;
            }
            
            .content-section {
                background: white;
                border-radius: var(--border-radius);
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .section-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--text-dark);
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .filter-section {
                background: var(--bg-light);
                border-radius: var(--border-radius);
                padding: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .insights-box {
                background: white;
                border-radius: var(--border-radius);
                padding: 1.5rem;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border-left: 4px solid var(--primary-color);
            }
            
            .insight-item {
                margin: 0.5rem 0;
                padding: 0.5rem;
                background: var(--bg-light);
                border-radius: 8px;
            }
            
            .calculator-input {
                margin: 1rem 0;
            }
            
            .result-box {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 2rem;
                border-radius: var(--border-radius);
                margin-top: 2rem;
                text-align: center;
            }
            
            .result-value {
                font-size: 3rem;
                font-weight: 700;
                margin: 1rem 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Initialize data with defaults - will be fetched on first request
metrics = {
    'total_initiatives': 0, 
    'total_companies': 0, 
    'total_sectors': 0, 
    'total_categories': 0, 
    'total_technologies': 0
}
filter_options = {'sectors': [], 'categories': []}
companies_list = []

def load_initial_data():
    """Load initial data on first request"""
    global metrics, filter_options, companies_list
    
    if metrics['total_initiatives'] == 0:
        try:
            metrics = fetch_metrics()
        except:
            pass
    
    if not filter_options['sectors']:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT company_sector FROM companies WHERE company_sector IS NOT NULL ORDER BY company_sector")
            filter_options['sectors'] = [row['company_sector'] for row in cursor.fetchall()]
            cursor.execute("SELECT DISTINCT category FROM initiatives WHERE category IS NOT NULL ORDER BY category")
            filter_options['categories'] = [row['category'] for row in cursor.fetchall()]
            conn.close()
        except:
            pass
    
    if not companies_list:
        try:
            companies_list = fetch_companies_list()
        except:
            pass

# ==================== LAYOUT ====================

app.layout = dbc.Container([
    # Store for data
    dcc.Store(id='data-store'),
    
    # Header
    html.Div([
        html.H1("IDE Digital Transformation Dashboard", className="header-title"),
        html.P(f"Comprehensive analysis of digital initiatives", 
               className="header-subtitle")
    ], className="dashboard-header"),
    
    # Metrics Cards
    dbc.Row([
        dbc.Col([
            html.Div([
                html.I(className="fas fa-rocket metric-icon"),
                html.Div(f"{metrics['initiatives']:,}", className="metric-value"),
                html.Div("Total Initiatives", className="metric-label")
            ], className="metric-card")
        ], width=12, md=6, lg=2),
        
        dbc.Col([
            html.Div([
                html.I(className="fas fa-building metric-icon"),
                html.Div(f"{metrics['companies']:,}", className="metric-value"),
                html.Div("Companies", className="metric-label")
            ], className="metric-card")
        ], width=12, md=6, lg=2),
        
        dbc.Col([
            html.Div([
                html.I(className="fas fa-industry metric-icon"),
                html.Div(f"{metrics['sectors']:,}", className="metric-value"),
                html.Div("Sectors", className="metric-label")
            ], className="metric-card")
        ], width=12, md=6, lg=2),
        
        dbc.Col([
            html.Div([
                html.I(className="fas fa-layer-group metric-icon"),
                html.Div(f"{metrics['categories']:,}", className="metric-value"),
                html.Div("Categories", className="metric-label")
            ], className="metric-card")
        ], width=12, md=6, lg=2),
        
        dbc.Col([
            html.Div([
                html.I(className="fas fa-microchip metric-icon"),
                html.Div(f"{metrics['technologies']:,}", className="metric-value"),
                html.Div("Technologies", className="metric-label")
            ], className="metric-card")
        ], width=12, md=6, lg=2),
    ], className="mb-4"),
    
    # Quick Insights
    html.Div([
        dbc.Button(
            [html.I(className="fas fa-chart-line me-2"), "Research Summary & Key Findings"],
            id="insights-toggle",
            color="light",
            className="mb-3 w-100",
            style={"textAlign": "left"}
        ),
        dbc.Collapse(
            html.Div(id="quick-insights-content", className="insights-box"),
            id="insights-collapse",
            is_open=True
        )
    ]),
    
    # Filters
    html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label("Search", html_for="search-input"),
                dbc.Input(id="search-input", type="text", placeholder="Search initiatives, companies...")
            ], width=12, md=4),
            
            dbc.Col([
                dbc.Label("Sector", html_for="sector-filter"),
                dcc.Dropdown(
                    id="sector-filter",
                    options=[{'label': 'All Sectors', 'value': ''}] + [{'label': s, 'value': s} for s in filter_options['sectors']],
                    value='',
                    clearable=True
                )
            ], width=12, md=4),
            
            dbc.Col([
                dbc.Label("Category", html_for="category-filter"),
                dcc.Dropdown(
                    id="category-filter",
                    options=[{'label': 'All Categories', 'value': ''}] + [{'label': c, 'value': c} for c in filter_options['categories']],
                    value='',
                    clearable=True
                )
            ], width=12, md=4),
        ])
    ], className="filter-section"),
    
    # Tabs
    dbc.Tabs([
        # Overview Tab
        dbc.Tab([
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H3("📊 Sector Distribution", className="section-title"),
                            dcc.Graph(id="sector-chart")
                        ], className="content-section")
                    ], width=12, lg=6),
                    
                    dbc.Col([
                        html.Div([
                            html.H3("📈 Yearly Trend", className="section-title"),
                            dcc.Graph(id="yearly-chart")
                        ], className="content-section")
                    ], width=12, lg=6),
                ]),
                
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H3("🏆 Digital Maturity Levels", className="section-title"),
                            dcc.Graph(id="maturity-chart")
                        ], className="content-section")
                    ], width=12, lg=6),
                    
                    dbc.Col([
                        html.Div([
                            html.H3("💡 Innovation Distribution", className="section-title"),
                            dcc.Graph(id="innovation-chart")
                        ], className="content-section")
                    ], width=12, lg=6),
                ])
            ])
        ], label=" Executive Summary", tab_id="overview"),
        
        # Sectoral Analysis Tab
        dbc.Tab([
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H3("📦 Initiative Categories", className="section-title"),
                            dcc.Graph(id="category-bar-chart")
                        ], className="content-section")
                    ], width=12, lg=6),
                    
                    dbc.Col([
                        html.Div([
                            html.H3("🌟 Innovation Levels", className="section-title"),
                            dcc.Graph(id="innovation-pie-chart")
                        ], className="content-section")
                    ], width=12, lg=6),
                ]),
                
                html.Div([
                    html.H3("🎯 Sector-Category Analysis", className="section-title"),
                    dcc.Graph(id="sunburst-chart")
                ], className="content-section")
            ])
        ], label="Sectoral Analysis", tab_id="sectoral", label_style={"color": "black"}),
        
        # Technology Tab
        dbc.Tab([
            html.Div([
                html.Div([
                    html.H3("🔧 Top Technologies", className="section-title"),
                    dcc.Graph(id="tech-chart")
                ], className="content-section"),
                
                html.Div([
                    html.H3("📊 Category Distribution", className="section-title"),
                    dcc.Graph(id="category-treemap")
                ], className="content-section")
            ])
        ], label=" Technology Patterns", tab_id="technology", label_style={"color": "black"}),
        
        # PLCT Framework Tab
        dbc.Tab([
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H3("🎯 Average PLCT Scores", className="section-title"),
                            dcc.Graph(id="plct-radar")
                        ], className="content-section")
                    ], width=12, lg=6),
                    
                    dbc.Col([
                        html.Div([
                            html.H3("📊 Score Distribution", className="section-title"),
                            dcc.Graph(id="plct-box-plot")
                        ], className="content-section")
                    ], width=12, lg=6),
                ]),
                
                html.Div([
                    html.H3("🔗 Dimension Correlation Matrix", className="section-title"),
                    dcc.Graph(id="plct-correlation")
                ], className="content-section"),
                
                html.Div([
                    html.H3(" PLCT Scatter Matrix", className="section-title"),
                    dcc.Graph(id="plct-scatter-matrix")
                ], className="content-section")
            ])
        ], label=" PLCT Framework", tab_id="plct", label_style={"color": "black"}),
        
        # Advanced Analytics Tab
        dbc.Tab([
            html.Div([
                html.Div([
                    html.H3(" Advanced Statistical Analysis", className="section-title"),
                    html.P("Comprehensive correlation and distribution analysis", className="text-muted"),
                    dcc.Graph(id="advanced-analytics-chart")
                ], className="content-section")
            ])
        ], label=" Advanced Analytics", tab_id="advanced", label_style={"color": "black"}),
        
        # Comparative Analysis Tab
        dbc.Tab([
            html.Div([
                html.Div([
                    html.H3("⚖️ Company Comparison", className="section-title"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Company A"),
                            dcc.Dropdown(
                                id="company-a-select",
                                options=[{'label': c, 'value': c} for c in companies_list],
                                value=companies_list[0] if companies_list else None
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Company B"),
                            dcc.Dropdown(
                                id="company-b-select",
                                options=[{'label': c, 'value': c} for c in companies_list],
                                value=companies_list[1] if len(companies_list) > 1 else None
                            )
                        ], width=6),
                    ]),
                    html.Div(id="comparison-metrics", className="mt-4"),
                    dcc.Graph(id="comparison-chart", className="mt-4")
                ], className="content-section")
            ])
        ], label=" Comparative Analysis", tab_id="comparison", label_style={"color": "black"}),
        
        # ROI Calculator Tab
        dbc.Tab([
            html.Div([
                html.Div([
                    html.H3(" ROI Estimator", className="section-title"),
                    html.P("Calculate potential return on investment for digital initiatives", className="text-muted"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Initial Investment (RM)"),
                            dcc.Input(
                                id="roi-investment",
                                type="number",
                                value=1000000,
                                className="form-control"
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Implementation Period (months)"),
                            dcc.Input(
                                id="roi-period",
                                type="number",
                                value=12,
                                className="form-control"
                            )
                        ], width=6),
                    ], className="calculator-input"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Expected Annual Benefit (RM)"),
                            dcc.Input(
                                id="roi-benefit",
                                type="number",
                                value=500000,
                                className="form-control"
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Annual Operating Cost (RM)"),
                            dcc.Input(
                                id="roi-cost",
                                type="number",
                                value=100000,
                                className="form-control"
                            )
                        ], width=6),
                    ], className="calculator-input"),
                    
                    dbc.Button(
                        "Calculate ROI",
                        id="calculate-roi-btn",
                        color="primary",
                        className="mt-3 w-100"
                    ),
                    
                    html.Div(id="roi-results", className="mt-4")
                ], className="content-section")
            ])
        ], label="ROI Estimator", tab_id="roi", label_style={"color": "black"}),
        
        # Data Explorer Tab (Simple)
        dbc.Tab([
            html.Div([
                html.Div([
                    html.H3("🔍 Initiatives Data Explorer", className="section-title"),
                    html.Div(id="data-table-explorer")
                ], className="content-section")
            ])
        ], label="🔍 Data Explorer", tab_id="explorer", label_style={"color": "black"}),
        
        # Research Data Tab (with Download)
        dbc.Tab([
            html.Div([
                html.Div([
                    html.H3("Research Dataset", className="section-title"),
                    dbc.Button(
                        [html.I(className="fas fa-download me-2"), "Download CSV"],
                        id="download-csv-btn",
                        color="primary",
                        className="mb-3"
                    ),
                    dcc.Download(id="download-csv"),
                    html.Div(id="data-table")
                ], className="content-section")
            ])
        ], label="📋 Research Data", tab_id="data", label_style={"color": "black"}),
        
    ], id="main-tabs", active_tab="overview"),
    
], fluid=True, style={'padding': '0'})

# ==================== CALLBACKS ====================

@callback(
    Output("insights-collapse", "is_open"),
    Input("insights-toggle", "n_clicks"),
    State("insights-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_insights(n, is_open):
    return not is_open

@callback(
    Output("quick-insights-content", "children"),
    Input("search-input", "value")
)
def update_quick_insights(_):
    load_initial_data()  # Ensure data is loaded
    insights = fetch_quick_insights()
    
    return [
        dbc.Row([
            dbc.Col([
                html.H5("Primary Findings", className="text-primary"),
                html.Div([
                    html.Strong("Most Active Organization: "),
                    f"{insights['top_company']} ({insights['top_company_count']} initiatives)"
                ], className="insight-item"),
                html.Div([
                    html.Strong("Dominant Sector: "),
                    f"{insights['top_sector']} ({insights['top_sector_count']} initiatives)"
                ], className="insight-item"),
                html.Div([
                    html.Strong("Primary Category: "),
                    f"{insights['top_category']} ({insights['top_category_count']} initiatives)"
                ], className="insight-item"),
            ], width=6),
            
            dbc.Col([
                html.H5("Temporal & Innovation Patterns", className="text-primary"),
                html.Div([
                    html.Strong("Peak Activity Year: "),
                    f"{insights['peak_year']} ({insights['peak_year_count']} initiatives)"
                ], className="insight-item"),
                html.Div([
                    html.Strong("Transformational Projects: "),
                    f"{insights['transformational_count']} high-impact initiatives"
                ], className="insight-item"),
                html.Div([
                    html.Strong("Total Observations: "),
                    f"{metrics['initiatives']} initiatives analyzed"
                ], className="insight-item"),
            ], width=6),
        ])
    ]

@callback(
    Output("data-store", "data"),
    [Input("search-input", "value"),
     Input("sector-filter", "value"),
     Input("category-filter", "value")]
)
def update_data_store(search, sector, category):
    load_initial_data()  # Ensure data is loaded
    df = fetch_all_data()
    
    # Apply filters
    if search:
        mask = (
            df['initiative'].str.contains(search, case=False, na=False) |
            df['company_name'].str.contains(search, case=False, na=False)
        )
        df = df[mask]
    
    if sector:
        df = df[df['company_sector'] == sector]
    
    if category:
        df = df[df['category'] == category]
    
    return df.to_json(date_format='iso', orient='split')

@callback(
    [Output("sector-chart", "figure"),
     Output("yearly-chart", "figure"),
     Output("maturity-chart", "figure"),
     Output("innovation-chart", "figure"),
     Output("tech-chart", "figure"),
     Output("category-treemap", "figure"),
     Output("category-bar-chart", "figure"),
     Output("innovation-pie-chart", "figure"),
     Output("sunburst-chart", "figure"),
     Output("data-table", "children")],
    Input("data-store", "data")
)
def update_charts(data_json):
    if not data_json:
        empty_fig = go.Figure()
        return [empty_fig] * 9 + [html.Div("No data available")]
    
    df = pd.read_json(data_json, orient='split')
    
    if df.empty:
        empty_fig = go.Figure()
        return [empty_fig] * 9 + [html.Div("No data matches filters")]
    
    # Create charts
    sector_fig = create_sector_chart(df)
    yearly_fig = create_yearly_trend_chart(df)
    maturity_fig = create_maturity_chart(df)
    innovation_fig = create_innovation_chart(df)
    
    # Tech chart
    tech_data = df['technology_used'].value_counts().head(20).reset_index()
    tech_data.columns = ['technology', 'count']
    tech_fig = px.bar(
        tech_data,
        x='count',
        y='technology',
        orientation='h',
        color='count',
        color_continuous_scale='Turbo'
    )
    tech_fig.update_layout(showlegend=False, height=600, margin=dict(l=0, r=0, t=20, b=0))
    
    category_treemap = create_category_treemap(df)
    
    # Category bar
    cat_data = df['category'].value_counts().reset_index()
    cat_data.columns = ['category', 'count']
    cat_bar_fig = px.bar(
        cat_data,
        x='category',
        y='count',
        color='count',
        color_continuous_scale='Blues'
    )
    cat_bar_fig.update_layout(showlegend=False, height=450, xaxis_tickangle=-45)
    
    # Innovation pie
    innov_data = df['innovation_level'].value_counts().reset_index()
    innov_data.columns = ['level', 'count']
    innov_pie_fig = px.pie(
        innov_data,
        values='count',
        names='level',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Oranges
    )
    innov_pie_fig.update_layout(height=450)
    
    sunburst_fig = create_sunburst_chart(df)
    
    # Data table
    display_cols = ['company_name', 'company_sector', 'report_year', 'digital_maturity_level',
                    'category', 'innovation_level']
    display_cols = [col for col in display_cols if col in df.columns]
    
    table = dbc.Table.from_dataframe(
        df[display_cols].head(100),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm'
    )
    
    return (sector_fig, yearly_fig, maturity_fig, innovation_fig, tech_fig,
            category_treemap, cat_bar_fig, innov_pie_fig, sunburst_fig, table)

@callback(
    Output("data-table-explorer", "children"),
    [Input("search-input", "value"),
     Input("sector-filter", "value"),
     Input("category-filter", "value")]
)
def update_data_explorer(search, sector, category):
    """Update Data Explorer tab - exactly like dash_app.py"""
    initiatives = fetch_initiatives(
        limit=100,
        search=search or '',
        sector=sector or '',
        category=category or ''
    )
    df_initiatives = pd.DataFrame(initiatives)
    
    if not df_initiatives.empty:
        table = dbc.Table.from_dataframe(
            df_initiatives,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            style={'fontSize': '0.9rem'}
        )
    else:
        table = html.Div("No data found matching your filters.", className="text-muted text-center p-4")
    
    return table

@callback(
    [Output("plct-radar", "figure"),
     Output("plct-box-plot", "figure"),
     Output("plct-correlation", "figure"),
     Output("plct-scatter-matrix", "figure")],
    Input("main-tabs", "active_tab")
)
def update_plct_charts(active_tab):
    if active_tab != "plct":
        empty_fig = go.Figure()
        return [empty_fig] * 4
    
    plct_df = fetch_plct_data()
    
    if plct_df.empty:
        empty_fig = go.Figure()
        return [empty_fig] * 4
    
    radar_fig = create_plct_radar_chart(plct_df)
    box_fig = create_box_plot_comparison(plct_df)
    corr_fig = create_correlation_heatmap(plct_df)
    scatter_fig = create_scatter_matrix(plct_df)
    
    return radar_fig, box_fig, corr_fig, scatter_fig

@callback(
    Output("advanced-analytics-chart", "figure"),
    Input("main-tabs", "active_tab")
)
def update_advanced_analytics(active_tab):
    if active_tab != "advanced":
        return go.Figure()
    
    plct_df = fetch_plct_data()
    if plct_df.empty:
        return go.Figure()
    
    return create_correlation_heatmap(plct_df)

@callback(
    [Output("comparison-metrics", "children"),
     Output("comparison-chart", "figure")],
    [Input("company-a-select", "value"),
     Input("company-b-select", "value")]
)
def update_comparison(company_a, company_b):
    if not company_a or not company_b:
        return html.Div("Select two companies to compare"), go.Figure()
    
    df_a = fetch_company_data(company_a)
    df_b = fetch_company_data(company_b)
    
    # Metrics
    metrics_html = dbc.Row([
        dbc.Col([
            html.H5(company_a, className="text-primary"),
            html.P(f"Total Initiatives: {len(df_a)}"),
            html.P(f"Categories: {df_a['category'].nunique()}"),
            html.P(f"Maturity: {df_a['digital_maturity_level'].mode()[0] if not df_a.empty else 'N/A'}")
        ], width=6),
        dbc.Col([
            html.H5(company_b, className="text-primary"),
            html.P(f"Total Initiatives: {len(df_b)}"),
            html.P(f"Categories: {df_b['category'].nunique()}"),
            html.P(f"Maturity: {df_b['digital_maturity_level'].mode()[0] if not df_b.empty else 'N/A'}")
        ], width=6),
    ])
    
    chart = create_comparison_charts(df_a, df_b, company_a, company_b)
    
    return metrics_html, chart

@callback(
    Output("roi-results", "children"),
    Input("calculate-roi-btn", "n_clicks"),
    [State("roi-investment", "value"),
     State("roi-period", "value"),
     State("roi-benefit", "value"),
     State("roi-cost", "value")],
    prevent_initial_call=True
)
def calculate_roi(n, investment, period, benefit, cost):
    if not all([investment, period, benefit, cost]):
        return html.Div("Please fill all fields", className="alert alert-warning")
    
    # Calculations
    net_annual_benefit = benefit - cost
    total_benefit = net_annual_benefit * (period / 12)
    roi = ((total_benefit - investment) / investment) * 100
    payback_period = investment / net_annual_benefit if net_annual_benefit > 0 else float('inf')
    
    return html.Div([
        html.Div([
            html.H4("ROI Analysis Results", className="text-white"),
            html.Div(f"{roi:.1f}%", className="result-value"),
            html.P(f"Return on Investment over {period} months")
        ], className="result-box"),
        
        dbc.Row([
            dbc.Col([
                html.H6("Net Annual Benefit"),
                html.H4(f"RM {net_annual_benefit:,.0f}", className="text-success")
            ]),
            dbc.Col([
                html.H6("Total Benefit"),
                html.H4(f"RM {total_benefit:,.0f}", className="text-primary")
            ]),
            dbc.Col([
                html.H6("Payback Period"),
                html.H4(f"{payback_period:.1f} years" if payback_period != float('inf') else "N/A", className="text-info")
            ]),
        ], className="mt-4 text-center")
    ])

@callback(
    Output("download-csv", "data"),
    Input("download-csv-btn", "n_clicks"),
    State("data-store", "data"),
    prevent_initial_call=True
)
def download_data(n, data_json):
    if not data_json:
        return None
    
    df = pd.read_json(data_json, orient='split')
    return dcc.send_data_frame(df.to_csv, "ide_dashboard_data.csv", index=False)

# Run server
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8050))
    app.run_server(debug=True, host='0.0.0.0', port=port)
