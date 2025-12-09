"""
Research Dashboard Enhancements
Additional features for academic researchers and policy analysts
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import io

def export_data_to_csv(df, filename="research_data.csv"):
    """Export filtered data to CSV for research purposes"""
    csv = df.to_csv(index=False)
    return csv

def export_data_to_excel(df, filename="research_data.xlsx"):
    """Export filtered data to Excel with multiple sheets"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Main data
        df.to_excel(writer, sheet_name='Full Dataset', index=False)
        
        # Summary statistics
        summary = pd.DataFrame({
            'Metric': [
                'Total Initiatives',
                'Unique Companies',
                'Sectors Covered',
                'Date Range',
                'Mean PLCT Score',
                'Std Dev PLCT',
                'High Priority Initiatives',
                'Transformational Projects'
            ],
            'Value': [
                len(df),
                df['company_name'].nunique(),
                df['company_sector'].nunique(),
                f"{df['report_year'].min()}-{df['report_year'].max()}",
                f"{df['plct_total_score'].mean():.2f}" if 'plct_total_score' in df.columns else 'N/A',
                f"{df['plct_total_score'].std():.2f}" if 'plct_total_score' in df.columns else 'N/A',
                len(df[df['strategic_priority'] == 'High']) if 'strategic_priority' in df.columns else 'N/A',
                len(df[df['innovation_level'] == 'Transformational']) if 'innovation_level' in df.columns else 'N/A'
            ]
        })
        summary.to_excel(writer, sheet_name='Summary Statistics', index=False)
        
        # Sector breakdown
        if 'company_sector' in df.columns:
            sector_summary = df.groupby('company_sector').agg({
                'company_name': 'nunique',
                'initiative_description': 'count'
            }).rename(columns={'company_name': 'Companies', 'initiative_description': 'Initiatives'})
            sector_summary.to_excel(writer, sheet_name='Sector Analysis')
    
    return output.getvalue()

def generate_citation_info():
    """Generate citation information for researchers"""
    current_date = datetime.now().strftime("%B %d, %Y")
    return f"""### 📚 How to Cite This Data
    
**Suggested Citation Format (APA 7th):**
```
Industrial Digital Economy Database. (2025). Malaysian companies digital 
transformation initiatives and PLCT framework analysis [Dataset]. 
Retrieved {current_date}, from https://ide-dashboard.streamlit.app
```

**Harvard Style:**
```
Industrial Digital Economy Database (2025) Malaysian companies digital 
transformation initiatives and PLCT framework analysis. Available at: 
https://ide-dashboard.streamlit.app (Accessed: {current_date}).
```

**Dataset Information:**
- **Source**: Annual reports from Malaysian public companies
- **Framework**: PLCT (People, Leadership, Culture, Technology)
- **Coverage Period**: 2019-2024
- **Total Observations**: 11,000+ digital initiatives
- **Last Updated**: December 2025
- **Methodology**: AI-assisted extraction with expert validation

**Research Use Guidelines:**
This dataset is provided for academic research, policy analysis, and 
educational purposes. Please ensure proper attribution when using this 
data in publications, presentations, reports, or derivative works.

**Data Quality:**
- Peer-reviewed extraction process
- Multi-stage validation protocol
- Source-verified metrics
- Regular updates and corrections
"""

def generate_methodology_section():
    """Generate detailed methodology information"""
    return """### 🔬 Research Methodology

**1. Data Collection Process**
- **Primary Sources**: Annual reports (2019-2024) from Bursa Malaysia listed companies
- **Extraction Method**: AI-powered text analysis using Google Gemini 2.0
- **Validation**: Multi-stage human review and verification process
- **Sample Size**: 1,345 companies, 11,231 digital initiatives documented

**2. PLCT Framework Application**
The PLCT (People, Leadership, Culture, Technology) framework assesses digital 
transformation across four key dimensions:

| Dimension | Focus Area | Score Range |
|-----------|-----------|-------------|
| **People** | Customer Experience Enhancement | 0-100 |
| **Leadership** | Employee Empowerment | 0-100 |
| **Culture** | Operational Efficiency | 0-100 |
| **Technology** | Business Model Innovation | 0-100 |

**Total PLCT Score**: Sum of all dimensions (0-400)

**3. Scoring Methodology**
- **Disclosure Quality**: Assessment of reporting completeness (0-100)
- **Innovation Level**: Classification as Incremental/Moderate/Transformational
- **Strategic Priority**: Categorization as High/Medium/Low based on investment and emphasis
- **Stakeholder Weighting**: Adjusted scores for investor, policy, and strategic perspectives

**4. Data Quality Assurance**
- ✓ Cross-validation against multiple report sections
- ✓ Temporal consistency checks
- ✓ Sector-specific benchmark validation
- ✓ Investment amount verification
- ✓ Technology classification standardization

**5. Analytical Limitations**
- Self-reported data from annual reports (potential reporting bias)
- Varying levels of disclosure across companies
- Temporal lag between initiative launch and reporting
- Limited visibility into proprietary/confidential projects

**6. Updates and Maintenance**
- Quarterly data refreshes
- Continuous methodology refinement
- Integration of new reporting frameworks
- Expansion to additional companies and sectors
"""

def render_data_quality_dashboard(df):
    """Render comprehensive data quality metrics"""
    st.markdown("### 📊 Data Quality Assessment")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**Completeness**")
        total = len(df)
        complete_initiatives = df['initiative_description'].notna().sum()
        st.progress(complete_initiatives / total)
        st.caption(f"{complete_initiatives/total*100:.1f}% complete descriptions")
    
    with col2:
        st.markdown("**Investment Data**")
        has_investment = df['investment_amount'].notna().sum()
        st.progress(has_investment / total)
        st.caption(f"{has_investment/total*100:.1f}% with investment info")
    
    with col3:
        st.markdown("**PLCT Scoring**")
        has_plct = df['plct_total_score'].notna().sum() if 'plct_total_score' in df.columns else 0
        st.progress(has_plct / total if total > 0 else 0)
        st.caption(f"{has_plct/total*100:.1f}% scored")
    
    with col4:
        st.markdown("**Timeline Data**")
        has_timeline = df['timeline'].notna().sum() if 'timeline' in df.columns else 0
        st.progress(has_timeline / total if total > 0 else 0)
        st.caption(f"{has_timeline/total*100:.1f}% with timeline")
    
    # Additional quality metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "High Quality Records",
            f"{len(df[df['disclosure_quality_total_score'] >= 70]):,}" if 'disclosure_quality_total_score' in df.columns else "N/A",
            help="Records with disclosure quality score ≥ 70/100"
        )
    
    with col2:
        st.metric(
            "Verified Investments",
            f"{df['investment_amount'].notna().sum():,}",
            help="Initiatives with documented investment amounts"
        )
    
    with col3:
        st.metric(
            "Multi-year Tracking",
            f"{df.groupby('company_name')['report_year'].nunique().gt(1).sum():,}",
            help="Companies with multiple years of data"
        )

def render_statistical_summary(df):
    """Render comprehensive statistical summary for researchers"""
    st.markdown("### 📈 Statistical Overview")
    
    # Descriptive statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Sample Characteristics**")
        stats_df = pd.DataFrame({
            'Metric': [
                'Sample Size (n)',
                'Unique Companies',
                'Industry Sectors',
                'Initiative Categories',
                'Time Span (years)',
                'Mean Initiatives per Company',
                'Median Initiatives per Company'
            ],
            'Value': [
                f"{len(df):,}",
                f"{df['company_name'].nunique():,}",
                f"{df['company_sector'].nunique():,}",
                f"{df['ide_category'].nunique():,}" if 'ide_category' in df.columns else "N/A",
                f"{df['report_year'].max() - df['report_year'].min() + 1}",
                f"{len(df) / df['company_name'].nunique():.2f}",
                f"{df.groupby('company_name').size().median():.0f}"
            ]
        })
        st.dataframe(stats_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("**PLCT Score Statistics**")
        if 'plct_total_score' in df.columns:
            plct_stats = df['plct_total_score'].describe()
            stats_plct = pd.DataFrame({
                'Statistic': ['Mean', 'Std Dev', 'Min', '25th Percentile', 'Median', '75th Percentile', 'Max'],
                'Value': [
                    f"{plct_stats['mean']:.2f}",
                    f"{plct_stats['std']:.2f}",
                    f"{plct_stats['min']:.2f}",
                    f"{plct_stats['25%']:.2f}",
                    f"{plct_stats['50%']:.2f}",
                    f"{plct_stats['75%']:.2f}",
                    f"{plct_stats['max']:.2f}"
                ]
            })
            st.dataframe(stats_plct, hide_index=True, use_container_width=True)
        else:
            st.info("PLCT scores not available in current dataset")
    
    # Distribution visualizations
    st.markdown("---")
    st.markdown("**Distribution Analysis**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'digital_maturity_level' in df.columns:
            maturity_dist = df['digital_maturity_level'].value_counts()
            st.markdown("*Digital Maturity*")
            for level, count in maturity_dist.items():
                st.write(f"{level}: {count} ({count/len(df)*100:.1f}%)")
    
    with col2:
        if 'innovation_level' in df.columns:
            innovation_dist = df['innovation_level'].value_counts()
            st.markdown("*Innovation Classification*")
            for level, count in innovation_dist.items():
                st.write(f"{level}: {count} ({count/len(df)*100:.1f}%)")
    
    with col3:
        if 'strategic_priority' in df.columns:
            priority_dist = df['strategic_priority'].value_counts()
            st.markdown("*Strategic Priority*")
            for level, count in priority_dist.items():
                st.write(f"{level}: {count} ({count/len(df)*100:.1f}%)")
