# 📊 Malaysian Digital Transformation Research Dashboard

An interactive data analytics dashboard analyzing digital transformation initiatives across Malaysian listed companies based on annual report disclosures (2017-2023).

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 🎯 Overview

This research dashboard provides comprehensive visual analytics of digital transformation trends among Malaysian public companies, examining how organizations communicate their digitalization strategies through annual reports.

### Key Features

- **📈 Yearly Trend Analysis**: Track digital transformation adoption from 2017-2023
- **🏢 Company Rankings**: Identify leading organizations in digital transformation
- **🔍 Initiative Tracking**: Monitor 11,792 digital initiatives across 925 companies
- **📊 Sector Analysis**: Compare digital maturity across different industries
- **💡 Technology Insights**: Analyze adoption of AI, Cloud, IoT, Blockchain, and more
- **🎯 PLCT Framework**: Evaluate initiatives across People, Leadership, Culture, and Technology dimensions
- **📉 Disclosure Quality Metrics**: Assess reporting transparency and depth

## 🚀 Live Demo

**Dashboard**: [View Live Dashboard](https://your-app-url.streamlit.app)

## 📊 Dataset Statistics

- **Companies Analyzed**: 2,506 (925 unique companies)
- **Digital Initiatives**: 11,792
- **Years Covered**: 2017-2023
- **Annual Reports Processed**: 2,506
- **Sectors**: 12 major industry sectors

## 🛠️ Technology Stack

### Backend

- **Python 3.12**
- **MySQL** (Railway Cloud Database)
- **Streamlit** - Interactive web framework
- **Pandas** - Data manipulation
- **Plotly** - Interactive visualizations

### Database

- **Railway MySQL Cloud Database**
  - 3 core tables (companies, initiatives, unique_companies)
  - Real-time data access
  - Secure cloud hosting

### Deployment

- **Streamlit Cloud** - Dashboard hosting
- **GitHub** - Version control

## 📁 Project Structure

```
.
├── streamlit_dashboard.py      # Main Streamlit dashboard application
├── extract_initiatives.py      # Data extraction and processing
├── export_database_tables.py   # Database export utilities
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in repo)
├── schema.sql                  # Database schema
└── utils/                      # Utility scripts
    ├── export_for_looker_studio.py
    ├── export_research_dataset.py
    └── ...
```

## 🔧 Local Setup

### Prerequisites

- Python 3.12+
- Git

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/abdull6771/ide-dashboard.git
cd ide-dashboard
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the root directory:

```env
MYSQL_HOST=yamabiko.proxy.rlwy.net
MYSQL_PORT=22359
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=railway
```

5. **Run the dashboard**

```bash
streamlit run streamlit_dashboard.py
```

The dashboard will open at `http://localhost:8501`

## 🌐 Deployment to Streamlit Cloud

1. **Push to GitHub**

```bash
git add .
git commit -m "Your message"
git push origin main
```

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io/)
   - Sign in with GitHub
   - Click "New app"
   - Select repository: `abdull6771/ide-dashboard`
   - Main file: `streamlit_dashboard.py`
   - Add secrets in Advanced Settings (same as .env file)
   - Deploy!

## 📊 Database Schema

### Tables

**companies**

- Company information and annual report metadata
- 2,506 records

**initiatives**

- Digital transformation initiatives extracted from reports
- 11,792 records
- Categories: AI, Cloud, IoT, Blockchain, Big Data, etc.

**unique_companies**

- Deduplicated company master list
- 925 unique organizations

## 🔍 Research Methodology

This dashboard is built on a comprehensive analysis of annual reports from Malaysian listed companies:

1. **Data Collection**: Automated extraction from annual reports (2017-2023)
2. **Text Analysis**: NLP-based identification of digital transformation keywords
3. **Categorization**: Classification using PLCT framework (People, Leadership, Culture, Technology)
4. **Validation**: Manual review and quality checks
5. **Visualization**: Interactive dashboards for insight discovery

## 📈 Key Insights

- Digital transformation disclosure increased **245%** from 2017 to 2023
- **Technology sector** leads with 35% of all initiatives
- **Cloud Computing** and **AI** show highest growth rates
- **Leadership** dimension has strongest correlation with successful implementation

## 🤝 Contributing

This is a research project. For questions or collaboration inquiries, please open an issue.

## 📄 License

This project is for academic research purposes.

## 👨‍💻 Author

**Abdullah**

- GitHub: [@abdull6771](https://github.com/abdull6771)

## 📧 Contact

For research collaboration or data access requests, please open an issue in this repository.

---

**Note**: This dashboard is part of ongoing research on digital transformation in Malaysian corporate sector. Data is continuously updated as new annual reports become available.
