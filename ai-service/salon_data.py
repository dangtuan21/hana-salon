#!/usr/bin/env python3
"""
Nail Salon Data - Services, Technicians, and Business Logic
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

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
class NailService:
    id: str
    name: str
    category: ServiceCategory
    duration_minutes: int
    price: float
    description: str
    required_skill_level: SkillLevel
    popularity_score: int  # 1-10, higher = more popular

@dataclass
class Technician:
    id: str
    name: str
    skill_level: SkillLevel
    specialties: List[str]  # Service IDs they excel at
    rating: float  # 1.0-5.0
    years_experience: int
    hourly_rate: float
    available_days: List[str]  # ["Monday", "Tuesday", ...]
    work_hours: Dict[str, str]  # {"start": "09:00", "end": "18:00"}
    is_available: bool
    bio: str

# Comprehensive Nail Services Catalog
NAIL_SERVICES = [
    # Basic Services
    NailService("basic_manicure", "Classic Manicure", ServiceCategory.BASIC, 45, 35.00, 
               "Traditional nail care with cuticle treatment, shaping, and regular polish", 
               SkillLevel.JUNIOR, 8),
    NailService("basic_pedicure", "Classic Pedicure", ServiceCategory.BASIC, 60, 45.00,
               "Foot soak, callus removal, nail care, and regular polish",
               SkillLevel.JUNIOR, 9),
    NailService("express_manicure", "Express Manicure", ServiceCategory.BASIC, 30, 25.00,
               "Quick nail shaping, cuticle care, and polish application",
               SkillLevel.JUNIOR, 7),
    
    # Advanced Services  
    NailService("gel_manicure", "Gel Manicure", ServiceCategory.ADVANCED, 60, 55.00,
               "Long-lasting gel polish with UV curing, lasts 2-3 weeks",
               SkillLevel.SENIOR, 10),
    NailService("gel_pedicure", "Gel Pedicure", ServiceCategory.ADVANCED, 75, 65.00,
               "Gel polish for toes with extended wear and chip resistance",
               SkillLevel.SENIOR, 9),
    NailService("acrylic_full_set", "Acrylic Full Set", ServiceCategory.ADVANCED, 90, 75.00,
               "Complete acrylic nail extensions with shaping and polish",
               SkillLevel.SENIOR, 8),
    NailService("acrylic_fill", "Acrylic Fill", ServiceCategory.ADVANCED, 60, 45.00,
               "Maintenance for existing acrylic nails",
               SkillLevel.SENIOR, 7),
    NailService("dip_powder", "Dip Powder Nails", ServiceCategory.ADVANCED, 75, 60.00,
               "Durable dip powder system for long-lasting color",
               SkillLevel.SENIOR, 8),
    
    # Specialty Services
    NailService("nail_art_simple", "Simple Nail Art", ServiceCategory.SPECIALTY, 30, 20.00,
               "Basic designs, dots, stripes, or simple patterns (add-on)",
               SkillLevel.SENIOR, 6),
    NailService("nail_art_complex", "Complex Nail Art", ServiceCategory.SPECIALTY, 60, 50.00,
               "Intricate designs, hand-painted art, 3D elements",
               SkillLevel.EXPERT, 5),
    NailService("french_manicure", "French Manicure", ServiceCategory.SPECIALTY, 50, 40.00,
               "Classic white tips with nude or clear base",
               SkillLevel.SENIOR, 7),
    NailService("ombre_nails", "Ombre/Gradient Nails", ServiceCategory.SPECIALTY, 75, 65.00,
               "Beautiful color gradient effect on nails",
               SkillLevel.EXPERT, 6),
    
    # Luxury Services
    NailService("luxury_spa_mani", "Luxury Spa Manicure", ServiceCategory.LUXURY, 90, 85.00,
               "Premium treatment with paraffin, massage, and luxury products",
               SkillLevel.EXPERT, 4),
    NailService("luxury_spa_pedi", "Luxury Spa Pedicure", ServiceCategory.LUXURY, 120, 95.00,
               "Deluxe foot treatment with hot stones, extended massage, and premium care",
               SkillLevel.EXPERT, 5),
    NailService("bridal_package", "Bridal Nail Package", ServiceCategory.LUXURY, 150, 150.00,
               "Complete bridal nail service with trial, custom design, and premium finish",
               SkillLevel.MASTER, 3),
    NailService("nail_repair", "Nail Repair", ServiceCategory.SPECIALTY, 30, 15.00,
               "Fix broken or damaged nails",
               SkillLevel.SENIOR, 4),
]

# Salon Technicians
TECHNICIANS = [
    # Master Level
    Technician("tech_001", "Isabella Rodriguez", SkillLevel.MASTER, 
              ["bridal_package", "nail_art_complex", "luxury_spa_mani", "luxury_spa_pedi"],
              4.9, 12, 85.00, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
              {"start": "10:00", "end": "19:00"}, True,
              "Master nail artist with 12+ years experience. Specializes in bridal and luxury services."),
    
    Technician("tech_002", "Sophia Chen", SkillLevel.MASTER,
              ["nail_art_complex", "ombre_nails", "bridal_package", "acrylic_full_set"],
              4.8, 10, 80.00, ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
              {"start": "09:00", "end": "18:00"}, True,
              "Award-winning nail artist known for intricate designs and perfect execution."),
    
    # Expert Level
    Technician("tech_003", "Emma Thompson", SkillLevel.EXPERT,
              ["luxury_spa_mani", "luxury_spa_pedi", "nail_art_complex", "gel_manicure"],
              4.7, 8, 70.00, ["Monday", "Wednesday", "Thursday", "Friday", "Saturday"],
              {"start": "09:30", "end": "18:30"}, True,
              "Expert in luxury treatments and complex nail art. Gentle touch with attention to detail."),
    
    Technician("tech_004", "Olivia Kim", SkillLevel.EXPERT,
              ["ombre_nails", "nail_art_complex", "gel_manicure", "dip_powder"],
              4.6, 7, 65.00, ["Monday", "Tuesday", "Thursday", "Friday", "Saturday"],
              {"start": "10:00", "end": "19:00"}, True,
              "Creative artist specializing in color gradients and modern nail trends."),
    
    Technician("tech_005", "Ava Martinez", SkillLevel.EXPERT,
              ["acrylic_full_set", "acrylic_fill", "nail_art_simple", "french_manicure"],
              4.5, 6, 60.00, ["Tuesday", "Wednesday", "Friday", "Saturday", "Sunday"],
              {"start": "11:00", "end": "20:00"}, True,
              "Acrylic specialist with precise shaping and long-lasting results."),
    
    # Senior Level
    Technician("tech_006", "Mia Johnson", SkillLevel.SENIOR,
              ["gel_manicure", "gel_pedicure", "french_manicure", "nail_art_simple"],
              4.4, 5, 50.00, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
              {"start": "09:00", "end": "17:00"}, True,
              "Reliable and efficient with gel services. Great for classic looks."),
    
    Technician("tech_007", "Charlotte Davis", SkillLevel.SENIOR,
              ["dip_powder", "gel_manicure", "basic_manicure", "basic_pedicure"],
              4.3, 4, 45.00, ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
              {"start": "10:00", "end": "18:00"}, True,
              "Dip powder expert with consistent, durable results."),
    
    Technician("tech_008", "Amelia Wilson", SkillLevel.SENIOR,
              ["acrylic_fill", "gel_pedicure", "nail_repair", "basic_pedicure"],
              4.2, 4, 45.00, ["Monday", "Tuesday", "Wednesday", "Saturday", "Sunday"],
              {"start": "12:00", "end": "20:00"}, True,
              "Afternoon specialist, great with maintenance services and repairs."),
    
    # Junior Level
    Technician("tech_009", "Harper Brown", SkillLevel.JUNIOR,
              ["basic_manicure", "basic_pedicure", "express_manicure"],
              4.1, 2, 35.00, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
              {"start": "09:00", "end": "17:00"}, True,
              "Enthusiastic junior technician, perfect for basic services and quick treatments."),
    
    Technician("tech_010", "Evelyn Garcia", SkillLevel.JUNIOR,
              ["basic_manicure", "express_manicure", "nail_repair"],
              4.0, 1, 30.00, ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
              {"start": "11:00", "end": "19:00"}, True,
              "New team member with great attention to detail and eagerness to learn."),
    
    Technician("tech_011", "Abigail Miller", SkillLevel.JUNIOR,
              ["basic_pedicure", "basic_manicure", "express_manicure"],
              4.0, 1, 30.00, ["Monday", "Wednesday", "Thursday", "Friday", "Saturday"],
              {"start": "10:00", "end": "18:00"}, True,
              "Gentle and thorough with basic services, building experience steadily."),
]

# Business Hours and Availability
BUSINESS_HOURS = {
    "Monday": {"open": "09:00", "close": "20:00"},
    "Tuesday": {"open": "09:00", "close": "20:00"},
    "Wednesday": {"open": "09:00", "close": "20:00"},
    "Thursday": {"open": "09:00", "close": "20:00"},
    "Friday": {"open": "09:00", "close": "21:00"},
    "Saturday": {"open": "08:00", "close": "21:00"},
    "Sunday": {"open": "10:00", "close": "18:00"},
}

def get_service_by_id(service_id: str) -> Optional[NailService]:
    """Get service details by ID"""
    for service in NAIL_SERVICES:
        if service.id == service_id:
            return service
    return None

def get_service_by_name(service_name: str) -> Optional[NailService]:
    """Get service details by name (fuzzy matching)"""
    service_name_lower = service_name.lower()
    
    # Exact match first
    for service in NAIL_SERVICES:
        if service.name.lower() == service_name_lower:
            return service
    
    # Partial match
    for service in NAIL_SERVICES:
        if service_name_lower in service.name.lower() or service.name.lower() in service_name_lower:
            return service
    
    return None

def get_technician_by_id(tech_id: str) -> Optional[Technician]:
    """Get technician details by ID"""
    for tech in TECHNICIANS:
        if tech.id == tech_id:
            return tech
    return None

def get_technician_by_name(tech_name: str) -> Optional[Technician]:
    """Get technician by name (fuzzy matching)"""
    tech_name_lower = tech_name.lower()
    
    # Exact match first
    for tech in TECHNICIANS:
        if tech.name.lower() == tech_name_lower:
            return tech
    
    # Partial match (first name or last name)
    for tech in TECHNICIANS:
        if tech_name_lower in tech.name.lower():
            return tech
    
    return None

def get_available_technicians_for_service(service_id: str, day: str = None) -> List[Technician]:
    """Get technicians who can perform a specific service"""
    service = get_service_by_id(service_id)
    if not service:
        return []
    
    available_techs = []
    for tech in TECHNICIANS:
        # Check if technician is available and has required skill level
        if (tech.is_available and 
            tech.skill_level.value in [service.required_skill_level.value, 
                                     SkillLevel.SENIOR.value, 
                                     SkillLevel.EXPERT.value, 
                                     SkillLevel.MASTER.value][
                                         [SkillLevel.JUNIOR.value, 
                                          SkillLevel.SENIOR.value, 
                                          SkillLevel.EXPERT.value, 
                                          SkillLevel.MASTER.value].index(service.required_skill_level.value):]):
            
            # Check day availability if specified
            if day and day not in tech.available_days:
                continue
                
            available_techs.append(tech)
    
    # Sort by rating (highest first) and specialization
    available_techs.sort(key=lambda t: (
        service_id in t.specialties,  # Specialists first
        t.rating
    ), reverse=True)
    
    return available_techs

def calculate_total_cost(service_id: str, technician_id: str) -> float:
    """Calculate total cost including technician premium"""
    service = get_service_by_id(service_id)
    technician = get_technician_by_id(technician_id)
    
    if not service or not technician:
        return 0.0
    
    base_cost = service.price
    
    # Add premium for higher skill levels
    skill_premium = {
        SkillLevel.JUNIOR: 0.0,
        SkillLevel.SENIOR: 0.1,    # 10% premium
        SkillLevel.EXPERT: 0.25,   # 25% premium  
        SkillLevel.MASTER: 0.5     # 50% premium
    }
    
    premium = base_cost * skill_premium.get(technician.skill_level, 0.0)
    return round(base_cost + premium, 2)

def get_popular_services(limit: int = 5) -> List[NailService]:
    """Get most popular services"""
    sorted_services = sorted(NAIL_SERVICES, key=lambda s: s.popularity_score, reverse=True)
    return sorted_services[:limit]

def get_services_by_category(category: ServiceCategory) -> List[NailService]:
    """Get services by category"""
    return [service for service in NAIL_SERVICES if service.category == category]
