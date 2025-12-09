import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import re
import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote
import google.generativeai as genai
from nl_query_helper import RAGQueryHelper
from research_enhancements import (
    export_data_to_csv, export_data_to_excel, generate_citation_info,
    generate_methodology_section, render_data_quality_dashboard,
    render_statistical_summary
)

# Fix plotly orjson compatibility issue
pio.json.config.default_engine = "json"

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'ide_index')
}


def apply_custom_css():
    """Apply academic-style custom CSS for research dashboard"""
    st.markdown("""
    <style>
        /* Import professional font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Professional light background for entire app */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* Light background for main content */
        .main .block-container {
            background-color: #f8f9fa;
            padding-top: 2rem;
        }
        
        /* White background for sidebar with subtle border */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
        }
        
        /* Ensure all text is dark and visible */
        .stApp, .main, p, span, div, label {
            color: #1f2937;
        }
        
        /* Main header - academic style */
        .main-header {
            font-size: 2.5rem;
            font-weight: 600;
            color: #1a1a1a;
            text-align: center;
            margin-bottom: 0.5rem;
            padding: 1.5rem 0 0.5rem 0;
            letter-spacing: -0.02em;
        }
        
        .subtitle {
            font-size: 1rem;
            font-weight: 400;
            color: #6b7280;
            text-align: center;
            margin-bottom: 2rem;
            line-height: 1.5;
        }
        
        /* Metric cards - clean professional style */
        .metric-card {
            background: #ffffff;
            padding: 1.25rem;
            border-radius: 0.5rem;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }
        
        .metric-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 4px 12px rgba(59,130,246,0.1);
        }
        
        /* Sidebar - academic style */
        .sidebar-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid #e5e7eb;
        }
        
        /* Section headers */
        h1, h2, h3 {
            color: #1f2937;
            font-weight: 600;
            letter-spacing: -0.01em;
        }
        
        /* Chat interface - professional style */
        .chat-message {
            padding: 1rem 1.25rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            border: 1px solid #e5e7eb;
        }
        
        .user-message {
            background: #f9fafb;
            border-left: 3px solid #3b82f6;
        }
        
        .assistant-message {
            background: #ffffff;
            border-left: 3px solid #10b981;
        }
        
        /* Tabs - clean design */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background-color: #f9fafb;
            padding: 0.5rem;
            border-radius: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            color: #6b7280;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #ffffff;
            color: #1f2937;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Info boxes */
        .info-box {
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .info-box-title {
            font-weight: 600;
            color: #1e40af;
            margin-bottom: 0.5rem;
        }
        
        /* Data tables */
        .dataframe {
            font-size: 0.875rem;
            border: 1px solid #e5e7eb;
            border-radius: 0.5rem;
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 0.375rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        /* Remove default Streamlit padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Professional color scheme for visualizations */
        .plotly-graph-div {
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)


def check_database_credentials():
    """Validate database credentials and prompt if missing"""
    if not DB_CONFIG['password']:
        st.sidebar.warning("⚠️ Database password not set. Please configure in .env file or enter below.")
        db_password = st.sidebar.text_input("Database Password", type="password")
        if db_password:
            DB_CONFIG['password'] = db_password
            return True
        st.error("Please enter database password to continue.")
        return False
    return True


@st.cache_data(ttl=300)
def load_data():
    """Load and preprocess data from MySQL database with new schema"""
    try:
        password_encoded = quote(DB_CONFIG['password'])
        port = os.getenv('MYSQL_PORT', '3306')
        
        # Build connection string with SSL and timeout settings
        connection_string = f"mysql+pymysql://{DB_CONFIG['user']}:{password_encoded}@{DB_CONFIG['host']}:{port}/{DB_CONFIG['database']}?charset=utf8mb4"
        
        engine = create_engine(
            connection_string,
            connect_args={
                'connect_timeout': 30,
                'read_timeout': 30,
                'write_timeout': 30
            },
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Join companies and initiatives tables
        query = """
        SELECT 
            c.id as company_id,
            c.company_name,
            c.company_sector,
            c.year_mentioned as report_year,
            c.report_type,
            c.technology_used,
            c.department,
            c.digital_investment,
            c.digital_maturity_level,
            c.plct_dimensions,
            c.strategic_priority,
            i.id as initiative_id,
            i.category as ide_category,
            i.initiative as initiative_description,
            i.plct_alignment,
            i.expected_impact,
            i.investment_amount,
            i.timeline,
            i.success_metrics,
            i.business_rationale,
            i.implementation_approach,
            i.workforce_impact,
            i.technology_partners,
            i.innovation_level,
            i.risk_factors,
            i.competitive_advantage,
            i.policy_implications,
            i.governance_structure,
            i.data_strategy,
            i.security_considerations,
            i.sustainability_impact,
            i.plct_customer_experience_score,
            i.plct_customer_experience_rationale,
            i.plct_people_empowerment_score,
            i.plct_people_empowerment_rationale,
            i.plct_operational_efficiency_score,
            i.plct_operational_efficiency_rationale,
            i.plct_new_business_models_score,
            i.plct_new_business_models_rationale,
            i.plct_total_score,
            i.plct_dominant_dimension,
            i.plct_adjustment_factors,
            i.plct_investor_weighted_score,
            i.plct_policy_weighted_score,
            i.plct_strategic_weighted_score,
            i.disclosure_quality_investment_score,
            i.disclosure_quality_timeline_score,
            i.disclosure_quality_metrics_score,
            i.disclosure_quality_technical_score,
            i.disclosure_quality_rationale_score,
            i.disclosure_quality_total_score,
            i.disclosure_quality_tier,
            i.confidence_level,
            i.confidence_justification,
            i.confidence_flagged_for_verification,
            i.confidence_verification_notes
        FROM companies c
        LEFT JOIN initiatives i ON c.id = i.company_id
        """
        
        df = pd.read_sql(query, engine)
        engine.dispose()

        # Preprocess columns
        df['report_year'] = pd.to_numeric(df['report_year'], errors='coerce')
        
        # Convert digital_investment to numeric (extract numbers from text)
        def extract_numeric_investment(text):
            if pd.isna(text) or not text:
                return 100000  # Default baseline
            # Try to extract numeric values (e.g., "RM 1,000,000" or "1.5 million")
            import re
            text = str(text).lower()
            
            # Check for explicit "not mentioned", "not applicable", "n/a"
            if any(phrase in text for phrase in ['not mentioned', 'not applicable', 'n/a', 'not specified']):
                return 50000  # Minimal investment
            
            # Extract actual numbers first
            numbers = re.findall(r'[\d,]+\.?\d*', text.replace(',', ''))
            if numbers:
                try:
                    num = float(numbers[0])
                    # Handle millions/thousands keywords
                    if 'million' in text:
                        return num * 1000000
                    elif 'thousand' in text or 'k' in text:
                        return num * 1000
                    return num if num > 1000 else num * 1000000  # Assume millions if small number
                except:
                    pass
            
            # Estimate based on keywords
            if any(word in text for word in ['significant', 'major', 'substantial', 'large']):
                return 2000000
            if any(word in text for word in ['moderate', 'medium']):
                return 800000
            if any(word in text for word in ['minor', 'small', 'limited']):
                return 300000
            if 'investment' in text or 'rm' in text:
                return 500000  # Generic investment mention
            
            return 100000  # Default baseline
        
        df['digital_investment_numeric'] = df['digital_investment'].apply(extract_numeric_investment)
        
        # Parse JSON columns
        for col in ['technology_used', 'department', 'plct_dimensions', 'timeline', 
                    'success_metrics', 'workforce_impact', 'risk_factors', 
                    'competitive_advantage', 'policy_implications']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: json.loads(x) if pd.notna(x) and x else {})
        
        return df
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return pd.DataFrame()


def create_wordcloud(text_data, title):
    """Generate word cloud visualization from text data"""
    if text_data.empty:
        return None

    combined_text = ' '.join(str(text) for text in text_data if text)
    cleaned_text = re.sub(r'[^\w\s]', '', combined_text.lower())

    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        max_words=100, 
        colormap='viridis'
    ).generate(cleaned_text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(title, fontsize=16, fontweight='bold')
    plt.tight_layout()

    return fig


def render_sidebar_filters(df):
    """Render sidebar filters and return filtered dataframe"""
    st.sidebar.markdown('<p class="sidebar-header">🔍 Filters</p>', unsafe_allow_html=True)

    companies = sorted(df['company_name'].dropna().unique())
    selected_companies = st.sidebar.multiselect(
        "Select Companies",
        companies,
        default=companies
    )

    years = sorted(df['report_year'].dropna().unique())
    selected_years = st.sidebar.multiselect(
        "Select Years",
        years,
        default=years
    )

    sectors = sorted(df['company_sector'].dropna().unique())
    selected_sectors = st.sidebar.multiselect(
        "Select Sectors",
        sectors,
        default=sectors
    )
    
    categories = sorted(df['ide_category'].dropna().unique())
    selected_categories = st.sidebar.multiselect(
        "Select Initiative Categories",
        categories,
        default=categories
    )
    
    maturity_levels = sorted(df['digital_maturity_level'].dropna().unique())
    selected_maturity = st.sidebar.multiselect(
        "Digital Maturity Level",
        maturity_levels,
        default=maturity_levels
    )

    # Apply filters
    filtered_df = df[
        (df['company_name'].isin(selected_companies)) &
        (df['report_year'].isin(selected_years)) &
        (df['company_sector'].isin(selected_sectors)) &
        (df['ide_category'].isin(selected_categories)) &
        (df['digital_maturity_level'].isin(selected_maturity))
    ]

    return filtered_df


def render_metric_cards(filtered_df):
    """Render key metric cards"""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown('<div class="metric-card" style="border-left: 4px solid #3b82f6; background: linear-gradient(135deg, #ffffff 0%, #eff6ff 100%);">', unsafe_allow_html=True)
        st.metric("Total Initiatives", len(filtered_df))
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        unique_companies = filtered_df['company_name'].nunique()
        st.markdown('<div class="metric-card" style="border-left: 4px solid #10b981; background: linear-gradient(135deg, #ffffff 0%, #ecfdf5 100%);">', unsafe_allow_html=True)
        st.metric("Companies", unique_companies)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        unique_sectors = filtered_df['company_sector'].nunique()
        st.markdown('<div class="metric-card" style="border-left: 4px solid #f59e0b; background: linear-gradient(135deg, #ffffff 0%, #fffbeb 100%);">', unsafe_allow_html=True)
        st.metric("Sectors", unique_sectors)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        unique_categories = filtered_df['ide_category'].nunique()
        st.markdown('<div class="metric-card" style="border-left: 4px solid #8b5cf6; background: linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%);">', unsafe_allow_html=True)
        st.metric("Categories", unique_categories)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col5:
        tech_count = filtered_df['technology_used'].apply(lambda x: len(x) if isinstance(x, list) else 0).sum()
        st.markdown('<div class="metric-card" style="border-left: 4px solid #ec4899; background: linear-gradient(135deg, #ffffff 0%, #fdf2f8 100%);">', unsafe_allow_html=True)
        st.metric("Technologies", int(tech_count))
        st.markdown('</div>', unsafe_allow_html=True)


def render_quick_insights(filtered_df):
    """Display research summary with key findings"""
    
    # Add export button before insights
    col_export1, col_export2, col_export3 = st.columns([1, 1, 2])
    with col_export1:
        if st.button("📥 Export Filtered Data"):
            csv_data = export_data_to_csv(filtered_df, "ide_research_export.csv")
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"ide_research_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    with col_export2:
        if st.button("📄 Citation Info"):
            st.session_state.show_citation = True
    
    if st.session_state.get('show_citation', False):
        st.markdown(generate_citation_info())
        if st.button("Close Citation Info"):
            st.session_state.show_citation = False
    
    with st.expander("📊 Research Summary & Key Findings", expanded=True):
        if not filtered_df.empty:
            try:
                top_company = filtered_df['company_name'].mode()[0] if not filtered_df['company_name'].empty else "N/A"
                top_sector = filtered_df['company_sector'].mode()[0] if not filtered_df['company_sector'].empty else "N/A"
                top_category = filtered_df['ide_category'].mode()[0] if not filtered_df['ide_category'].empty else "N/A"
                peak_year = filtered_df['report_year'].mode()[0] if not filtered_df['report_year'].empty else "N/A"
                peak_year_display = int(peak_year) if peak_year != 'N/A' else 'N/A'
                
                # Count transformational initiatives
                transformational = filtered_df[filtered_df['innovation_level'] == 'Transformational'].shape[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Primary Findings:**")
                    st.markdown(f"""
                    - **Most Active Organization**: {top_company}
                    - **Dominant Sector**: {top_sector}
                    - **Primary Initiative Category**: {top_category}
                    """)
                
                with col2:
                    st.markdown("**Temporal & Innovation Patterns:**")
                    st.markdown(f"""
                    - **Peak Activity Period**: {peak_year_display}
                    - **Transformational Projects**: {transformational} high-impact initiatives
                    - **Data Coverage**: {len(filtered_df)} observations analyzed
                    """)
            except Exception as e:
                st.info("Summary statistics are being computed...")
        else:
            st.info("⚠️ No data matches current filter criteria. Please adjust filters to view insights.")


def render_ai_query_tab(db_config):
    """Render AI-powered natural language query interface"""
    st.header("🔍 Natural Language Database Query")
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">About This Tool</div>
        Use natural language to query the research database. The AI will translate your question 
        into SQL and return structured results with interpretive analysis.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize RAG helper
    if 'rag_helper' not in st.session_state:
        st.session_state.rag_helper = RAGQueryHelper(db_config)
    
    # Sample questions for researchers
    with st.expander("📚 Example Research Questions", expanded=False):
        st.markdown("""
        **Maturity & Capability Assessment:**
        - Which companies demonstrate highest digital maturity levels?
        - What is the distribution of innovation levels across sectors?
        
        **Sectoral Analysis:**
        - Compare technology adoption patterns between manufacturing and services sectors
        - Which sectors show highest investment in digital transformation?
        
        **Technology Patterns:**
        - What technologies are most frequently adopted?
        - Identify companies implementing AI or machine learning initiatives
        
        **Investment & ROI:**
        - What is the average investment amount by sector?
        - Which companies have the largest digital transformation budgets?
        
        **Strategic Priorities:**
        - What are the most common strategic priorities for digital initiatives?
        - How do PLCT dimensions correlate with business outcomes?
        """)
    
    # Query input
    user_question = st.text_area(
        "Enter your question:",
        placeholder="E.g., Which companies are investing in AI and automation?",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        query_button = st.button("🔍 Query", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear History", use_container_width=True)
    
    # Initialize session state for chat history
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    if clear_button:
        st.session_state.query_history = []
        st.rerun()
    
    if query_button and user_question:
        with st.spinner("🔄 Analyzing your question..."):
            try:
                sql_query, data, insights = st.session_state.rag_helper.query(user_question)
                
                # Add to history
                st.session_state.query_history.append({
                    'question': user_question,
                    'sql': sql_query,
                    'data': data,
                    'insights': insights
                })
                
            except Exception as e:
                st.error(f"Error processing query: {e}")
    
    # Display results
    if st.session_state.query_history:
        st.markdown("---")
        st.subheader("Query Results")
        
        for idx, result in enumerate(reversed(st.session_state.query_history)):
            with st.container():
                st.markdown(f'<div class="chat-message user-message"><strong>Question {len(st.session_state.query_history) - idx}:</strong> {result["question"]}</div>', unsafe_allow_html=True)
                
                # Show SQL query in expander
                with st.expander("🔍 View Generated SQL"):
                    st.code(result['sql'], language='sql')
                
                # Show insights
                st.markdown(f'<div class="chat-message assistant-message">', unsafe_allow_html=True)
                st.markdown("**📊 Analysis:**")
                st.markdown(result['insights'])
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Show data table
                if result['data'] is not None and not result['data'].empty:
                    with st.expander(f"📋 View Data ({len(result['data'])} rows)"):
                        st.dataframe(result['data'], use_container_width=True)
                        
                        # Download button
                        csv = result['data'].to_csv(index=False)
                        st.download_button(
                            label="Download Results",
                            data=csv,
                            file_name=f"query_result_{idx+1}.csv",
                            mime="text/csv",
                            key=f"download_{idx}"
                        )
                
                st.markdown("---")


def render_overview_tab(filtered_df):
    """Render executive summary and key trends"""
    st.header("📊 Executive Summary")
    
    if filtered_df.empty:
        st.warning("⚠️ No data available for current filter selection")
        return
    
    # Strategic overview metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Leading Organizations by Digital Activity")
        st.caption("Ranked by total number of documented initiatives")
        company_count = filtered_df['company_name'].value_counts().head(10).reset_index()
        company_count.columns = ['Company', 'Initiatives']
        
        fig = px.bar(
            company_count,
            x='Initiatives',
            y='Company',
            orientation='h',
            color='Initiatives',
            color_continuous_scale='Blues',
            labels={'Initiatives': 'Number of Initiatives', 'Company': ''}
        )
        fig.update_layout(
            height=400,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Digital Maturity Assessment")
        st.caption("Distribution of organizational digital capability levels")
        maturity_dist = filtered_df['digital_maturity_level'].value_counts().reset_index()
        maturity_dist.columns = ['Maturity Level', 'Count']
        
        fig = px.pie(
            maturity_dist,
            values='Count',
            names='Maturity Level',
            color_discrete_sequence=px.colors.sequential.Blues,
            hole=0.4
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Temporal analysis
    if 'report_year' in filtered_df.columns:
        st.subheader("📅 Temporal Patterns in Digital Transformation")
        st.caption("Longitudinal view of initiative adoption across reporting periods")
        yearly_count = filtered_df.groupby('report_year').size().reset_index(name='count')
        
        fig = px.line(
            yearly_count,
            x='report_year',
            y='count',
            markers=True,
            labels={'report_year': 'Reporting Year', 'count': 'Number of Initiatives'}
        )
        fig.update_traces(line_color='#3b82f6', line_width=2.5, marker=dict(size=8))
        fig.update_layout(
            height=350,
            hovermode='x unified',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Sectoral distribution
    st.subheader("🏭 Sectoral Distribution of Digital Initiatives")
    st.caption("Comparative analysis of initiative frequency across industry sectors")
    sector_count = filtered_df['company_sector'].value_counts().reset_index()
    sector_count.columns = ['Sector', 'Initiatives']
    
    fig = px.bar(
        sector_count,
        x='Sector',
        y='Initiatives',
        color='Initiatives',
        color_continuous_scale='Greens',
        labels={'Initiatives': 'Number of Initiatives', 'Sector': 'Industry Sector'}
    )
    fig.update_xaxes(tickangle=45)
    fig.update_layout(
        height=350,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=60)
    )
    st.plotly_chart(fig, use_container_width=True)


def render_plct_framework_tab(filtered_df):
    """Render comprehensive PLCT Framework scoring analysis"""
    st.header("📈 PLCT Framework Scoring Analysis")
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">PLCT Scoring Framework</div>
        Quantitative assessment of digital transformation initiatives across four dimensions (0-100 scale each):
        <ul>
            <li><strong>Customer Experience (CX):</strong> Digital initiatives improving customer interactions</li>
            <li><strong>People Empowerment (PE):</strong> Workforce development and capability building</li>
            <li><strong>Operational Efficiency (OE):</strong> Process optimization and automation</li>
            <li><strong>New Business Models (BM):</strong> Innovation in revenue streams and value delivery</li>
        </ul>
        <strong>Total PLCT Score:</strong> Sum of four dimensions (0-400 scale)
    </div>
    """, unsafe_allow_html=True)
    
    # Check for PLCT scoring data
    plct_score_cols = ['plct_customer_experience_score', 'plct_people_empowerment_score', 
                       'plct_operational_efficiency_score', 'plct_new_business_models_score']
    
    if filtered_df.empty or not all(col in filtered_df.columns for col in plct_score_cols):
        st.warning("⚠️ PLCT scoring data not available for current selection")
        return
    
    # Filter out rows with null PLCT scores
    plct_df = filtered_df[filtered_df['plct_total_score'].notna()].copy()
    
    if plct_df.empty:
        st.info("⚠️ No PLCT scores available in the filtered dataset")
        return
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        avg_cx = plct_df['plct_customer_experience_score'].mean()
        st.metric("Avg CX Score", f"{avg_cx:.1f}/100")
    with col2:
        avg_pe = plct_df['plct_people_empowerment_score'].mean()
        st.metric("Avg PE Score", f"{avg_pe:.1f}/100")
    with col3:
        avg_oe = plct_df['plct_operational_efficiency_score'].mean()
        st.metric("Avg OE Score", f"{avg_oe:.1f}/100")
    with col4:
        avg_bm = plct_df['plct_new_business_models_score'].mean()
        st.metric("Avg BM Score", f"{avg_bm:.1f}/100")
    with col5:
        avg_total = plct_df['plct_total_score'].mean()
        st.metric("Avg Total Score", f"{avg_total:.1f}/400")
    
    st.markdown("---")
    
    # Dimensional Score Distribution
    st.subheader("📊 PLCT Dimension Score Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart - Average scores by dimension
        avg_scores = {
            'Customer Experience': plct_df['plct_customer_experience_score'].mean(),
            'People Empowerment': plct_df['plct_people_empowerment_score'].mean(),
            'Operational Efficiency': plct_df['plct_operational_efficiency_score'].mean(),
            'New Business Models': plct_df['plct_new_business_models_score'].mean()
        }
        
        radar_df = pd.DataFrame({
            'Dimension': list(avg_scores.keys()),
            'Score': list(avg_scores.values())
        })
        
        fig = px.bar(
            radar_df,
            x='Dimension',
            y='Score',
            color='Score',
            color_continuous_scale='Blues',
            labels={'Score': 'Average Score (0-100)'},
            title='Average PLCT Dimension Scores'
        )
        fig.update_layout(height=400, showlegend=False)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Dominant dimension distribution
        if 'plct_dominant_dimension' in plct_df.columns:
            dominant_counts = plct_df['plct_dominant_dimension'].value_counts().reset_index()
            dominant_counts.columns = ['Dimension', 'Count']
            
            fig = px.pie(
                dominant_counts,
                values='Count',
                names='Dimension',
                title='Dominant PLCT Dimensions',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Stakeholder-Weighted Scores
    st.subheader("👥 Stakeholder-Weighted PLCT Scores")
    st.caption("Different stakeholder perspectives on transformation impact")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if 'plct_investor_weighted_score' in plct_df.columns:
            avg_investor = plct_df['plct_investor_weighted_score'].mean()
            st.metric("Investor View", f"{avg_investor:.1f}", 
                     help="Weighted: CX×0.3 + PE×0.1 + OE×0.3 + BM×0.3")
    with col2:
        if 'plct_policy_weighted_score' in plct_df.columns:
            avg_policy = plct_df['plct_policy_weighted_score'].mean()
            st.metric("Policy View", f"{avg_policy:.1f}",
                     help="Weighted: CX×0.2 + PE×0.4 + OE×0.2 + BM×0.2")
    with col3:
        if 'plct_strategic_weighted_score' in plct_df.columns:
            avg_strategic = plct_df['plct_strategic_weighted_score'].mean()
            st.metric("Strategic View", f"{avg_strategic:.1f}",
                     help="Weighted: Equal 25% across all dimensions")
    
    # Stakeholder comparison chart
    if all(col in plct_df.columns for col in ['plct_investor_weighted_score', 'plct_policy_weighted_score', 'plct_strategic_weighted_score']):
        stakeholder_data = {
            'Stakeholder': ['Investor', 'Policy', 'Strategic'],
            'Average Score': [
                plct_df['plct_investor_weighted_score'].mean(),
                plct_df['plct_policy_weighted_score'].mean(),
                plct_df['plct_strategic_weighted_score'].mean()
            ]
        }
        stakeholder_df = pd.DataFrame(stakeholder_data)
        
        fig = px.bar(
            stakeholder_df,
            x='Stakeholder',
            y='Average Score',
            color='Average Score',
            color_continuous_scale='Greens',
            title='Average Scores by Stakeholder Perspective'
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Disclosure Quality Assessment
    st.subheader("📝 Disclosure Quality Assessment")
    st.caption("Quality of information disclosure in initiatives (0-100 scale)")
    
    col1, col2 = st.columns(2)
    with col1:
        if 'disclosure_quality_total_score' in plct_df.columns:
            avg_disclosure = plct_df['disclosure_quality_total_score'].mean()
            st.metric("Average Disclosure Quality", f"{avg_disclosure:.1f}/100")
            
            # Disclosure quality tier distribution
            if 'disclosure_quality_tier' in plct_df.columns:
                # Extract tier from text (e.g., "Good (60-79)" -> "Good")
                plct_df['disclosure_tier_clean'] = plct_df['disclosure_quality_tier'].str.extract(r'^(\w+)', expand=False)
                tier_counts = plct_df['disclosure_tier_clean'].value_counts().reset_index()
                tier_counts.columns = ['Tier', 'Count']
                
                fig = px.bar(
                    tier_counts,
                    x='Tier',
                    y='Count',
                    color='Tier',
                    title='Disclosure Quality Tier Distribution',
                    color_discrete_map={
                        'Comprehensive': '#10b981',
                        'Good': '#3b82f6',
                        'Moderate': '#f59e0b',
                        'Limited': '#ef4444'
                    }
                )
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Disclosure quality component breakdown
        if all(col in plct_df.columns for col in ['disclosure_quality_investment_score', 'disclosure_quality_timeline_score', 
                                                    'disclosure_quality_metrics_score', 'disclosure_quality_technical_score']):
            component_avg = {
                'Investment (30)': plct_df['disclosure_quality_investment_score'].mean(),
                'Timeline (20)': plct_df['disclosure_quality_timeline_score'].mean(),
                'Metrics (25)': plct_df['disclosure_quality_metrics_score'].mean(),
                'Technical (15)': plct_df['disclosure_quality_technical_score'].mean(),
                'Rationale (10)': plct_df['disclosure_quality_rationale_score'].mean()
            }
            
            component_df = pd.DataFrame({
                'Component': list(component_avg.keys()),
                'Average Score': list(component_avg.values())
            })
            
            fig = px.bar(
                component_df,
                x='Component',
                y='Average Score',
                color='Average Score',
                color_continuous_scale='Oranges',
                title='Disclosure Quality Components'
            )
            fig.update_layout(height=350, showlegend=False)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Confidence Level Analysis
    st.subheader("🎯 Data Confidence Assessment")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'confidence_level' in plct_df.columns:
            # Extract confidence level from text
            plct_df['confidence_clean'] = plct_df['confidence_level'].str.extract(r'^(\w+)', expand=False)
            confidence_counts = plct_df['confidence_clean'].value_counts().reset_index()
            confidence_counts.columns = ['Confidence Level', 'Count']
            
            fig = px.pie(
                confidence_counts,
                values='Count',
                names='Confidence Level',
                title='Confidence Level Distribution',
                color='Confidence Level',
                color_discrete_map={'High': '#10b981', 'Medium': '#f59e0b', 'Low': '#ef4444'}
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'confidence_flagged_for_verification' in plct_df.columns:
            flagged = plct_df['confidence_flagged_for_verification'].sum()
            total = len(plct_df)
            st.metric("Initiatives Flagged for Verification", f"{flagged} / {total}")
            st.metric("Verification Rate", f"{(flagged/total*100):.1f}%")
    
    st.markdown("---")
    
    # Sector Analysis
    st.subheader("🏭 PLCT Scores by Sector")
    if 'company_sector' in plct_df.columns:
        sector_scores = plct_df.groupby('company_sector').agg({
            'plct_customer_experience_score': 'mean',
            'plct_people_empowerment_score': 'mean',
            'plct_operational_efficiency_score': 'mean',
            'plct_new_business_models_score': 'mean',
            'plct_total_score': 'mean'
        }).reset_index()
        
        sector_scores.columns = ['Sector', 'CX', 'PE', 'OE', 'BM', 'Total']
        sector_scores = sector_scores.sort_values('Total', ascending=False)
        
        fig = px.bar(
            sector_scores,
            x='Sector',
            y=['CX', 'PE', 'OE', 'BM'],
            title='Average PLCT Dimension Scores by Sector',
            labels={'value': 'Score', 'variable': 'Dimension'},
            barmode='group'
        )
        fig.update_layout(height=450)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Top performing initiatives
    st.subheader("🏆 Top Performing Initiatives by PLCT Score")
    top_initiatives = plct_df.nlargest(10, 'plct_total_score')[[
        'company_name', 'company_sector', 'initiative_description',
        'plct_customer_experience_score', 'plct_people_empowerment_score',
        'plct_operational_efficiency_score', 'plct_new_business_models_score',
        'plct_total_score', 'plct_dominant_dimension'
    ]].copy()
    
    top_initiatives.columns = ['Company', 'Sector', 'Initiative', 'CX', 'PE', 'OE', 'BM', 'Total', 'Dominant']
    st.dataframe(top_initiatives, use_container_width=True, height=400)

def render_investment_tab(filtered_df):
    """Render investment analysis tab"""
    st.header("Investment Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Investment by company
        company_investment = filtered_df.groupby('company_name')['digital_investment_numeric'].sum().reset_index()
        company_investment = company_investment.sort_values('digital_investment_numeric', ascending=True)

        fig = px.bar(
            company_investment,
            x='digital_investment_amount',
            y='company_name',
            orientation='h',
            title='Total Investment by Company (RM)',
            labels={'digital_investment_amount': 'Investment (RM)', 'company_name': 'Company'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Investment by category
        category_investment = filtered_df.groupby('ide_category')['digital_investment_numeric'].sum().reset_index()
        category_investment = category_investment.sort_values('digital_investment_numeric', ascending=False)

        fig = px.pie(
            category_investment,
            values='digital_investment_numeric',
            names='ide_category',
            title='Investment Distribution by Category'
        )
        fig.update_layout(height=500, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Investment timeline
    if 'report_year' in filtered_df.columns:
        yearly_investment = filtered_df.groupby('report_year')['digital_investment_numeric'].sum().reset_index()

        fig = px.line(
            yearly_investment,
            x='report_year',
            y='digital_investment_numeric',
            title='Investment Trend Over Years',
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)


def render_category_tab(filtered_df):
    """Render sectoral and categorical analysis"""
    st.header("🏭 Sectoral & Categorical Analysis")
    st.caption("Disaggregated analysis of initiative types and industry distribution patterns")

    # Initiative categorization
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Initiative Categories")
        st.caption("Distribution by strategic focus area")
        category_count = filtered_df['ide_category'].value_counts().reset_index()
        category_count.columns = ['Category', 'Count']

        fig = px.bar(
            category_count,
            x='Category',
            y='Count',
            color='Count',
            color_continuous_scale='Blues',
            labels={'Count': 'Frequency', 'Category': 'Initiative Category'}
        )
        fig.update_xaxes(tickangle=45)
        fig.update_layout(
            height=450,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=100)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Innovation Levels")
        st.caption("Classification of initiatives by transformational impact")
        innovation_dist = filtered_df['innovation_level'].value_counts().reset_index()
        innovation_dist.columns = ['Innovation Level', 'Count']
        
        fig = px.pie(
            innovation_dist,
            values='Count',
            names='Innovation Level',
            color_discrete_sequence=px.colors.sequential.Oranges,
            hole=0.4
        )
        fig.update_layout(
            height=450,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    # Cross-sectional analysis
    st.subheader("📊 Cross-Sectional Analysis: Sectors × Categories")
    st.caption("Initiative distribution across industry sectors and strategic categories")
    
    cross_tab = pd.crosstab(filtered_df['company_sector'], filtered_df['ide_category'])
    
    fig = px.imshow(
        cross_tab,
        labels=dict(x="Initiative Category", y="Industry Sector", color="Frequency"),
        x=cross_tab.columns,
        y=cross_tab.index,
        color_continuous_scale='Blues',
        aspect="auto"
    )
    fig.update_layout(height=500, margin=dict(l=20, r=20, t=40, b=120))
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    # Investment hierarchy visualization
    st.subheader("💰 Investment Distribution Hierarchy")
    st.caption("Treemap showing relative investment allocation by category and organization")
    if not filtered_df.empty:
        try:
            fig = px.treemap(
                filtered_df,
                path=[px.Constant("All Categories"), 'ide_category', 'company_name'],
                values='digital_investment_numeric',
                color='digital_investment_numeric',
                color_continuous_scale='Viridis',
                title='Investment Distribution Hierarchy'
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate treemap: {e}")


def render_technology_tab(filtered_df):
    """Render technology adoption patterns tab"""
    st.header("💡 Technology Adoption Patterns")

    if filtered_df.empty:
        st.warning("No data to display")
        return

    # Extract technology keywords from JSON
    tech_keywords = []
    for tech_list in filtered_df['technology_used'].dropna():
        if isinstance(tech_list, list):
            tech_keywords.extend(tech_list)
        elif isinstance(tech_list, str):
            try:
                tech_list_parsed = json.loads(tech_list)
                if isinstance(tech_list_parsed, list):
                    tech_keywords.extend(tech_list_parsed)
            except:
                pass

    if not tech_keywords:
        st.info("No technology data available")
        return

    # Count technologies
    tech_counts = Counter(tech_keywords)
    tech_df = pd.DataFrame(list(tech_counts.items()), columns=['Technology', 'Count'])
    tech_df = tech_df.sort_values('Count', ascending=False).head(20)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Technologies")
        fig = px.bar(
            tech_df.head(15),
            x='Count',
            y='Technology',
            orientation='h',
            title='Top 15 Technologies Used',
            color='Count',
            color_continuous_scale='Greens'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Technology Distribution")
        fig = px.pie(
            tech_df.head(10),
            values='Count',
            names='Technology',
            title='Technology Distribution (Top 10)'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Technology by sector
    st.subheader("📊 Technology Adoption by Sector")
    sector_tech = []
    for idx, row in filtered_df.iterrows():
        if isinstance(row['technology_used'], list):
            for tech in row['technology_used']:
                sector_tech.append({
                    'Sector': row['company_sector'],
                    'Technology': tech
                })
    
    if sector_tech:
        sector_tech_df = pd.DataFrame(sector_tech)
        sector_tech_count = sector_tech_df.groupby(['Sector', 'Technology']).size().reset_index(name='Count')
        sector_tech_top = sector_tech_count.nlargest(20, 'Count')
        
        fig = px.bar(
            sector_tech_top,
            x='Sector',
            y='Count',
            color='Technology',
            title='Top Technologies by Sector',
            barmode='stack'
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)



def render_comparison_tab(df, companies):
    """Render comparative analysis tab"""
    st.header("⚖️ Comparative Analysis")
    
    if len(companies) < 2:
        st.warning("Need at least 2 companies for comparison")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        company_a = st.selectbox("Select Company A", companies, index=0)
    with col2:
        company_b = st.selectbox("Select Company B", companies, index=min(1, len(companies)-1))
        
    if company_a and company_b:
        comp_a_data = df[df['company_name'] == company_a]
        comp_b_data = df[df['company_name'] == company_b]
        
        # Metrics comparison
        st.subheader("📊 Key Metrics Comparison")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        # Initiative count
        count_a = len(comp_a_data)
        count_b = len(comp_b_data)
        
        with m_col1:
            st.metric(label=f"{company_a}", value=f"{count_a} initiatives")
            st.metric(label=f"{company_b}", value=f"{count_b} initiatives", delta=count_a - count_b, delta_color="off")

        # Categories
        cat_a = comp_a_data['ide_category'].nunique()
        cat_b = comp_b_data['ide_category'].nunique()
        
        with m_col2:
            st.metric(label=f"{company_a}", value=f"{cat_a} categories")
            st.metric(label=f"{company_b}", value=f"{cat_b} categories", delta=cat_a - cat_b, delta_color="off")
        
        # Maturity
        maturity_a = comp_a_data['digital_maturity_level'].mode()[0] if not comp_a_data.empty else "N/A"
        maturity_b = comp_b_data['digital_maturity_level'].mode()[0] if not comp_b_data.empty else "N/A"
        
        with m_col3:
            st.metric(label=f"{company_a}", value=maturity_a)
            st.metric(label=f"{company_b}", value=maturity_b)
        
        # Technologies
        tech_a = comp_a_data['technology_used'].apply(lambda x: len(x) if isinstance(x, list) else 0).sum()
        tech_b = comp_b_data['technology_used'].apply(lambda x: len(x) if isinstance(x, list) else 0).sum()
        
        with m_col4:
            st.metric(label=f"{company_a}", value=f"{int(tech_a)} technologies")
            st.metric(label=f"{company_b}", value=f"{int(tech_b)} technologies")
            
        # Visual comparison
        st.subheader("📈 Initiative Categories Comparison")
        
        cat_comp_a = comp_a_data['ide_category'].value_counts().reset_index()
        cat_comp_a.columns = ['Category', 'Count']
        cat_comp_a['Company'] = company_a
        
        cat_comp_b = comp_b_data['ide_category'].value_counts().reset_index()
        cat_comp_b.columns = ['Category', 'Count']
        cat_comp_b['Company'] = company_b
        
        comp_data = pd.concat([cat_comp_a, cat_comp_b])
        
        fig = px.bar(
            comp_data, 
            x='Category', 
            y='Count',
            color='Company',
            title='Initiative Distribution by Category',
            barmode='group',
            color_discrete_sequence=['#667eea', '#764ba2']
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Innovation level comparison
        st.subheader("🚀 Innovation Level Comparison")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            innov_a = comp_a_data['innovation_level'].value_counts().reset_index()
            innov_a.columns = ['Level', 'Count']
            fig = px.pie(innov_a, values='Count', names='Level', title=f"{company_a} - Innovation Levels")
            st.plotly_chart(fig, use_container_width=True)
        
        with col_b:
            innov_b = comp_b_data['innovation_level'].value_counts().reset_index()
            innov_b.columns = ['Level', 'Count']
            fig = px.pie(innov_b, values='Count', names='Level', title=f"{company_b} - Innovation Levels")
            st.plotly_chart(fig, use_container_width=True)


def render_roi_calculator_tab():
    """ROI estimation and projection tool"""
    st.header("🧮 Investment Return Estimator")
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">Methodological Note</div>
        This calculator provides hypothetical ROI projections based on user-defined parameters. 
        Results should be interpreted as illustrative scenarios rather than financial forecasts.
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Investment Parameters")
        base_investment = st.number_input("Initial Investment (RM)", value=1000000, step=100000, format="%d")
        years_projected = st.slider("Projection Period (Years)", 1, 10, 5)
    with c2:
        st.subheader("Return Assumptions")
        expected_roi = st.slider("Expected Annual ROI (%)", 1, 50, 15)
        compounding = st.checkbox("Apply Compound Growth", value=True)
        
    # Calculate projection
    years_list = list(range(years_projected + 1))
    values = []
    
    current_value = base_investment
    values.append(current_value)
    
    for _ in range(years_projected):
        if compounding:
            current_value = current_value * (1 + expected_roi/100)
        else:
            current_value = current_value + (base_investment * expected_roi/100)
        values.append(current_value)
        
    # Display results
    final_value = values[-1]
    total_gain = final_value - base_investment
    roi_percent = (total_gain / base_investment) * 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Projected Value", f"RM {final_value:,.2f}", delta=f"+{roi_percent:.1f}%")
    with col2:
        st.metric("Total Gain", f"RM {total_gain:,.2f}")
    with col3:
        st.metric("Projection Period", f"{years_projected} years")
    
    # Visualization
    proj_df = pd.DataFrame({'Year': years_list, 'Value (RM)': values})
    fig = px.line(
        proj_df, 
        x='Year', 
        y='Value (RM)', 
        markers=True,
        labels={'Value (RM)': 'Projected Value (RM)', 'Year': 'Years from Investment'}
    )
    fig.add_hline(y=base_investment, line_dash="dash", line_color="gray", 
                  annotation_text="Initial Investment", annotation_position="right")
    fig.update_traces(line_color='#3b82f6', line_width=2.5, marker=dict(size=8))
    fig.update_layout(height=400, hovermode='x unified', margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)


def render_data_table_tab(filtered_df):
    """Research data table with export functionality"""
    st.header("📋 Research Dataset")
    st.caption("Complete dataset with filtering and export capabilities for further analysis")

    if filtered_df.empty:
        st.warning("⚠️ No data available for current filter selection")
        return

    # Select key columns for display
    display_columns = [
        'company_name', 'company_sector', 'report_year', 'digital_maturity_level',
        'ide_category', 'initiative_description', 'innovation_level', 
        'investment_amount', 'strategic_priority'
    ]
    
    # Filter to only existing columns
    display_columns = [col for col in display_columns if col in filtered_df.columns]
    
    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        column_config={
            "report_year": st.column_config.NumberColumn("Year", format="%d"),
            "company_name": "Organization",
            "company_sector": "Industry Sector",
            "ide_category": "Initiative Type",
            "initiative_description": st.column_config.TextColumn("Description", width="large"),
            "digital_maturity_level": "Digital Maturity",
            "innovation_level": "Innovation Class",
            "investment_amount": "Investment (RM)",
            "strategic_priority": "Strategic Priority"
        },
        height=500
    )

    # Export functionality
    col1, col2 = st.columns([1, 3])
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"digital_economy_research_data_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Dataset statistics
    st.markdown("---")
    st.subheader("📊 Dataset Descriptive Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Observations", f"{len(filtered_df):,}")
    with col2:
        st.metric("Unique Organizations", filtered_df['company_name'].nunique())
    with col3:
        st.metric("Industry Sectors", filtered_df['company_sector'].nunique())
    with col4:
        st.metric("Initiative Categories", filtered_df['ide_category'].nunique())


def render_footer(df, filtered_df):
    """Render dashboard footer"""
    pass


def main():
    """Main application entry point"""
    # Page configuration - must be first Streamlit command
    st.set_page_config(
        page_title="Digital Economy Research Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    apply_custom_css()
    
    if not check_database_credentials():
        return

    # Academic-style header
    st.markdown('<h1 class="main-header">Digital Economy Initiatives Research Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('''<p class="subtitle">
        A comprehensive analytical platform for examining corporate digital transformation strategies, 
        technology adoption patterns, and policy implications across Malaysian publicly-listed companies.
    </p>''', unsafe_allow_html=True)
    
    # Add methodology and citation sections
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("📚 Citation & How to Cite"):
            st.session_state.show_citation = True
    with col2:
        if st.button("🔬 Research Methodology"):
            st.session_state.show_methodology = True
    
    if st.session_state.get('show_citation', False):
        st.markdown(generate_citation_info())
        if st.button("✖️ Close Citation"):
            st.session_state.show_citation = False
            st.rerun()
    
    if st.session_state.get('show_methodology', False):
        st.markdown(generate_methodology_section())
        if st.button("✖️ Close Methodology"):
            st.session_state.show_methodology = False
            st.rerun()

    df = load_data()
    if df.empty:
        st.error("⚠️ Data unavailable. Please verify database connection and credentials.")
        return

    filtered_df = render_sidebar_filters(df)
    
    render_metric_cards(filtered_df)
    st.markdown("---")
    
    # Add export and statistics section
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    with col1:
        csv_data = export_data_to_csv(filtered_df)
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name=f"ide_research_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            help="Download filtered data as CSV"
        )
    with col2:
        excel_data = export_data_to_excel(filtered_df)
        st.download_button(
            label="📊 Export Excel",
            data=excel_data,
            file_name=f"ide_research_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download with summary sheets"
        )
    with col3:
        if st.button("📈 Show Statistics"):
            st.session_state.show_stats = not st.session_state.get('show_stats', False)
    
    if st.session_state.get('show_stats', False):
        with st.expander("📊 Comprehensive Statistical Summary", expanded=True):
            render_statistical_summary(filtered_df)
            st.markdown("---")
            render_data_quality_dashboard(filtered_df)
    
    st.markdown("---")
    render_quick_insights(filtered_df)

    # Analytical tabs with clear academic organization
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🔍 Query & Analysis",
        "📊 Executive Summary", 
        "🏭 Sectoral Analysis", 
        "💻 Technology Patterns", 
        "📈 PLCT Framework",
        "⚖️ Comparative Analysis", 
        "🧮 ROI Estimator", 
        "📋 Research Data"
    ])

    with tab1:
        render_ai_query_tab(DB_CONFIG)

    with tab2:
        render_overview_tab(filtered_df)

    with tab3:
        render_category_tab(filtered_df)

    with tab4:
        render_technology_tab(filtered_df)

    with tab5:
        render_plct_framework_tab(filtered_df)

    with tab6:
        companies = sorted(df['company_name'].dropna().unique())
        render_comparison_tab(df, companies)

    with tab7:
        render_roi_calculator_tab()

    with tab8:
        render_data_table_tab(filtered_df)

    render_footer(df, filtered_df)


if __name__ == "__main__":
    main()
