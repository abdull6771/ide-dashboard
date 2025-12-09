from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
# Enable CORS for all origins (adjust in production for specific domains)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'ide_index')
}

def get_db_connection():
    """Create database connection"""
    return pymysql.connect(**DB_CONFIG)

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get dashboard metrics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Total initiatives
        cursor.execute("SELECT COUNT(*) as count FROM initiatives")
        total_initiatives = cursor.fetchone()['count']
        
        # Total companies
        cursor.execute("SELECT COUNT(DISTINCT company_id) as count FROM initiatives")
        total_companies = cursor.fetchone()['count']
        
        # Total sectors
        cursor.execute("SELECT COUNT(DISTINCT c.sector) as count FROM companies c INNER JOIN initiatives i ON c.id = i.company_id")
        total_sectors = cursor.fetchone()['count']
        
        # Total categories
        cursor.execute("SELECT COUNT(DISTINCT category) as count FROM initiatives WHERE category IS NOT NULL")
        total_categories = cursor.fetchone()['count']
        
        # Total technologies (count from JSON array)
        cursor.execute("SELECT technology_used FROM initiatives WHERE technology_used IS NOT NULL")
        tech_count = 0
        for row in cursor.fetchall():
            try:
                if row['technology_used']:
                    tech_list = json.loads(row['technology_used']) if isinstance(row['technology_used'], str) else row['technology_used']
                    if isinstance(tech_list, list):
                        tech_count += len(tech_list)
            except:
                pass
        
        conn.close()
        
        return jsonify({
            'total_initiatives': total_initiatives,
            'total_companies': total_companies,
            'total_sectors': total_sectors,
            'total_categories': total_categories,
            'total_technologies': tech_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get list of companies"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT DISTINCT c.id, c.name, c.sector, COUNT(i.id) as initiative_count
            FROM companies c
            LEFT JOIN initiatives i ON c.id = i.company_id
            GROUP BY c.id, c.name, c.sector
            ORDER BY c.name
        """)
        
        companies = cursor.fetchall()
        conn.close()
        
        return jsonify(companies)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/initiatives', methods=['GET'])
def get_initiatives():
    """Get initiatives with optional filters"""
    try:
        # Get filter parameters
        company_id = request.args.get('company_id')
        sector = request.args.get('sector')
        category = request.args.get('category')
        year = request.args.get('year')
        limit = request.args.get('limit', 100)
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Build query with filters
        query = """
            SELECT 
                i.id,
                c.name as company_name,
                c.sector as company_sector,
                i.report_year,
                i.category,
                i.description,
                i.innovation_level,
                i.digital_maturity_level,
                i.investment_amount,
                i.technology_used,
                i.strategic_priority
            FROM initiatives i
            INNER JOIN companies c ON i.company_id = c.id
            WHERE i.id IS NOT NULL
        """
        
        params = []
        
        if company_id:
            query += " AND i.company_id = %s"
            params.append(company_id)
        
        if sector:
            query += " AND c.sector = %s"
            params.append(sector)
        
        if category:
            query += " AND i.category = %s"
            params.append(category)
        
        if year:
            query += " AND i.report_year = %s"
            params.append(year)
        
        query += f" ORDER BY i.report_year DESC, c.name LIMIT {limit}"
        
        cursor.execute(query, params)
        initiatives = cursor.fetchall()
        
        # Parse JSON fields
        for initiative in initiatives:
            if initiative['technology_used']:
                try:
                    initiative['technology_used'] = json.loads(initiative['technology_used']) if isinstance(initiative['technology_used'], str) else initiative['technology_used']
                except:
                    initiative['technology_used'] = []
        
        conn.close()
        
        return jsonify(initiatives)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    """Get list of sectors with counts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT c.sector, COUNT(i.id) as count
            FROM companies c
            INNER JOIN initiatives i ON c.id = i.company_id
            WHERE c.sector IS NOT NULL
            GROUP BY c.sector
            ORDER BY count DESC
        """)
        
        sectors = cursor.fetchall()
        conn.close()
        
        return jsonify(sectors)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get list of initiative categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM initiatives
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        """)
        
        categories = cursor.fetchall()
        conn.close()
        
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-companies', methods=['GET'])
def get_top_companies():
    """Get top companies by initiative count"""
    try:
        limit = request.args.get('limit', 10)
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute(f"""
            SELECT c.name, COUNT(i.id) as initiative_count
            FROM companies c
            INNER JOIN initiatives i ON c.id = i.company_id
            GROUP BY c.id, c.name
            ORDER BY initiative_count DESC
            LIMIT {limit}
        """)
        
        companies = cursor.fetchall()
        conn.close()
        
        return jsonify(companies)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/maturity-distribution', methods=['GET'])
def get_maturity_distribution():
    """Get digital maturity level distribution"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT digital_maturity_level, COUNT(*) as count
            FROM initiatives
            WHERE digital_maturity_level IS NOT NULL
            GROUP BY digital_maturity_level
            ORDER BY count DESC
        """)
        
        distribution = cursor.fetchall()
        conn.close()
        
        return jsonify(distribution)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/yearly-trend', methods=['GET'])
def get_yearly_trend():
    """Get initiatives by year"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT report_year, COUNT(*) as count
            FROM initiatives
            WHERE report_year IS NOT NULL
            GROUP BY report_year
            ORDER BY report_year
        """)
        
        trends = cursor.fetchall()
        conn.close()
        
        return jsonify(trends)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/innovation-levels', methods=['GET'])
def get_innovation_levels():
    """Get innovation level distribution"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT innovation_level, COUNT(*) as count
            FROM initiatives
            WHERE innovation_level IS NOT NULL
            GROUP BY innovation_level
            ORDER BY count DESC
        """)
        
        levels = cursor.fetchall()
        conn.close()
        
        return jsonify(levels)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/technologies', methods=['GET'])
def get_technologies():
    """Get top technologies used"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("SELECT technology_used FROM initiatives WHERE technology_used IS NOT NULL")
        
        tech_count = {}
        for row in cursor.fetchall():
            try:
                if row['technology_used']:
                    tech_list = json.loads(row['technology_used']) if isinstance(row['technology_used'], str) else row['technology_used']
                    if isinstance(tech_list, list):
                        for tech in tech_list:
                            tech_count[tech] = tech_count.get(tech, 0) + 1
            except:
                pass
        
        # Sort and get top 20
        sorted_tech = sorted(tech_count.items(), key=lambda x: x[1], reverse=True)[:20]
        technologies = [{'technology': tech, 'count': count} for tech, count in sorted_tech]
        
        conn.close()
        
        return jsonify(technologies)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quick-insights', methods=['GET'])
def get_quick_insights():
    """Get quick insights for dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Most active company
        cursor.execute("""
            SELECT c.name, COUNT(i.id) as count
            FROM companies c
            INNER JOIN initiatives i ON c.id = i.company_id
            GROUP BY c.id, c.name
            ORDER BY count DESC
            LIMIT 1
        """)
        top_company = cursor.fetchone()
        
        # Leading sector
        cursor.execute("""
            SELECT c.sector, COUNT(i.id) as count
            FROM companies c
            INNER JOIN initiatives i ON c.id = i.company_id
            WHERE c.sector IS NOT NULL
            GROUP BY c.sector
            ORDER BY count DESC
            LIMIT 1
        """)
        top_sector = cursor.fetchone()
        
        # Dominant category
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
            SELECT report_year, COUNT(*) as count
            FROM initiatives
            WHERE report_year IS NOT NULL
            GROUP BY report_year
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
        
        conn.close()
        
        return jsonify({
            'top_company': top_company,
            'top_sector': top_sector,
            'top_category': top_category,
            'peak_year': peak_year,
            'transformational_count': transformational['count'] if transformational else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
