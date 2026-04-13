"""
Script to add comprehensive health products to the database
Run: python add_health_products.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URI")  # Changed from MONGODB_URL to MONGODB_URI

# Comprehensive product catalog
PRODUCTS = [
    # Medicines
    {
        "name": "Paracetamol 500mg",
        "category": "medicines",
        "price": 25.0,
        "original_price": 30.0,
        "stock": 500,
        "description": "Effective pain relief and fever reducer",
        "manufacturer": "Cipla",
        "requires_prescription": False,
        "dosage_form": "tablet",
        "strength": "500mg",
        "pack_size": "10 tablets",
        "in_stock": True,
        "health_concern": "general"
    },
    {
        "name": "Metformin 500mg",
        "category": "medicines",
        "price": 120.0,
        "original_price": 150.0,
        "stock": 200,
        "description": "Blood sugar control for diabetes management",
        "manufacturer": "Sun Pharma",
        "requires_prescription": True,
        "dosage_form": "tablet",
        "strength": "500mg",
        "pack_size": "30 tablets",
        "in_stock": True,
        "health_concern": "diabetes"
    },
    {
        "name": "Aspirin 75mg",
        "category": "medicines",
        "price": 45.0,
        "stock": 300,
        "description": "Blood thinner for heart health",
        "manufacturer": "Bayer",
        "requires_prescription": True,
        "dosage_form": "tablet",
        "strength": "75mg",
        "pack_size": "20 tablets",
        "in_stock": True,
        "health_concern": "heart"
    },
    
    # Vitamins & Supplements
    {
        "name": "Vitamin D3 60000 IU",
        "category": "vitamins",
        "price": 85.0,
        "original_price": 100.0,
        "stock": 400,
        "description": "Bone health and immunity booster",
        "manufacturer": "HealthKart",
        "requires_prescription": False,
        "dosage_form": "capsule",
        "strength": "60000 IU",
        "pack_size": "4 capsules",
        "in_stock": True,
        "health_concern": "bone"
    },
    {
        "name": "Multivitamin Tablets",
        "category": "vitamins",
        "price": 299.0,
        "original_price": 399.0,
        "stock": 250,
        "description": "Complete daily nutrition with 25+ vitamins and minerals",
        "manufacturer": "Himalaya",
        "requires_prescription": False,
        "dosage_form": "tablet",
        "pack_size": "60 tablets",
        "in_stock": True,
        "health_concern": "immunity"
    },
    {
        "name": "Omega-3 Fish Oil",
        "category": "vitamins",
        "price": 599.0,
        "original_price": 799.0,
        "stock": 150,
        "description": "Heart and brain health support with EPA and DHA",
        "manufacturer": "GNC",
        "requires_prescription": False,
        "dosage_form": "softgel",
        "pack_size": "90 softgels",
        "in_stock": True,
        "health_concern": "heart"
    },
    {
        "name": "Calcium + Vitamin D Tablets",
        "category": "vitamins",
        "price": 249.0,
        "stock": 300,
        "description": "Strengthens bones and teeth",
        "manufacturer": "Carbamide Forte",
        "requires_prescription": False,
        "dosage_form": "tablet",
        "pack_size": "60 tablets",
        "in_stock": True,
        "health_concern": "bone"
    },
    {
        "name": "Vitamin C 1000mg",
        "category": "vitamins",
        "price": 399.0,
        "original_price": 499.0,
        "stock": 200,
        "description": "Immunity booster and antioxidant",
        "manufacturer": "Healthvit",
        "requires_prescription": False,
        "dosage_form": "tablet",
        "strength": "1000mg",
        "pack_size": "60 tablets",
        "in_stock": True,
        "health_concern": "immunity"
    },
    
    # Diet & Nutrition
    {
        "name": "Whey Protein Powder - Chocolate",
        "category": "diet_nutrition",
        "price": 1899.0,
        "original_price": 2499.0,
        "stock": 100,
        "description": "24g protein per serving for muscle building",
        "manufacturer": "MuscleBlaze",
        "requires_prescription": False,
        "pack_size": "1kg",
        "in_stock": True,
        "health_concern": "fitness"
    },
    {
        "name": "Plant-Based Protein Powder",
        "category": "diet_nutrition",
        "price": 1599.0,
        "original_price": 1999.0,
        "stock": 80,
        "description": "Vegan protein from pea and brown rice",
        "manufacturer": "Oziva",
        "requires_prescription": False,
        "pack_size": "1kg",
        "in_stock": True,
        "health_concern": "fitness"
    },
    {
        "name": "Apple Cider Vinegar",
        "category": "diet_nutrition",
        "price": 399.0,
        "stock": 200,
        "description": "Weight management and digestion support",
        "manufacturer": "WOW",
        "requires_prescription": False,
        "dosage_form": "liquid",
        "pack_size": "750ml",
        "in_stock": True
    },
    {
        "name": "Green Tea Extract Capsules",
        "category": "diet_nutrition",
        "price": 499.0,
        "original_price": 699.0,
        "stock": 150,
        "description": "Metabolism booster and fat burner",
        "manufacturer": "Nutrabay",
        "requires_prescription": False,
        "dosage_form": "capsule",
        "pack_size": "60 capsules",
        "in_stock": True
    },
    {
        "name": "Collagen Peptides Powder",
        "category": "diet_nutrition",
        "price": 1299.0,
        "stock": 100,
        "description": "Skin, hair, and joint health support",
        "manufacturer": "Boldfit",
        "requires_prescription": False,
        "pack_size": "500g",
        "in_stock": True
    },
    
    # Medical Devices
    {
        "name": "Digital BP Monitor",
        "category": "medical_devices",
        "price": 1499.0,
        "original_price": 1999.0,
        "stock": 50,
        "description": "Automatic blood pressure monitor with large display",
        "manufacturer": "Omron",
        "requires_prescription": False,
        "in_stock": True,
        "health_concern": "heart"
    },
    {
        "name": "Glucometer with 50 Strips",
        "category": "medical_devices",
        "price": 899.0,
        "original_price": 1299.0,
        "stock": 60,
        "description": "Blood glucose monitoring system",
        "manufacturer": "Accu-Chek",
        "requires_prescription": False,
        "in_stock": True,
        "health_concern": "diabetes"
    },
    {
        "name": "Digital Thermometer",
        "category": "medical_devices",
        "price": 199.0,
        "original_price": 299.0,
        "stock": 200,
        "description": "Fast and accurate temperature measurement",
        "manufacturer": "Dr. Morepen",
        "requires_prescription": False,
        "in_stock": True
    },
    {
        "name": "Pulse Oximeter",
        "category": "medical_devices",
        "price": 799.0,
        "original_price": 1199.0,
        "stock": 100,
        "description": "SpO2 and heart rate monitor",
        "manufacturer": "Beurer",
        "requires_prescription": False,
        "in_stock": True,
        "health_concern": "heart"
    },
    {
        "name": "Nebulizer Machine",
        "category": "medical_devices",
        "price": 1899.0,
        "stock": 40,
        "description": "Compact nebulizer for respiratory care",
        "manufacturer": "Omron",
        "requires_prescription": False,
        "in_stock": True
    },
    
    # Personal Care
    {
        "name": "Hand Sanitizer 500ml",
        "category": "personal_care",
        "price": 149.0,
        "original_price": 199.0,
        "stock": 500,
        "description": "70% alcohol-based sanitizer with moisturizers",
        "manufacturer": "Dettol",
        "requires_prescription": False,
        "in_stock": True
    },
    {
        "name": "Surgical Face Masks (Box of 50)",
        "category": "personal_care",
        "price": 299.0,
        "stock": 300,
        "description": "3-ply disposable face masks",
        "manufacturer": "3M",
        "requires_prescription": False,
        "in_stock": True
    },
    {
        "name": "Antiseptic Cream",
        "category": "personal_care",
        "price": 89.0,
        "stock": 200,
        "description": "First aid cream for cuts and burns",
        "manufacturer": "Boroline",
        "requires_prescription": False,
        "pack_size": "20g",
        "in_stock": True
    },
    
    # Ayurveda & Herbs
    {
        "name": "Ashwagandha Tablets",
        "category": "ayurveda",
        "price": 349.0,
        "original_price": 449.0,
        "stock": 150,
        "description": "Stress relief and energy booster",
        "manufacturer": "Himalaya",
        "requires_prescription": False,
        "dosage_form": "tablet",
        "pack_size": "60 tablets",
        "in_stock": True,
        "health_concern": "mental"
    },
    {
        "name": "Triphala Churna",
        "category": "ayurveda",
        "price": 199.0,
        "stock": 180,
        "description": "Digestive health and detox powder",
        "manufacturer": "Patanjali",
        "requires_prescription": False,
        "pack_size": "100g",
        "in_stock": True
    },
    {
        "name": "Giloy Capsules",
        "category": "ayurveda",
        "price": 299.0,
        "stock": 120,
        "description": "Immunity booster and fever management",
        "manufacturer": "Baidyanath",
        "requires_prescription": False,
        "dosage_form": "capsule",
        "pack_size": "60 capsules",
        "in_stock": True,
        "health_concern": "immunity"
    },
    {
        "name": "Brahmi Tablets",
        "category": "ayurveda",
        "price": 249.0,
        "stock": 140,
        "description": "Memory and brain function support",
        "manufacturer": "Himalaya",
        "requires_prescription": False,
        "dosage_form": "tablet",
        "pack_size": "60 tablets",
        "in_stock": True,
        "health_concern": "brain"
    },
    
    # Baby Care
    {
        "name": "Baby Lotion 200ml",
        "category": "baby_care",
        "price": 199.0,
        "stock": 150,
        "description": "Gentle moisturizing lotion for babies",
        "manufacturer": "Johnson's",
        "requires_prescription": False,
        "pack_size": "200ml",
        "in_stock": True
    },
    {
        "name": "Baby Diapers Large (44 pieces)",
        "category": "baby_care",
        "price": 599.0,
        "original_price": 699.0,
        "stock": 100,
        "description": "Ultra-soft and absorbent diapers",
        "manufacturer": "Pampers",
        "requires_prescription": False,
        "in_stock": True
    },
    {
        "name": "Baby Gripe Water",
        "category": "baby_care",
        "price": 89.0,
        "stock": 200,
        "description": "Relief from gas and colic",
        "manufacturer": "Woodward's",
        "requires_prescription": False,
        "pack_size": "130ml",
        "in_stock": True
    },
    
    # Fitness & Wellness
    {
        "name": "Resistance Bands Set",
        "category": "fitness",
        "price": 499.0,
        "original_price": 799.0,
        "stock": 80,
        "description": "5-piece resistance band set for home workouts",
        "manufacturer": "Boldfit",
        "requires_prescription": False,
        "in_stock": True
    },
    {
        "name": "Yoga Mat - Premium",
        "category": "fitness",
        "price": 799.0,
        "original_price": 1299.0,
        "stock": 60,
        "description": "Anti-slip exercise and yoga mat",
        "manufacturer": "Strauss",
        "requires_prescription": False,
        "in_stock": True
    },
    {
        "name": "Pre-Workout Energy Drink Mix",
        "category": "fitness",
        "price": 899.0,
        "stock": 90,
        "description": "Energy boost for intense workouts",
        "manufacturer": "BigMuscles",
        "requires_prescription": False,
        "pack_size": "300g",
        "in_stock": True
    },
]

async def add_products():
    """Add comprehensive product catalog to database"""
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client.medai
        
        print("🏥 Adding comprehensive health products to database...")
        
        # Add timestamps
        for product in PRODUCTS:
            product["created_at"] = datetime.utcnow()
            product["updated_at"] = datetime.utcnow()
            product["rating"] = 4.5
            product["reviews_count"] = 0
        
        # Insert products
        result = await db.products.insert_many(PRODUCTS)
        
        print(f"✅ Successfully added {len(result.inserted_ids)} products!")
        print(f"   - Medicines: {len([p for p in PRODUCTS if p['category'] == 'medicines'])}")
        print(f"   - Vitamins & Supplements: {len([p for p in PRODUCTS if p['category'] == 'vitamins'])}")
        print(f"   - Diet & Nutrition: {len([p for p in PRODUCTS if p['category'] == 'diet_nutrition'])}")
        print(f"   - Medical Devices: {len([p for p in PRODUCTS if p['category'] == 'medical_devices'])}")
        print(f"   - Personal Care: {len([p for p in PRODUCTS if p['category'] == 'personal_care'])}")
        print(f"   - Ayurveda & Herbs: {len([p for p in PRODUCTS if p['category'] == 'ayurveda'])}")
        print(f"   - Baby Care: {len([p for p in PRODUCTS if p['category'] == 'baby_care'])}")
        print(f"   - Fitness & Wellness: {len([p for p in PRODUCTS if p['category'] == 'fitness'])}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error adding products: {e}")

if __name__ == "__main__":
    asyncio.run(add_products())
