"""
IDE Digital Transformation Dashboard - Dash/Plotly Version
Modern interactive dashboard with Plotly visualizations
"""

import os
from datetime import datetime
import pymysql
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

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

# Data fetching functions
def fetch_metrics():
    """Fetch dashboard KPIs"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Total initiatives
        cursor.execute("SELECT COUNT(DISTINCT id) as count FROM initiatives")
        total_initiatives = cursor.fetchone()['count']
        
        # Total companies
        cursor.execute("SELECT COUNT(DISTINCT id) as count FROM companies")
        total_companies = cursor.fetchone()['count']
        
        # Total sectors
        cursor.execute("SELECT COUNT(DISTINCT company_sector) as count FROM companies WHERE company_sector IS NOT NULL")
        total_sectors = cursor.fetchone()['count']
        
        # Total categories
        cursor.execute("SELECT COUNT(DISTINCT category) as count FROM initiatives WHERE category IS NOT NULL")
        total_categories = cursor.fetchone()['count']
        
        # Total technologies
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

def fetch_initiatives(limit=100, search='', sector='', category=''):
    """Fetch initiatives with filters"""
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

def fetch_sector_distribution():
    """Fetch sector distribution data"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.company_sector as sector, COUNT(DISTINCT i.id) as initiative_count
            FROM companies c
            LEFT JOIN initiatives i ON c.id = i.company_id
            WHERE c.company_sector IS NOT NULL
            GROUP BY c.company_sector
            ORDER BY initiative_count DESC
        """)
        return cursor.fetchall()
    finally:
        conn.close()

def fetch_yearly_trend():
    """Fetch yearly trend data"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.year_mentioned as year, COUNT(DISTINCT i.id) as count
            FROM companies c
            LEFT JOIN initiatives i ON c.id = i.company_id
            WHERE c.year_mentioned IS NOT NULL
            GROUP BY c.year_mentioned
            ORDER BY c.year_mentioned
        """)
        return cursor.fetchall()
    finally:
        conn.close()

def fetch_top_technologies(limit=20):
    """Fetch top technologies"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.technology_used as technology, COUNT(DISTINCT i.id) as count
            FROM companies c
            LEFT JOIN initiatives i ON c.id = i.company_id
            WHERE c.technology_used IS NOT NULL AND c.technology_used != ''
            GROUP BY c.technology_used
            ORDER BY count DESC
            LIMIT %s
        """, (limit,))
        return cursor.fetchall()
    finally:
        conn.close()

def fetch_maturity_distribution():
    """Fetch digital maturity distribution"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.digital_maturity_level, COUNT(DISTINCT i.id) as count
            FROM companies c
            LEFT JOIN initiatives i ON c.id = i.company_id
            WHERE c.digital_maturity_level IS NOT NULL
            GROUP BY c.digital_maturity_level
            ORDER BY 
                CASE c.digital_maturity_level
                    WHEN 'Basic' THEN 1
                    WHEN 'Developing' THEN 2
                    WHEN 'Defined' THEN 3
                    WHEN 'Advanced' THEN 4
                    WHEN 'Optimized' THEN 5
                    ELSE 6
                END
        """)
        return cursor.fetchall()
    finally:
        conn.close()

def fetch_innovation_distribution():
    """Fetch innovation level distribution"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT innovation_level, COUNT(*) as count
            FROM initiatives
            WHERE innovation_level IS NOT NULL
            GROUP BY innovation_level
            ORDER BY count DESC
        """)
        return cursor.fetchall()
    finally:
        conn.close()

def fetch_category_distribution():
    """Fetch category distribution"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM initiatives
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        """)
        return cursor.fetchall()
    finally:
        conn.close()

def fetch_filter_options():
    """Fetch unique values for filters"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT company_sector FROM companies WHERE company_sector IS NOT NULL ORDER BY company_sector")
        sectors = [row['company_sector'] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT category FROM initiatives WHERE category IS NOT NULL ORDER BY category")
        categories = [row['category'] for row in cursor.fetchall()]
        
        return {'sectors': sectors, 'categories': categories}
    finally:
        conn.close()

# Initialize Dash app with Bootstrap theme
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)
app.title = "IDE Digital Transformation Dashboard"

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
            
            .tab-content {
                padding: 2rem 0;
            }
            
            .plotly-chart {
                border-radius: var(--border-radius);
                overflow: hidden;
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

# Fetch initial data
metrics = fetch_metrics()
filter_options = fetch_filter_options()

# Layout
app.layout = dbc.Container([
    # Header
    html.Div([
        html.H1("🚀 IDE Digital Transformation Dashboard", className="header-title"),
        html.P(f"Comprehensive analysis of digital initiatives • Last updated: {datetime.now().strftime('%B %d, %Y')}", 
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
    
    # Filters
    html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label("Search", html_for="search-input"),
                dbc.Input(id="search-input", type="text", placeholder="Search initiatives, companies, technologies...")
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
                            dcc.Graph(id="sector-chart", className="plotly-chart")
                        ], className="content-section")
                    ], width=12, lg=6),
                    
                    dbc.Col([
                        html.Div([
                            html.H3("📈 Yearly Trend", className="section-title"),
                            dcc.Graph(id="yearly-chart", className="plotly-chart")
                        ], className="content-section")
                    ], width=12, lg=6),
                ]),
                
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H3("🏆 Digital Maturity Levels", className="section-title"),
                            dcc.Graph(id="maturity-chart", className="plotly-chart")
                        ], className="content-section")
                    ], width=12, lg=6),
                    
                    dbc.Col([
                        html.Div([
                            html.H3("💡 Innovation Distribution", className="section-title"),
                            dcc.Graph(id="innovation-chart", className="plotly-chart")
                        ], className="content-section")
                    ], width=12, lg=6),
                ])
            ], className="tab-content")
        ], label="📊 Overview", tab_id="overview"),
        
        # Technologies Tab
        dbc.Tab([
            html.Div([
                html.Div([
                    html.H3("🔧 Top Technologies", className="section-title"),
                    dcc.Graph(id="tech-chart", className="plotly-chart")
                ], className="content-section")
            ], className="tab-content")
        ], label="🔧 Technologies", tab_id="technologies"),
        
        # Categories Tab
        dbc.Tab([
            html.Div([
                html.Div([
                    html.H3("📦 Category Distribution", className="section-title"),
                    dcc.Graph(id="category-chart", className="plotly-chart")
                ], className="content-section")
            ], className="tab-content")
        ], label="📦 Categories", tab_id="categories"),
        
        # Data Explorer Tab
        dbc.Tab([
            html.Div([
                html.Div([
                    html.H3("🔍 Initiatives Data Explorer", className="section-title"),
                    html.Div(id="data-table")
                ], className="content-section")
            ], className="tab-content")
        ], label="🔍 Data Explorer", tab_id="data"),
        
    ], id="main-tabs", active_tab="overview"),
    
], fluid=True, style={'padding': '0'})

# Callbacks
@callback(
    [Output("sector-chart", "figure"),
     Output("yearly-chart", "figure"),
     Output("maturity-chart", "figure"),
     Output("innovation-chart", "figure"),
     Output("tech-chart", "figure"),
     Output("category-chart", "figure"),
     Output("data-table", "children")],
    [Input("search-input", "value"),
     Input("sector-filter", "value"),
     Input("category-filter", "value")]
)
def update_dashboard(search, sector, category):
    """Update all dashboard components"""
    
    # Sector Distribution
    sector_data = fetch_sector_distribution()
    df_sector = pd.DataFrame(sector_data)
    fig_sector = px.bar(
        df_sector, 
        x='initiative_count', 
        y='sector',
        orientation='h',
        title=None,
        labels={'initiative_count': 'Number of Initiatives', 'sector': 'Sector'},
        color='initiative_count',
        color_continuous_scale='Viridis'
    )
    fig_sector.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Yearly Trend
    yearly_data = fetch_yearly_trend()
    df_yearly = pd.DataFrame(yearly_data)
    fig_yearly = px.line(
        df_yearly,
        x='year',
        y='count',
        title=None,
        labels={'year': 'Year', 'count': 'Number of Initiatives'},
        markers=True
    )
    fig_yearly.update_traces(
        line_color='#667eea',
        line_width=3,
        marker=dict(size=8)
    )
    fig_yearly.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    
    # Maturity Distribution
    maturity_data = fetch_maturity_distribution()
    df_maturity = pd.DataFrame(maturity_data)
    fig_maturity = px.pie(
        df_maturity,
        values='count',
        names='digital_maturity_level',
        title=None,
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig_maturity.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    # Innovation Distribution
    innovation_data = fetch_innovation_distribution()
    df_innovation = pd.DataFrame(innovation_data)
    fig_innovation = px.bar(
        df_innovation,
        x='innovation_level',
        y='count',
        title=None,
        labels={'innovation_level': 'Innovation Level', 'count': 'Number of Initiatives'},
        color='count',
        color_continuous_scale='Plasma'
    )
    fig_innovation.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Technologies
    tech_data = fetch_top_technologies(20)
    df_tech = pd.DataFrame(tech_data)
    fig_tech = px.bar(
        df_tech,
        x='count',
        y='technology',
        orientation='h',
        title=None,
        labels={'count': 'Usage Count', 'technology': 'Technology'},
        color='count',
        color_continuous_scale='Turbo'
    )
    fig_tech.update_layout(
        showlegend=False,
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Categories
    category_data = fetch_category_distribution()
    df_category = pd.DataFrame(category_data)
    fig_category = px.treemap(
        df_category,
        path=['category'],
        values='count',
        title=None,
        color='count',
        color_continuous_scale='Viridis'
    )
    fig_category.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    # Data Table
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
    
    return fig_sector, fig_yearly, fig_maturity, fig_innovation, fig_tech, fig_category, table

# Run server
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8050))
    app.run_server(debug=True, host='0.0.0.0', port=port)
