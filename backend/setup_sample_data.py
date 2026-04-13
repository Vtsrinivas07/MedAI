"""
Complete setup script to populate the database with sample data
Run this to set up a fully functional demo
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DB_NAME", "medai")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def setup_database():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    print("🚀 Starting database setup...")
    
    # Clear existing data
    await db.products.delete_many({})
    await db.lab_tests.delete_many({})
    print("✅ Cleared existing data")
    
    # Add sample products
    products = [
        # Medicines
        {
            "name": "Paracetamol 500mg",
            "generic_name": "Paracetamol",
            "brand": "Crocin",
            "category": "medicine",
            "product_type": "tablet",
            "price": 30.00,
            "discounted_price": 25.00,
            "discount_percentage": 16.67,
            "description": "Relief from fever and mild to moderate pain",
            "detailed_description": "Paracetamol is a pain reliever and a fever reducer used to treat many conditions such as headache, muscle aches, arthritis, backache, toothaches, colds, and fevers.",
            "how_to_use": "Take 1-2 tablets every 4-6 hours as needed. Do not exceed 8 tablets in 24 hours.",
            "side_effects": "Nausea, stomach pain, loss of appetite",
            "stock_quantity": 500,
            "in_stock": True,
            "prescription_required": False,
            "manufacturer": "GSK",
            "pack_size": "15 tablets",
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "rating": 4.5,
            "review_count": 259,
            "tags": ["fever", "pain relief", "headache"],
            "is_featured": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Cetrizine 10mg",
            "generic_name": "Cetirizine",
            "brand": "Zyrtec",
            "category": "medicine",
            "product_type": "tablet",
            "price": 45.00,
            "discounted_price": 38.00,
            "discount_percentage": 15.56,
            "description": "Antihistamine for allergy relief",
            "detailed_description": "Cetirizine is an antihistamine used to relieve allergy symptoms such as watery eyes, runny nose, itching eyes/nose, sneezing, hives, and itching.",
            "how_to_use": "Take 1 tablet once daily",
            "side_effects": "Drowsiness, dry mouth, stomach pain",
            "stock_quantity": 300,
            "in_stock": True,
            "prescription_required": False,
            "manufacturer": "UCB India",
            "pack_size": "10 tablets",
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Pune"],
            "rating": 4.3,
            "review_count": 187,
            "tags": ["allergy", "antihistamine"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Azithromycin 500mg",
            "generic_name": "Azithromycin",
            "brand": "Azithral",
            "category": "medicine",
            "product_type": "tablet",
            "price": 120.00,
            "discounted_price": 95.00,
            "discount_percentage": 20.83,
            "description": "Antibiotic for bacterial infections",
            "detailed_description": "Azithromycin is a macrolide antibiotic used to treat various bacterial infections including respiratory infections, skin infections, ear infections, and sexually transmitted diseases.",
            "how_to_use": "Take as prescribed by physician, usually once daily for 3-5 days",
            "side_effects": "Diarrhea, nausea, stomach pain, vomiting",
            "stock_quantity": 200,
            "in_stock": True,
            "prescription_required": True,
            "manufacturer": "Alembic Pharmaceuticals",
            "pack_size": "5 tablets",
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "rating": 4.4,
            "review_count": 156,
            "tags": ["antibiotic", "bacterial infection"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Medical Devices
        {
            "name": "Digital Thermometer",
            "brand": "Omron",
            "category": "medical_device",
            "product_type": "device",
            "price": 350.00,
            "discounted_price": 280.00,
            "discount_percentage": 20.00,
            "description": "Fast and accurate digital thermometer",
            "detailed_description": "Omron digital thermometer provides quick and accurate temperature readings in just 30 seconds. Features include fever alarm, memory recall, and waterproof design.",
            "how_to_use": "Place under tongue, armpit, or rectally as recommended",
            "stock_quantity": 150,
            "in_stock": True,
            "prescription_required": False,
            "manufacturer": "Omron Healthcare",
            "pack_size": "1 unit",
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "rating": 4.6,
            "review_count": 342,
            "tags": ["thermometer", "temperature", "fever"],
            "is_featured": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Blood Pressure Monitor",
            "brand": "Dr Trust",
            "category": "medical_device",
            "product_type": "device",
            "price": 1499.00,
            "discounted_price": 999.00,
            "discount_percentage": 33.36,
            "description": "Automatic blood pressure monitor with large display",
            "detailed_description": "Fully automatic upper arm blood pressure monitor with irregular heartbeat detector, large LCD display, and memory for 2 users (90 readings each).",
            "how_to_use": "Wrap cuff around upper arm, press start button, wait for reading",
            "stock_quantity": 80,
            "in_stock": True,
            "prescription_required": False,
            "manufacturer": "Dr Trust",
            "pack_size": "1 unit with cuff",
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Pune"],
            "rating": 4.5,
            "review_count": 456,
            "tags": ["BP monitor", "blood pressure", "hypertension"],
            "is_featured": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Supplements
        {
            "name": "Vitamin D3 60000 IU",
            "generic_name": "Cholecalciferol",
            "brand": "Uprise D3",
            "category": "supplement",
            "product_type": "capsule",
            "price": 85.00,
            "discounted_price": 72.00,
            "discount_percentage": 15.29,
            "description": "Vitamin D3 supplement for bone health",
            "detailed_description": "Cholecalciferol (Vitamin D3) is essential for calcium absorption, bone health, immune function, and overall wellbeing.",
            "how_to_use": "Take one capsule weekly or as directed by physician",
            "side_effects": "Nausea, vomiting (rare)",
            "stock_quantity": 250,
            "in_stock": True,
            "prescription_required": False,
            "manufacturer": "Alkem Laboratories",
            "pack_size": "4 capsules",
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "rating": 4.7,
            "review_count": 528,
            "tags": ["vitamin d", "bone health", "immunity"],
            "is_featured": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Omega 3 Fish Oil Capsules",
            "brand": "HealthKart",
            "category": "supplement",
            "product_type": "capsule",
            "price": 599.00,
            "discounted_price": 449.00,
            "discount_percentage": 25.04,
            "description": "Omega-3 fatty acids for heart and brain health",
            "detailed_description": "High-strength Omega-3 fish oil providing EPA and DHA for cardiovascular health, brain function, and joint support.",
            "how_to_use": "Take 1-2 capsules daily with meals",
            "stock_quantity": 180,
            "in_stock": True,
            "prescription_required": False,
            "manufacturer": "HealthKart",
            "pack_size": "60 capsules",
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Pune"],
            "rating": 4.4,
            "review_count": 289,
            "tags": ["omega 3", "heart health", "brain health"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Personal Care
        {
            "name": "Betadine Antiseptic Solution",
            "brand": "Betadine",
            "category": "personal_care",
            "product_type": "solution",
            "price": 120.00,
            "discounted_price": 95.00,
            "discount_percentage": 20.83,
            "description": "Antiseptic solution for wounds and cuts",
            "detailed_description": "Povidone-iodine antiseptic solution for treating minor cuts, wounds, abrasions, and burns. Kills bacteria, fungi, and viruses.",
            "how_to_use": "Clean the affected area, apply solution, let it dry",
            "stock_quantity": 200,
            "in_stock": True,
            "prescription_required": False,
            "manufacturer": "Win-Medicare",
            "pack_size": "100ml",
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "rating": 4.6,
            "review_count": 178,
            "tags": ["antiseptic", "wound care", "first aid"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # First Aid
        {
            "name": "Band-Aid Adhesive Bandages",
            "brand": "Band-Aid",
            "category": "first_aid",
            "product_type": "bandage",
            "price": 75.00,
            "discounted_price": 65.00,
            "discount_percentage": 13.33,
            "description": "Flexible adhesive bandages for minor cuts",
            "detailed_description": "Sterile adhesive bandages with hurt-free pad that won't stick to the wound. Provides cushioning and protection.",
            "how_to_use": "Clean wound, apply bandage, change daily",
            "stock_quantity": 400,
            "in_stock": True,
            "prescription_required": False,
            "manufacturer": "Johnson & Johnson",
            "pack_size": "20 strips",
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "rating": 4.5,
            "review_count": 234,
            "tags": ["bandage", "first aid", "wound care"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Baby Care
        {
            "name": "Johnson's Baby Powder",
            "brand": "Johnson's Baby",
            "category": "baby_care",
            "product_type": "powder",
            "price": 150.00,
            "discounted_price": 128.00,
            "discount_percentage": 14.67,
            "description": "Gentle baby powder for delicate skin",
            "detailed_description": "Clinically proven mild baby powder that helps absorb excess moisture and keeps baby's skin soft and dry.",
            "how_to_use": "Apply gently on clean, dry skin",
            "stock_quantity": 220,
            "in_stock": True,
            "prescription_required": False,
            "manufacturer": "Johnson & Johnson",
            "pack_size": "200g",
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "rating": 4.7,
            "review_count": 567,
            "tags": ["baby care", "powder", "skin care"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = await db.products.insert_many(products)
    print(f"✅ Added {len(result.inserted_ids)} products")
    
    # Add sample lab tests
    lab_tests = [
        # Full Body
        {
            "name": "Complete Health Checkup Package",
            "test_code": "FBP001",
            "category": "full_body",
            "package_type": "package",
            "description": "Comprehensive full body health checkup covering all vital parameters",
            "detailed_description": "This package includes complete blood count, lipid profile, liver function, kidney function, thyroid profile, blood sugar, and more. Ideal for annual health screening.",
            "what_it_measures": [
                "Complete Blood Count (CBC) - 28 parameters",
                "Lipid Profile - 8 parameters",
                "Liver Function Test - 12 parameters",
                "Kidney Function Test - 7 parameters",
                "Thyroid Profile - 3 parameters",
                "Blood Sugar - Fasting & PP",
                "Vitamin D3, B12",
                "Iron Studies"
            ],
            "why_take_this_test": "Regular health checkups help detect diseases early when they are most treatable. This comprehensive package screens for diabetes, heart disease, liver problems, kidney issues, and nutritional deficiencies.",
            "preparation_instructions": "Fasting of 10-12 hours required. Drink water normally. Avoid alcohol 24 hours before test.",
            "tests_included": [
                "CBC", "Lipid Profile", "LFT", "KFT", "Thyroid Profile", "Blood Sugar", "Vitamin D", "Vitamin B12", "Iron Studies"
            ],
            "parameters_count": 98,
            "price": 2499.00,
            "discounted_price": 1499.00,
            "discount_percentage": 40.02,
            "sample_type": "Blood",
            "fasting_required": True,
            "fasting_hours": 10,
            "report_time": "24 hours",
            "available_for_home_collection": True,
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "is_popular": True,
            "is_featured": True,
            "booking_count": 8940,
            "tags": ["full body", "health checkup", "annual screening"],
            "keywords": ["complete checkup", "full body test", "health package"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Routine Tests
        {
            "name": "Complete Blood Count (CBC)",
            "test_code": "CBC001",
            "category": "routine",
            "package_type": "individual",
            "description": "Comprehensive blood test to evaluate overall health",
            "detailed_description": "CBC measures red blood cells, white blood cells, and platelets. It helps detect infections, anemia, and other blood disorders.",
            "what_it_measures": [
                "Red Blood Cell Count",
                "Hemoglobin",
                "Hematocrit",
                "White Blood Cell Count",
                "Platelet Count",
                "MCV, MCH, MCHC",
                "Differential Count"
            ],
            "why_take_this_test": "CBC is the most common blood test ordered by doctors. It provides valuable information about your overall health and can help diagnose various conditions.",
            "preparation_instructions": "No fasting required. No special preparation needed.",
            "tests_included": ["CBC with Differential"],
            "parameters_count": 26,
            "price": 399.00,
            "discounted_price": 299.00,
            "discount_percentage": 25.06,
            "sample_type": "Blood",
            "fasting_required": False,
            "report_time": "6 hours",
            "available_for_home_collection": True,
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "is_popular": True,
            "is_featured": True,
            "booking_count": 15420,
            "tags": ["CBC", "blood test", "routine"],
            "keywords": ["complete blood count", "hemogram", "blood count"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # For Women
        {
            "name": "Women's Health Package",
            "test_code": "WHC001",
            "category": "for_women",
            "package_type": "package",
            "description": "Comprehensive health package designed specifically for women",
            "detailed_description": "This package includes tests for hormonal balance, thyroid function, bone health, anemia, and reproductive health markers important for women's wellbeing.",
            "what_it_measures": [
                "Complete Blood Count",
                "Thyroid Profile (T3, T4, TSH)",
                "Iron Studies",
                "Vitamin D3",
                "Vitamin B12",
                "Calcium, Vitamin levels",
                "Hormonal Profile (FSH, LH, Prolactin)",
                "Pap Smear (if applicable)"
            ],
            "why_take_this_test": "Women have unique health needs. This package screens for common issues like thyroid disorders, anemia, PCOS, and vitamin deficiencies.",
            "preparation_instructions": "Fasting of 8-10 hours required. Best done on day 2-5 of menstrual cycle for hormone tests.",
            "tests_included": [
                "CBC", "Thyroid Profile", "Iron Studies", "Vitamin D", "B12", "Hormonal Profile"
            ],
            "parameters_count": 45,
            "price": 2999.00,
            "discounted_price": 1999.00,
            "discount_percentage": 33.34,
            "sample_type": "Blood",
            "fasting_required": True,
            "fasting_hours": 10,
            "report_time": "24 hours",
            "available_for_home_collection": True,
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "is_popular": True,
            "is_featured": True,
            "booking_count": 5680,
            "tags": ["women health", "female", "hormones"],
            "keywords": ["women checkup", "female health", "PCOS"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # For Men
        {
            "name": "Men's Health Package",
            "test_code": "MHC001",
            "category": "for_men",
            "package_type": "package",
            "description": "Complete health screening package for men",
            "detailed_description": "Comprehensive package covering heart health, prostate health, testosterone levels, liver function, kidney function, and more.",
            "what_it_measures": [
                "Complete Blood Count",
                "Lipid Profile",
                "Liver Function",
                "Kidney Function",
                "Thyroid Profile",
                "Testosterone (Total & Free)",
                "PSA (Prostate)",
                "Vitamin D, B12"
            ],
            "why_take_this_test": "Men over 30 should get regular health checkups to screen for heart disease, diabetes, prostate issues, and hormonal imbalances.",
            "preparation_instructions": "Fasting of 10-12 hours required. Avoid smoking and alcohol 24 hours before test.",
            "tests_included": [
                "CBC", "Lipid Profile", "LFT", "KFT", "Thyroid", "Testosterone", "PSA"
            ],
            "parameters_count": 52,
            "price": 2799.00,
            "discounted_price": 1799.00,
            "discount_percentage": 35.73,
            "sample_type": "Blood",
            "fasting_required": True,
            "fasting_hours": 10,
            "report_time": "24 hours",
            "available_for_home_collection": True,
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "is_popular": True,
            "is_featured": True,
            "booking_count": 4820,
            "tags": ["men health", "male", "prostate"],
            "keywords": ["men checkup", "male health", "testosterone"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # X-rays & Scans
        {
            "name": "Chest X-Ray (PA View)",
            "test_code": "XR001",
            "category": "xrays_scans",
            "package_type": "individual",
            "description": "Chest X-ray to examine lungs, heart, and chest wall",
            "detailed_description": "PA (Posteroanterior) chest X-ray helps diagnose conditions affecting the lungs, heart, and chest wall including pneumonia, tuberculosis, lung cancer, and heart enlargement.",
            "what_it_measures": [
                "Lung fields",
                "Heart size and shape",
                "Chest wall",
                "Mediastinum",
                "Diaphragm"
            ],
            "why_take_this_test": "Chest X-ray is commonly used to diagnose respiratory symptoms like persistent cough, chest pain, shortness of breath, or to screen for tuberculosis.",
            "preparation_instructions": "No special preparation required. Remove jewelry and metal objects from chest area.",
            "tests_included": ["Chest X-Ray PA View"],
            "parameters_count": 1,
            "price": 4500.00,
            "discounted_price": 299.00,
            "discount_percentage": 25.00,
            "sample_type": "Imaging",
            "fasting_required": False,
            "report_time": "4 hours",
            "available_for_home_collection": False,
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "is_popular": True,
            "booking_count": 6250,
            "tags": ["xray", "chest", "lungs"],
            "keywords": ["chest xray", "lung xray", "PA view"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Lifestyle
        {
            "name": "Diabetes Screening Package",
            "test_code": "DIA001",
            "category": "lifestyle",
            "package_type": "package",
            "description": "Comprehensive diabetes screening and monitoring",
            "detailed_description": "Complete diabetes evaluation including blood sugar levels, HbA1c, kidney function, lipid profile to assess diabetes control and complications.",
            "what_it_measures": [
                "Fasting Blood Sugar",
                "Post Prandial Blood Sugar",
                "HbA1c (3-month average)",
                "Kidney Function",
                "Lipid Profile",
                "Urine Microalbumin"
            ],
            "why_take_this_test": "Essential for diabetes diagnosis, monitoring blood sugar control, and screening for diabetes-related complications.",
            "preparation_instructions": "Fast for 10-12 hours for fasting sugar. Eat normal meal 2 hours before PP sugar test.",
            "tests_included": [
                "FBS", "PPBS", "HbA1c", "KFT", "Lipid Profile", "Urine Microalbumin"
            ],
            "parameters_count": 22,
            "price": 1299.00,
            "discounted_price": 899.00,
            "discount_percentage": 30.79,
            "sample_type": "Blood, Urine",
            "fasting_required": True,
            "fasting_hours": 12,
            "report_time": "12 hours",
            "available_for_home_collection": True,
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "is_popular": True,
            "is_featured": True,
            "booking_count": 7340,
            "tags": ["diabetes", "blood sugar", "HbA1c"],
            "keywords": ["diabetes test", "sugar test", "diabetic screening"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Health Concerns
        {
            "name": "Heart Health Package",
            "test_code": "HRT001",
            "category": "health_concerns",
            "package_type": "package",
            "description": "Comprehensive cardiac health assessment",
            "detailed_description": "Complete cardiovascular risk assessment including lipid profile, cardiac enzymes, ECG, and other heart-related markers.",
            "what_it_measures": [
                "Lipid Profile (Total Cholesterol, LDL, HDL, Triglycerides)",
                "hs-CRP (inflammation marker)",
                "Homocysteine",
                "Lipoprotein (a)",
                "Blood Sugar",
                "ECG"
            ],
            "why_take_this_test": "Assess cardiovascular risk, monitor heart health, and detect early signs of heart disease.",
            "preparation_instructions": "Fasting of 12-14 hours required. Avoid alcohol and smoking 24 hours before test.",
            "tests_included": [
                "Lipid Profile", "hs-CRP", "Homocysteine", "Lp(a)", "ECG"
            ],
            "parameters_count": 15,
            "price": 2199.00,
            "discounted_price": 1599.00,
            "discount_percentage": 27.29,
            "sample_type": "Blood",
            "fasting_required": True,
            "fasting_hours": 12,
            "report_time": "24 hours",
            "available_for_home_collection": True,
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "is_popular": True,
            "booking_count": 4560,
            "tags": ["heart", "cardiac", "cholesterol"],
            "keywords": ["heart test", "cardiac checkup", "cholesterol"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # By Organ - Liver
        {
            "name": "Liver Function Test (LFT)",
            "test_code": "LFT001",
            "category": "by_organ",
            "package_type": "profile",
            "description": "Complete liver function assessment",
            "detailed_description": "Comprehensive panel to evaluate liver health, detect liver diseases, and monitor liver function.",
            "what_it_measures": [
                "Bilirubin (Total, Direct, Indirect)",
                "SGOT (AST)",
                "SGPT (ALT)",
                "Alkaline Phosphatase",
                "GGT",
                "Total Protein",
                "Albumin",
                "Globulin",
                "A/G Ratio"
            ],
            "why_take_this_test": "Diagnose liver diseases, monitor treatment progress, screen for hepatitis, fatty liver, cirrhosis.",
            "preparation_instructions": "Fasting of 8-10 hours recommended. Avoid alcohol 48 hours before test.",
            "tests_included": ["Complete LFT Panel"],
            "parameters_count": 12,
            "price": 699.00,
            "discounted_price": 499.00,
            "discount_percentage": 28.61,
            "sample_type": "Blood",
            "fasting_required": True,
            "fasting_hours": 8,
            "report_time": "12 hours",
            "available_for_home_collection": True,
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "is_popular": True,
            "booking_count": 8920,
            "tags": ["liver", "LFT", "hepatic"],
            "keywords": ["liver test", "LFT", "liver function"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        # Special Tests
        {
            "name": "Allergy Panel - Food & Inhalant",
            "test_code": "ALG001",
            "category": "special_tests",
            "package_type": "package",
            "description": "Comprehensive allergy testing for food and environmental allergens",
            "detailed_description": "Tests for IgE antibodies against 40+ common food and inhalant allergens including pollen, dust mites, molds, pet dander, nuts, milk, eggs, wheat, and seafood.",
            "what_it_measures": [
                "Food Allergens (20+ items)",
                "Inhalant Allergens (20+ items)",
                "Total IgE",
                "Specific IgE levels"
            ],
            "why_take_this_test": "Identify specific allergens causing symptoms like skin rashes, respiratory issues, digestive problems, or anaphylaxis.",
            "preparation_instructions": "No fasting required. Continue medications unless advised otherwise.",
            "tests_included": ["Food Allergy Panel", "Inhalant Allergy Panel"],
            "parameters_count": 42,
            "price": 4999.00,
            "discounted_price": 3499.00,
            "discount_percentage": 30.01,
            "sample_type": "Blood",
            "fasting_required": False,
            "report_time": "48 hours",
            "available_for_home_collection": True,
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Pune"],
            "is_popular": False,
            "booking_count": 1240,
            "tags": ["allergy", "IgE", "food allergy"],
            "keywords": ["allergy test", "food allergy", "environmental allergy"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Thyroid Profile (T3, T4, TSH)",
            "test_code": "THY001",
            "category": "by_organ",
            "package_type": "profile",
            "description": "Complete thyroid function assessment",
            "detailed_description": "Evaluates thyroid gland function by measuring T3, T4, and TSH levels to diagnose hypothyroidism, hyperthyroidism, and monitor thyroid treatment.",
            "what_it_measures": [
                "T3 (Triiodothyronine)",
                "T4 (Thyroxine)",
                "TSH (Thyroid Stimulating Hormone)"
            ],
            "why_take_this_test": "Diagnose thyroid disorders causing symptoms like weight changes, fatigue, hair loss, or irregular periods.",
            "preparation_instructions": "No fasting required. Morning sample preferred.",
            "tests_included": ["T3", "T4", "TSH"],
            "parameters_count": 3,
            "price": 599.00,
            "discounted_price": 449.00,
            "discount_percentage": 25.04,
            "sample_type": "Blood",
            "fasting_required": False,
            "report_time": "12 hours",
            "available_for_home_collection": True,
            "available_locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
            "is_popular": True,
            "is_featured": True,
            "booking_count": 11250,
            "tags": ["thyroid", "TSH", "T3 T4"],
            "keywords": ["thyroid test", "thyroid profile", "hypothyroid"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = await db.lab_tests.insert_many(lab_tests)
    print(f"✅ Added {len(result.inserted_ids)} lab tests")
    
    print("\n🎉 Database setup complete!")
    print(f"\n📊 Summary:")
    print(f"   - Products: {len(products)}")
    print(f"   - Lab Tests: {len(lab_tests)}")
    print(f"\n✨ Your MedAI platform is ready to use!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_database())
