#!/usr/bin/env python3
"""
Initialize MongoDB database with salon data
"""

from database import DatabaseManager, Service, Technician, SkillLevel, ServiceCategory, Customer, Booking
from salon_data import services, technicians

def init_database():
    """Initialize database with salon data"""
    print("🚀 Initializing Hana Salon Database...")
    
    db = DatabaseManager()
    
    # Clear existing data (for fresh start)
    print("🧹 Clearing existing data...")
    db.services.delete_many({})
    db.technicians.delete_many({})
    db.customers.delete_many({})
    db.bookings.delete_many({})
    
    # Insert services
    print("💅 Inserting salon services...")
    service_id_mapping = {}  # Map old IDs to new MongoDB IDs
    
    for old_service in services:
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
    
    for old_tech in technicians:
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
    
    # Insert sample customers for testing
    print("👥 Inserting sample customers...")
    sample_customers = [
        Customer(
            name="Sarah Johnson",
            phone="555-123-4567",
            email="sarah.johnson@email.com",
            preferences={"preferred_technician": "Emma Thompson"},
            booking_history=[]
        ),
        Customer(
            name="Michael Chen",
            phone="555-987-6543",
            email="michael.chen@email.com",
            preferences={"preferred_service": "Gel Manicure"},
            booking_history=[]
        ),
        Customer(
            name="Emily Davis",
            phone="555-456-7890",
            email="emily.davis@email.com",
            preferences={},
            booking_history=[]
        ),
        Customer(
            name="John Smith",
            phone=None,  # Customer without phone
            email="john.smith@email.com",
            preferences={"preferred_technician": "Isabella Rodriguez"},
            booking_history=[]
        )
    ]
    
    customer_ids = []
    for customer in sample_customers:
        customer_id = db.create_customer(customer)
        customer_ids.append(customer_id)
        print(f"  ✅ {customer.name} -> {customer_id}")
    
    # Insert sample bookings for testing
    print("� Inserting sample bookings...")
    from datetime import datetime, timedelta
    
    # Get some services and technicians for bookings
    gel_service = db.get_service_by_name("Gel Manicure")
    basic_service = db.get_service_by_name("Classic Manicure")
    emma = db.get_technician_by_name("Emma Thompson")
    isabella = db.get_technician_by_name("Isabella Rodriguez")
    
    sample_bookings = []
    if gel_service and basic_service and emma and isabella:
        sample_bookings = [
            Booking(
                customer_id=customer_ids[0],  # Sarah Johnson
                service_id=gel_service._id,
                technician_id=emma._id,
                date="2024-12-20",
                time="14:00",
                duration_minutes=gel_service.duration_minutes,
                total_cost=db.calculate_total_cost(gel_service._id, emma._id),
                status="confirmed",
                confirmation_id="SPA-20241220140000",
                notes="Booked via test data - Gel Manicure with Emma"
            ),
            Booking(
                customer_id=customer_ids[1],  # Michael Chen
                service_id=basic_service._id,
                technician_id=isabella._id,
                date="2024-12-21",
                time="10:30",
                duration_minutes=basic_service.duration_minutes,
                total_cost=db.calculate_total_cost(basic_service._id, isabella._id),
                status="confirmed",
                confirmation_id="SPA-20241221103000",
                notes="Booked via test data - Classic Manicure with Isabella"
            ),
            Booking(
                customer_id=customer_ids[2],  # Emily Davis
                service_id=gel_service._id,
                technician_id=emma._id,
                date="2024-12-22",
                time="16:00",
                duration_minutes=gel_service.duration_minutes,
                total_cost=db.calculate_total_cost(gel_service._id, emma._id),
                status="completed",
                confirmation_id="SPA-20241222160000",
                notes="Booked via test data - Completed Gel Manicure"
            )
        ]
        
        booking_ids = []
        for booking in sample_bookings:
            booking_id = db.create_booking(booking)
            booking_ids.append(booking_id)
            customer = db.get_customer_by_id(booking.customer_id)
            service = db.get_service_by_id(booking.service_id)
            print(f"  ✅ {customer.name} - {service.name} -> {booking_id}")
            
            # Update customer booking history
            if customer.booking_history is None:
                customer.booking_history = []
            customer.booking_history.append(booking_id)
            db.update_customer(customer._id, {"booking_history": customer.booking_history})

    print("\n📊 Database Initialization Summary:")
    print(f"  Services: {len(services)}")
    print(f"  Technicians: {len(technicians)}")
    print(f"  Customers: {len(sample_customers)}")
    print(f"  Bookings: {len(sample_bookings)}")
    print(f"  Categories: {len(set(service.category for service in services))}")
    print(f"  Skill Levels: {len(set(tech.skill_level for tech in technicians))}")
    
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
