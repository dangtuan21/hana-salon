#!/usr/bin/env python3
"""
Initialize MongoDB database with nail salon data
"""

from database import DatabaseManager, Service, Technician, SkillLevel, ServiceCategory
from salon_data import NAIL_SERVICES, TECHNICIANS

def init_database():
    """Initialize database with salon data"""
    print("🚀 Initializing Hana AI Nail Salon Database...")
    
    db = DatabaseManager()
    
    # Clear existing data (for fresh start)
    print("🧹 Clearing existing data...")
    db.services.delete_many({})
    db.technicians.delete_many({})
    db.customers.delete_many({})
    db.bookings.delete_many({})
    
    # Insert services
    print("💅 Inserting nail services...")
    service_id_mapping = {}  # Map old IDs to new MongoDB IDs
    
    for old_service in NAIL_SERVICES:
        service = Service(
            name=old_service.name,
            category=old_service.category.value,
            duration_minutes=old_service.duration_minutes,
            price=old_service.price,
            description=old_service.description,
            required_skill_level=old_service.required_skill_level.value,
            popularity_score=old_service.popularity_score
        )
        
        new_id = db.create_service(service)
        service_id_mapping[old_service.id] = new_id
        print(f"  ✅ {service.name} -> {new_id}")
    
    # Insert technicians
    print("👩‍💼 Inserting technicians...")
    technician_id_mapping = {}  # Map old IDs to new MongoDB IDs
    
    for old_tech in TECHNICIANS:
        # Map old service IDs to new MongoDB IDs in specialties
        new_specialties = []
        for old_service_id in old_tech.specialties:
            if old_service_id in service_id_mapping:
                new_specialties.append(service_id_mapping[old_service_id])
        
        technician = Technician(
            name=old_tech.name,
            skill_level=old_tech.skill_level.value,
            specialties=new_specialties,
            rating=old_tech.rating,
            years_experience=old_tech.years_experience,
            hourly_rate=old_tech.hourly_rate,
            available_days=old_tech.available_days,
            work_hours=old_tech.work_hours,
            is_available=old_tech.is_available,
            bio=old_tech.bio
        )
        
        new_id = db.create_technician(technician)
        technician_id_mapping[old_tech.id] = new_id
        print(f"  ✅ {technician.name} ({technician.skill_level}) -> {new_id}")
    
    # Print summary
    print("\n📊 Database Initialization Summary:")
    print(f"  Services: {len(service_id_mapping)}")
    print(f"  Technicians: {len(technician_id_mapping)}")
    print(f"  Categories: {len(set(s.category for s in NAIL_SERVICES))}")
    print(f"  Skill Levels: {len(set(t.skill_level.value for t in TECHNICIANS))}")
    
    # Print ID mappings for reference
    print("\n🔗 Service ID Mappings:")
    for old_id, new_id in service_id_mapping.items():
        service = db.get_service_by_id(new_id)
        print(f"  {old_id} -> {new_id} ({service.name})")
    
    print("\n🔗 Technician ID Mappings:")
    for old_id, new_id in technician_id_mapping.items():
        tech = db.get_technician_by_id(new_id)
        print(f"  {old_id} -> {new_id} ({tech.name})")
    
    print("\n✅ Database initialization completed successfully!")
    return service_id_mapping, technician_id_mapping

def test_database():
    """Test database operations"""
    print("\n🧪 Testing database operations...")
    
    db = DatabaseManager()
    
    # Test service queries
    print("\n📋 Testing service queries:")
    services = db.get_all_services()
    print(f"  Total services: {len(services)}")
    
    gel_service = db.get_service_by_name("Gel Manicure")
    if gel_service:
        print(f"  Found service: {gel_service.name} - ${gel_service.price}")
    
    # Test technician queries
    print("\n👥 Testing technician queries:")
    technicians = db.get_available_technicians()
    print(f"  Available technicians: {len(technicians)}")
    
    if gel_service:
        specialists = db.get_technicians_for_service(gel_service._id)
        print(f"  Gel manicure specialists: {len(specialists)}")
        if specialists:
            print(f"    Best specialist: {specialists[0].name} ({specialists[0].rating}⭐)")
    
    # Test cost calculation
    if gel_service and specialists:
        cost = db.calculate_total_cost(gel_service._id, specialists[0]._id)
        print(f"  Total cost with {specialists[0].name}: ${cost}")
    
    print("\n✅ Database tests completed!")

if __name__ == "__main__":
    try:
        service_mapping, tech_mapping = init_database()
        test_database()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
