#!/usr/bin/env python3
"""
MongoDB Database Configuration and Models for Hana Salon

This module provides database operations for the AI booking service.
The AI service focuses on booking/scheduling operations only.
CRUD operations for services, technicians, and customers should be 
handled by the main backend application or admin interface.
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from bson import ObjectId
from dataclasses import dataclass, asdict
from enum import Enum
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "hanadb")

class SkillLevel(Enum):
    JUNIOR = "Junior"
    SENIOR = "Senior"
    EXPERT = "Expert"
    MASTER = "Master"

class ServiceCategory(Enum):
    BASIC = "Basic Services"
    ADVANCED = "Advanced Services"
    SPECIALTY = "Specialty Services"
    LUXURY = "Luxury Services"

@dataclass
class Service:
    name: str
    category: str
    duration_minutes: int
    price: float
    description: str
    required_skill_level: str
    popularity_score: int
    _id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Technician:
    name: str
    skill_level: str
    specialties: List[str]  # Service IDs they excel at
    rating: float
    years_experience: int
    hourly_rate: float
    available_days: List[str]
    work_hours: Dict[str, str]
    is_available: bool
    bio: str
    phone: Optional[str] = None
    email: Optional[str] = None
    _id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Customer:
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    booking_history: Optional[List[str]] = None  # Booking IDs
    _id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Booking:
    customer_id: str
    service_id: str
    technician_id: str
    date: str
    time: str
    duration_minutes: int
    total_cost: float
    status: str  # pending, confirmed, completed, cancelled
    confirmation_id: str
    notes: Optional[str] = None
    _id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class DatabaseManager:
    """
    Read-only database manager for AI booking service.
    Database initialization and schema management should be handled by the backend service.
    """
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.services = self.db.services
        self.technicians = self.db.technicians
        self.customers = self.db.customers
        self.bookings = self.db.bookings
    
    # Service operations (read-only)
    
    def get_service_by_id(self, service_id: str) -> Optional[Service]:
        """Get service by ID"""
        try:
            service_doc = self.services.find_one({"_id": ObjectId(service_id)})
            if service_doc:
                service_doc['_id'] = str(service_doc['_id'])
                return Service(**service_doc)
        except:
            pass
        return None
    
    def get_service_by_name(self, name: str) -> Optional[Service]:
        """Get service by name (case insensitive)"""
        service_doc = self.services.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        if service_doc:
            service_doc['_id'] = str(service_doc['_id'])
            return Service(**service_doc)
        return None
    
    def get_all_services(self) -> List[Service]:
        """Get all services"""
        services = []
        for doc in self.services.find():
            doc['_id'] = str(doc['_id'])
            services.append(Service(**doc))
        return services
    
    def get_services_by_category(self, category: str) -> List[Service]:
        """Get services by category"""
        services = []
        for doc in self.services.find({"category": category}):
            doc['_id'] = str(doc['_id'])
            services.append(Service(**doc))
        return services
    
    # Technician operations (read-only)
    
    def get_technician_by_id(self, tech_id: str) -> Optional[Technician]:
        """Get technician by ID"""
        try:
            tech_doc = self.technicians.find_one({"_id": ObjectId(tech_id)})
            if tech_doc:
                tech_doc['_id'] = str(tech_doc['_id'])
                return Technician(**tech_doc)
        except:
            pass
        return None
    
    def get_technician_by_name(self, name: str) -> Optional[Technician]:
        """Get technician by name (case insensitive)"""
        tech_doc = self.technicians.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        if tech_doc:
            tech_doc['_id'] = str(tech_doc['_id'])
            return Technician(**tech_doc)
        return None
    
    def get_available_technicians(self) -> List[Technician]:
        """Get all available technicians"""
        technicians = []
        for doc in self.technicians.find({"is_available": True}):
            doc['_id'] = str(doc['_id'])
            technicians.append(Technician(**doc))
        return technicians
    
    def get_technicians_for_service(self, service_id: str) -> List[Technician]:
        """Get technicians who can perform a specific service"""
        service = self.get_service_by_id(service_id)
        if not service:
            return []
        
        # Find technicians with appropriate skill level and availability
        skill_hierarchy = {
            "Junior": 1,
            "Senior": 2,
            "Expert": 3,
            "Master": 4
        }
        
        required_level = skill_hierarchy.get(service.required_skill_level, 1)
        
        technicians = []
        for doc in self.technicians.find({"is_available": True}):
            tech_level = skill_hierarchy.get(doc.get("skill_level", "Junior"), 1)
            if tech_level >= required_level:
                doc['_id'] = str(doc['_id'])
                technicians.append(Technician(**doc))
        
        # Sort by specialization and rating
        technicians.sort(key=lambda t: (
            service_id in t.specialties,  # Specialists first
            t.rating
        ), reverse=True)
        
        return technicians
    
    # Customer operations (read-only)
    
    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        """Get customer by phone number"""
        if not phone:
            return None
        customer_doc = self.customers.find_one({"phone": phone})
        if customer_doc:
            customer_doc['_id'] = str(customer_doc['_id'])
            return Customer(**customer_doc)
        return None
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        try:
            customer_doc = self.customers.find_one({"_id": ObjectId(customer_id)})
            if customer_doc:
                customer_doc['_id'] = str(customer_doc['_id'])
                return Customer(**customer_doc)
        except:
            pass
        return None
    
    # Booking operations (read-only)
    
    def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID"""
        try:
            booking_doc = self.bookings.find_one({"_id": ObjectId(booking_id)})
            if booking_doc:
                booking_doc['_id'] = str(booking_doc['_id'])
                return Booking(**booking_doc)
        except:
            pass
        return None
    
    def get_booking_by_confirmation_id(self, confirmation_id: str) -> Optional[Booking]:
        """Get booking by confirmation ID"""
        booking_doc = self.bookings.find_one({"confirmation_id": confirmation_id})
        if booking_doc:
            booking_doc['_id'] = str(booking_doc['_id'])
            return Booking(**booking_doc)
        return None
    
    def get_customer_bookings(self, customer_id: str) -> List[Booking]:
        """Get all bookings for a customer"""
        bookings = []
        for doc in self.bookings.find({"customer_id": customer_id}):
            doc['_id'] = str(doc['_id'])
            bookings.append(Booking(**doc))
        return bookings
    
    # Utility methods
    def calculate_total_cost(self, service_id: str, technician_id: str) -> float:
        """Calculate total cost including technician premium"""
        service = self.get_service_by_id(service_id)
        technician = self.get_technician_by_id(technician_id)
        
        if not service or not technician:
            return 0.0
        
        base_cost = service.price
        
        # Add premium for higher skill levels
        skill_premium = {
            "Junior": 0.0,
            "Senior": 0.1,    # 10% premium
            "Expert": 0.25,   # 25% premium  
            "Master": 0.5     # 50% premium
        }
        
        premium = base_cost * skill_premium.get(technician.skill_level, 0.0)
        return round(base_cost + premium, 2)
    
    def close_connection(self):
        """Close database connection"""
        self.client.close()

# Global database instance
db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get database manager instance (singleton)"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
