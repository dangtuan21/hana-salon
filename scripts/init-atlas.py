#!/usr/bin/env python3
"""
Initialize MongoDB Atlas with Hana Salon data
Run this script after setting up your Atlas cluster
"""

import os
import sys
from pathlib import Path

# Add the ai-service directory to Python path
ai_service_path = Path(__file__).parent.parent / "ai-service"
sys.path.insert(0, str(ai_service_path))

from database import get_db_manager
from salon_data import services, technicians

def main():
    """Initialize Atlas database with salon data"""
    
    print("🚀 Initializing MongoDB Atlas with Hana Salon data...")
    
    # Check if environment variables are set
    mongodb_url = os.getenv('MONGODB_URL')
    if not mongodb_url:
        print("❌ Error: MONGODB_URL environment variable not set")
        print("Please set your Atlas connection string:")
        print("export MONGODB_URL='mongodb+srv://username:password@cluster.xxxxx.mongodb.net/hana_ai_salon?retryWrites=true&w=majority'")
        return False
    
    if not mongodb_url.startswith('mongodb+srv://'):
        print("⚠️  Warning: This doesn't look like an Atlas connection string")
        print("Atlas URLs should start with 'mongodb+srv://'")
    
    try:
        # Initialize database manager
        print("📡 Connecting to MongoDB Atlas...")
        db = get_db_manager()
        
        # Test connection
        db.client.admin.command('ping')
        print("✅ Successfully connected to Atlas!")
        
        # Clear existing data (optional - comment out if you want to preserve data)
        print("🧹 Clearing existing collections...")
        db.services_collection.delete_many({})
        db.technicians_collection.delete_many({})
        db.customers_collection.delete_many({})
        db.bookings_collection.delete_many({})
        
        # Initialize services
        print("💅 Adding nail services...")
        service_id_map = {}
        
        for service_data in services:
            service = db.create_service(
                name=service_data["name"],
                category=service_data["category"],
                duration_minutes=service_data["duration_minutes"],
                price=service_data["price"],
                description=service_data["description"],
                required_skill_level=service_data["required_skill_level"],
                popularity_score=service_data["popularity_score"]
            )
            if service:
                service_id_map[service_data["id"]] = str(service._id)
                print(f"  ✅ Added service: {service_data['name']}")
        
        # Initialize technicians
        print("👩‍💼 Adding technicians...")
        
        for tech_data in technicians:
            # Map old service IDs to new MongoDB ObjectIds
            mapped_specialties = []
            for old_service_id in tech_data["specialties"]:
                if old_service_id in service_id_map:
                    mapped_specialties.append(service_id_map[old_service_id])
            
            technician = db.create_technician(
                name=tech_data["name"],
                skill_level=tech_data["skill_level"],
                specialties=mapped_specialties,
                rating=tech_data["rating"],
                years_experience=tech_data["years_experience"],
                hourly_rate=tech_data["hourly_rate"],
                available_days=tech_data["available_days"],
                work_hours=tech_data["work_hours"],
                is_available=tech_data["is_available"],
                bio=tech_data["bio"]
            )
            if technician:
                print(f"  ✅ Added technician: {tech_data['name']}")
        
        # Print summary
        services_count = db.services_collection.count_documents({})
        technicians_count = db.technicians_collection.count_documents({})
        
        print("\n🎉 Atlas initialization completed successfully!")
        print(f"📊 Summary:")
        print(f"  • Services: {services_count}")
        print(f"  • Technicians: {technicians_count}")
        print(f"  • Database: {db.db_name}")
        print(f"  • Connection: Atlas Cloud")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing Atlas: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your Atlas connection string")
        print("2. Verify network access (IP whitelist)")
        print("3. Confirm database user permissions")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
