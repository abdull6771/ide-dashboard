"""
Sector Mapping based on company list.pdf
Maps companies to their respective sectors (12 sectors total)
"""

# The 12 official sectors
SECTORS = [
    "INDUSTRIAL PRODUCTS AND SERVICES",
    "CONSUMER PRODUCTS AND SERVICES",
    "TECHNOLOGY",
    "PROPERTY",
    "CONSTRUCTION",
    "ENERGY",
    "TRANSPORTATION AND LOGISTICS",
    "TELECOMMUNICATIONS AND MEDIA",
    "HEALTH CARE",
    "UTILITIES",
    "PLANTATION",
    "FINANCIAL SERVICES"
]

# Company to Sector mapping from company list.pdf
COMPANY_SECTOR_MAPPING = {
    # INDUSTRIAL PRODUCTS AND SERVICES
    "Advance Synergy Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Ageson Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Ahealth Group Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Alcom Group Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Annum Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Asdion Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Astino Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Atlan Holdings Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Aturmaju Resources Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Axteria Group Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Berjaya Media Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Beshom Holdings Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Borneo Oil Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Brem Holding Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Bright Packaging Industry Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Catureka Sdn Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Comintel Corporation Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Compugates Holdings Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Cypark Resources Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Dagang NeXchange Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Datasonic Group Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Deleum Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "DNeX Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Dufu Technology Corp Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Ecomate Holdings Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Elsoft Research Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Engtex Group Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Fitters Diversified Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Freight Management Holdings Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Goh Ban Huat Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Hextar Industries Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Insights Analytics Holdings Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "JAG Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Kawan Renergy Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "KJTS Group Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Leform Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Master Tec Group Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "MClean Technologies Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Minox International Group Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "West River Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "WTEC Group Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "YBS International Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Yew Lee Pacific Group Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Zantat Holdings Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    
    # CONSUMER PRODUCTS AND SERVICES
    "A1 A.K. Koh Group Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Agricore CS Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Aquawalk Group Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Bioalpha Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Carlo Rino Group Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Daythree Digital Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "DPI Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Farm Price Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Farmiera Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Kanger International Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Oasis Home Holding Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "OB Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Ocean Fresh Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Orgabio Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Oriental Kopi Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Parlo Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "PEOPLElogy Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "PT Resources Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "RichTech Digital Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "SBH Marine Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "SCC Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "SEDANIA Innovator Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Sik Cheong Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Sorento Capital Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Spring Art Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "SSF Home Group Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Supreme Consolidated Resources Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Synergy House Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Vanzo Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Wellspire Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    
    # TECHNOLOGY
    "Aemulus Holdings Bhd": "TECHNOLOGY",
    "Agmo Holdings Bhd": "TECHNOLOGY",
    "AIMFLEX Bhd": "TECHNOLOGY",
    "Aldrich Resources Bhd": "TECHNOLOGY",
    "Cabnet Holdings Bhd": "TECHNOLOGY",
    "Divfex Bhd": "TECHNOLOGY",
    "ECA Integrated Solution Bhd": "TECHNOLOGY",
    "Edelteq Holdings Bhd": "TECHNOLOGY",
    "Eduspec Holdings Bhd": "TECHNOLOGY",
    "EVD Bhd": "TECHNOLOGY",
    "Go Hub Capital Bhd": "TECHNOLOGY",
    "Harvest Miracle Capital Bhd": "TECHNOLOGY",
    "ICT Zone Asia Bhd": "TECHNOLOGY",
    "IFCA MSC Bhd": "TECHNOLOGY",
    "Infomina Bhd": "TECHNOLOGY",
    "IRIS Corporation Bhd": "TECHNOLOGY",
    "Key Alliance Group Bhd": "TECHNOLOGY",
    "K-One Technology Bhd": "TECHNOLOGY",
    "Kronologi Asia Bhd": "TECHNOLOGY",
    "LGMS Bhd": "TECHNOLOGY",
    "ManagePay Systems Bhd": "TECHNOLOGY",
    "Mikro MSC Bhd": "TECHNOLOGY",
    "MQ Technology Bhd": "TECHNOLOGY",
    "Nova MSC Bhd": "TECHNOLOGY",
    "Oppstar Bhd": "TECHNOLOGY",
    "Panda ECO System Bhd": "TECHNOLOGY",
    "Radiant Globaltech Bhd": "TECHNOLOGY",
    "Ramssol Group Bhd": "TECHNOLOGY",
    "Securemetric Bhd": "TECHNOLOGY",
    "SFP Tech Holdings Bhd": "TECHNOLOGY",
    "SMRT Holdings Bhd": "TECHNOLOGY",
    "Solution Group Bhd": "TECHNOLOGY",
    "Systech Bhd": "TECHNOLOGY",
    "TechnoDex Bhd": "TECHNOLOGY",
    "TechStore Bhd": "TECHNOLOGY",
    "TFP Solutions Bhd": "TECHNOLOGY",
    "THMY Holdings Bhd": "TECHNOLOGY",
    "TT Vision Holdings Bhd": "TECHNOLOGY",
    "VETECE Holdings Bhd": "TECHNOLOGY",
    "Vinvest Capital Holdings Bhd": "TECHNOLOGY",
    "YGL Convergence Bhd": "TECHNOLOGY",
    "Zen Tech International Bhd": "TECHNOLOGY",
    
    # PROPERTY
    "KTI Landmark Bhd": "PROPERTY",
    
    # CONSTRUCTION
    "Aneka Jaringan Holdings Bhd": "CONSTRUCTION",
    "Cheeding Holdings Bhd": "CONSTRUCTION",
    "ES Sunlogy Bhd": "CONSTRUCTION",
    "Gagasan Nadi Cergas Bhd": "CONSTRUCTION",
    "Haily Group Bhd": "CONSTRUCTION",
    "Hartanah Kenyalang Bhd": "CONSTRUCTION",
    "Jati Tinggi Group Bhd": "CONSTRUCTION",
    "Lim Seong Hai Capital Bhd": "CONSTRUCTION",
    "MN Holdings Bhd": "CONSTRUCTION",
    "Nestcon Bhd": "CONSTRUCTION",
    "SC Estate Builder Bhd": "CONSTRUCTION",
    "Signature Alliance Group Bhd": "CONSTRUCTION",
    "Southern Score Builders Bhd": "CONSTRUCTION",
    "Taghill Holdings Bhd": "CONSTRUCTION",
    "TCS Group Holdings Bhd": "CONSTRUCTION",
    "UUE Holdings Bhd": "CONSTRUCTION",
    "Vestland Bhd": "CONSTRUCTION",
    "Wawasan Dengkil Holdings Bhd": "CONSTRUCTION",
    "Widad Group Bhd": "CONSTRUCTION",
    
    # ENERGY
    "Elridge Energy Holdings Bhd": "ENERGY",
    "Enproserve Group Bhd": "ENERGY",
    "JS Solar Holding Bhd": "ENERGY",
    "Pekat Group Bhd": "ENERGY",
    "Steel Hawk Bhd": "ENERGY",
    "Sunview Group Bhd": "ENERGY",
    "Verdant Solar Holdings Bhd": "ENERGY",
    
    # TRANSPORTATION AND LOGISTICS
    "AGX Group Bhd": "TRANSPORTATION AND LOGISTICS",
    "Ancom Logistics Bhd": "TRANSPORTATION AND LOGISTICS",
    "KGW Group Bhd": "TRANSPORTATION AND LOGISTICS",
    "MMAG Holdings Bhd": "TRANSPORTATION AND LOGISTICS",
    "Sin-Kung Logistics Bhd": "TRANSPORTATION AND LOGISTICS",
    "Straits Energy Resources Bhd": "TRANSPORTATION AND LOGISTICS",
    "Tri-Mode System (M) Bhd": "TRANSPORTATION AND LOGISTICS",
    
    # TELECOMMUNICATIONS AND MEDIA
    "Binasat Communications Bhd": "TELECOMMUNICATIONS AND MEDIA",
    "Hextar Capital Bhd": "TELECOMMUNICATIONS AND MEDIA",
    "Nexgram Holdings Bhd": "TELECOMMUNICATIONS AND MEDIA",
    "Privasia Technology Bhd": "TELECOMMUNICATIONS AND MEDIA",
    "PUC Bhd": "TELECOMMUNICATIONS AND MEDIA",
    "Silver Ridge Holdings Bhd": "TELECOMMUNICATIONS AND MEDIA",
    "XOX Bhd": "TELECOMMUNICATIONS AND MEDIA",
    "XOX Technology Bhd": "TELECOMMUNICATIONS AND MEDIA",
    
    # HEALTH CARE
    "Cengild Medical Bhd": "HEALTH CARE",
    "DC Healthcare Holdings Bhd": "HEALTH CARE",
    "Malaysian Genomics Resource Centre Bhd": "HEALTH CARE",
    "Metro Healthcare Bhd": "HEALTH CARE",
    "PMCK Bhd": "HEALTH CARE",
    "Topvision Eye Specialist Bhd": "HEALTH CARE",
    
    # UTILITIES
    "Brite-Tech Bhd": "UTILITIES",
    
    # LEAP MARKET Companies
    # INDUSTRIAL PRODUCTS AND SERVICES (LEAP)
    "CE Technology Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "GPP Resources Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Hydropipes Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Jishan Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "MMIS Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Polydamic Group Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Ray Go Solar Holdings Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "Supergenics Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "TP Tec Holding Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "TSiC Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    "UCI Resources Bhd": "INDUSTRIAL PRODUCTS AND SERVICES",
    
    # CONSUMER PRODUCTS AND SERVICES (LEAP)
    "Alpha Ocean Resources Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Aurora Italia International Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Baba Eco Group Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "CC International Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Enest Group Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Manforce Group Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Matrix Parking Solution Holdings Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "MyAxis Group Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "Ping Edge Technology Bhd": "CONSUMER PRODUCTS AND SERVICES",
    "SEERS Bhd": "CONSUMER PRODUCTS AND SERVICES",
    
    # TECHNOLOGY (LEAP)
    "Amlex Holdings Bhd": "TECHNOLOGY",
    "Cloudaron Group Bhd": "TECHNOLOGY",
    "RedPlanet Bhd": "TECHNOLOGY",
    "RTS Technology Holdings Bhd": "TECHNOLOGY",
    "Sancy Bhd": "TECHNOLOGY",
    "SL Innovation Capital Bhd": "TECHNOLOGY",
    
    # CONSTRUCTION (LEAP)
    "BV Land Holdings Bhd": "CONSTRUCTION",
    "LPC Group Bhd": "CONSTRUCTION",
    "Sunmow Holding Bhd": "CONSTRUCTION",
    "Uni Wall APS Holdings Bhd": "CONSTRUCTION",
    
    # PLANTATION (LEAP)
    "DSR Taiko Bhd": "PLANTATION",
    
    # FINANCIAL SERVICES (LEAP)
    "Autoris Group Holdings Bhd": "FINANCIAL SERVICES",
    
    # HEALTH CARE (LEAP)
    "Smile-Link Healthcare Global Bhd": "HEALTH CARE",
}

def get_sector_for_company(company_name):
    """
    Get the sector for a given company name.
    Returns the sector if found, otherwise returns None.
    """
    return COMPANY_SECTOR_MAPPING.get(company_name)

def get_all_sectors():
    """
    Returns the list of all 12 sectors.
    """
    return SECTORS.copy()

def get_companies_by_sector(sector):
    """
    Returns a list of companies in a given sector.
    """
    return [company for company, sec in COMPANY_SECTOR_MAPPING.items() if sec == sector]
