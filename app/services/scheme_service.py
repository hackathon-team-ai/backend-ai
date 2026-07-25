from typing import List, Optional
from app.schemas.scheme import GovernmentScheme

GOVERNMENT_SCHEMES_DB: List[GovernmentScheme] = [
    GovernmentScheme(
        id="scheme_01",
        title="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        ministry="Ministry of Agriculture & Farmers Welfare",
        category="Income Support",
        description="Direct income support of ₹6,000 per year in three equal installments to all landholding farmer families across India.",
        eligibility=[
            "All landholding farmers' families possessing cultivable land.",
            "Valid Aadhaar card linked with bank account.",
            "Must pass e-KYC verification."
        ],
        benefits=[
            "Financial benefit of ₹6,000 per annum paid directly to bank account.",
            "Zero middleman intervention.",
            "Assured quarterly installments."
        ],
        required_documents=[
            "Aadhaar Card",
            "Land Ownership Document (7/12 extract / Khatauni)",
            "Active Bank Passbook",
            "Mobile Number linked with Aadhaar"
        ],
        application_link="https://pmkisan.gov.in/",
        is_national=True
    ),
    GovernmentScheme(
        id="scheme_02",
        title="Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        ministry="Ministry of Agriculture & Farmers Welfare",
        category="Crop Insurance",
        description="Comprehensive crop risk insurance coverage against yield loss caused by non-preventable natural risks like drought, flood, pests, and disease.",
        eligibility=[
            "All farmers growing notified crops in notified areas including sharecroppers and tenant farmers."
        ],
        benefits=[
            "Minimal premium payment: 2% for Kharif, 1.5% for Rabi, 5% for Annual Horticultural crops.",
            "Remaining premium subsidized by Central and State Governments.",
            "Direct claim settlement to bank account based on Crop Cutting Experiments."
        ],
        required_documents=[
            "Land Possession Certificate / Sowing Certificate",
            "Aadhaar Card",
            "Bank Account details",
            "Proposal Form"
        ],
        application_link="https://pmfby.gov.in/",
        is_national=True
    ),
    GovernmentScheme(
        id="scheme_03",
        title="Kisan Credit Card (KCC) Scheme",
        ministry="Ministry of Finance & RBI",
        category="Credit & Subsidized Loans",
        description="Provides timely credit to farmers to meet cultivation expenses, post-harvest costs, and maintenance of farm assets at subsidized interest rates.",
        eligibility=[
            "All farmers – individuals / joint borrowers who are owner cultivators.",
            "Tenant farmers, oral lessees & sharecroppers.",
            "Self Help Groups (SHGs) or Joint Liability Groups (JLGs) of farmers."
        ],
        benefits=[
            "Concessional interest rate of 4% per annum (with prompt repayment incentive).",
            "Collateral-free loan limit up to ₹1.60 Lakh.",
            "Rupay KCC debit card provided for easy cash withdrawals at ATMs."
        ],
        required_documents=[
            "Application form",
            "Two Passport size photographs",
            "Identity Proof (Voter ID / Aadhaar)",
            "Land record documents certified by Revenue Officer"
        ],
        application_link="https://www.myscheme.gov.in/schemes/kcc",
        is_national=True
    ),
    GovernmentScheme(
        id="scheme_04",
        title="Paramparagat Krishi Vikas Yojana (PKVY)",
        ministry="Ministry of Agriculture & Farmers Welfare",
        category="Organic Farming",
        description="Promotes organic farming through adoption of organic village clusters and Participatory Guarantee System (PGS) certification.",
        eligibility=[
            "Farmers forming clusters of 50 or more farmers having 50-acre land.",
            "Willingness to adopt organic inputs and zero chemical farming."
        ],
        benefits=[
            "Financial assistance of ₹50,000 per hectare for 3 years.",
            "₹31,000/ha provided directly for organic inputs (seeds, bio-fertilizers).",
            "Free organic certification and branding support."
        ],
        required_documents=[
            "Cluster registration details",
            "Farmer Aadhaar card",
            "Bank passbook",
            "Land records"
        ],
        application_link="https://pgsindia-ncof.dac.gov.in/pkvy/index.aspx",
        is_national=True
    ),
    GovernmentScheme(
        id="scheme_05",
        title="Sub-Mission on Agricultural Mechanization (SMAM)",
        ministry="Ministry of Agriculture & Farmers Welfare",
        category="Farm Machinery Subsidy",
        description="Provides financial subsidy for purchasing tractors, power tillers, harvesters, seed drills, and solar pumps to boost farm mechanization.",
        eligibility=[
            "Small and marginal farmers.",
            "Women farmers and SC/ST farmers get priority."
        ],
        benefits=[
            "40% to 50% subsidy on purchase of agriculture machinery.",
            "Custom Hiring Centers (CHCs) establishment support up to ₹10 Lakh."
        ],
        required_documents=[
            "Aadhaar Card",
            "Land Ownership proof",
            "Bank Passbook",
            "Quotation of machinery from authorized dealer"
        ],
        application_link="https://agrimachinery.nic.in/",
        is_national=True
    )
]

class SchemeService:
    def get_schemes(self, search: Optional[str] = None, category: Optional[str] = None) -> List[GovernmentScheme]:
        results = GOVERNMENT_SCHEMES_DB
        if category and category != "All":
            results = [s for s in results if s.category.lower() == category.lower()]
        
        if search:
            q = search.lower()
            results = [
                s for s in results 
                if q in s.title.lower() or q in s.description.lower() or q in s.ministry.lower()
            ]
        
        return results

scheme_service = SchemeService()
