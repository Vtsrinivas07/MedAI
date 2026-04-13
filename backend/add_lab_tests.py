import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os

MONGODB_URI = "mongodb+srv://medai:Medaiteja123@cluster0.mqzrp.mongodb.net/medai"

LAB_TESTS = [
    # Full Body Packages
    {
        "name": "Complete Health Checkup",
        "description": "Comprehensive package covering 70+ tests including CBC, lipid profile, liver, kidney, thyroid, diabetes, and more",
        "category": "packages",
        "price": 2499,
        "original_price": 3999,
        "tests_included": 72,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/health-checkup.jpg",
        "health_concerns": ["heart", "diabetes", "liver", "kidney", "thyroid"],
        "organs": ["heart", "liver", "kidney", "thyroid"],
        "popular": True,
        "turnaround_time": "24-48 hours"
    },
    {
        "name": "Executive Health Package",
        "description": "Premium package with 100+ tests including advanced cardiac markers, cancer screening, and organ function tests",
        "category": "packages",
        "price": 4999,
        "original_price": 7999,
        "tests_included": 105,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/executive-package.jpg",
        "health_concerns": ["heart", "diabetes", "liver", "kidney", "thyroid", "bone"],
        "organs": ["heart", "liver", "kidney", "thyroid", "lungs", "brain"],
        "popular": True,
        "turnaround_time": "48-72 hours"
    },
    {
        "name": "Basic Health Checkup",
        "description": "Essential package with 40+ tests covering diabetes, lipid profile, liver and kidney function",
        "category": "packages",
        "price": 999,
        "original_price": 1499,
        "tests_included": 42,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/basic-checkup.jpg",
        "health_concerns": ["diabetes", "heart", "liver", "kidney"],
        "organs": ["heart", "liver", "kidney"],
        "popular": True,
        "turnaround_time": "12-24 hours"
    },
    
    # Women's Health
    {
        "name": "Women's Health Package",
        "description": "Comprehensive package for women including hormonal profile, thyroid, bone health, vitamins, and reproductive health tests",
        "category": "women",
        "price": 2199,
        "original_price": 3499,
        "tests_included": 55,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/women-health.jpg",
        "health_concerns": ["thyroid", "bone", "heart"],
        "organs": ["thyroid", "bones"],
        "popular": True,
        "turnaround_time": "24-48 hours"
    },
    {
        "name": "PCOS Profile",
        "description": "Hormonal panel for PCOS including FSH, LH, testosterone, prolactin, insulin, and thyroid tests",
        "category": "women",
        "price": 1699,
        "original_price": 2299,
        "tests_included": 12,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/pcos-profile.jpg",
        "health_concerns": ["thyroid", "diabetes"],
        "organs": ["thyroid"],
        "popular": True,
        "turnaround_time": "24 hours"
    },
    {
        "name": "Pregnancy Profile",
        "description": "Essential tests for pregnancy including CBC, blood group, TSH, glucose, and infection screening",
        "category": "women",
        "price": 1299,
        "original_price": 1799,
        "tests_included": 18,
        "fasting_required": False,
        "home_collection": True,
        "image_url": "https://example.com/pregnancy-profile.jpg",
        "health_concerns": ["thyroid", "diabetes"],
        "organs": ["thyroid"],
        "popular": False,
        "turnaround_time": "24 hours"
    },
    {
        "name": "Menopause Health Package",
        "description": "Tests for post-menopausal women including hormones, bone density markers, lipid profile, and vitamin D",
        "category": "women",
        "price": 1899,
        "original_price": 2699,
        "tests_included": 25,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/menopause-package.jpg",
        "health_concerns": ["bone", "heart"],
        "organs": ["bones", "heart"],
        "popular": False,
        "turnaround_time": "24-48 hours"
    },
    
    # Men's Health
    {
        "name": "Men's Health Package",
        "description": "Complete package for men including testosterone, PSA, lipid profile, liver, kidney, and vitamin tests",
        "category": "men",
        "price": 1999,
        "original_price": 2999,
        "tests_included": 48,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/men-health.jpg",
        "health_concerns": ["heart", "diabetes", "liver", "kidney"],
        "organs": ["heart", "liver", "kidney"],
        "popular": True,
        "turnaround_time": "24-48 hours"
    },
    {
        "name": "Male Fertility Profile",
        "description": "Fertility assessment including semen analysis, hormonal profile (testosterone, FSH, LH, prolactin)",
        "category": "men",
        "price": 1499,
        "original_price": 2199,
        "tests_included": 8,
        "fasting_required": False,
        "home_collection": False,
        "image_url": "https://example.com/male-fertility.jpg",
        "health_concerns": [],
        "organs": [],
        "popular": False,
        "turnaround_time": "48 hours"
    },
    {
        "name": "Testosterone Test",
        "description": "Total and free testosterone levels to assess hormonal health",
        "category": "men",
        "price": 599,
        "original_price": 899,
        "tests_included": 2,
        "fasting_required": False,
        "home_collection": True,
        "image_url": "https://example.com/testosterone.jpg",
        "health_concerns": [],
        "organs": [],
        "popular": True,
        "turnaround_time": "24 hours"
    },
    {
        "name": "PSA Test (Prostate)",
        "description": "Prostate Specific Antigen test for prostate health screening",
        "category": "men",
        "price": 499,
        "original_price": 699,
        "tests_included": 1,
        "fasting_required": False,
        "home_collection": True,
        "image_url": "https://example.com/psa-test.jpg",
        "health_concerns": [],
        "organs": [],
        "popular": False,
        "turnaround_time": "24 hours"
    },
    
    # X-rays & Scans
    {
        "name": "Chest X-ray",
        "description": "Digital X-ray of chest for lung and heart health assessment",
        "category": "xray_scans",
        "price": 399,
        "original_price": 599,
        "tests_included": 1,
        "fasting_required": False,
        "home_collection": False,
        "image_url": "https://example.com/chest-xray.jpg",
        "health_concerns": ["heart"],
        "organs": ["lungs", "heart"],
        "popular": True,
        "turnaround_time": "2-4 hours"
    },
    {
        "name": "Whole Abdomen Ultrasound",
        "description": "Ultrasound scan of liver, gallbladder, pancreas, spleen, kidneys, and bladder",
        "category": "xray_scans",
        "price": 799,
        "original_price": 1199,
        "tests_included": 1,
        "fasting_required": True,
        "home_collection": False,
        "image_url": "https://example.com/abdomen-ultrasound.jpg",
        "health_concerns": ["liver", "kidney"],
        "organs": ["liver", "kidney"],
        "popular": True,
        "turnaround_time": "4-6 hours"
    },
    {
        "name": "Thyroid Ultrasound",
        "description": "Ultrasound imaging of thyroid gland to detect nodules, cysts, or enlargement",
        "category": "xray_scans",
        "price": 599,
        "original_price": 899,
        "tests_included": 1,
        "fasting_required": False,
        "home_collection": False,
        "image_url": "https://example.com/thyroid-ultrasound.jpg",
        "health_concerns": ["thyroid"],
        "organs": ["thyroid"],
        "popular": False,
        "turnaround_time": "4 hours"
    },
    {
        "name": "Bone Density Scan (DEXA)",
        "description": "DEXA scan to measure bone mineral density and osteoporosis risk",
        "category": "xray_scans",
        "price": 1499,
        "original_price": 2199,
        "tests_included": 1,
        "fasting_required": False,
        "home_collection": False,
        "image_url": "https://example.com/dexa-scan.jpg",
        "health_concerns": ["bone"],
        "organs": ["bones"],
        "popular": False,
        "turnaround_time": "24 hours"
    },
    {
        "name": "CT Scan - Brain",
        "description": "Computed tomography scan of brain for detailed imaging",
        "category": "xray_scans",
        "price": 2999,
        "original_price": 4499,
        "tests_included": 1,
        "fasting_required": False,
        "home_collection": False,
        "image_url": "https://example.com/ct-brain.jpg",
        "health_concerns": [],
        "organs": ["brain"],
        "popular": False,
        "turnaround_time": "24 hours"
    },
    {
        "name": "MRI - Spine",
        "description": "Magnetic resonance imaging of spine for detailed soft tissue imaging",
        "category": "xray_scans",
        "price": 4999,
        "original_price": 7499,
        "tests_included": 1,
        "fasting_required": False,
        "home_collection": False,
        "image_url": "https://example.com/mri-spine.jpg",
        "health_concerns": [],
        "organs": [],
        "popular": False,
        "turnaround_time": "24-48 hours"
    },
    
    # Lifestyle Checkups
    {
        "name": "Diabetes Screening",
        "description": "Comprehensive diabetes panel including HbA1c, fasting glucose, post-meal glucose, and insulin levels",
        "category": "lifestyle",
        "price": 799,
        "original_price": 1199,
        "tests_included": 5,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/diabetes-screening.jpg",
        "health_concerns": ["diabetes"],
        "organs": [],
        "popular": True,
        "turnaround_time": "24 hours"
    },
    {
        "name": "Heart Health Package",
        "description": "Cardiac risk assessment with lipid profile, apolipoprotein, homocysteine, and hs-CRP",
        "category": "lifestyle",
        "price": 1299,
        "original_price": 1999,
        "tests_included": 15,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/heart-health.jpg",
        "health_concerns": ["heart"],
        "organs": ["heart"],
        "popular": True,
        "turnaround_time": "24 hours"
    },
    {
        "name": "Fitness & Sports Package",
        "description": "Tests for active individuals including vitamins, minerals, hormones, and metabolic markers",
        "category": "lifestyle",
        "price": 1699,
        "original_price": 2499,
        "tests_included": 32,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/fitness-package.jpg",
        "health_concerns": ["bone"],
        "organs": ["bones"],
        "popular": True,
        "turnaround_time": "24-48 hours"
    },
    {
        "name": "Weight Management Package",
        "description": "Tests for weight issues including thyroid, insulin resistance, cortisol, and metabolic panel",
        "category": "lifestyle",
        "price": 1499,
        "original_price": 2199,
        "tests_included": 22,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/weight-management.jpg",
        "health_concerns": ["thyroid", "diabetes"],
        "organs": ["thyroid"],
        "popular": False,
        "turnaround_time": "24 hours"
    },
    {
        "name": "Vitamin Deficiency Panel",
        "description": "Complete vitamin screening including B12, D, folate, and iron studies",
        "category": "lifestyle",
        "price": 1199,
        "original_price": 1799,
        "tests_included": 8,
        "fasting_required": False,
        "home_collection": True,
        "image_url": "https://example.com/vitamin-panel.jpg",
        "health_concerns": ["bone"],
        "organs": ["bones"],
        "popular": True,
        "turnaround_time": "24 hours"
    },
    
    # Special Tests
    {
        "name": "Allergy Panel - Food",
        "description": "IgE antibody test for 40+ common food allergens",
        "category": "special",
        "price": 3499,
        "original_price": 4999,
        "tests_included": 42,
        "fasting_required": False,
        "home_collection": True,
        "image_url": "https://example.com/food-allergy.jpg",
        "health_concerns": [],
        "organs": [],
        "popular": False,
        "turnaround_time": "72 hours"
    },
    {
        "name": "Genetic Cancer Screening",
        "description": "Genetic markers for hereditary cancer risk including BRCA1/BRCA2",
        "category": "special",
        "price": 15999,
        "original_price": 19999,
        "tests_included": 8,
        "fasting_required": False,
        "home_collection": True,
        "image_url": "https://example.com/genetic-cancer.jpg",
        "health_concerns": [],
        "organs": [],
        "popular": False,
        "turnaround_time": "14-21 days"
    },
    {
        "name": "COVID-19 RT-PCR Test",
        "description": "RT-PCR test for COVID-19 detection",
        "category": "special",
        "price": 499,
        "original_price": 699,
        "tests_included": 1,
        "fasting_required": False,
        "home_collection": True,
        "image_url": "https://example.com/covid-test.jpg",
        "health_concerns": [],
        "organs": ["lungs"],
        "popular": True,
        "turnaround_time": "24 hours"
    },
    {
        "name": "Autoimmune Panel",
        "description": "Comprehensive autoimmune markers including ANA, anti-dsDNA, RF, anti-CCP",
        "category": "special",
        "price": 2499,
        "original_price": 3499,
        "tests_included": 12,
        "fasting_required": False,
        "home_collection": True,
        "image_url": "https://example.com/autoimmune-panel.jpg",
        "health_concerns": [],
        "organs": [],
        "popular": False,
        "turnaround_time": "48-72 hours"
    },
    {
        "name": "Liver Function Test (LFT)",
        "description": "Complete liver panel including bilirubin, SGOT, SGPT, alkaline phosphatase, proteins",
        "category": "special",
        "price": 449,
        "original_price": 649,
        "tests_included": 11,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/lft.jpg",
        "health_concerns": ["liver"],
        "organs": ["liver"],
        "popular": True,
        "turnaround_time": "12 hours"
    },
    {
        "name": "Kidney Function Test (KFT)",
        "description": "Complete kidney panel including creatinine, urea, uric acid, electrolytes",
        "category": "special",
        "price": 399,
        "original_price": 599,
        "tests_included": 8,
        "fasting_required": True,
        "home_collection": True,
        "image_url": "https://example.com/kft.jpg",
        "health_concerns": ["kidney"],
        "organs": ["kidney"],
        "popular": True,
        "turnaround_time": "12 hours"
    },
    {
        "name": "Thyroid Profile Total",
        "description": "Complete thyroid assessment including TSH, T3, T4, anti-TPO antibodies",
        "category": "special",
        "price": 699,
        "original_price": 999,
        "tests_included": 5,
        "fasting_required": False,
        "home_collection": True,
        "image_url": "https://example.com/thyroid-profile.jpg",
        "health_concerns": ["thyroid"],
        "organs": ["thyroid"],
        "popular": True,
        "turnaround_time": "24 hours"
    },
    {
        "name": "Cardiac Biomarkers",
        "description": "Emergency cardiac panel including troponin, CPK-MB, myoglobin for heart attack detection",
        "category": "special",
        "price": 1299,
        "original_price": 1799,
        "tests_included": 4,
        "fasting_required": False,
        "home_collection": False,
        "image_url": "https://example.com/cardiac-biomarkers.jpg",
        "health_concerns": ["heart"],
        "organs": ["heart"],
        "popular": False,
        "turnaround_time": "2-4 hours"
    }
]

async def add_lab_tests():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client.medai
    
    try:
        # Clear existing lab tests
        await db.lab_tests.delete_many({})
        print("Cleared existing lab tests")
        
        # Add created_at timestamp to each test
        for test in LAB_TESTS:
            test["created_at"] = datetime.utcnow()
            test["updated_at"] = datetime.utcnow()
        
        # Insert new lab tests
        result = await db.lab_tests.insert_many(LAB_TESTS)
        print(f"Successfully added {len(result.inserted_ids)} lab tests")
        
        # Print summary by category
        categories = {}
        for test in LAB_TESTS:
            cat = test["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nTests by category:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} tests")
        
    except Exception as e:
        print(f"Error adding lab tests: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_lab_tests())
