"""
Malaysian Digital Transformation Research Dashboard
Streamlit Implementation - All Visualizations
Based on LOOKER_STUDIO_VISUALIZATION_GUIDE.md
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import mysql.connector
import os
from dotenv import load_dotenv
from io import BytesIO

# Page config
st.set_page_config(
    page_title="Malaysian Digital Transformation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv(override=True)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1A73E8;
    }
    h1 {
        color: #1A73E8;
        padding-bottom: 10px;
        border-bottom: 3px solid #1A73E8;
    }
    h2 {
        color: #34A853;
        margin-top: 30px;
    }
    .plot-container {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Database connection
def get_db_connection():
    """Create a new database connection"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=int(os.getenv('MYSQL_PORT')),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            connect_timeout=10
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        st.info("Please check if MySQL server is running: `brew services start mysql`")
        raise

# Data loading functions
@st.cache_data(ttl=3600)
def load_company_overview():
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            id, company_name, stock_code, company_sector,
            first_year_mentioned, last_year_mentioned, total_reports,
            (last_year_mentioned - first_year_mentioned + 1) as years_active
        FROM unique_companies
        ORDER BY company_name
        """
        df = pd.read_sql(query, conn)
        
        # Normalize sector names
        df['company_sector'] = df['company_sector'].apply(normalize_sector)
        
        # Filter out None values (unclassifiable sectors)
        df = df[df['company_sector'].notna()]
        
        return df
    finally:
        conn.close()

def normalize_sector(sector):
    """Normalize sector names to standard 12 categories"""
    if pd.isna(sector) or str(sector).strip() == '':
        return None  # Will be filtered out
    
    sector_upper = str(sector).upper().strip()
    
    # Direct exact matches for the 12 standard sectors
    standard_sectors = {
        'INDUSTRIAL PRODUCTS AND SERVICES',
        'CONSUMER PRODUCTS AND SERVICES',
        'TELECOMMUNICATIONS AND MEDIA',
        'TRANSPORTATION AND LOGISTICS',
        'HEALTH CARE',
        'FINANCIAL SERVICES',
        'CONSTRUCTION',
        'TECHNOLOGY',
        'PROPERTY',
        'PLANTATION',
        'ENERGY',
        'UTILITIES'
    }
    
    if sector_upper in standard_sectors:
        return sector_upper
    
    # Variant mappings with comprehensive patterns
    if any(term in sector_upper for term in ['INDUSTRIAL PRODUCTS', 'INDUSTRIAL PRODUCT', 'MANUFACTUR', 'BUILDING MATERIALS', 'TOOLS AND EQUIPMENT']):
        return 'INDUSTRIAL PRODUCTS AND SERVICES'
    
    if any(term in sector_upper for term in ['CONSUMER PRODUCTS', 'CONSUMER PRODUCT', 'BUSINESS SERVICE', 'RETAIL', 'FOOD', 'BEVERAGE', 'HOSPITAL', 'LEISURE', 'TRADING']):
        return 'CONSUMER PRODUCTS AND SERVICES'
    
    if any(term in sector_upper for term in ['TELECOMMUNICATION', 'MEDIA']):
        return 'TELECOMMUNICATIONS AND MEDIA'
    
    if any(term in sector_upper for term in ['TRANSPORTATION', 'TRANSPORT', 'LOGISTICS']):
        return 'TRANSPORTATION AND LOGISTICS'
    
    if any(term in sector_upper for term in ['HEALTHCARE', 'HEALTH CARE', 'HEALTH']):
        return 'HEALTH CARE'
    
    if any(term in sector_upper for term in ['FINANCIAL', 'FINANCE', 'INVESTMENT', 'HOLDING']):
        return 'FINANCIAL SERVICES'
    
    if 'CONSTRUCTION' in sector_upper or 'ENGINEERING' in sector_upper:
        return 'CONSTRUCTION'
    
    if 'TECHNOLOGY' in sector_upper or 'TECH ' in sector_upper:
        return 'TECHNOLOGY'
    
    if 'PROPERTY' in sector_upper or 'REAL ESTATE' in sector_upper:
        return 'PROPERTY'
    
    if 'PLANTATION' in sector_upper or 'AGRICULTURE' in sector_upper:
        return 'PLANTATION'
    
    if any(term in sector_upper for term in ['ENERGY', 'MINING', 'PETROLEUM', 'OIL', 'GAS']):
        return 'ENERGY'
    
    if 'UTILIT' in sector_upper or 'ELECTRIC' in sector_upper:
        return 'UTILITIES'
    
    # Unclassifiable sectors - return None to be filtered
    return None

@st.cache_data(ttl=3600)
def load_sector_analysis():
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            company_sector,
            COUNT(DISTINCT company_name) as total_companies,
            SUM(total_reports) as total_reports,
            MIN(first_year_mentioned) as earliest_year,
            MAX(last_year_mentioned) as latest_year
        FROM unique_companies
        WHERE company_sector IS NOT NULL
        GROUP BY company_sector
        ORDER BY total_companies DESC
        """
        df = pd.read_sql(query, conn)
        
        # Normalize sector names
        df['company_sector'] = df['company_sector'].apply(normalize_sector)
        
        # Filter out None values (unclassifiable sectors)
        df = df[df['company_sector'].notna()]
        
        # Re-aggregate after normalization
        df = df.groupby('company_sector').agg({
            'total_companies': 'sum',
            'total_reports': 'sum',
            'earliest_year': 'min',
            'latest_year': 'max'
        }).reset_index()
        
        df = df.sort_values('total_companies', ascending=False)
        
        return df
    finally:
        conn.close()

@st.cache_data(ttl=3600)
def load_initiatives_data():
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            c.company_name, c.stock_code, c.company_sector, c.year_mentioned,
            i.category, i.innovation_level,
            i.plct_customer_experience_score, i.plct_people_empowerment_score,
            i.plct_operational_efficiency_score, i.plct_new_business_models_score,
            i.plct_total_score, i.plct_dominant_dimension,
            i.disclosure_quality_total_score, i.disclosure_quality_tier,
            i.confidence_level
        FROM initiatives i
        JOIN companies c ON i.company_id = c.id
        """
        df = pd.read_sql(query, conn)
        
        # Normalize disclosure_quality_tier
        def normalize_tier(tier):
            if pd.isna(tier):
                return 'Unknown'
            tier_lower = str(tier).lower()
            if 'comprehensive' in tier_lower or '80-100' in tier_lower:
                return 'Tier 1 - Excellent'
            elif 'good' in tier_lower or '60-79' in tier_lower:
                return 'Tier 2 - Good'
            elif 'moderate' in tier_lower or '40-59' in tier_lower:
                return 'Tier 3 - Fair'
            else:
                return 'Tier 4 - Limited'
        
        df['disclosure_quality_tier'] = df['disclosure_quality_tier'].apply(normalize_tier)
        
        # Normalize confidence_level
        def normalize_confidence(confidence):
            if pd.isna(confidence):
                return 'Unknown'
            conf_lower = str(confidence).lower().strip()
            if 'high' in conf_lower:
                return 'High'
            elif 'medium' in conf_lower or 'moderate' in conf_lower:
                return 'Medium'
            elif 'low' in conf_lower:
                return 'Low'
            else:
                return 'Unknown'
        
        df['confidence_level'] = df['confidence_level'].apply(normalize_confidence)
        
        # Normalize sector names
        df['company_sector'] = df['company_sector'].apply(normalize_sector)
        
        # Filter out None values (unclassifiable sectors)
        df = df[df['company_sector'].notna()]
        
        return df
    finally:
        conn.close()

@st.cache_data(ttl=3600)
def load_company_ranking():
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            c.company_name, c.stock_code, c.company_sector,
            uc.total_reports, COUNT(i.id) as total_initiatives,
            ROUND(AVG(i.plct_total_score), 2) as avg_plct_score,
            ROUND(AVG(i.disclosure_quality_total_score), 2) as avg_disclosure_score,
            COUNT(CASE WHEN i.innovation_level = 'High' THEN 1 END) as high_innovation_count,
            COUNT(CASE WHEN i.disclosure_quality_tier = 'Tier 1 - Excellent' THEN 1 END) as excellent_disclosure_count
        FROM companies c
        JOIN unique_companies uc ON c.company_name = uc.company_name
        LEFT JOIN initiatives i ON c.id = i.company_id
        GROUP BY c.company_name, c.stock_code, c.company_sector, uc.total_reports
        HAVING total_initiatives > 0
        ORDER BY avg_plct_score DESC
        """
        df = pd.read_sql(query, conn)
        
        # Normalize sector names
        df['company_sector'] = df['company_sector'].apply(normalize_sector)
        
        # Filter out None values (unclassifiable sectors)
        df = df[df['company_sector'].notna()]
        
        return df
    finally:
        conn.close()

@st.cache_data(ttl=3600)
def load_yearly_trends():
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            c.year_mentioned, c.company_sector,
            COUNT(DISTINCT c.company_name) as company_count,
            COUNT(i.id) as initiative_count,
            ROUND(AVG(i.plct_total_score), 2) as avg_plct_score,
            ROUND(AVG(i.disclosure_quality_total_score), 2) as avg_disclosure_score
        FROM companies c
        LEFT JOIN initiatives i ON c.id = i.company_id
        WHERE c.year_mentioned IS NOT NULL
        GROUP BY c.year_mentioned, c.company_sector
        ORDER BY c.year_mentioned, c.company_sector
        """
        df = pd.read_sql(query, conn)
        
        # Normalize sector names
        df['company_sector'] = df['company_sector'].apply(normalize_sector)
        
        # Filter out None values (unclassifiable sectors)
        df = df[df['company_sector'].notna()]
        
        # Re-aggregate after normalization
        df = df.groupby(['year_mentioned', 'company_sector']).agg({
            'company_count': 'sum',
            'initiative_count': 'sum',
            'avg_plct_score': 'mean',
            'avg_disclosure_score': 'mean'
        }).reset_index()
        
        return df
    finally:
        conn.close()

@st.cache_data(ttl=3600)
def load_technology_categories():
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            category,
            COUNT(*) as initiative_count,
            COUNT(DISTINCT c.company_name) as company_count,
            ROUND(AVG(i.plct_total_score), 2) as avg_plct_score,
            ROUND(AVG(i.disclosure_quality_total_score), 2) as avg_disclosure_score
        FROM initiatives i
        JOIN companies c ON i.company_id = c.id
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY initiative_count DESC
        """
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1A73E8/FFFFFF?text=MY+Digital+Transformation", use_column_width=True)
    st.title("📊 Navigation")
    
    page = st.radio(
        "Select Page",
        ["🏠 Executive Overview", 
         "🏢 Sector Analysis", 
         "🏆 Company Performance",
         "🎯 PLCT Strategic Analysis",
         "💡 Technology Trends",
         "📋 Disclosure Quality"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Global filters
    st.subheader("🔍 Global Filters")
    
    # Load data for filters
    try:
        companies_df = load_company_overview()
        
        # Year filter
        year_range = st.slider(
            "Year Range",
            min_value=int(companies_df['first_year_mentioned'].min()),
            max_value=int(companies_df['last_year_mentioned'].max()),
            value=(int(companies_df['first_year_mentioned'].min()), 
                   int(companies_df['last_year_mentioned'].max()))
        )
        
        # Sector filter - prioritize the 12 main sectors
        all_sectors = sorted(companies_df['company_sector'].dropna().unique())
        
        # Define the 12 standard sectors for default selection
        standard_sectors = [
            'CONSUMER PRODUCTS AND SERVICES',
            'CONSTRUCTION',
            'ENERGY',
            'FINANCIAL SERVICES',
            'HEALTH CARE',
            'INDUSTRIAL PRODUCTS AND SERVICES',
            'PLANTATION',
            'PROPERTY',
            'TECHNOLOGY',
            'TELECOMMUNICATIONS AND MEDIA',
            'TRANSPORTATION AND LOGISTICS',
            'UTILITIES'
        ]
        
        # Use standard sectors that exist in the data, otherwise use all sectors
        default_sectors = [s for s in standard_sectors if s in all_sectors]
        if not default_sectors:
            default_sectors = all_sectors[:5] if len(all_sectors) > 5 else all_sectors
        
        selected_sectors = st.multiselect(
            "Sectors",
            options=all_sectors,
            default=default_sectors
        )
        
        # Company search
        company_search = st.text_input("🔎 Search Company", "")
        
    except Exception as e:
        st.error(f"Error loading filters: {str(e)}")
        year_range = (2020, 2024)
        selected_sectors = []
        company_search = ""
    
    st.divider()
    st.caption("Data last updated: January 26, 2026")

# Main content
if page == "🏠 Executive Overview":
    st.title("📈 Executive Overview")
    st.markdown("*High-level summary for executives and stakeholders*")
    
    try:
        companies_df = load_company_overview()
        sector_df = load_sector_analysis()
        yearly_df = load_yearly_trends()
        ranking_df = load_company_ranking()
        
        # Apply filters
        if selected_sectors:
            companies_df = companies_df[companies_df['company_sector'].isin(selected_sectors)]
            sector_df = sector_df[sector_df['company_sector'].isin(selected_sectors)]
        
        # Key Metrics Scorecard
        st.subheader("📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Companies", f"{len(companies_df):,}", delta=None)
        with col2:
            st.metric("Active Sectors", f"{companies_df['company_sector'].nunique()}", delta=None)
        with col3:
            st.metric("Total Reports", f"{companies_df['total_reports'].sum():,}", delta=None)
        with col4:
            st.metric("Avg Reports/Company", f"{companies_df['total_reports'].mean():.1f}", delta=None)
        
        st.divider()
        
        # Charts row 1
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🏢 Companies by Sector (Top 10)")
            top_sectors = sector_df.nlargest(10, 'total_companies')
            fig = px.bar(
                top_sectors,
                y='company_sector',
                x='total_companies',
                orientation='h',
                title="",
                color='total_companies',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                showlegend=False,
                xaxis_title="Number of Companies",
                yaxis_title="Sector",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Sector Distribution")
            top_8_sectors = sector_df.nlargest(8, 'total_companies')
            others = pd.DataFrame([{
                'company_sector': 'Others',
                'total_companies': sector_df.iloc[8:]['total_companies'].sum()
            }])
            pie_data = pd.concat([top_8_sectors[['company_sector', 'total_companies']], others])
            
            fig = px.pie(
                pie_data,
                names='company_sector',
                values='total_companies',
                title="",
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Yearly Activity Trend
        st.subheader("📈 Yearly Activity Trend")
        yearly_agg = yearly_df.groupby('year_mentioned').agg({
            'company_count': 'sum',
            'initiative_count': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly_agg['year_mentioned'],
            y=yearly_agg['company_count'],
            name='Companies',
            mode='lines+markers',
            line=dict(color='#1A73E8', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=yearly_agg['year_mentioned'],
            y=yearly_agg['initiative_count'],
            name='Initiatives',
            mode='lines+markers',
            line=dict(color='#34A853', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Number of Companies",
            yaxis2=dict(title="Number of Initiatives", overlaying='y', side='right'),
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent Activity Table
        st.subheader("🏆 Top Performing Companies")
        display_df = ranking_df.head(15)[['company_name', 'company_sector', 'total_initiatives', 
                                          'avg_plct_score', 'avg_disclosure_score']]
        
        # Add styling
        def color_plct_score(val):
            if pd.isna(val):
                return ''
            color = 'green' if val >= 8 else 'orange' if val >= 5 else 'red'
            return f'background-color: {color}; color: white'
        
        styled_df = display_df.style.map(color_plct_score, subset=['avg_plct_score'])
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Excel export button
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            display_df.to_excel(writer, index=False, sheet_name='Top Performing Companies')
        buffer.seek(0)
        st.download_button(
            label="📥 Download as Excel",
            data=buffer,
            file_name="top_performing_companies.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.divider()
        
        # Performance Summary Metrics
        st.subheader("📊 Performance Summary")
        initiatives_df = load_initiatives_data()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            avg_plct = initiatives_df['plct_total_score'].mean()
            st.metric("Avg PLCT Score", f"{avg_plct:.1f}", delta=None)
        with col2:
            avg_disclosure = initiatives_df['disclosure_quality_total_score'].mean()
            st.metric("Avg Disclosure Score", f"{avg_disclosure:.1f}", delta=None)
        with col3:
            high_innovation = (initiatives_df['innovation_level'] == 'High').sum()
            st.metric("High Innovation Count", f"{high_innovation:,}", delta=None)
        with col4:
            total_initiatives = len(initiatives_df)
            st.metric("Total Initiatives", f"{total_initiatives:,}", delta=None)
        with col5:
            avg_confidence = initiatives_df[initiatives_df['confidence_level'] != 'Unknown']['confidence_level'].value_counts(normalize=True).get('High', 0) * 100
            st.metric("High Confidence %", f"{avg_confidence:.1f}%", delta=None)
        
        st.divider()
        
        # PLCT Dimensions Overview
        st.subheader("🎯 PLCT Dimensions Performance")
        col1, col2 = st.columns(2)
        
        with col1:
            dimension_data = pd.DataFrame({
                'Dimension': ['Customer Experience', 'People Empowerment', 'Operational Efficiency', 'New Business Models'],
                'Average Score': [
                    initiatives_df['plct_customer_experience_score'].mean(),
                    initiatives_df['plct_people_empowerment_score'].mean(),
                    initiatives_df['plct_operational_efficiency_score'].mean(),
                    initiatives_df['plct_new_business_models_score'].mean()
                ]
            })
            
            fig = px.bar(
                dimension_data,
                x='Dimension',
                y='Average Score',
                title="Average Score by PLCT Dimension",
                color='Average Score',
                color_continuous_scale='RdYlGn',
                text='Average Score'
            )
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig.update_layout(height=350, xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Dominant dimension distribution
            dominant_counts = initiatives_df['plct_dominant_dimension'].value_counts()
            
            fig = px.pie(
                values=dominant_counts.values,
                names=dominant_counts.index,
                title="Dominant PLCT Dimension Distribution",
                hole=0.4
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Innovation and Disclosure Quality
        st.subheader("💡 Innovation & Quality Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            innovation_counts = initiatives_df['innovation_level'].value_counts()
            
            fig = px.bar(
                x=innovation_counts.index,
                y=innovation_counts.values,
                title="Innovation Level Distribution",
                color=innovation_counts.values,
                color_continuous_scale='Oranges',
                labels={'x': 'Innovation Level', 'y': 'Count'},
                text=innovation_counts.values
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            disclosure_tier_counts = initiatives_df['disclosure_quality_tier'].value_counts()
            
            fig = px.pie(
                values=disclosure_tier_counts.values,
                names=disclosure_tier_counts.index,
                title="Disclosure Quality Tier Distribution",
                hole=0.4,
                color_discrete_sequence=['#34A853', '#FBBC04', '#FF9800', '#EA4335']
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Sector PLCT Comparison
        st.subheader("🏢 Sector PLCT Performance Comparison")
        sector_plct = initiatives_df.groupby('company_sector')['plct_total_score'].mean().nlargest(12).reset_index()
        sector_plct.columns = ['Sector', 'Avg PLCT Score']
        
        fig = px.bar(
            sector_plct,
            x='Sector',
            y='Avg PLCT Score',
            title="Top 12 Sectors by Average PLCT Score",
            color='Avg PLCT Score',
            color_continuous_scale='Viridis',
            text='Avg PLCT Score'
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Technology Adoption Overview
        st.subheader("💻 Technology Adoption Snapshot")
        tech_df = load_technology_categories()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Technology Categories", len(tech_df), delta=None)
        with col2:
            top_tech = tech_df.loc[tech_df['initiative_count'].idxmax(), 'category']
            st.metric("Most Adopted Technology", top_tech[:30] + "..." if len(top_tech) > 30 else top_tech, delta=None)
        with col3:
            avg_tech_per_company = tech_df['company_count'].mean()
            st.metric("Avg Companies per Tech", f"{avg_tech_per_company:.1f}", delta=None)
        
        # Top 10 Technologies
        top_10_tech = tech_df.nlargest(10, 'initiative_count')
        
        fig = px.bar(
            top_10_tech,
            y='category',
            x='initiative_count',
            orientation='h',
            title="Top 10 Technology Categories",
            color='initiative_count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, showlegend=False, yaxis_title="", xaxis_title="Number of Initiatives")
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Year-over-Year Growth
        st.subheader("📊 Year-over-Year Growth Analysis")
        
        yearly_growth = yearly_agg.copy()
        yearly_growth['company_growth'] = yearly_growth['company_count'].pct_change() * 100
        yearly_growth['initiative_growth'] = yearly_growth['initiative_count'].pct_change() * 100
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=yearly_growth['year_mentioned'],
            y=yearly_growth['company_growth'],
            name='Company Growth %',
            marker_color='#1A73E8'
        ))
        fig.add_trace(go.Bar(
            x=yearly_growth['year_mentioned'],
            y=yearly_growth['initiative_growth'],
            name='Initiative Growth %',
            marker_color='#34A853'
        ))
        
        fig.update_layout(
            title="Year-over-Year Growth Rate (%)",
            xaxis_title="Year",
            yaxis_title="Growth Rate (%)",
            barmode='group',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Executive Summary Statistics
        st.subheader("📋 Executive Summary Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Key Achievements")
            st.markdown(f"- **{len(companies_df):,}** companies analyzed across **{companies_df['company_sector'].nunique()}** sectors")
            st.markdown(f"- **{total_initiatives:,}** digital transformation initiatives documented")
            st.markdown(f"- **{high_innovation:,}** high-innovation initiatives identified")
            st.markdown(f"- Average PLCT maturity score of **{avg_plct:.1f}** out of 400")
            st.markdown(f"- **{(initiatives_df['disclosure_quality_tier'] == 'Tier 1 - Excellent').sum():,}** initiatives with excellent disclosure quality")
        
        with col2:
            st.markdown("### 🏆 Top Performers")
            top_5_companies = ranking_df.nlargest(5, 'avg_plct_score')
            for idx, row in top_5_companies.iterrows():
                st.markdown(f"**{idx+1}. {row['company_name']}** ({row['company_sector']}) - PLCT: {row['avg_plct_score']:.1f}")
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.exception(e)

elif page == "🏢 Sector Analysis":
    st.title("🏢 Sector Analysis")
    st.markdown("*Deep dive into industry sectors*")
    
    try:
        sector_df = load_sector_analysis()
        yearly_df = load_yearly_trends()
        initiatives_df = load_initiatives_data()
        
        # Apply filters
        if selected_sectors:
            sector_df = sector_df[sector_df['company_sector'].isin(selected_sectors)]
        
        # Overview metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sectors", len(sector_df))
        with col2:
            st.metric("Avg Companies/Sector", f"{sector_df['total_companies'].mean():.1f}")
        with col3:
            st.metric("Total Reports", f"{sector_df['total_reports'].sum():,}")
        
        st.divider()
        
        # Treemap
        st.subheader("🗺️ Sector Landscape (Treemap)")
        fig = px.treemap(
            sector_df,
            path=['company_sector'],
            values='total_companies',
            color='total_reports',
            color_continuous_scale='Viridis',
            title=""
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Sector Performance Matrix
        st.subheader("📊 Sector Performance Matrix")
        st.dataframe(
            sector_df.style.background_gradient(subset=['total_companies'], cmap='Blues'),
            use_container_width=True,
            height=400
        )
        
        # Excel export button
        buffer2 = BytesIO()
        with pd.ExcelWriter(buffer2, engine='openpyxl') as writer:
            sector_df.to_excel(writer, index=False, sheet_name='Sector Performance Matrix')
        buffer2.seek(0)
        st.download_button(
            label="📥 Download as Excel",
            data=buffer2,
            file_name="sector_performance_matrix.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Sector Timeline
        st.subheader("📈 Sector Timeline (Top 10)")
        top_sectors = sector_df.nlargest(10, 'total_companies')['company_sector'].tolist()
        timeline_data = yearly_df[yearly_df['company_sector'].isin(top_sectors)]
        
        fig = px.area(
            timeline_data,
            x='year_mentioned',
            y='company_count',
            color='company_sector',
            title=""
        )
        fig.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Sector Growth Analysis
        st.subheader("📊 Sector Growth Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            # Companies per sector - horizontal bar
            top_12 = sector_df.nlargest(12, 'total_companies')
            fig = px.bar(
                top_12,
                y='company_sector',
                x='total_companies',
                orientation='h',
                title="Top 12 Sectors by Company Count",
                color='total_companies',
                color_continuous_scale='Blues',
                text='total_companies'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=450, yaxis_title="", xaxis_title="Number of Companies")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Reports per sector - horizontal bar
            top_12_reports = sector_df.nlargest(12, 'total_reports')
            fig = px.bar(
                top_12_reports,
                y='company_sector',
                x='total_reports',
                orientation='h',
                title="Top 12 Sectors by Report Volume",
                color='total_reports',
                color_continuous_scale='Greens',
                text='total_reports'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=450, yaxis_title="", xaxis_title="Number of Reports")
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Sector PLCT Performance
        st.subheader("🎯 Sector PLCT Performance Comparison")
        sector_plct = initiatives_df.groupby('company_sector').agg({
            'plct_total_score': 'mean',
            'plct_customer_experience_score': 'mean',
            'plct_people_empowerment_score': 'mean',
            'plct_operational_efficiency_score': 'mean',
            'plct_new_business_models_score': 'mean'
        }).reset_index()
        sector_plct = sector_plct.sort_values('plct_total_score', ascending=False).head(12)
        
        fig = px.bar(
            sector_plct,
            x='company_sector',
            y='plct_total_score',
            title="Average PLCT Score by Sector (Top 12)",
            color='plct_total_score',
            color_continuous_scale='RdYlGn',
            text='plct_total_score'
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(height=450, xaxis_tickangle=-45, xaxis_title="", yaxis_title="Avg PLCT Score")
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Sector Innovation & Disclosure Analysis
        st.subheader("💡 Sector Innovation & Disclosure Quality")
        sector_metrics = initiatives_df.groupby('company_sector').agg({
            'innovation_level': lambda x: (x == 'High').sum(),
            'disclosure_quality_total_score': 'mean',
            'company_name': 'count'
        }).reset_index()
        sector_metrics.columns = ['company_sector', 'high_innovation_count', 'avg_disclosure_score', 'initiative_count']
        sector_metrics = sector_metrics.nlargest(12, 'initiative_count')
        
        # Scatter plot: Innovation vs Disclosure
        fig = px.scatter(
            sector_metrics,
            x='avg_disclosure_score',
            y='high_innovation_count',
            size='initiative_count',
            color='company_sector',
            title="Sector Innovation Count vs Disclosure Quality",
            labels={'avg_disclosure_score': 'Avg Disclosure Score', 
                    'high_innovation_count': 'High Innovation Count',
                    'initiative_count': 'Total Initiatives'},
            hover_data=['initiative_count']
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Sector Activity Timeline - Stacked Area
        st.subheader("📅 Sector Activity Over Years (All Sectors)")
        yearly_initiatives = initiatives_df.groupby(['year_mentioned', 'company_sector']).size().reset_index(name='count')
        
        fig = px.area(
            yearly_initiatives,
            x='year_mentioned',
            y='count',
            color='company_sector',
            title="Initiative Count by Sector Over Time",
            labels={'count': 'Number of Initiatives', 'year_mentioned': 'Year'}
        )
        fig.update_layout(height=500, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Sector Maturity Gauge
        st.subheader("⚡ Sector Maturity Index")
        col1, col2, col3 = st.columns(3)
        
        # Calculate maturity scores
        sector_maturity = initiatives_df.groupby('company_sector').agg({
            'plct_total_score': 'mean',
            'disclosure_quality_total_score': 'mean',
            'company_name': 'nunique'
        }).reset_index()
        sector_maturity['maturity_score'] = (
            (sector_maturity['plct_total_score'] / 305 * 100) * 0.5 +
            (sector_maturity['disclosure_quality_total_score'] / 100 * 100) * 0.3 +
            (sector_maturity['company_name'] / sector_maturity['company_name'].max() * 100) * 0.2
        )
        top_3_mature = sector_maturity.nlargest(3, 'maturity_score')
        
        for idx, (col, row) in enumerate(zip([col1, col2, col3], top_3_mature.itertuples())):
            with col:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=row.maturity_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"{row.company_sector}", 'font': {'size': 14}},
                    delta={'reference': 70},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#1f77b4" if idx == 0 else "#ff7f0e" if idx == 1 else "#2ca02c"},
                        'steps': [
                            {'range': [0, 50], 'color': "#f0f0f0"},
                            {'range': [50, 75], 'color': "#d9d9d9"},
                            {'range': [75, 100], 'color': "#bdbdbd"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 85
                        }
                    }
                ))
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Sector Comparison Table with Sparklines
        st.subheader("📋 Comprehensive Sector Comparison")
        sector_summary = initiatives_df.groupby('company_sector').agg({
            'company_name': 'nunique',
            'plct_total_score': ['mean', 'std'],
            'disclosure_quality_total_score': ['mean', 'std'],
            'innovation_level': lambda x: f"{(x == 'High').sum()}/{len(x)}"
        }).reset_index()
        sector_summary.columns = ['Sector', 'Companies', 'Avg PLCT', 'PLCT StdDev', 'Avg Disclosure', 'Disclosure StdDev', 'High Innovation']
        sector_summary = sector_summary.sort_values('Avg PLCT', ascending=False)
        
        st.dataframe(
            sector_summary.style.background_gradient(subset=['Avg PLCT'], cmap='RdYlGn')
                                .background_gradient(subset=['Avg Disclosure'], cmap='Blues')
                                .format({'Avg PLCT': '{:.1f}', 'PLCT StdDev': '{:.1f}', 
                                        'Avg Disclosure': '{:.1f}', 'Disclosure StdDev': '{:.1f}'}),
            use_container_width=True,
            height=500
        )
        
        # Excel export button
        buffer3 = BytesIO()
        with pd.ExcelWriter(buffer3, engine='openpyxl') as writer:
            sector_summary.to_excel(writer, index=False, sheet_name='Comprehensive Sector Comparison')
        buffer3.seek(0)
        st.download_button(
            label="📥 Download as Excel",
            data=buffer3,
            file_name="comprehensive_sector_comparison.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)

elif page == "🏆 Company Performance":
    st.title("🏆 Company Performance")
    st.markdown("*Company-level analysis and rankings*")
    
    try:
        ranking_df = load_company_ranking()
        
        # Apply filters
        if selected_sectors:
            ranking_df = ranking_df[ranking_df['company_sector'].isin(selected_sectors)]
        if company_search:
            ranking_df = ranking_df[ranking_df['company_name'].str.contains(company_search, case=False, na=False)]
        
        # Top Performers
        st.subheader("🥇 Top 25 Performers by PLCT Score")
        top_25 = ranking_df.nlargest(25, 'avg_plct_score')
        
        fig = px.bar(
            top_25,
            y='company_name',
            x='avg_plct_score',
            orientation='h',
            color='avg_plct_score',
            color_continuous_scale='RdYlGn',
            title=""
        )
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Innovation Leaders
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💡 Innovation Leaders")
            innovation_df = ranking_df[ranking_df['high_innovation_count'] > 0].nlargest(15, 'high_innovation_count')
            fig = px.bar(
                innovation_df,
                y='company_name',
                x='high_innovation_count',
                orientation='h',
                color='high_innovation_count',
                color_continuous_scale='Oranges',
                title=""
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Quality vs Performance")
            fig = px.scatter(
                ranking_df.head(50),
                x='avg_plct_score',
                y='avg_disclosure_score',
                size='total_initiatives',
                color='company_sector',
                hover_data=['company_name'],
                title=""
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed comparison table
        st.subheader("📋 Company Comparison Table")
        display_cols = ['company_name', 'company_sector', 'total_reports', 'total_initiatives',
                       'avg_plct_score', 'avg_disclosure_score', 'high_innovation_count']
        st.dataframe(
            ranking_df[display_cols].head(50).style.background_gradient(
                subset=['avg_plct_score', 'avg_disclosure_score'], cmap='RdYlGn'
            ),
            use_container_width=True,
            height=400
        )
        
        st.divider()
        
        # Company Activity Distribution
        st.subheader("📊 Company Activity Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            # Total initiatives distribution
            fig = px.histogram(
                ranking_df,
                x='total_initiatives',
                nbins=30,
                title="Distribution of Total Initiatives per Company",
                color_discrete_sequence=['#1f77b4'],
                labels={'total_initiatives': 'Number of Initiatives', 'count': 'Number of Companies'}
            )
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Total reports distribution
            fig = px.histogram(
                ranking_df,
                x='total_reports',
                nbins=30,
                title="Distribution of Total Reports per Company",
                color_discrete_sequence=['#2ca02c'],
                labels={'total_reports': 'Number of Reports', 'count': 'Number of Companies'}
            )
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Top Companies by Sector
        st.subheader("🏅 Top Performers by Sector")
        selected_sector_filter = st.selectbox(
            "Select Sector to View Top Companies",
            options=sorted(ranking_df['company_sector'].unique())
        )
        
        sector_companies = ranking_df[ranking_df['company_sector'] == selected_sector_filter].nlargest(10, 'avg_plct_score')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                sector_companies,
                y='company_name',
                x='avg_plct_score',
                orientation='h',
                title=f"Top 10 Companies in {selected_sector_filter} by PLCT",
                color='avg_plct_score',
                color_continuous_scale='Greens',
                text='avg_plct_score'
            )
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig.update_layout(height=400, showlegend=False, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                sector_companies,
                y='company_name',
                x='avg_disclosure_score',
                orientation='h',
                title=f"Top 10 Companies in {selected_sector_filter} by Disclosure",
                color='avg_disclosure_score',
                color_continuous_scale='Blues',
                text='avg_disclosure_score'
            )
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig.update_layout(height=400, showlegend=False, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Company Performance Quadrant Analysis
        st.subheader("🎯 Performance Quadrant Analysis")
        st.markdown("*Companies positioned by PLCT and Disclosure scores*")
        
        median_plct = ranking_df['avg_plct_score'].median()
        median_disclosure = ranking_df['avg_disclosure_score'].median()
        
        fig = px.scatter(
            ranking_df,
            x='avg_plct_score',
            y='avg_disclosure_score',
            size='total_initiatives',
            color='company_sector',
            hover_data=['company_name', 'total_reports', 'high_innovation_count'],
            title="",
            labels={'avg_plct_score': 'Average PLCT Score', 'avg_disclosure_score': 'Average Disclosure Score'}
        )
        
        # Add quadrant lines
        fig.add_hline(y=median_disclosure, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=median_plct, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add quadrant labels
        fig.add_annotation(x=median_plct * 1.15, y=median_disclosure * 1.15, text="Leaders", showarrow=False, font=dict(size=14, color="green"))
        fig.add_annotation(x=median_plct * 0.85, y=median_disclosure * 1.15, text="High Disclosure", showarrow=False, font=dict(size=14, color="blue"))
        fig.add_annotation(x=median_plct * 1.15, y=median_disclosure * 0.85, text="High PLCT", showarrow=False, font=dict(size=14, color="orange"))
        fig.add_annotation(x=median_plct * 0.85, y=median_disclosure * 0.85, text="Developing", showarrow=False, font=dict(size=14, color="gray"))
        
        fig.update_layout(height=550)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Company Excellence Scores
        st.subheader("⭐ Company Excellence Ranking")
        st.markdown("*Composite score based on PLCT, Disclosure, and Innovation*")
        
        # Calculate excellence score with safe division
        ranking_df_copy = ranking_df.copy()
        
        max_plct = ranking_df_copy['avg_plct_score'].max() if ranking_df_copy['avg_plct_score'].max() > 0 else 1
        max_disclosure = ranking_df_copy['avg_disclosure_score'].max() if ranking_df_copy['avg_disclosure_score'].max() > 0 else 1
        max_innovation = ranking_df_copy['high_innovation_count'].max() if ranking_df_copy['high_innovation_count'].max() > 0 else 1
        
        ranking_df_copy['excellence_score'] = (
            (ranking_df_copy['avg_plct_score'] / max_plct * 40) +
            (ranking_df_copy['avg_disclosure_score'] / max_disclosure * 30) +
            (ranking_df_copy['high_innovation_count'] / max_innovation * 30)
        )
        
        top_excellence = ranking_df_copy.nlargest(20, 'excellence_score')
        
        fig = px.bar(
            top_excellence,
            y='company_name',
            x='excellence_score',
            orientation='h',
            title="Top 20 Companies by Excellence Score",
            color='excellence_score',
            color_continuous_scale='Plasma',
            hover_data=['company_sector', 'avg_plct_score', 'avg_disclosure_score', 'high_innovation_count']
        )
        fig.update_traces(texttemplate='%{x:.1f}', textposition='outside')
        fig.update_layout(height=550, showlegend=False, yaxis_title="", xaxis_title="Excellence Score (0-100)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Multi-dimensional Company Comparison
        st.subheader("🔍 Multi-Dimensional Company Analysis")
        
        # Select companies for comparison
        default_companies = ranking_df.nlargest(5, 'avg_plct_score')['company_name'].tolist()
        selected_companies = st.multiselect(
            "Select up to 8 companies to compare",
            options=sorted(ranking_df['company_name'].unique()),
            default=default_companies[:5],
            max_selections=8
        )
        
        if selected_companies:
            compare_df = ranking_df[ranking_df['company_name'].isin(selected_companies)]
            
            # Parallel coordinates plot
            fig = px.parallel_coordinates(
                compare_df,
                dimensions=['avg_plct_score', 'avg_disclosure_score', 'total_initiatives', 'high_innovation_count', 'total_reports'],
                color='avg_plct_score',
                color_continuous_scale='Viridis',
                labels={
                    'avg_plct_score': 'PLCT Score',
                    'avg_disclosure_score': 'Disclosure Score',
                    'total_initiatives': 'Total Initiatives',
                    'high_innovation_count': 'High Innovation',
                    'total_reports': 'Total Reports'
                },
                title="Multi-Dimensional Company Comparison"
            )
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed comparison table for selected companies
            st.dataframe(
                compare_df[display_cols].style.background_gradient(
                    subset=['avg_plct_score', 'avg_disclosure_score'], cmap='RdYlGn'
                ),
                use_container_width=True
            )
        
        st.divider()
        
        # Company Growth Potential
        st.subheader("🚀 Company Growth Potential Matrix")
        
        # Calculate growth potential (companies with high initiatives but lower scores have room to grow)
        ranking_df_copy['growth_potential'] = (
            (ranking_df_copy['total_initiatives'] / ranking_df_copy['total_initiatives'].max() * 50) +
            ((100 - ranking_df_copy['avg_plct_score']) / 100 * 50)
        )
        
        high_potential = ranking_df_copy[ranking_df_copy['total_initiatives'] >= 5].nlargest(15, 'growth_potential')
        
        fig = px.scatter(
            high_potential,
            x='total_initiatives',
            y='avg_plct_score',
            size='growth_potential',
            color='company_sector',
            text='company_name',
            title="Growth Potential: High Activity Companies with Room for Improvement",
            labels={'total_initiatives': 'Total Initiatives', 'avg_plct_score': 'Average PLCT Score'}
        )
        fig.update_traces(textposition='top center', textfont_size=8)
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)

elif page == "🎯 PLCT Strategic Analysis":
    st.title("🎯 PLCT Strategic Analysis")
    st.markdown("*Digital transformation maturity assessment*")
    
    try:
        initiatives_df = load_initiatives_data()
        
        # Apply filters
        if selected_sectors:
            initiatives_df = initiatives_df[initiatives_df['company_sector'].isin(selected_sectors)]
        
        # PLCT Dimension Overview
        st.subheader("📊 PLCT Dimension Averages")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            avg_ce = initiatives_df['plct_customer_experience_score'].mean()
            st.metric("Customer Experience", f"{avg_ce:.2f}")
        with col2:
            avg_pe = initiatives_df['plct_people_empowerment_score'].mean()
            st.metric("People Empowerment", f"{avg_pe:.2f}")
        with col3:
            avg_oe = initiatives_df['plct_operational_efficiency_score'].mean()
            st.metric("Operational Efficiency", f"{avg_oe:.2f}")
        with col4:
            avg_nb = initiatives_df['plct_new_business_models_score'].mean()
            st.metric("New Business Models", f"{avg_nb:.2f}")
        with col5:
            avg_total = initiatives_df['plct_total_score'].mean()
            st.metric("Overall PLCT", f"{avg_total:.2f}")
        
        st.divider()
        
        # PLCT by Sector
        st.subheader("📊 PLCT Dimensions by Sector (Top 10)")
        plct_by_sector = initiatives_df.groupby('company_sector').agg({
            'plct_customer_experience_score': 'mean',
            'plct_people_empowerment_score': 'mean',
            'plct_operational_efficiency_score': 'mean',
            'plct_new_business_models_score': 'mean'
        }).reset_index()
        
        top_10_sectors = initiatives_df.groupby('company_sector').size().nlargest(10).index
        plct_by_sector = plct_by_sector[plct_by_sector['company_sector'].isin(top_10_sectors)]
        
        fig = go.Figure()
        dimensions = [
            ('plct_customer_experience_score', 'Customer Experience', '#1A73E8'),
            ('plct_people_empowerment_score', 'People Empowerment', '#34A853'),
            ('plct_operational_efficiency_score', 'Operational Efficiency', '#FBBC04'),
            ('plct_new_business_models_score', 'New Business Models', '#EA4335')
        ]
        
        for col, name, color in dimensions:
            fig.add_trace(go.Bar(
                name=name,
                x=plct_by_sector['company_sector'],
                y=plct_by_sector[col],
                marker_color=color
            ))
        
        fig.update_layout(
            barmode='group',
            height=500,
            xaxis_tickangle=-45,
            yaxis_title="Average Score"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # PLCT Score Categories
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 PLCT Score Distribution")
            
            def categorize_plct(score):
                if pd.isna(score):
                    return 'Unknown'
                # PLCT scores: sum of 4 dimensions (each 0-100), total range 0-400
                # Observed range: 40-305, max possible ~350
                # Categorize based on actual distribution
                if score >= 240:
                    return 'Excellent (≥240)'
                elif score >= 180:
                    return 'Good (180-239)'
                elif score >= 120:
                    return 'Average (120-179)'
                else:
                    return 'Below Average (<120)'
            
            initiatives_df['plct_category'] = initiatives_df['plct_total_score'].apply(categorize_plct)
            category_counts = initiatives_df['plct_category'].value_counts()
            
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="",
                hole=0.4,
                color_discrete_sequence=['#34A853', '#FBBC04', '#EA4335', '#9AA0A6']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎨 Dominant Dimension Analysis")
            dominant_counts = initiatives_df['plct_dominant_dimension'].value_counts()
            
            fig = px.bar(
                x=dominant_counts.index,
                y=dominant_counts.values,
                title="",
                color=dominant_counts.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                xaxis_title="Dominant Dimension",
                yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # PLCT Dimension Comparison by Year
        st.subheader("📈 PLCT Dimensions Evolution Over Time")
        plct_by_year = initiatives_df.groupby('year_mentioned').agg({
            'plct_customer_experience_score': 'mean',
            'plct_people_empowerment_score': 'mean',
            'plct_operational_efficiency_score': 'mean',
            'plct_new_business_models_score': 'mean',
            'plct_total_score': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=plct_by_year['year_mentioned'], y=plct_by_year['plct_customer_experience_score'],
                                 mode='lines+markers', name='Customer Experience', line=dict(color='#1A73E8', width=3)))
        fig.add_trace(go.Scatter(x=plct_by_year['year_mentioned'], y=plct_by_year['plct_people_empowerment_score'],
                                 mode='lines+markers', name='People Empowerment', line=dict(color='#34A853', width=3)))
        fig.add_trace(go.Scatter(x=plct_by_year['year_mentioned'], y=plct_by_year['plct_operational_efficiency_score'],
                                 mode='lines+markers', name='Operational Efficiency', line=dict(color='#FBBC04', width=3)))
        fig.add_trace(go.Scatter(x=plct_by_year['year_mentioned'], y=plct_by_year['plct_new_business_models_score'],
                                 mode='lines+markers', name='New Business Models', line=dict(color='#EA4335', width=3)))
        
        fig.update_layout(height=450, xaxis_title="Year", yaxis_title="Average Score", hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # PLCT Heatmap by Sector and Dimension
        st.subheader("🔥 PLCT Heatmap: Sector Performance Matrix")
        heatmap_data = initiatives_df.groupby('company_sector').agg({
            'plct_customer_experience_score': 'mean',
            'plct_people_empowerment_score': 'mean',
            'plct_operational_efficiency_score': 'mean',
            'plct_new_business_models_score': 'mean'
        }).reset_index()
        
        # Get top 12 sectors by initiative count
        top_sectors = initiatives_df['company_sector'].value_counts().head(12).index
        heatmap_data = heatmap_data[heatmap_data['company_sector'].isin(top_sectors)]
        
        heatmap_matrix = heatmap_data.set_index('company_sector')[
            ['plct_customer_experience_score', 'plct_people_empowerment_score', 
             'plct_operational_efficiency_score', 'plct_new_business_models_score']
        ]
        heatmap_matrix.columns = ['Customer Exp.', 'People Emp.', 'Operational Eff.', 'New Business']
        
        fig = px.imshow(
            heatmap_matrix.T,
            labels=dict(x="Sector", y="PLCT Dimension", color="Score"),
            x=heatmap_matrix.index,
            y=heatmap_matrix.columns,
            color_continuous_scale='RdYlGn',
            aspect="auto"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # PLCT Radar Chart - Top 5 Sectors
        st.subheader("📡 PLCT Radar: Top 5 Sectors Comparison")
        top_5_sectors = initiatives_df['company_sector'].value_counts().head(5).index
        radar_data = initiatives_df[initiatives_df['company_sector'].isin(top_5_sectors)].groupby('company_sector').agg({
            'plct_customer_experience_score': 'mean',
            'plct_people_empowerment_score': 'mean',
            'plct_operational_efficiency_score': 'mean',
            'plct_new_business_models_score': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        categories = ['Customer Experience', 'People Empowerment', 'Operational Efficiency', 'New Business Models']
        
        for idx, row in radar_data.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row['plct_customer_experience_score'], row['plct_people_empowerment_score'],
                   row['plct_operational_efficiency_score'], row['plct_new_business_models_score']],
                theta=categories,
                fill='toself',
                name=row['company_sector']
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # PLCT Score vs Innovation Level
        st.subheader("💎 PLCT Score vs Innovation Level")
        col1, col2 = st.columns(2)
        
        with col1:
            innovation_plct = initiatives_df.groupby('innovation_level')['plct_total_score'].agg(['mean', 'count']).reset_index()
            innovation_plct.columns = ['innovation_level', 'avg_plct', 'count']
            
            fig = px.bar(
                innovation_plct,
                x='innovation_level',
                y='avg_plct',
                text='count',
                title="Average PLCT by Innovation Level",
                color='avg_plct',
                color_continuous_scale='Blues'
            )
            fig.update_traces(texttemplate='%{text} initiatives', textposition='outside')
            fig.update_layout(height=350, xaxis_title="Innovation Level", yaxis_title="Avg PLCT Score")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # PLCT Distribution by Top Companies
            top_companies = initiatives_df.groupby('company_name')['plct_total_score'].mean().nlargest(10)
            
            fig = px.bar(
                x=top_companies.values,
                y=top_companies.index,
                orientation='h',
                title="Top 10 Companies by Avg PLCT Score",
                color=top_companies.values,
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=350, xaxis_title="Avg PLCT Score", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # PLCT Correlation Matrix
        st.subheader("🔗 PLCT Dimensions Correlation")
        corr_data = initiatives_df[['plct_customer_experience_score', 'plct_people_empowerment_score',
                                     'plct_operational_efficiency_score', 'plct_new_business_models_score']].corr()
        corr_data.columns = ['Customer Exp.', 'People Emp.', 'Operational Eff.', 'New Business']
        corr_data.index = ['Customer Exp.', 'People Emp.', 'Operational Eff.', 'New Business']
        
        fig = px.imshow(
            corr_data,
            labels=dict(color="Correlation"),
            x=corr_data.columns,
            y=corr_data.index,
            color_continuous_scale='RdBu',
            zmin=-1, zmax=1,
            text_auto='.2f'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)

elif page == "💡 Technology Trends":
    st.title("💡 Technology Trends")
    st.markdown("*Technology adoption patterns over time*")
    
    try:
        tech_df = load_technology_categories()
        initiatives_df = load_initiatives_data()
        yearly_df = load_yearly_trends()
        
        # Overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Categories", len(tech_df))
        with col2:
            st.metric("Avg Initiatives/Category", f"{tech_df['initiative_count'].mean():.1f}")
        with col3:
            most_common = tech_df.loc[tech_df['initiative_count'].idxmax(), 'category']
            st.metric("Most Common Category", most_common)
        
        st.divider()
        
        # Top Technology Categories
        st.subheader("🔝 Top 20 Technology Categories")
        top_20 = tech_df.nlargest(20, 'initiative_count')
        
        fig = px.bar(
            top_20,
            y='category',
            x='initiative_count',
            orientation='h',
            color='initiative_count',
            color_continuous_scale='Blues',
            title=""
        )
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Category Reach
        st.subheader("🎯 Category Reach & Impact")
        top_30 = tech_df.nlargest(30, 'initiative_count')
        
        fig = px.scatter(
            top_30,
            x='initiative_count',
            y='company_count',
            size='avg_plct_score',
            color='avg_disclosure_score',
            hover_data=['category'],
            title="",
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Innovation Level by Category
        st.subheader("💡 Innovation Level by Category (Top 15)")
        top_categories = tech_df.nlargest(15, 'initiative_count')['category'].tolist()
        filtered_initiatives = initiatives_df[initiatives_df['category'].isin(top_categories)]
        
        innovation_data = filtered_initiatives.groupby(['category', 'innovation_level']).size().reset_index(name='count')
        
        fig = px.bar(
            innovation_data,
            x='category',
            y='count',
            color='innovation_level',
            title="",
            color_discrete_map={'High': '#34A853', 'Medium': '#FBBC04', 'Low': '#EA4335'}
        )
        fig.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Technology Adoption by Sector
        st.subheader("🏢 Technology Adoption by Sector")
        tech_by_sector = initiatives_df.groupby(['company_sector', 'category']).size().reset_index(name='count')
        top_tech = tech_by_sector.groupby('category')['count'].sum().nlargest(10).index
        tech_by_sector_filtered = tech_by_sector[tech_by_sector['category'].isin(top_tech)]
        
        fig = px.bar(
            tech_by_sector_filtered,
            x='category',
            y='count',
            color='company_sector',
            title="Top 10 Technologies Across Sectors",
            barmode='stack'
        )
        fig.update_layout(height=500, xaxis_tickangle=-45, xaxis_title="", yaxis_title="Initiative Count")
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Technology Category Timeline
        st.subheader("📅 Technology Adoption Timeline")
        top_10_tech = tech_df.nlargest(10, 'initiative_count')['category'].tolist()
        tech_timeline = initiatives_df[initiatives_df['category'].isin(top_10_tech)]
        tech_yearly = tech_timeline.groupby(['year_mentioned', 'category']).size().reset_index(name='count')
        
        fig = px.line(
            tech_yearly,
            x='year_mentioned',
            y='count',
            color='category',
            title="Top 10 Technologies - Adoption Over Time",
            markers=True
        )
        fig.update_layout(height=500, hovermode='x unified', xaxis_title="Year", yaxis_title="Number of Initiatives")
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Technology Heatmap
        st.subheader("🔥 Technology-Sector Heatmap")
        pivot_data = initiatives_df.groupby(['company_sector', 'category']).size().reset_index(name='count')
        top_12_sectors = initiatives_df['company_sector'].value_counts().head(12).index
        top_15_tech = tech_df.nlargest(15, 'initiative_count')['category'].tolist()
        
        heatmap_filtered = pivot_data[
            (pivot_data['company_sector'].isin(top_12_sectors)) & 
            (pivot_data['category'].isin(top_15_tech))
        ]
        
        heatmap_pivot = heatmap_filtered.pivot_table(
            index='category', 
            columns='company_sector', 
            values='count', 
            fill_value=0
        )
        
        fig = px.imshow(
            heatmap_pivot,
            labels=dict(x="Sector", y="Technology Category", color="Initiatives"),
            aspect="auto",
            color_continuous_scale='YlOrRd'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Technology PLCT Performance
        st.subheader("🎯 Technology Category PLCT Performance")
        col1, col2 = st.columns(2)
        
        with col1:
            tech_plct = initiatives_df.groupby('category')['plct_total_score'].mean().nlargest(15)
            
            fig = px.bar(
                x=tech_plct.values,
                y=tech_plct.index,
                orientation='h',
                title="Top 15 Technologies by Avg PLCT Score",
                color=tech_plct.values,
                color_continuous_scale='Greens',
                labels={'x': 'Avg PLCT Score', 'y': 'Category'}
            )
            fig.update_layout(height=450, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            tech_disclosure = initiatives_df.groupby('category')['disclosure_quality_total_score'].mean().nlargest(15)
            
            fig = px.bar(
                x=tech_disclosure.values,
                y=tech_disclosure.index,
                orientation='h',
                title="Top 15 Technologies by Avg Disclosure Score",
                color=tech_disclosure.values,
                color_continuous_scale='Blues',
                labels={'x': 'Avg Disclosure Score', 'y': 'Category'}
            )
            fig.update_layout(height=450, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Technology Treemap
        st.subheader("🗺️ Technology Portfolio Treemap")
        top_50_tech = tech_df.nlargest(50, 'initiative_count')
        
        fig = px.treemap(
            top_50_tech,
            path=['category'],
            values='initiative_count',
            color='avg_plct_score',
            color_continuous_scale='RdYlGn',
            title="Top 50 Technologies by Initiative Count (colored by PLCT Score)"
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Emerging vs Established Technologies
        st.subheader("🚀 Emerging vs Established Technologies")
        
        # Calculate technology maturity based on initiative count and years active
        tech_maturity = initiatives_df.groupby('category').agg({
            'year_mentioned': ['min', 'max', 'count'],
            'plct_total_score': 'mean'
        }).reset_index()
        tech_maturity.columns = ['category', 'first_year', 'last_year', 'initiative_count', 'avg_plct']
        tech_maturity['years_active'] = tech_maturity['last_year'] - tech_maturity['first_year'] + 1
        tech_maturity = tech_maturity[tech_maturity['initiative_count'] >= 5]  # Filter for meaningful data
        
        fig = px.scatter(
            tech_maturity,
            x='years_active',
            y='initiative_count',
            size='avg_plct',
            color='avg_plct',
            hover_data=['category'],
            title="Technology Maturity Analysis",
            labels={'years_active': 'Years Active', 'initiative_count': 'Total Initiatives', 'avg_plct': 'Avg PLCT'},
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Technology Comparison Table
        st.subheader("📊 Comprehensive Technology Comparison")
        tech_summary = initiatives_df.groupby('category').agg({
            'company_name': 'nunique',
            'plct_total_score': ['mean', 'std'],
            'disclosure_quality_total_score': 'mean',
            'innovation_level': lambda x: f"{(x == 'High').sum()}/{len(x)}",
            'year_mentioned': 'count'
        }).reset_index()
        tech_summary.columns = ['Technology', 'Companies', 'Avg PLCT', 'PLCT StdDev', 'Avg Disclosure', 'High Innovation', 'Total Initiatives']
        tech_summary = tech_summary.sort_values('Total Initiatives', ascending=False).head(30)
        
        st.dataframe(
            tech_summary.style.background_gradient(subset=['Avg PLCT'], cmap='RdYlGn')
                               .background_gradient(subset=['Total Initiatives'], cmap='Blues')
                               .format({'Avg PLCT': '{:.1f}', 'PLCT StdDev': '{:.1f}', 'Avg Disclosure': '{:.1f}'}),
            use_container_width=True,
            height=500
        )
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)

elif page == "📋 Disclosure Quality":
    st.title("📋 Disclosure Quality")
    st.markdown("*Transparency and reporting quality metrics*")
    
    try:
        initiatives_df = load_initiatives_data()
        
        # Apply filters
        if selected_sectors:
            initiatives_df = initiatives_df[initiatives_df['company_sector'].isin(selected_sectors)]
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_overall = initiatives_df['disclosure_quality_total_score'].mean()
            st.metric("Avg Overall Score", f"{avg_overall:.2f}")
        with col2:
            high_conf_pct = (initiatives_df['confidence_level'] == 'High').sum() / len(initiatives_df) * 100
            st.metric("High Confidence %", f"{high_conf_pct:.1f}%")
        with col3:
            tier1_count = (initiatives_df['disclosure_quality_tier'] == 'Tier 1 - Excellent').sum()
            st.metric("Tier 1 Count", tier1_count)
        with col4:
            median_score = initiatives_df['disclosure_quality_total_score'].median()
            st.metric("Median Score", f"{median_score:.2f}")
        
        st.divider()
        
        # Tier Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Disclosure Tier Distribution")
            tier_counts = initiatives_df['disclosure_quality_tier'].value_counts()
            tier_order = ['Tier 1 - Excellent', 'Tier 2 - Good', 'Tier 3 - Fair', 'Tier 4 - Limited']
            tier_counts = tier_counts.reindex([t for t in tier_order if t in tier_counts.index])
            
            # Create dataframe for plotly
            tier_df = pd.DataFrame({
                'tier': tier_counts.index,
                'count': tier_counts.values
            })
            
            colors = ['#34A853', '#93C47D', '#F6B26B', '#EA4335']
            fig = px.bar(
                tier_df,
                x='tier',
                y='count',
                title="",
                color='tier',
                color_discrete_sequence=colors
            )
            fig.update_layout(height=400, showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Confidence Level Distribution")
            
            # Define order for confidence levels
            confidence_order = ['High', 'Medium', 'Low', 'Unknown']
            conf_counts = initiatives_df['confidence_level'].value_counts()
            
            # Reorder to match confidence_order
            ordered_conf = pd.Series({level: conf_counts.get(level, 0) for level in confidence_order if conf_counts.get(level, 0) > 0})
            
            fig = px.pie(
                values=ordered_conf.values,
                names=ordered_conf.index,
                title="",
                hole=0.4,
                color_discrete_map={
                    'High': '#34A853',
                    'Medium': '#FBBC04', 
                    'Low': '#EA4335',
                    'Unknown': '#9AA0A6'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Top Disclosure Leaders
        st.subheader("🏆 Top Disclosure Leaders")
        disclosure_by_company = initiatives_df.groupby('company_name').agg({
            'disclosure_quality_total_score': 'mean',
            'company_sector': 'first',
            'disclosure_quality_tier': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'N/A'
        }).reset_index()
        disclosure_by_company.columns = ['company_name', 'avg_disclosure_score', 'company_sector', 'most_common_tier']
        disclosure_by_company['record_count'] = initiatives_df.groupby('company_name').size().values
        
        top_disclosure = disclosure_by_company.nlargest(25, 'avg_disclosure_score')
        
        st.dataframe(
            top_disclosure.style.background_gradient(subset=['avg_disclosure_score'], cmap='RdYlGn'),
            use_container_width=True,
            height=400
        )
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Malaysian Digital Transformation Research Dashboard</strong></p>
        <p>Data as of January 26, 2026 | 925 Companies | 11,792 Initiatives | 51 Sectors</p>
    </div>
""", unsafe_allow_html=True)
