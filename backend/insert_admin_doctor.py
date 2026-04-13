"""
Insert admin and doctor accounts directly into MongoDB
"""
from pymongo import MongoClient
import bcrypt
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DB_NAME", "medai")

# Connect to MongoDB
client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]

print("🔐 Creating Admin and Doctor accounts...")
print("=" * 60)

# Admin account
admin_email = "admin@medai.com"
existing_admin = db.users.find_one({"email": admin_email})
if existing_admin:
    print(f"⚠️  Admin: {admin_email} already exists")
else:
    pw_hash = bcrypt.hashpw(b"Admin@123", bcrypt.gensalt()).decode()
    db.users.insert_one({
        "email":         admin_email,
        "name":          "Admin User",
        "password_hash": pw_hash,
        "role":          "admin",
        "profile_picture": None,
        "is_active":     True,
        "created_at":    datetime.utcnow(),
        "updated_at":    datetime.utcnow(),
    })
    print(f"✅ Admin: {admin_email} created")

# Doctor account — with full profile for NearbyDoctors / Doctor pages
doctor_email = "doctor@medai.com"
existing_doctor = db.users.find_one({"email": doctor_email})
if existing_doctor:
    # Update with rich profile fields if missing
    db.users.update_one(
        {"email": doctor_email},
        {"$set": {
            "specialty":          "General Physician",
            "specialization":     "General Physician",
            "qualification":      "MBBS, MD (Internal Medicine)",
            "experience_years":   12,
            "consultation_fee":   500,
            "rating":             4.8,
            "reviews":            187,
            "bio":                "Dr. Sarah Johnson is a highly experienced General Physician with over 12 years of practice specialising in Diabetes Management, Hypertension, and Preventive Healthcare. She is passionate about patient education and chronic disease management.",
            "languages":          ["English", "Spanish"],
            "location":           "New York, NY",
            "hospital":           "MedAI Health Centre, 45 Park Ave, New York, NY",
            "available_for_video": True,
            "available_for_appointment": True,
            "next_available":     "Today, 4:00 PM",
            "distance":           "1.5 km",
            "updated_at":         datetime.utcnow(),
        }}
    )
    print(f"⚠️  Doctor: {doctor_email} already exists — profile updated with rich data")
else:
    pw_hash = bcrypt.hashpw(b"Doctor@123", bcrypt.gensalt()).decode()
    db.users.insert_one({
        "email":           doctor_email,
        "name":            "Dr. Sarah Johnson",
        "password_hash":   pw_hash,
        "role":            "doctor",
        "mobile":          "+1 555-100-2000",
        "location":        "New York, NY",
        "specialty":       "General Physician",
        "specialization":  "General Physician",
        "qualification":   "MBBS, MD (Internal Medicine)",
        "experience_years": 12,
        "consultation_fee": 500,
        "rating":           4.8,
        "reviews":          187,
        "bio":              "Dr. Sarah Johnson is a highly experienced General Physician with over 12 years of practice specialising in Diabetes Management, Hypertension, and Preventive Healthcare.",
        "languages":        ["English", "Spanish"],
        "hospital":         "MedAI Health Centre, 45 Park Ave, New York, NY",
        "available_for_video": True,
        "available_for_appointment": True,
        "next_available":   "Today, 4:00 PM",
        "distance":         "1.5 km",
        "profile_picture":  None,
        "is_active":        True,
        "created_at":       datetime.utcnow(),
        "updated_at":       datetime.utcnow(),
    })
    print(f"✅ Doctor: {doctor_email} created")

print("=" * 60)
print("\n📝 Login Credentials:")
print("=" * 60)
print("\n🔑 ADMIN ACCOUNT:")
print("   Email:    admin@medai.com")
print("   Password: Admin@123")
print("   Access:   Full system control, create doctors")
print("\n👨‍⚕️ DOCTOR ACCOUNT:")
print("   Email:    doctor@medai.com")
print("   Password: Doctor@123")
print("   Access:   Patient management, prescriptions")
print("\n" + "=" * 60)
print("✨ You can now login at http://localhost:5173")
print("=" * 60)

client.close()
