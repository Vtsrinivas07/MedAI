"""
Demo Patient Seed Script
Creates a fully-populated test patient account with rich mock data across ALL features.

Login:  patient@medai.com
Pass:   Patient@123
"""
from pymongo import MongoClient
import bcrypt
from datetime import datetime, timedelta, date
import os
from dotenv import load_dotenv
from bson import ObjectId
import random

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "medai")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

print("=" * 60)
print("🌱  MedAI — Demo Patient Seed  (Full Data)")
print("=" * 60)

# ------------------------------------------------------------------
# 1. PATIENT USER
# ------------------------------------------------------------------
email = "patient@medai.com"
existing = db.users.find_one({"email": email})
if existing:
    patient_id = str(existing["_id"])
    print(f"⚠️  Patient already exists  →  id={patient_id}")
else:
    pw_hash = bcrypt.hashpw(b"Patient@123", bcrypt.gensalt()).decode()
    doc = {
        "email":           email,
        "name":            "Alex Carter",
        "password_hash":   pw_hash,
        "role":            "patient",
        "mobile":          "+1 555-234-7890",
        "location":        "New York, NY",
        "date_of_birth":   datetime(1993, 6, 15),
        "gender":          "male",
        "height":          178.0,
        "weight":          73.5,
        "blood_group":     "O+",
        "allergies":       ["Penicillin"],
        "chronic_conditions": ["Type 2 Diabetes", "Hypertension"],
        "is_active":       True,
        "created_at":      datetime.utcnow(),
        "updated_at":      datetime.utcnow(),
    }
    result = db.users.insert_one(doc)
    patient_id = str(result.inserted_id)
    print(f"✅  Patient created  →  id={patient_id}")

# Fetch doctor id
doctor = db.users.find_one({"role": "doctor"})
if not doctor:
    print("❌  No doctor found — run insert_admin_doctor.py first")
    client.close()
    exit(1)
doctor_id   = str(doctor["_id"])
doctor_name = doctor.get("name", "Dr. Sarah Johnson")
print(f"🩺  Linked to doctor: {doctor_name}  ({doctor_id})")

# ------------------------------------------------------------------
# 2. CLEAR OLD DEMO DATA
# ------------------------------------------------------------------
db.prescriptions.delete_many({"patient_id": patient_id})
db.health_logs.delete_many({"user_id": patient_id})
db.medicine_reminders.delete_many({"user_id": patient_id})
db.orders.delete_many({"user_id": patient_id})
db.lab_orders.delete_many({"user_id": patient_id})
db.lab_test_bookings.delete_many({"user_id": patient_id})
db.chat_sessions.delete_many({"user_id": patient_id})
print("🗑️   Cleared old demo data")

# ------------------------------------------------------------------
# 3. PRESCRIPTIONS  (5 records)
# ------------------------------------------------------------------
prescriptions = [
    {
        "patient_id":   patient_id,
        "doctor_id":    doctor_id,
        "patient_name": "Alex Carter",
        "doctor_name":  doctor_name,
        "diagnosis":    "Type 2 Diabetes Mellitus",
        "medicines": [
            {"name": "Metformin",   "dosage": "500mg",  "frequency": "Twice daily",  "duration": "90 days", "instructions": "Take with meals to reduce GI side effects"},
            {"name": "Glimepiride", "dosage": "2mg",    "frequency": "Once daily",   "duration": "90 days", "instructions": "Take before breakfast"},
            {"name": "Vitamin B12", "dosage": "500mcg", "frequency": "Once daily",   "duration": "90 days", "instructions": "Take with water"},
        ],
        "lab_tests":  ["HbA1c", "Fasting Blood Sugar", "Lipid Profile"],
        "notes":      "Monitor blood sugar weekly. Target HbA1c < 7.0%. Diet control essential. Avoid sugary beverages.",
        "date":       datetime.utcnow() - timedelta(days=30),
        "status":     "active",
        "created_at": datetime.utcnow() - timedelta(days=30),
    },
    {
        "patient_id":   patient_id,
        "doctor_id":    doctor_id,
        "patient_name": "Alex Carter",
        "doctor_name":  doctor_name,
        "diagnosis":    "Essential Hypertension",
        "medicines": [
            {"name": "Amlodipine",  "dosage": "5mg",   "frequency": "Once daily", "duration": "60 days", "instructions": "Take in the morning"},
            {"name": "Losartan",    "dosage": "50mg",  "frequency": "Once daily", "duration": "60 days", "instructions": "Take with or without food"},
        ],
        "lab_tests":  ["Complete Blood Count", "Kidney Function Test"],
        "notes":      "Limit sodium intake to < 2g/day. Check BP every 3 days. Reduce stress. Regular exercise recommended.",
        "date":       datetime.utcnow() - timedelta(days=60),
        "status":     "active",
        "created_at": datetime.utcnow() - timedelta(days=60),
    },
    {
        "patient_id":   patient_id,
        "doctor_id":    doctor_id,
        "patient_name": "Alex Carter",
        "doctor_name":  doctor_name,
        "diagnosis":    "Upper Respiratory Tract Infection",
        "medicines": [
            {"name": "Amoxicillin",   "dosage": "500mg", "frequency": "Three times daily", "duration": "7 days",  "instructions": "Complete the full course even if feeling better"},
            {"name": "Paracetamol",   "dosage": "650mg", "frequency": "Every 6 hours",      "duration": "5 days",  "instructions": "For fever and pain, do not exceed 4g/day"},
            {"name": "Cetirizine",    "dosage": "10mg",  "frequency": "Once daily",          "duration": "5 days",  "instructions": "Take at bedtime; may cause drowsiness"},
        ],
        "notes":      "Rest well, stay hydrated. Steam inhalation helps. Consult immediately if breathing difficulty.",
        "date":       datetime.utcnow() - timedelta(days=90),
        "status":     "completed",
        "created_at": datetime.utcnow() - timedelta(days=90),
    },
    {
        "patient_id":   patient_id,
        "doctor_id":    doctor_id,
        "patient_name": "Alex Carter",
        "doctor_name":  doctor_name,
        "diagnosis":    "Vitamin D Deficiency",
        "medicines": [
            {"name": "Vitamin D3",  "dosage": "60,000 IU", "frequency": "Once a week", "duration": "12 weeks", "instructions": "Take with a fatty meal for better absorption"},
            {"name": "Calcium Carbonate", "dosage": "500mg", "frequency": "Twice daily", "duration": "12 weeks", "instructions": "Take after meals"},
        ],
        "lab_tests":  ["Vitamin D (25-OH)", "Serum Calcium"],
        "notes":      "Increase sun exposure (15-20 min/day). Foods rich in Vitamin D recommended.",
        "date":       datetime.utcnow() - timedelta(days=45),
        "status":     "active",
        "created_at": datetime.utcnow() - timedelta(days=45),
    },
    {
        "patient_id":   patient_id,
        "doctor_id":    doctor_id,
        "patient_name": "Alex Carter",
        "doctor_name":  doctor_name,
        "diagnosis":    "Acute Gastroenteritis",
        "medicines": [
            {"name": "Ondansetron",   "dosage": "4mg",   "frequency": "Every 8 hours", "duration": "3 days", "instructions": "For nausea and vomiting"},
            {"name": "ORS Sachets",   "dosage": "1 sachet", "frequency": "After every loose stool", "duration": "5 days", "instructions": "Dissolve in 200ml water"},
            {"name": "Pan-D",         "dosage": "1 tablet", "frequency": "Once daily",  "duration": "7 days", "instructions": "Take 30 minutes before meal"},
        ],
        "notes":      "Increase fluid intake. Bland diet (BRAT). Avoid dairy and spicy food for 5 days.",
        "date":       datetime.utcnow() - timedelta(days=150),
        "status":     "completed",
        "created_at": datetime.utcnow() - timedelta(days=150),
    },
]
db.prescriptions.insert_many(prescriptions)
print(f"✅  Prescriptions inserted  ({len(prescriptions)})")

# ------------------------------------------------------------------
# 4. HEALTH LOGS  (30 days of vitals)
# ------------------------------------------------------------------
health_logs = []
for i in range(30):
    day = datetime.utcnow() - timedelta(days=29 - i)
    day_str = day.strftime("%Y-%m-%d")
    # Simulate gradual BP improvement over the month
    bp_s   = 138 - int(i * 0.2) + random.randint(-4, 4)
    bp_d   = 88  - int(i * 0.1) + random.randint(-3, 3)
    hr     = 78 + random.randint(-5, 5)
    sugar  = 152.0 - (i * 0.3) + random.uniform(-8, 10)
    weight = round(74.2 - (i * 0.03) + random.uniform(-0.2, 0.2), 1)
    temp   = round(36.6 + random.uniform(-0.2, 0.4), 1)
    spo2   = random.choice([96, 97, 97, 97, 98, 98, 98, 99])

    health_logs.append({
        "user_id": patient_id,
        "date":    day_str,
        "vital_signs": {
            "blood_pressure_systolic":  max(110, bp_s),
            "blood_pressure_diastolic": max(68, bp_d),
            "heart_rate":               hr,
            "temperature":              temp,
            "weight":                   weight,
            "blood_sugar":              round(max(90, sugar), 1),
            "oxygen_saturation":        spo2,
        },
        "symptoms": random.choice([
            [],
            ["mild headache"],
            ["fatigue"],
            ["slight dizziness"],
            ["back pain"],
            [],
            [],
            [],
        ]),
        "mood":       random.choice(["good", "good", "okay", "great", "good", "okay"]),
        "notes":      random.choice(["", "", "Walked 30 mins", "Slept well", "Drank 2L water", ""]),
        "created_at": day,
        "updated_at": day,
    })

db.health_logs.insert_many(health_logs)
print(f"✅  Health logs inserted  ({len(health_logs)} days)")

# ------------------------------------------------------------------
# 5. MEDICINE REMINDERS  (5 active)
# ------------------------------------------------------------------
reminders = [
    {
        "user_id":      patient_id,
        "medicine_name":"Metformin 500mg",
        "dosage":       "500mg",
        "frequency":    "Twice daily",
        "times":        ["08:00", "20:00"],
        "start_date":   (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "end_date":     (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "is_active":    True,
        "notes":        "Take with meals",
        "created_at":   datetime.utcnow(),
    },
    {
        "user_id":      patient_id,
        "medicine_name":"Amlodipine 5mg",
        "dosage":       "5mg",
        "frequency":    "Once daily",
        "times":        ["08:00"],
        "start_date":   (datetime.utcnow() - timedelta(days=60)).strftime("%Y-%m-%d"),
        "end_date":     (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "is_active":    True,
        "notes":        "Take in the morning",
        "created_at":   datetime.utcnow(),
    },
    {
        "user_id":      patient_id,
        "medicine_name":"Glimepiride 2mg",
        "dosage":       "2mg",
        "frequency":    "Once daily",
        "times":        ["07:30"],
        "start_date":   (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "end_date":     (datetime.utcnow() + timedelta(days=60)).strftime("%Y-%m-%d"),
        "is_active":    True,
        "notes":        "Before breakfast",
        "created_at":   datetime.utcnow(),
    },
    {
        "user_id":      patient_id,
        "medicine_name":"Vitamin D3 60,000 IU",
        "dosage":       "60,000 IU",
        "frequency":    "Once weekly",
        "times":        ["09:00"],
        "start_date":   (datetime.utcnow() - timedelta(days=45)).strftime("%Y-%m-%d"),
        "end_date":     (datetime.utcnow() + timedelta(days=10)).strftime("%Y-%m-%d"),
        "is_active":    True,
        "notes":        "Take on Sunday with fatty meal",
        "created_at":   datetime.utcnow(),
    },
    {
        "user_id":      patient_id,
        "medicine_name":"Losartan 50mg",
        "dosage":       "50mg",
        "frequency":    "Once daily",
        "times":        ["19:00"],
        "start_date":   (datetime.utcnow() - timedelta(days=60)).strftime("%Y-%m-%d"),
        "end_date":     (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "is_active":    True,
        "notes":        "Take in the evening",
        "created_at":   datetime.utcnow(),
    },
]
db.medicine_reminders.insert_many(reminders)
print(f"✅  Medicine reminders inserted  ({len(reminders)})")

# ------------------------------------------------------------------
# 6. PHARMACY ORDERS  (5 orders — various statuses)
# ------------------------------------------------------------------
orders = [
    {
        "user_id":        patient_id,
        "order_number":   "ORD20260207001",
        "items": [
            {"product_id": "p1", "product_name": "Metformin 500mg (30 tabs)",   "quantity": 2, "price": 85.0},
            {"product_id": "p2", "product_name": "Paracetamol 650mg (10 tabs)", "quantity": 1, "price": 28.0},
            {"product_id": "p3", "product_name": "Cetirizine 10mg (10 tabs)",   "quantity": 1, "price": 32.0},
        ],
        "total_amount":   230.0,
        "status":         "delivered",
        "payment_status": "paid",
        "payment_method": "card",
        "shipping_address": {"street": "45 Park Ave", "city": "New York", "state": "NY", "zip": "10016"},
        "requires_prescription": True,
        "notes":          "",
        "created_at":     datetime.utcnow() - timedelta(days=30),
        "updated_at":     datetime.utcnow() - timedelta(days=27),
        "delivered_at":   datetime.utcnow() - timedelta(days=27),
    },
    {
        "user_id":        patient_id,
        "order_number":   "ORD20260215002",
        "items": [
            {"product_id": "p4", "product_name": "Amlodipine 5mg (30 tabs)",  "quantity": 1, "price": 120.0},
            {"product_id": "p5", "product_name": "Losartan 50mg (30 tabs)",   "quantity": 1, "price": 145.0},
            {"product_id": "p6", "product_name": "Vitamin D3 60,000 IU (4 caps)", "quantity": 1, "price": 180.0},
        ],
        "total_amount":   445.0,
        "status":         "delivered",
        "payment_status": "paid",
        "payment_method": "upi",
        "shipping_address": {"street": "45 Park Ave", "city": "New York", "state": "NY", "zip": "10016"},
        "requires_prescription": True,
        "notes":          "Delivered on time",
        "created_at":     datetime.utcnow() - timedelta(days=22),
        "updated_at":     datetime.utcnow() - timedelta(days=19),
        "delivered_at":   datetime.utcnow() - timedelta(days=19),
    },
    {
        "user_id":        patient_id,
        "order_number":   "ORD20260225003",
        "items": [
            {"product_id": "p7", "product_name": "Digital BP Monitor",         "quantity": 1, "price": 1299.0},
            {"product_id": "p8", "product_name": "Glucometer Kit (50 strips)", "quantity": 1, "price": 890.0},
            {"product_id": "p9", "product_name": "Digital Thermometer",        "quantity": 1, "price": 349.0},
        ],
        "total_amount":   2538.0,
        "status":         "delivered",
        "payment_status": "paid",
        "payment_method": "card",
        "shipping_address": {"street": "45 Park Ave", "city": "New York", "state": "NY", "zip": "10016"},
        "requires_prescription": False,
        "notes":          "",
        "created_at":     datetime.utcnow() - timedelta(days=12),
        "updated_at":     datetime.utcnow() - timedelta(days=9),
        "delivered_at":   datetime.utcnow() - timedelta(days=9),
    },
    {
        "user_id":        patient_id,
        "order_number":   "ORD20260305004",
        "items": [
            {"product_id": "p10", "product_name": "Omega-3 Fish Oil (60 softgels)", "quantity": 1, "price": 299.0},
            {"product_id": "p11", "product_name": "Vitamin B12 (30 tabs)",          "quantity": 2, "price": 180.0},
            {"product_id": "p12", "product_name": "Calcium + D3 (60 tabs)",         "quantity": 1, "price": 260.0},
        ],
        "total_amount":   919.0,
        "status":         "shipped",
        "payment_status": "paid",
        "payment_method": "upi",
        "shipping_address": {"street": "45 Park Ave", "city": "New York", "state": "NY", "zip": "10016"},
        "requires_prescription": False,
        "notes":          "Ring doorbell on arrival",
        "created_at":     datetime.utcnow() - timedelta(days=4),
        "updated_at":     datetime.utcnow() - timedelta(days=2),
    },
    {
        "user_id":        patient_id,
        "order_number":   "ORD20260308005",
        "items": [
            {"product_id": "p4", "product_name": "Amlodipine 5mg (30 tabs)",  "quantity": 1, "price": 120.0},
            {"product_id": "p1", "product_name": "Metformin 500mg (30 tabs)", "quantity": 2, "price": 85.0},
        ],
        "total_amount":   290.0,
        "status":         "processing",
        "payment_status": "paid",
        "payment_method": "card",
        "shipping_address": {"street": "45 Park Ave", "city": "New York", "state": "NY", "zip": "10016"},
        "requires_prescription": True,
        "notes":          "",
        "created_at":     datetime.utcnow() - timedelta(days=1),
        "updated_at":     datetime.utcnow(),
    },
]
db.orders.insert_many(orders)
print(f"✅  Orders inserted  ({len(orders)})")

# ------------------------------------------------------------------
# 7. LAB TEST BOOKINGS  (in lab_test_bookings collection)
# ------------------------------------------------------------------
# Try to fetch real lab test IDs from the catalog
hba1c_test   = db.lab_tests.find_one({"name": {"$regex": "HbA1c", "$options": "i"}})
lipid_test   = db.lab_tests.find_one({"name": {"$regex": "Lipid", "$options": "i"}})
cbc_test     = db.lab_tests.find_one({"name": {"$regex": "CBC|Complete Blood", "$options": "i"}})
fbs_test     = db.lab_tests.find_one({"name": {"$regex": "Fasting|Blood Sugar|Blood Glucose", "$options": "i"}})

hba1c_id  = str(hba1c_test["_id"])  if hba1c_test  else "test_hba1c"
lipid_id  = str(lipid_test["_id"])  if lipid_test  else "test_lipid"
cbc_id    = str(cbc_test["_id"])    if cbc_test    else "test_cbc"
fbs_id    = str(fbs_test["_id"])    if fbs_test    else "test_fbs"

lab_bookings = [
    {
        "user_id":          patient_id,
        "test_ids":         [hba1c_id],
        "test_names":       ["HbA1c (Glycated Hemoglobin)"],
        "total_price":      650.0,
        "scheduled_date":   (datetime.utcnow() - timedelta(days=20)).strftime("%Y-%m-%d"),
        "scheduled_time":   "08:00",
        "collection_type":  "lab",
        "address":          "45 Park Ave, New York, NY 10016",
        "contact_number":   "+1 555-234-7890",
        "status":           "completed",
        "payment_status":   "paid",
        "result":           "HbA1c: 7.2% (Reference: < 7.0%). Slightly elevated — medication dosage reviewed.",
        "notes":            "Fasting for 12 hours was maintained.",
        "created_at":       datetime.utcnow() - timedelta(days=22),
        "updated_at":       datetime.utcnow() - timedelta(days=18),
    },
    {
        "user_id":          patient_id,
        "test_ids":         [lipid_id],
        "test_names":       ["Lipid Profile (Total Cholesterol, LDL, HDL, Triglycerides)"],
        "total_price":      850.0,
        "scheduled_date":   (datetime.utcnow() - timedelta(days=10)).strftime("%Y-%m-%d"),
        "scheduled_time":   "07:30",
        "collection_type":  "home",
        "address":          "45 Park Ave, New York, NY 10016",
        "contact_number":   "+1 555-234-7890",
        "status":           "completed",
        "payment_status":   "paid",
        "result":           "Total Cholesterol: 198 mg/dL | LDL: 122 mg/dL | HDL: 48 mg/dL | Triglycerides: 164 mg/dL",
        "notes":            "Borderline LDL. Dietary changes and follow-up in 3 months advised.",
        "created_at":       datetime.utcnow() - timedelta(days=12),
        "updated_at":       datetime.utcnow() - timedelta(days=8),
    },
    {
        "user_id":          patient_id,
        "test_ids":         [cbc_id],
        "test_names":       ["Complete Blood Count (CBC)"],
        "total_price":      380.0,
        "scheduled_date":   (datetime.utcnow() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "scheduled_time":   "09:00",
        "collection_type":  "lab",
        "address":          "45 Park Ave, New York, NY 10016",
        "contact_number":   "+1 555-234-7890",
        "status":           "sample_collected",
        "payment_status":   "paid",
        "result":           None,
        "notes":            "Sample collected. Report expected in 24 hours.",
        "created_at":       datetime.utcnow() - timedelta(days=6),
        "updated_at":       datetime.utcnow() - timedelta(days=5),
    },
    {
        "user_id":          patient_id,
        "test_ids":         [fbs_id, hba1c_id],
        "test_names":       ["Fasting Blood Sugar", "HbA1c (Glycated Hemoglobin)"],
        "total_price":      900.0,
        "scheduled_date":   (datetime.utcnow() + timedelta(days=4)).strftime("%Y-%m-%d"),
        "scheduled_time":   "08:00",
        "collection_type":  "home",
        "address":          "45 Park Ave, New York, NY 10016",
        "contact_number":   "+1 555-234-7890",
        "status":           "confirmed",
        "payment_status":   "paid",
        "result":           None,
        "notes":            "Fast for 12 hours. Technician will arrive between 7:30-8:30 AM.",
        "created_at":       datetime.utcnow() - timedelta(days=1),
        "updated_at":       datetime.utcnow(),
    },
]
db.lab_test_bookings.insert_many(lab_bookings)
print(f"✅  Lab test bookings inserted  ({len(lab_bookings)})")

# ------------------------------------------------------------------
# 8. CHAT SESSIONS  (3 sessions with conversation history)
# ------------------------------------------------------------------
now = datetime.utcnow()
chat_sessions = [
    {
        "user_id":    patient_id,
        "title":      "Diabetes & Blood Sugar Management",
        "messages": [
            {"role": "user",      "content": "My blood sugar has been high lately, around 160 mg/dL. I'm on Metformin. What should I do?", "timestamp": (now - timedelta(days=5, hours=2)).isoformat()},
            {"role": "assistant", "content": "High blood sugar despite Metformin can happen for several reasons — diet, stress, or the need for dose adjustment. Here are some steps:\n\n1. **Check your diet**: Reduce refined carbs and sugary drinks. Focus on whole grains, vegetables, and lean proteins.\n2. **Increase physical activity**: Even 30 minutes of walking can significantly lower blood sugar.\n3. **Stay hydrated**: Drink at least 2–3 litres of water daily.\n4. **Medication compliance**: Ensure you're taking Metformin with meals as prescribed.\n5. **Monitor closely**: Log readings morning and evening for the next week.\n\nIf readings stay above 160 consistently, please consult Dr. Johnson for a possible dose adjustment or addition of another medication.", "timestamp": (now - timedelta(days=5, hours=1, minutes=58)).isoformat()},
            {"role": "user",      "content": "What foods should I completely avoid?", "timestamp": (now - timedelta(days=5, hours=1, minutes=50)).isoformat()},
            {"role": "assistant", "content": "For Type 2 Diabetes, strictly avoid or minimise:\n\n❌ **High glycemic foods**: White bread, white rice, potatoes, pasta\n❌ **Sugary beverages**: Sodas, fruit juices, energy drinks\n❌ **Sweets & desserts**: Cakes, cookies, candy, ice cream\n❌ **Processed snacks**: Chips, crackers, packaged foods\n❌ **Alcohol**: Especially beer and sweet cocktails\n\n✅ **Good alternatives**: Brown rice, whole wheat roti, oats, vegetables, nuts, legumes, and water/herbal tea.\n\nA diabetic dietitian consultation would be highly beneficial for a personalised meal plan.", "timestamp": (now - timedelta(days=5, hours=1, minutes=48)).isoformat()},
        ],
        "created_at": (now - timedelta(days=5, hours=2)).isoformat(),
        "updated_at": (now - timedelta(days=5, hours=1, minutes=48)).isoformat(),
    },
    {
        "user_id":    patient_id,
        "title":      "Blood Pressure & Hypertension Questions",
        "messages": [
            {"role": "user",      "content": "My BP reading today is 138/88. Is this concerning? I'm already on Amlodipine 5mg.", "timestamp": (now - timedelta(days=3, hours=3)).isoformat()},
            {"role": "assistant", "content": "A BP of 138/88 mmHg falls in the **Stage 1 Hypertension** range (target is < 130/80 for most adults with cardiovascular risk factors).\n\nSince you're on Amlodipine 5mg, this reading suggests partial control. Here's what can help:\n\n1. **Sodium reduction**: Limit salt to < 2g/day. Avoid pickles, processed meats, papad.\n2. **DASH diet**: Rich in fruits, vegetables, low-fat dairy, and whole grains.\n3. **Limit caffeine and alcohol**\n4. **Stress management**: Meditation or yoga for 20–30 minutes daily\n5. **Regular exercise**: 150 min/week of moderate aerobic activity\n\nI'd recommend logging your BP readings twice daily (morning and evening) and sharing them with Dr. Johnson at your next visit. The Losartan in your prescription should also be helping.", "timestamp": (now - timedelta(days=3, hours=2, minutes=57)).isoformat()},
            {"role": "user",      "content": "Should I be worried about kidney damage with high BP?", "timestamp": (now - timedelta(days=3, hours=2, minutes=45)).isoformat()},
            {"role": "assistant", "content": "Yes, prolonged uncontrolled hypertension can damage the kidneys — this is called **hypertensive nephropathy**. It happens because high pressure damages the tiny blood vessels in the kidneys over time.\n\n**Signs to watch out for:**\n- Swelling in feet or ankles\n- Decreased urine output\n- Foamy/frothy urine (protein in urine)\n- Persistent fatigue\n\n**Your prescribed Kidney Function Test (Creatinine, eGFR, BUN) will help assess kidney health.**\n\nThe good news: Losartan, which is part of your prescription, is specifically kidney-protective in hypertensive diabetic patients. Continue medications regularly and stay well-hydrated.", "timestamp": (now - timedelta(days=3, hours=2, minutes=40)).isoformat()},
        ],
        "created_at": (now - timedelta(days=3, hours=3)).isoformat(),
        "updated_at": (now - timedelta(days=3, hours=2, minutes=40)).isoformat(),
    },
    {
        "user_id":    patient_id,
        "title":      "Lab Results & Next Steps",
        "messages": [
            {"role": "user",      "content": "I got my HbA1c result: 7.2%. My doctor said it should be below 7.0%. How worried should I be?", "timestamp": (now - timedelta(days=1, hours=4)).isoformat()},
            {"role": "assistant", "content": "An HbA1c of **7.2%** means your average blood sugar over the past 2-3 months was approximately **154 mg/dL**. The target for most diabetics is **< 7.0%**.\n\nWhile 7.2% is only slightly above target, it's important to act now to prevent complications.\n\n📊 **What HbA1c means:**\n- Below 5.7%: Normal\n- 5.7–6.4%: Pre-diabetes\n- 6.5%+: Diabetes\n- Your target with medication: < 7.0%\n\n**Action plan:**\n1. Your doctor may consider increasing Metformin to 1000mg or adding a second medication.\n2. Tighten your diet — especially dinner and late-night snacks.\n3. Increase exercise to at least 45 min/day.\n4. Retest HbA1c in 3 months.\n\nYou're close to the target — small consistent changes will get you there! 💪", "timestamp": (now - timedelta(days=1, hours=3, minutes=57)).isoformat()},
            {"role": "user",      "content": "What medications could the doctor add if Metformin alone isn't enough?", "timestamp": (now - timedelta(days=1, hours=3, minutes=40)).isoformat()},
            {"role": "assistant", "content": "If Metformin alone isn't achieving target HbA1c, doctors commonly add one of these second-line agents:\n\n💊 **Common Add-on Medications:**\n1. **GLP-1 agonists** (e.g., Semaglutide, Liraglutide) — also help with weight loss\n2. **SGLT-2 inhibitors** (e.g., Empagliflozin, Dapagliflozin) — protect kidneys and heart, cause weight loss\n3. **DPP-4 inhibitors** (e.g., Sitagliptin, Vildagliptin) — well-tolerated, weight-neutral\n4. **Sulfonylureas** (e.g., Glimepiride, Gliclazide) — already part of your prescription!\n\nYour doctor will choose based on your specific risk profile, kidney function, weight, and cost considerations.\n\n⚠️ Never add or change medications without your doctor's guidance.", "timestamp": (now - timedelta(days=1, hours=3, minutes=35)).isoformat()},
        ],
        "created_at": (now - timedelta(days=1, hours=4)).isoformat(),
        "updated_at": (now - timedelta(days=1, hours=3, minutes=35)).isoformat(),
    },
]
db.chat_sessions.insert_many(chat_sessions)
print(f"✅  Chat sessions inserted  ({len(chat_sessions)})")

# ------------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("✨  Demo Patient Seed Complete!")
print("=" * 60)
print("\n🔑  PATIENT ACCOUNT:")
print("    Email:    patient@medai.com")
print("    Password: Patient@123")
print("\n📊  Data seeded:")
print(f"    • {len(prescriptions)} Prescriptions")
print(f"    • {len(health_logs)} Health logs (30 days)")
print(f"    • {len(reminders)} Medicine reminders")
print(f"    • {len(orders)} Pharmacy orders")
print(f"    • {len(lab_bookings)} Lab test bookings")
print(f"    • {len(chat_sessions)} Chat sessions")
print("=" * 60)

client.close()
