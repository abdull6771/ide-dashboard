import os
import logging
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai
import mysql.connector
import fitz
import pandas as pd
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

REPORTS_DIR = "Annual_Report_all"
PROCESSED_FILES_LOG = "processed_files.json"


# Load company code lookup
def load_company_lookup():
    """Load company code lookup from JSON"""
    try:
        with open('company_code_lookup.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"Could not load company_code_lookup.json: {e}")
        return {}


# Load company codes by year
def load_company_codes_by_year():
    """Load all company codes by year from CSV"""
    try:
        df = pd.read_csv('company_codes_all_years.csv')
        return df
    except Exception as e:
        logging.warning(f"Could not load company_codes_all_years.csv: {e}")
        return pd.DataFrame()


def extract_text_from_pdf(pdf_path):
    """Extract all text from PDF"""
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            full_text += page.get_text() + "\n"
        
        doc.close()
        return full_text
        
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return None


def build_extraction_prompt(text, filename):
    """Build extraction prompt for full document"""
    return f"""
You are a digital economy research analyst extracting data for investor, policy, corporate strategy, and academic analysis.
Analyze the following complete company report and extract ALL digital transformation initiatives with comprehensive metadata for multi-stakeholder analysis using the PLCT Framework.

Source File: {filename}

PLCT FRAMEWORK OVERVIEW
======================
PLCT stands for the four foundational transformation dimensions:
1. Customer Experience (CX): Digital initiatives improving customer interactions, omnichannel platforms, personalization engines, customer analytics, customer service automation.
2. People Empowerment (PE): Workforce development, digital skills training, learning platforms, collaboration tools, HR digitalization, remote work enablement.
3. Operational Efficiency (OE): Process optimization, automation, predictive maintenance, supply chain digitalization, ERP modernization, data analytics for operations.
4. New Business Models (BM): Platform ecosystems, subscription/recurring revenue, data monetization, digital products/services, ecosystem partnerships.

EXTRACTION REQUIREMENTS:
✅ Company Name, Industry Sector, Year, Report Type
✅ ALL digital initiatives, AI projects, automation, digitization efforts, technology investments
✅ Investment amounts, timelines, success metrics where mentioned
✅ Strategic rationale and business context
✅ Implementation approaches and methodologies
✅ Skills/workforce impact and policy implications
✅ PLCT Framework scoring and analysis (dimension scores, PLCT total, dominant dimension)
✅ Disclosure quality assessment and confidence levels
✅ Respond with ONLY valid JSON - no explanations, no markdown, no extra text
✅ Your response must start with [ and end with ]

REQUIRED JSON FORMAT:
[
  {{
    "CompanyName": "Exact company name from report",
    "CompanySector": "Primary industry sector - Technology, Manufacturing, Financial Services, Healthcare, Retail, Energy, Telecommunications, Construction, Transportation, Real Estate, Agriculture, Business Services, etc.",
    "YearMentioned": "2023",
    "ReportType": "Annual Report",
    "TechnologyUsed": ["AI", "Machine Learning", "Cloud Computing"],
    "Department": ["IT", "Operations", "Finance"],
    "DigitalInvestment": "$X million" or "percentage" or description,
    "DigitalMaturityLevel": "Basic/Developing/Advanced/Leading",
    "PLCTDimensions": {{
      "CustomerExperience": "Company-level CX focus: omnichannel platforms, customer analytics, digital touchpoints mentioned",
      "PeopleEmpowerment": "Company-level PE focus: workforce transformation, digital skills programs, culture change mentioned",
      "OperationalEfficiency": "Company-level OE focus: automation, process optimization, supply chain digital transformation",
      "NewBusinessModels": "Company-level BM focus: platform strategies, new revenue models, ecosystem partnerships"
    }},
    "StrategicPriority": "High/Medium/Low",
    "Initiatives": [
      {{
        "Category": "Process Automation",
        "Initiative": "Specific initiative description",
        "PLCTAlignment": "Primary PLCT dimension(s) - CustomerExperience, PeopleEmpowerment, OperationalEfficiency, NewBusinessModels, or combination like 'OperationalEfficiency + CustomerExperience'",
        "ExpectedImpact": "Expected outcome or benefit - NEVER leave empty, always infer from context",
        "InvestmentAmount": "Specific amount if mentioned, otherwise estimate scale: Minor/Moderate/Major/Strategic with estimated range",
        "Timeline": {{
          "start": "2024 Q1 or estimated year",
          "duration": "18 months or estimated duration", 
          "end": "2025 Q2 or estimated",
          "phases": ["Planning: Q1 2024", "Implementation: Q2-Q4 2024"] or estimated phases
        }},
        "SuccessMetrics": {{
          "baseline": "current state or estimated baseline",
          "target": "specific improvement target or estimated improvement",
          "measurement": "how success will be measured or estimated measurement approach",
          "kpis": ["specific KPIs mentioned or estimated relevant KPIs"]
        }},
        "BusinessRationale": "Strategic reasoning and business case - NEVER empty, infer from strategic context",
        "ImplementationApproach": "How they plan to execute - extract or infer: phased rollout, pilot-then-scale, agile, waterfall, etc.",
        "WorkforceImpact": {{
          "skillsDevelopment": "specific skills or infer from technology: digital skills, technical training, etc.",
          "trainingHours": "quantified commitment or estimate: 20-40 hours for basic, 40-80 for advanced",
          "jobsAffected": "number of roles or estimate scope: department-wide, company-wide, specific teams",
          "upskilling": "programs mentioned or infer: reskilling program, continuous learning, certification",
          "redundancyRisk": "potential displacement or estimate: minimal, moderate automation, transformation"
        }},
        "TechnologyPartners": "Vendors, consultants, or technology partners mentioned",
        "InnovationLevel": "Incremental/Moderate/Transformational",
        "RiskFactors": {{
          "technicalRisks": "technology-related challenges",
          "financialRisks": "budget or ROI concerns", 
          "changeManagementRisks": "people and culture challenges",
          "mitigationStrategies": "how risks are being addressed"
        }},
        "CompetitiveAdvantage": {{
          "description": "how this creates differentiation",
          "quantifiedBenefit": "measurable advantage gained",
          "marketPosition": "impact on competitive position"
        }},
        "PolicyImplications": {{
          "regulatoryRequirements": "compliance needs",
          "infrastructureNeeds": "government infrastructure required",
          "skillsPolicy": "implications for national skills development",
          "economicImpact": "broader economic implications"
        }},
        "GovernanceStructure": "oversight and governance approach mentioned",
        "DataStrategy": "data management and analytics approach",
        "SecurityConsiderations": "cybersecurity and data protection measures",
        "SustainabilityImpact": "environmental or ESG implications",
        
        "PLCTScoring": {{
          "CustomerExperienceScore": 45,
          "CustomerExperienceRationale": "EXAMPLE: Score 45 (Moderate) because: Initiative focuses on digital printers improving customer turnaround times (CX impact). Single-channel improvement (digital printing output), basic metrics tracking (turnaround time only). No personalization, omnichannel, or advanced customer analytics mentioned. Investment moderate. Aligns with 41-60 range for incremental impact with some quantified objectives.",
          "PeopleEmpowermentScore": 35,
          "PeopleEmpowermentRationale": "EXAMPLE: Score 35 (Low) because: Training mentioned (40-80 hours estimated) but limited scope. No comprehensive program, no certification pathways, no culture change initiatives. Affects specific department only (printing/packaging). Falls in 21-40 range for minimal training programs and technology deployment focused.",
          "OperationalEfficiencyScore": 70,
          "OperationalEfficiencyRationale": "EXAMPLE: Score 70 (High) because: Direct automation of workflow processes through digital printers and software. Mentions faster turnaround times and cost reduction potential. Clear efficiency targets (reduced turnaround). Multi-functional impact (printing + workflow). Quantified benefits mentioned. Fits 61-80 range for significant automation with clear targets and quantified benefits.",
          "NewBusinessModelsScore": 15,
          "NewBusinessModelsRationale": "EXAMPLE: Score 15 (Minimal) because: No new business model mentioned. No platform, subscription, data monetization, or ecosystem partnerships. Pure operational improvement. No revenue stream innovation. Falls in 0-20 range - operational improvements only, no revenue impact.",
          "TotalPLCTScore": 165,
          "DominantDimension": "OperationalEfficiency",
          "AdjustmentFactors": {{
            "evidenceQuality": "Investment scale mentioned (Moderate RM 500K-5M) - +5 points. Timeline partially specified - +3 points. Some metrics (turnaround time) - +2 points. No named technology partners - 0 points. Phased approach mentioned - +2 points. Total adjustment: +12 points applied to OE score.",
            "sectorContext": "Manufacturing sector: High OE expected (automation, productivity focus) - initiative aligns well with sector average. Moderate PE and low CX/BM typical for manufacturing B2B context. No sector-based penalty.",
            "adjustmentApplied": "+5 OE (evidence quality premium), Sector-aligned, Final OE Score: 70"
          }}
        }},
        
        "StakeholderWeightedScores": {{
          "InvestorWeighted": 51.5,
          "InvestorWeightedFormula": "(45×0.3) + (35×0.1) + (70×0.3) + (15×0.3) = 13.5 + 3.5 + 21 + 4.5 = 42.5 ADJUSTED to 51.5 based on efficiency gains and cost reduction potential",
          "PolicyWeighted": 38.0,
          "PolicyWeightedFormula": "(45×0.2) + (35×0.4) + (70×0.2) + (15×0.2) = 9 + 14 + 14 + 3 = 40 ADJUSTED to 38.0 - Limited workforce upskilling reduces policy interest",
          "StrategicWeighted": 41.25,
          "StrategicWeightedFormula": "(45×0.25) + (35×0.25) + (70×0.25) + (15×0.25) = 11.25 + 8.75 + 17.5 + 3.75 = 41.25 - Balanced view shows moderate transformation potential"
        }},
        
        "DisclosureQualityScore": {{
          "investmentDisclosure": 10,
          "investmentDisclosureExplanation": "Scale mentioned (Moderate investment) but no specific amount - 10 points",
          "timelineDisclosure": 15,
          "timelineDisclosureExplanation": "Start date (2023) and duration (12-24 months) provided, estimated end date - 15 points",
          "metricsAndKpis": 15,
          "metricsAndKpisExplanation": "Qualitative success indicators (faster turnaround, customer satisfaction) mentioned, some quantification on impact - 15 points",
          "technicalDetail": 10,
          "technicalDetailExplanation": "Technology category (digital printers, workflow software) mentioned but no specific vendor names - 10 points",
          "businessRationale": 10,
          "businessRationaleExplanation": "Clear strategic rationale (competitiveness, efficiency) with industry context provided - 10 points",
          "totalScore": 60,
          "totalScoreCalculation": "10 + 15 + 15 + 10 + 10 = 60 points",
          "qualityTier": "Good (60-79) - Suitable for benchmarking and trend analysis, adequate for industry comparison"
        }},
        
        "ConfidenceLevel": {{
          "level": "Medium",
          "justification": "Medium confidence: Initiative description is clear and explicit (digital printers + workflow automation). Timeline and investment scale provided but not quantified amounts. Success metrics qualitative with some quantification (turnaround time, satisfaction). Some interpretation required for PLCT scoring as initiative details focus on operations. No conflicting information. Single source in annual report.",
          "flaggedForVerification": true,
          "verificationNotes": "Recommend independent verification: (1) Specific investment amount and actual ROI targets, (2) Quantified baseline and target turnaround times, (3) Actual vendor names and technology partners, (4) Detailed training curriculum and hours commitment, (5) Metrics on job displacement vs. productivity gains"
        }}
      }}
    ]
  }}
]

COMPANY-LEVEL FIELD EXTRACTION GUIDELINES
==========================================

TECHNOLOGY USED:
✅ Extract ALL technology categories mentioned across ALL initiatives in the report
✅ Look for: AI, Machine Learning, Cloud Computing, Blockchain, IoT, RPA, Big Data, Analytics, ERP Systems, CRM, Mobile Apps, E-commerce Platforms, Cybersecurity, Digital Payments, etc.
✅ Consolidate technologies from all initiatives into a single comprehensive list at company level
✅ Include both explicitly named technologies AND technology categories mentioned
✅ NEVER leave empty - if no specific technologies mentioned, infer from initiative descriptions: ["Digital Technologies", "Information Systems", "Automation Tools"]

DEPARTMENT:
✅ Extract ALL departments mentioned as being involved in digital initiatives across the entire report
✅ Look for: IT, Operations, Finance, HR, Marketing, Sales, Customer Service, Supply Chain, Manufacturing, R&D, Strategy, Risk Management, Compliance, etc.
✅ Consolidate departments from all initiatives into a single comprehensive list at company level
✅ Include departments explicitly named AND implied by initiative descriptions
✅ NEVER leave empty - if no departments mentioned, infer from initiative context: ["Operations"] for automation, ["IT"] for technology projects, ["Multiple Departments"] for transformation

PLCT DIMENSIONS (Company Level):
✅ Provide a company-wide summary of PLCT focus based on ALL initiatives in the report
✅ For each dimension, write 1-2 sentences describing the company's overall strategy and focus
✅ CustomerExperience: Summarize company-wide customer experience digital initiatives
✅ PeopleEmpowerment: Summarize workforce development, training, and cultural transformation efforts
✅ OperationalEfficiency: Summarize process automation, optimization, and efficiency initiatives
✅ NewBusinessModels: Summarize platform strategies, new revenue models, and ecosystem partnerships
✅ If a dimension has NO initiatives, state: "No company-level [dimension] focus mentioned in this report"
✅ ALWAYS provide content for all 4 dimensions - never leave empty

EXAMPLE - Technology & Departments Extraction:
If report mentions:
- Initiative 1: "Implementing AI-powered chatbot for customer service"
- Initiative 2: "RPA deployment in finance operations"
- Initiative 3: "Cloud migration of ERP systems across IT and operations"

Then extract:
"TechnologyUsed": ["AI", "Chatbots", "RPA", "Cloud Computing", "ERP Systems"]
"Department": ["Customer Service", "Finance", "IT", "Operations"]

PLCT DIMENSION SCORING RUBRIC (0-100 Scale)
============================================

CUSTOMER EXPERIENCE (CX) - Key Indicators:
✅ Omnichannel platforms (mobile apps, web portals, self-service)
✅ Personalization engines (recommendation systems, tailored offers)
✅ Customer analytics (journey mapping, sentiment analysis, behavioral insights)
✅ Digital marketing and engagement (social media, content platforms)
✅ Customer service automation (chatbots, AI assistants, ticketing systems)

Scoring Scale:
81-100 (Transformational): Multi-channel integration, personalization at scale, measurable customer metrics, enterprise-wide CX transformation, industry-leading capabilities
61-80 (High): Significant multi-channel improvements, clear personalization strategy, integrated systems, quantified customer satisfaction targets
41-60 (Moderate): Clear but incremental impact, multi-function efforts, some quantified objectives, medium investment
21-40 (Low): Single-channel improvements, basic analytics, limited personalization, minor impact, no quantified metrics
0-20 (Minimal): Backend only, no customer impact, generic description, infrastructure only

PEOPLE EMPOWERMENT (PE) - Key Indicators:
✅ Digital skills training (coding, data analytics, digital literacy programs)
✅ Learning platforms (LMS, e-learning, certification programs)
✅ Collaboration tools (Microsoft Teams, Slack, digital workplaces)
✅ HR digitalization (talent management, performance tracking, recruitment)
✅ Remote work enablement (VPN, cloud access, virtual meeting tools)

Scoring Scale:
81-100 (Transformational): Comprehensive training programs, measurable skills development, culture change initiatives, 500+ employees trained, certification pathways, 40-80+ training hours
61-80 (High): Significant training programs, clear upskilling strategy, multi-level capability building, quantified employee targets
41-60 (Moderate): Clear workforce impact, limited training scope, basic collaboration tools, some upskilling mentioned
21-40 (Low): Minimal training programs, technology deployment only, indirect workforce impact, no training mentioned
0-20 (Minimal): Technology only, no training or development, generic HR mentions

OPERATIONAL EFFICIENCY (OE) - Key Indicators:
✅ Process automation (RPA, workflow automation, document processing)
✅ Predictive maintenance (IoT sensors, ML models, asset optimization)
✅ Supply chain digitalization (tracking, optimization, supplier integration)
✅ ERP/Core system modernization (cloud ERP, integrated systems)
✅ Data analytics for operations (dashboards, performance monitoring, optimization)

Scoring Scale:
81-100 (Transformational): End-to-end automation, measurable efficiency gains (30%+ improvements), cross-functional integration, enterprise-wide impact, 40%+ cost reduction
61-80 (High): Significant automation, clear efficiency targets, integrated systems, quantified benefits (20-30% improvements)
41-60 (Moderate): Clear but incremental impact, point solutions, some automation, limited integration, 10-20% improvements
21-40 (Low): Minimal efficiency impact, isolated improvements, no quantified benefits, pilot projects
0-20 (Minimal): Isolated efforts, no clear efficiency gains, backend only, generic efficiency mentions

NEW BUSINESS MODELS (BM) - Key Indicators:
✅ Platform business models (marketplaces, ecosystems, API monetization)
✅ Subscription/recurring revenue models (SaaS, membership programs)
✅ Data monetization (analytics services, insights products)
✅ Digital products/services (complementary to physical offerings)
✅ Ecosystem partnerships (co-creation, revenue sharing, network effects)

Scoring Scale:
81-100 (Transformational): New revenue streams, platform economics, ecosystem participation (100+ partners), transformational business model change, RM 50M+ annual revenue potential
61-80 (High): Clear new business models, revenue generation planned, platform strategy, moderate ecosystem development
41-60 (Moderate): Incremental revenue opportunities, digital extensions, limited transformation, pilot monetization efforts
21-40 (Low): Minor new revenue potential, operational improvements only, no clear business model change
0-20 (Minimal): No new business model, traditional improvements, no revenue impact

SECTOR-SPECIFIC ADJUSTMENTS:
Banking/Financial Services: High CX expected (digital banking), moderate OE (core banking), lower BM (regulatory)
Manufacturing: High OE expected (automation, IoT), moderate PE (skills), lower CX (B2B)
Retail: High CX expected (e-commerce), moderate OE (supply chain), moderate BM (platforms)
Technology: High across all dimensions (digital-native)
Healthcare: High CX (patient experience), high PE (staff training), moderate OE, lower BM
Energy/Utilities: High OE (grid optimization, predictive maintenance), moderate PE, lower CX

EVIDENCE-BASED SCORE ADJUSTMENTS:
Increase score if present:
✅ Specific investment amount (shows commitment)
✅ Quantified KPIs/metrics (shows measurability)
✅ Timeline with milestones (shows planning rigor)
✅ Technology partners named (shows execution readiness)
✅ Expected ROI or impact quantified (shows business case)
✅ Risk mitigation strategies (shows sophistication)
Increase: +5-10 points per factor

Decrease score if absent:
❌ Vague language ("exploring", "considering", "planning to")
❌ No quantified outcomes
❌ No investment amount disclosed
❌ No timeline or milestones
❌ Generic technology descriptions
❌ No risk mitigation mentioned
Decrease: -5-10 points per factor

DISCLOSURE QUALITY SCORING
===========================
Investment Disclosure (30 points):
30: Specific amount in specific currency (RM 15M, $5M, etc.)
20: Range provided (RM 5-10 million)
10: Scale only (major investment, significant capex)
0: No investment information

Timeline Disclosure (20 points):
20: Start date, duration, AND milestones
15: Start date AND duration
10: Year or general timeframe
0: No timeline

Metrics & KPIs (25 points):
25: Quantified success metrics with specific targets
15: Qualitative success indicators described
5: Generic benefits mentioned
0: No success metrics

Technical Detail (15 points):
15: Specific technologies AND vendors named
10: Technology category mentioned
5: Generic "digital" or "technology" reference
0: No technical detail

Business Rationale (10 points):
10: Clear strategic rationale WITH competitive context
5: Generic rationale mentioned
0: No rationale provided

Quality Tiers:
80-100: Comprehensive (suitable for detailed analysis, investment research)
60-79: Good (ideal for benchmarking, trend analysis)
40-59: Moderate (suitable only for high-level insights)
0-39: Limited (insufficient for analysis)

CONFIDENCE LEVEL ASSESSMENT
============================
High Confidence:
✅ Specific quantified data extracted
✅ Clear initiative description
✅ Detailed disclosure (quality score >75)
✅ Cross-validated from multiple report sections
✅ No ambiguity in interpretation

Medium Confidence:
✅ Some quantified data
✅ Adequate description
✅ Moderate disclosure (quality score 50-75)
✅ Single source in report
✅ Minor interpretation required

Low Confidence:
✅ Minimal quantified data
✅ Vague description
✅ Limited disclosure (quality score <50)
✅ Interpretation heavily required
✅ Conflicting information in report

SECTOR IDENTIFICATION GUIDELINES:
🎯 Extract from business description, nature of operations, or industry classification
🎯 Common sectors to identify:
   - Manufacturing, Financial Services, Technology, Healthcare, Retail, Energy
   - Telecommunications, Construction, Transportation, Real Estate, Agriculture, Business Services
🎯 Choose the PRIMARY sector based on revenue

EXTRACTION GUIDELINES:
INVESTMENT AMOUNT EXTRACTION:
🎯 Priority 1: Extract EXACT amounts mentioned in text (e.g., "RM 5 million", "$2M", "15% of revenue")
🎯 Priority 2: Extract ranges if mentioned: "between $1-5M" → "RM 1-5 million estimated"
🎯 Priority 3: Extract contextual indicators and estimate scale:
   - "pilot", "trial" → "Minor investment (estimated < RM 500K)"
   - "significant investment" → "Moderate (estimated RM 500K - 5M)"
   - "major capital expenditure" → "Major (estimated RM 5M - 20M)"
   - "strategic transformation" → "Strategic (estimated > RM 20M)"
🎯 Priority 4: If NO direct financial clues, estimate from initiative scope:
   - Single department, basic tech → "Minor investment estimated"
   - Multiple departments, proven tech → "Moderate investment estimated"
   - Company-wide, advanced tech → "Major investment estimated"
   - Business transformation, cutting-edge tech → "Strategic investment estimated"
🎯 NEVER use "Not specified" - always provide an estimated scale with qualifier

TIMELINE - STRUCTURED FORMAT:
🎯 If explicit dates exist: {{"start": "2024 Q1", "duration": "18 months", "end": "2025 Q2", "phases": ["Planning: Q1 2024", "Implementation: Q2-Q4 2024"]}}
🎯 If partial information: {{"start": "2023", "status": "ongoing", "estimated_completion": "2025"}}
🎯 If no timeline mentioned, estimate based on complexity:
   - Pilot/PoC: {{"estimated_start": "[report year]", "estimated_duration": "6-12 months", "status": "planned/ongoing"}}
   - Implementation: {{"estimated_start": "[report year]", "estimated_duration": "12-24 months", "status": "ongoing"}}
   - Transformation: {{"estimated_start": "[report year or prior]", "estimated_duration": "24-36 months", "status": "multi-year initiative"}}

SUCCESS METRICS - ALWAYS PROVIDE:
🎯 If quantified targets exist: {{"baseline": "current: X", "target": "achieve Y", "measurement": "measured by Z", "kpis": ["KPI1", "KPI2"]}}
🎯 If qualitative only: {{"target": "improve efficiency and productivity", "measurement": "operational metrics and user feedback", "expected": "20-40% improvement based on industry benchmarks"}}
🎯 Based on initiative type, always include estimated impact:
   - Automation: {{"target": "process efficiency gains", "expected": "estimated 25-35% reduction in processing time"}}
   - AI/Analytics: {{"target": "enhanced insights and decision-making", "expected": "improved forecast accuracy by 15-25%"}}
   - Cloud: {{"target": "infrastructure optimization", "expected": "estimated 20-30% cost reduction"}}
   - Digital platform: {{"target": "user engagement", "expected": "improved customer satisfaction and retention"}}

WORKFORCE IMPACT - ALWAYS ESTIMATE:
🎯 Extract any mention of training, skills, hiring, restructuring
🎯 If not mentioned, infer from initiative:
   - New technology → {{"skillsDevelopment": "training on [technology]", "trainingHours": "estimated 20-40 hours", "upskilling": "technical skills development program"}}
   - Automation → {{"jobsAffected": "roles transformed to higher-value work", "upskilling": "process redesign and analytical skills"}}
   - Digital transformation → {{"skillsDevelopment": "digital literacy and agile practices", "trainingHours": "estimated 40-80 hours", "jobsAffected": "company-wide skill enhancement"}}

CRITICAL EXTRACTION RULES - MANDATORY:
✅ Extract ONLY initiatives explicitly mentioned in the text
✅ Include ALL digital initiatives, regardless of size
✅ ALWAYS provide meaningful values - avoid "Not mentioned" or "Not specified" whenever possible
✅ MANDATORY - Score EACH initiative across ALL FOUR PLCT dimensions independently (0-100 scale each)
✅ MANDATORY - For EACH dimension score, provide detailed rationale citing specific scoring rubric criteria
✅ MANDATORY - Calculate total PLCT score (sum of 4 dimensions, 0-400 scale) and identify dominant dimension
✅ MANDATORY - Apply adjustment factors (+/- 5-10 points) based on evidence quality and sector context
✅ MANDATORY - Calculate ALL THREE stakeholder-weighted scores with actual numeric results:
    - InvestorWeighted = (CX×0.3) + (PE×0.1) + (OE×0.3) + (BM×0.3) - MUST be numeric value
    - PolicyWeighted = (CX×0.2) + (PE×0.4) + (OE×0.2) + (BM×0.2) - MUST be numeric value
    - StrategicWeighted = (CX×0.25) + (PE×0.25) + (OE×0.25) + (BM×0.25) - MUST be numeric value
✅ MANDATORY - Assess disclosure quality using the rubric with numeric scores for each component
✅ MANDATORY - Assign confidence level (High/Medium/Low) with detailed justification
✅ MANDATORY - Include all PLCTScoring, StakeholderWeightedScores, DisclosureQualityScore, and ConfidenceLevel objects
✅ NO NULL VALUES - Every field in these objects must have an actual value, not null
✅ For ALL fields, provide reasonable estimates and inferences based on context:
   
   INVESTMENT AMOUNTS:
   - If exact amount not stated, infer scale from initiative description:
     * "pilot", "trial", "proof of concept" → "Minor (estimated < RM 500K)"
     * "implementation", "deployment", "rollout" → "Moderate (estimated RM 500K - 5M)"
     * "major", "significant", "large-scale" → "Major (estimated RM 5M - 20M)"
     * "strategic", "transformation", "enterprise-wide" → "Strategic (estimated > RM 20M)"
   - Look for indirect clues: team size, scope, duration, technology complexity
   
   TIMELINE:
   - If not explicitly stated, estimate based on:
     * Report year as likely start year
     * Initiative complexity: pilot (6-12 months), implementation (12-24 months), transformation (24-36 months)
     * Use phrases like "estimated ongoing", "likely started [year]", "projected completion [year+duration]"
   - Always populate at least: {{"status": "ongoing/planned", "estimated_start": "year", "estimated_duration": "X months"}}
   
   SUCCESS METRICS:
   - Extract any quantitative targets mentioned anywhere in the initiative description
   - Look for: efficiency gains, cost savings, revenue increases, time reductions, user adoption
   - If specific metrics not mentioned, infer from initiative type:
     * Automation → "Expected efficiency improvement of 20-40%"
     * AI/Analytics → "Improved decision-making accuracy and insights"
     * Digital platforms → "Enhanced user engagement and satisfaction"
     * Cloud migration → "Reduced infrastructure costs by 15-30%"
   
   BUSINESS RATIONALE:
   - NEVER leave empty - always infer from:
     * Strategic priorities mentioned in report
     * Industry trends and competitive pressures
     * Operational challenges being addressed
     * Growth or efficiency objectives
   - Use context: "Aligns with company's digital transformation strategy to [inferred goal]"
   
   IMPLEMENTATION APPROACH:
   - Infer from initiative description:
     * Mention of partners → "Partnership-based implementation"
     * Mention of phases → Extract and structure phases
     * Mention of teams → "Cross-functional team approach"
     * Default: "Phased implementation with pilot and scale-up stages"
   
   WORKFORCE IMPACT:
   - Always estimate based on initiative scale:
     * Digital training mentioned → "Upskilling program for affected staff"
     * Automation → "Workforce transition to higher-value tasks, estimated 10-15% productivity gain"
     * New technology → "Training programs for technology adoption, estimated 20-40 hours per employee"
   
   EXPECTED IMPACT:
   - NEVER leave as "Not mentioned" - infer from:
     * Initiative category and objectives
     * Similar initiatives in industry
     * Strategic goals mentioned in report
   - Structure: "Expected to [specific benefit] leading to [business outcome]"
   
   INNOVATION LEVEL:
   - Evaluate based on:
     * "Incremental": Improving existing processes, standard tech adoption
     * "Moderate": New capabilities, emerging tech, significant process changes
     * "Transformational": Disruptive tech, business model changes, industry-leading
   
   TECHNOLOGY PARTNERS:
   - If not explicitly mentioned: "To be determined" or "Likely major vendors in [technology area]"
   - Look for brand names anywhere in section (Microsoft, SAP, Oracle, AWS, etc.)

✅ Use contextual clues from entire report:
   - Budget discussions → estimate investment scales
   - Strategic priorities → business rationale
   - Operational metrics → baseline and targets
   - Industry benchmarks → expected improvements

✅ Provide specific, detailed responses even when inferring
✅ Use qualifiers when estimating: "estimated", "projected", "likely", "approximately"
✅ DO NOT fabricate: specific dollar amounts, exact dates, actual partner names, precise percentages
✅ DO estimate: ranges, scales, durations, qualitative impacts, strategic alignment

Full Report Text:
{text}
"""


def extract_with_gemini(prompt, max_retries=3):
    """Extract data using Gemini with retry logic"""
    logging.info("Sending to Gemini for full document extraction...")
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            
            if not response.text.strip():
                logging.warning(f"Empty response from Gemini on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return []
            
            logging.info(f"Gemini response length: {len(response.text)}")
            
            # Parse response
            return parse_gemini_response(response.text)
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logging.warning(f"Gemini request failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"Gemini request failed after {max_retries} attempts: {e}")
                return []


def parse_gemini_response(response_text):
    """Parse Gemini response text to JSON"""
    text = response_text.strip()
    if text.startswith('```json') and text.endswith('```'):
        text = text[7:-3].strip()
    elif text.startswith('```') and text.endswith('```'):
        text = text[3:-3].strip()
    
    try:
        extracted = json.loads(text)
        if not isinstance(extracted, list):
            logging.warning("Gemini response is not a list, returning empty")
            return []
        logging.info(f"Extracted {len(extracted)} companies with initiatives.")
        return extracted
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse Gemini response: {e}")
        logging.error(f"Response text preview: {text[:500]}")
        return []


def load_processed_files():
    """Load the list of already processed files"""
    if os.path.exists(PROCESSED_FILES_LOG):
        try:
            with open(PROCESSED_FILES_LOG, 'r') as f:
                data = json.load(f)
                return data.get('processed_files', [])
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Could not load processed files log: {e}")
            return []
    return []


def save_processed_file(filename):
    """Mark a file as processed"""
    processed_files = load_processed_files()
    if filename not in processed_files:
        processed_files.append(filename)
        try:
            with open(PROCESSED_FILES_LOG, 'w') as f:
                json.dump({'processed_files': processed_files}, f, indent=2)
            logging.info(f"Marked {filename} as processed")
        except IOError as e:
            logging.error(f"Could not save processed files log: {e}")


def is_file_processed(filename):
    """Check if a file has already been processed"""
    processed_files = load_processed_files()
    return filename in processed_files



def safe_json_dumps(value):
    """Safely convert value to JSON string"""
    if value is None:
        return None
    if isinstance(value, str):
        # If already a string, check if it's valid JSON
        try:
            json.loads(value)
            return value
        except (json.JSONDecodeError, TypeError):
            # Not valid JSON, treat as regular string
            return value
    # Convert lists and dicts to JSON
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return value


def insert_into_mysql(extracted_data, mysql_config, stock_code=None):
    """Insert extracted data into MySQL database"""
    try:
        conn = mysql.connector.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database'],
            port=mysql_config.get('port', 3306)
        )
        cursor = conn.cursor()
        
        for company_data in extracted_data:
            # Insert company
            cursor.execute("""
                INSERT INTO companies 
                (stock_code, company_name, company_sector, year_mentioned, report_type, technology_used, department, 
                 digital_investment, digital_maturity_level, plct_dimensions, strategic_priority)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                company_sector=VALUES(company_sector), 
                report_type=VALUES(report_type), technology_used=VALUES(technology_used), 
                department=VALUES(department), digital_investment=VALUES(digital_investment),
                digital_maturity_level=VALUES(digital_maturity_level), plct_dimensions=VALUES(plct_dimensions),
                strategic_priority=VALUES(strategic_priority)
            """, (
                stock_code,
                company_data.get('CompanyName', 'Unknown'),
                company_data.get('CompanySector'),
                company_data.get('YearMentioned'),
                company_data.get('ReportType'),
                safe_json_dumps(company_data.get('TechnologyUsed', [])),
                safe_json_dumps(company_data.get('Department', [])),
                company_data.get('DigitalInvestment'),
                company_data.get('DigitalMaturityLevel'),
                safe_json_dumps(company_data.get('PLCTDimensions', {})),
                company_data.get('StrategicPriority')
            ))
            
            
            company_id = cursor.lastrowid
            if company_id == 0:
                # Get existing company ID
                cursor.execute("SELECT id FROM companies WHERE stock_code = %s AND year_mentioned = %s", 
                             (stock_code, company_data.get('YearMentioned')))
                result = cursor.fetchone()
                if result:
                    company_id = result[0]
            
            # Insert initiatives
            for initiative in company_data.get('Initiatives', []):
                # Extract PLCT scoring data
                plct_scoring = initiative.get('PLCTScoring', {})
                stakeholder_weighted = initiative.get('StakeholderWeightedScores', {})
                disclosure_quality = initiative.get('DisclosureQualityScore', {})
                confidence_level = initiative.get('ConfidenceLevel', {})
                
                # Extract stakeholder weighted scores
                investor_weighted = stakeholder_weighted.get('InvestorWeighted')
                policy_weighted = stakeholder_weighted.get('PolicyWeighted')
                strategic_weighted = stakeholder_weighted.get('StrategicWeighted')
                
                # Parse weighted scores if they are formulas (strings with calculations)
                def extract_numeric_value(val):
                    """Extract numeric value from formula string"""
                    if isinstance(val, (int, float)):
                        return float(val)
                    if isinstance(val, str):
                        try:
                            # Try to parse as float directly
                            return float(val.split('-')[0].strip())
                        except (ValueError, IndexError):
                            return None
                    return None
                
                investor_weighted_val = extract_numeric_value(investor_weighted)
                policy_weighted_val = extract_numeric_value(policy_weighted)
                strategic_weighted_val = extract_numeric_value(strategic_weighted)
                
                cursor.execute("""
                    INSERT INTO initiatives 
                    (company_id, stock_code, category, initiative, plct_alignment, expected_impact, investment_amount,
                     timeline, success_metrics, business_rationale, implementation_approach, workforce_impact,
                     technology_partners, innovation_level, risk_factors, competitive_advantage, 
                     policy_implications, governance_structure, data_strategy, security_considerations, 
                     sustainability_impact,
                     plct_customer_experience_score, plct_customer_experience_rationale,
                     plct_people_empowerment_score, plct_people_empowerment_rationale,
                     plct_operational_efficiency_score, plct_operational_efficiency_rationale,
                     plct_new_business_models_score, plct_new_business_models_rationale,
                     plct_total_score, plct_dominant_dimension, plct_adjustment_factors,
                     plct_investor_weighted_score, plct_policy_weighted_score, plct_strategic_weighted_score,
                     disclosure_quality_investment_score, disclosure_quality_timeline_score,
                     disclosure_quality_metrics_score, disclosure_quality_technical_score,
                     disclosure_quality_rationale_score, disclosure_quality_total_score,
                     disclosure_quality_tier,
                     confidence_level, confidence_justification, confidence_flagged_for_verification,
                     confidence_verification_notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    company_id,
                    stock_code,
                    initiative.get('Category'),
                    initiative.get('Initiative'),
                    initiative.get('PLCTAlignment'),
                    initiative.get('ExpectedImpact'),
                    initiative.get('InvestmentAmount'),
                    safe_json_dumps(initiative.get('Timeline', {})),
                    safe_json_dumps(initiative.get('SuccessMetrics', {})),
                    initiative.get('BusinessRationale'),
                    initiative.get('ImplementationApproach'),
                    safe_json_dumps(initiative.get('WorkforceImpact', {})),
                    initiative.get('TechnologyPartners'),
                    initiative.get('InnovationLevel'),
                    safe_json_dumps(initiative.get('RiskFactors', {})),
                    safe_json_dumps(initiative.get('CompetitiveAdvantage', {})),
                    safe_json_dumps(initiative.get('PolicyImplications', {})),
                    initiative.get('GovernanceStructure'),
                    initiative.get('DataStrategy'),
                    initiative.get('SecurityConsiderations'),
                    initiative.get('SustainabilityImpact'),
                    # PLCT Scoring
                    plct_scoring.get('CustomerExperienceScore'),
                    plct_scoring.get('CustomerExperienceRationale'),
                    plct_scoring.get('PeopleEmpowermentScore'),
                    plct_scoring.get('PeopleEmpowermentRationale'),
                    plct_scoring.get('OperationalEfficiencyScore'),
                    plct_scoring.get('OperationalEfficiencyRationale'),
                    plct_scoring.get('NewBusinessModelsScore'),
                    plct_scoring.get('NewBusinessModelsRationale'),
                    plct_scoring.get('TotalPLCTScore'),
                    plct_scoring.get('DominantDimension'),
                    safe_json_dumps(plct_scoring.get('AdjustmentFactors', {})),
                    # Stakeholder Weighted Scores
                    investor_weighted_val,
                    policy_weighted_val,
                    strategic_weighted_val,
                    # Disclosure Quality Scores
                    disclosure_quality.get('investmentDisclosure'),
                    disclosure_quality.get('timelineDisclosure'),
                    disclosure_quality.get('metricsAndKpis'),
                    disclosure_quality.get('technicalDetail'),
                    disclosure_quality.get('businessRationale'),
                    disclosure_quality.get('totalScore'),
                    disclosure_quality.get('qualityTier'),
                    # Confidence Level
                    confidence_level.get('level'),
                    confidence_level.get('justification'),
                    confidence_level.get('flaggedForVerification', False),
                    confidence_level.get('verificationNotes')
                ))
        
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Data inserted into MySQL successfully.")
        return True
        
    except mysql.connector.Error as e:
        logging.error(f"MySQL error: {e}")
        if conn:
            conn.rollback()
        return False



def initialize_environment():
    """Initialize environment variables"""
    load_dotenv()
    
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        logging.error("Missing GOOGLE_API_KEY.")
        raise ValueError("Missing GOOGLE_API_KEY.")
    
    genai.configure(api_key=google_api_key)
    
    mysql_config = {
        'host': os.getenv('MYSQL_HOST'),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE'),
        'port': int(os.getenv('MYSQL_PORT', 3306))
    }
    
    return mysql_config



def load_sector_map():
    """Load the official sector map"""
    try:
        with open('sector_map.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Could not load sector_map.json: {e}")
        return {}

def match_company_to_stock_code(filename, company_name, company_codes_df):
    """
    Match a company from filename or extracted name to a stock code
    Returns: (stock_code, official_company_name, year) or (None, None, None)
    """
    # Extract year from filename (look for 2021-2025)
    year_match = re.search(r'20(2[1-5])', filename)
    year = int(year_match.group(0)) if year_match else None
    
    # Clean filename for matching
    clean_filename = filename.replace('.pdf', '').upper()
    clean_company_name = company_name.upper() if company_name else ""
    
    # Remove common words
    for word in [' ANNUAL', ' REPORT', ' CORPORATE', ' GOVERNANCE', ' CG', ' AR', ' INTEGRATED']:
        clean_filename = clean_filename.replace(word, '')
        clean_company_name = clean_company_name.replace(word, '')
    
    # Try exact match first
    for _, row in company_codes_df.iterrows():
        official_name = row['company_name'].upper()
        
        # Check if official name is in filename or extracted name
        if official_name in clean_filename or official_name in clean_company_name:
            return row['stock_code'], row['company_name'], row['year']
        
        # Check reverse - filename in official name
        if clean_filename and len(clean_filename) > 10 and clean_filename in official_name:
            return row['stock_code'], row['company_name'], row['year']
    
    # Try partial matching (remove suffixes)
    for _, row in company_codes_df.iterrows():
        official_name = row['company_name'].upper()
        # Remove legal suffixes
        for suffix in [' BERHAD', ' BHD', ' SDN', ' (M)', ' HOLDINGS', ' GROUP']:
            official_name = official_name.replace(suffix, '')
        
        clean_official = re.sub(r'[^\w\s]', '', official_name).strip()
        clean_file = re.sub(r'[^\w\s]', '', clean_filename).strip()
        clean_extracted = re.sub(r'[^\w\s]', '', clean_company_name).strip()
        
        if clean_official and (clean_official in clean_file or clean_official in clean_extracted):
            return row['stock_code'], row['company_name'], row['year']
    
    logging.warning(f"Could not match stock code for: {filename} / {company_name}")
    return None, None, year


def main():
    """Main function for full document extraction"""
    logging.info("Starting full document extraction process.")
    
    # Initialize environment
    mysql_config = initialize_environment()
    
    # Load Sector Map
    SECTOR_MAP = load_sector_map()
    logging.info(f"Loaded {len(SECTOR_MAP)} companies from sector map.")
    
    # Load company codes
    company_codes_df = load_company_codes_by_year()
    logging.info(f"Loaded {len(company_codes_df)} company-year records")
    
    # Get PDF files
    if not os.path.exists(REPORTS_DIR):
        logging.error(f"Directory {REPORTS_DIR} not found.")
        return
    
    pdf_files = [f for f in os.listdir(REPORTS_DIR) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logging.warning(f"No PDF files found in {REPORTS_DIR}.")
        return
    
    # Load processed files
    processed_files = load_processed_files()
    logging.info(f"Found {len(processed_files)} already processed files")
    
    # Filter out already processed files
    files_to_process = [f for f in pdf_files if f not in processed_files]
    
    if not files_to_process:
        logging.info("All PDF files have already been processed. Nothing to do.")
        pass
    
    logging.info(f"Processing {len(files_to_process)} out of {len(pdf_files)} total PDF files")
    
    # Process each PDF
    for filename in files_to_process:
        filepath = os.path.join(REPORTS_DIR, filename)
        logging.info(f"Processing {filename}...")
        
        # Extract full text
        text = extract_text_from_pdf(filepath)
        if not text:
            logging.warning(f"Skipping {filename}: No text extracted.")
            continue
        
        # Build prompt and extract
        prompt = build_extraction_prompt(text, filename)
        extracted_data = extract_with_gemini(prompt)
        
        if not extracted_data:
            logging.warning(f"No data extracted from {filename}")
            continue
        
        # Match company to stock code
        for company in extracted_data:
            ai_company_name = company.get('CompanyName', '')
            
            # Try to match stock code
            stock_code, official_name, matched_year = match_company_to_stock_code(
                filename, ai_company_name, company_codes_df
            )
            
            if stock_code:
                logging.info(f"Matched: {filename} -> {official_name} ({stock_code})")
                # Don't update company name yet - we'll use the exact format from sector_map
                
                # Update year if extracted year differs from filename year
                if matched_year and not company.get('YearMentioned'):
                    company['YearMentioned'] = matched_year
            else:
                logging.warning(f"No stock code match for {filename}")
                stock_code = None
            
            # === SECTOR OVERRIDE LOGIC & EXACT COMPANY NAME FROM SECTOR MAP ===
            matched_sector = None
            matched_company_name = None
            
            # 1. Exact Name Match in sector map
            if ai_company_name in SECTOR_MAP:
                matched_sector = SECTOR_MAP[ai_company_name]
                matched_company_name = ai_company_name
            elif official_name and official_name in SECTOR_MAP:
                matched_sector = SECTOR_MAP[official_name]
                matched_company_name = official_name
            
            # 2. Partial match in sector map
            if not matched_sector:
                normalized_file = filename.replace('.pdf', '')
                for map_name, map_sector in SECTOR_MAP.items():
                    clean_map_name = map_name.replace(' Bhd', '').replace(' Berhad', '').strip()
                    if clean_map_name.lower() in normalized_file.lower():
                        matched_sector = map_sector
                        matched_company_name = map_name  # Use exact format from sector_map.json
                        logging.info(f"Matched sector via filename: {filename} -> {map_name} -> {matched_sector}")
                        break
            
            if matched_sector:
                logging.info(f"OVERRIDING SECTOR: {company.get('CompanySector')} -> {matched_sector}")
                company['CompanySector'] = matched_sector
                
                # Update company name to exact format from sector_map.json
                if matched_company_name:
                    company['CompanyName'] = matched_company_name
                    logging.info(f"Using exact company name from sector_map: {matched_company_name}")
            else:
                logging.info(f"No sector match found. Keeping AI sector: {company.get('CompanySector')}")
                # If we have a stock code match but no sector match, use official name from CSV
                if stock_code and official_name:
                    company['CompanyName'] = official_name

        
        # Output results
        print(f"\n=== Extracted from {filename} ===")
        print(json.dumps(extracted_data, indent=2))
        
        # Insert into MySQL
        if all(mysql_config.values()):
            # Use the matched stock code
            success = insert_into_mysql(extracted_data, mysql_config, stock_code)
            if success:
                # Mark file as processed only if insertion was successful
                save_processed_file(filename)
                logging.info(f"Successfully processed and saved {filename}")
            else:
                logging.error(f"Failed to insert data from {filename} into MySQL")
        else:
            logging.warning("MySQL credentials not fully set. Data not saved to database.")
    
    logging.info("Full document extraction completed.")


if __name__ == "__main__":
    main()
