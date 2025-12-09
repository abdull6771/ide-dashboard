# Digital Economy Research Index - Data Extraction Pipeline

## Overview

This project automates the extraction of digital transformation initiatives from annual and corporate governance reports of companies. The extracted data provides comprehensive metadata for investor, policy, corporate strategy, and academic analysis using AI-powered structured extraction.

## Features

- **Direct PDF Processing:** Extracts complete text from PDF reports using PyMuPDF
- **AI-Powered Extraction:** Uses Google Gemini 2.0 Flash for intelligent structured data extraction with PLCT Framework scoring
- **PLCT Framework Analysis:** Comprehensive scoring across 4 dimensions (Customer Experience, People Empowerment, Operational Efficiency, New Business Models)
- **MySQL Database:** Normalized schema storing companies and initiatives with detailed metadata
- **Interactive Dashboard:** Streamlit-based visualization with filtering and analytics

## System Architecture

The pipeline uses a direct extraction approach:

1. **PDF Reports** → Annual reports in PDF format
2. **Full Text Extraction** → Complete document text extraction using PyMuPDF
3. **AI Extraction** → Google Gemini 2.0 Flash processes full documents with structured prompts
4. **PLCT Scoring** → Automated scoring across 4 dimensions with stakeholder-weighted perspectives
5. **MySQL Storage** → Structured data stored in relational database
6. **Dashboard Visualization** → Streamlit dashboard for analysis and exploration

## Database Schema

The system uses two main tables:

- **companies**: Stores company-level information including sector, digital maturity level, PLCT dimensions, strategic priority
- **initiatives**: Stores detailed initiative information with PLCT scoring (25+ fields), stakeholder-weighted scores, disclosure quality assessment, and confidence levels

## PLCT Framework

The extraction system scores each initiative across 4 dimensions (0-100 scale):

- **Customer Experience (CX)**: Digital customer interactions, omnichannel platforms, personalization
- **People Empowerment (PE)**: Workforce development, digital skills training, collaboration tools
- **Operational Efficiency (OE)**: Process automation, supply chain digitalization, analytics
- **New Business Models (BM)**: Platform ecosystems, new revenue models, data monetization

Additional analysis includes:

- Stakeholder-weighted scores (Investor, Policy, Strategic perspectives)
- Disclosure quality scoring (Investment, Timeline, Metrics, Technical, Rationale)
- Confidence level assessment (High/Medium/Low)

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- MySQL 8.0 or higher
- Google AI API key (for Gemini 2.0 Flash)

### Installation Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-repo/ide-index-pipeline.git
   cd ide-index-pipeline
   ```

2. **Create a Virtual Environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # .venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory:

   ```env
   GOOGLE_API_KEY=your_google_ai_api_key_here
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=ide_index
   ```

5. **Set Up MySQL Database:**
   ```bash
   mysql -u root -p < schema.sql
   ```

## Usage

1. **Place PDF reports** in the `Annual_Report_all/` folder

2. **Run extraction:**

   ```bash
   python extract_initiatives.py
├── nl_query_helper.py       # Natural language query assistant   ```

3. **Launch dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

## Project Structure

````
IDE/
├── extract_initiatives.py    # Main extraction script
├── nl_query_helper.py       # Natural language query assistant├── dashboard.py         # Streamlit dashboard
├── schema.sql               # Database schema
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
├── Annual_Report_all/       # PDF reports directory
└── annual_reports/          # Additional reports (optional)
```</content>
  <parameter name="filePath">/Users/mac/Documents/PUBLIC/IDE/README.md
````
