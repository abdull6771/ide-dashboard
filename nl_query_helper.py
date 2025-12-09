import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
import pymysql
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RAGQueryHelper:
    """Helper class for natural language database queries using Gemini AI"""
    
    def __init__(self, db_config):
        """
        Initialize RAG Query Helper
        
        Args:
            db_config: Dictionary with MySQL connection parameters
        """
        self.db_config = db_config
        
        # Initialize Gemini
        load_dotenv()
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            raise ValueError("Missing GOOGLE_API_KEY in environment")
        
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')
    
    def _get_schema_context(self):
        """Get database schema information for context"""
        return """
DATABASE SCHEMA:

Table: companies
- id (INT, PRIMARY KEY)
- company_name (VARCHAR, UNIQUE)
- company_sector (VARCHAR)
- year_mentioned (INT)
- report_type (VARCHAR)
- technology_used (JSON array)
- department (JSON array)
- digital_investment (TEXT)
- digital_maturity_level (VARCHAR: Basic/Developing/Advanced/Leading)
- plct_dimensions (JSON object)
- strategic_priority (VARCHAR: High/Medium/Low)

Table: initiatives
- id (INT, PRIMARY KEY)
- company_id (INT, FOREIGN KEY -> companies.id)
- category (VARCHAR)
- initiative (TEXT)
- plct_alignment (VARCHAR)
- expected_impact (TEXT)
- investment_amount (TEXT)
- timeline (JSON)
- success_metrics (JSON)
- business_rationale (TEXT)
- implementation_approach (TEXT)
- workforce_impact (JSON)
- technology_partners (TEXT)
- innovation_level (VARCHAR: Incremental/Moderate/Transformational)
- risk_factors (JSON)
- competitive_advantage (JSON)
- policy_implications (JSON)
- governance_structure (TEXT)
- data_strategy (TEXT)
- security_considerations (TEXT)
- sustainability_impact (TEXT)

PLCT Framework Scoring (initiatives table):
- plct_customer_experience_score (INT 0-100)
- plct_customer_experience_rationale (TEXT)
- plct_people_empowerment_score (INT 0-100)
- plct_people_empowerment_rationale (TEXT)
- plct_operational_efficiency_score (INT 0-100)
- plct_operational_efficiency_rationale (TEXT)
- plct_new_business_models_score (INT 0-100)
- plct_new_business_models_rationale (TEXT)
- plct_total_score (INT 0-400)
- plct_dominant_dimension (TEXT)
- plct_adjustment_factors (JSON)

Stakeholder Weighted Scores (initiatives table):
- plct_investor_weighted_score (DECIMAL)
- plct_policy_weighted_score (DECIMAL)
- plct_strategic_weighted_score (DECIMAL)

Disclosure Quality (initiatives table):
- disclosure_quality_investment_score (INT 0-30)
- disclosure_quality_timeline_score (INT 0-20)
- disclosure_quality_metrics_score (INT 0-25)
- disclosure_quality_technical_score (INT 0-15)
- disclosure_quality_rationale_score (INT 0-10)
- disclosure_quality_total_score (INT 0-100)
- disclosure_quality_tier (TEXT)

Confidence Assessment (initiatives table):
- confidence_level (TEXT: High/Medium/Low)
- confidence_justification (TEXT)
- confidence_flagged_for_verification (BOOLEAN)
- confidence_verification_notes (TEXT)

IMPORTANT JOIN:
To get company information with initiatives, use:
SELECT ... FROM initiatives i JOIN companies c ON i.company_id = c.id
"""
    
    def _generate_sql(self, question):
        """
        Generate SQL query from natural language question
        
        Args:
            question: Natural language question
            
        Returns:
            SQL query string
        """
        prompt = f"""You are a SQL expert. Convert the following natural language question into a MySQL query.

{self._get_schema_context()}

USER QUESTION: {question}

RULES:
1. Generate ONLY valid MySQL SELECT queries
2. Use JOINs when accessing both companies and initiatives data
3. Use appropriate aggregations (COUNT, AVG, SUM, etc.) when needed
4. Include company_name in results when relevant
5. Order results meaningfully (DESC for counts/scores)
6. Limit results to 50 rows maximum unless explicitly asked for more
7. Handle JSON columns carefully - use JSON_EXTRACT if needed
8. Return ONLY the SQL query, no explanations

SQL QUERY:"""

        try:
            response = self.model.generate_content(prompt)
            sql = response.text.strip()
            
            # Clean up markdown formatting if present
            if sql.startswith('```sql'):
                sql = sql[6:]
            if sql.startswith('```'):
                sql = sql[3:]
            if sql.endswith('```'):
                sql = sql[:-3]
            
            sql = sql.strip()
            logging.info(f"Generated SQL: {sql}")
            return sql
            
        except Exception as e:
            logging.error(f"Error generating SQL: {e}")
            raise
    
    def _execute_query(self, sql):
        """
        Execute SQL query and return results as DataFrame
        
        Args:
            sql: SQL query string
            
        Returns:
            pandas DataFrame with results
        """
        try:
            conn = pymysql.connect(
                **self.db_config,
                connect_timeout=30,
                read_timeout=30,
                write_timeout=30
            )
            df = pd.read_sql(sql, conn)
            conn.close()
            logging.info(f"Query returned {len(df)} rows")
            return df
            
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            raise
    
    def _generate_insights(self, question, sql, data):
        """
        Generate natural language insights from query results
        
        Args:
            question: Original user question
            sql: SQL query that was executed
            data: DataFrame with results
            
        Returns:
            Insights as markdown string
        """
        if data.empty:
            return "No results found for your query."
        
        # Prepare data summary
        data_summary = f"Query returned {len(data)} rows with {len(data.columns)} columns.\n\n"
        data_summary += "Column names: " + ", ".join(data.columns) + "\n\n"
        
        # Include sample data (first 10 rows)
        sample_data = data.head(10).to_string()
        data_summary += f"Sample data:\n{sample_data}\n\n"
        
        # Add basic statistics for numeric columns
        numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            data_summary += "Numeric statistics:\n"
            for col in numeric_cols:
                data_summary += f"- {col}: min={data[col].min():.1f}, max={data[col].max():.1f}, avg={data[col].mean():.1f}\n"
        
        prompt = f"""You are a research analyst. Provide insights and analysis based on the query results.

USER QUESTION: {question}

EXECUTED SQL: {sql}

DATA SUMMARY:
{data_summary}

Provide a clear, concise analysis that:
1. Directly answers the user's question
2. Highlights key findings and patterns
3. Provides context and interpretation
4. Uses bullet points for clarity
5. Mentions specific numbers and company names when relevant
6. Keeps it under 200 words

ANALYSIS:"""

        try:
            response = self.model.generate_content(prompt)
            insights = response.text.strip()
            logging.info("Generated insights successfully")
            return insights
            
        except Exception as e:
            logging.error(f"Error generating insights: {e}")
            return f"Results returned {len(data)} rows. Analysis unavailable due to error."
    
    def query(self, question):
        """
        Main method to process natural language query
        
        Args:
            question: Natural language question
            
        Returns:
            Tuple of (sql_query, dataframe, insights)
        """
        try:
            # Generate SQL
            sql = self._generate_sql(question)
            
            # Execute query
            data = self._execute_query(sql)
            
            # Generate insights
            insights = self._generate_insights(question, sql, data)
            
            return sql, data, insights
            
        except Exception as e:
            logging.error(f"Error in query pipeline: {e}")
            raise
