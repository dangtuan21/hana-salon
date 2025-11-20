#!/usr/bin/env python3
"""
Explicit BookingState data structures for type safety and documentation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class BookingStatus(str, Enum):
    """Booking status enumeration - aligned with backend IBooking"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PaymentMethod(str, Enum):
    """Payment method enumeration - aligned with backend IBooking"""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    DIGITAL_WALLET = "digital_wallet"


@dataclass
class TechnicianInfo:
    """Technician information structure"""
    _id: str
    firstName: str
    lastName: str
    employeeId: str
    specialties: List[str]
    skillLevel: str
    rating: int
    
    @property
    def full_name(self) -> str:
        """Get technician's full name"""
        return f"{self.firstName} {self.lastName}"


@dataclass
class ServiceInfo:
    """Service information structure"""
    _id: str
    name: str
    category: str
    duration_minutes: int
    price: float
    description: str


@dataclass
class ServiceTechnicianPair:
    """Service-Technician pair - aligned with backend IServiceTechnicianPair"""
    serviceId: str
    technicianId: str
    duration: int  # Duration for this specific service
    price: float   # Price for this specific service
    status: str = "scheduled"
    notes: Optional[str] = None  # Service-specific notes


@dataclass
class BookingRating:
    """Booking rating structure - aligned with backend IBooking.rating"""
    score: int  # Rating score
    comment: Optional[str] = None
    ratedAt: Optional[datetime] = None


@dataclass
class BookingState:
    """
    Booking state structure aligned with backend IBooking interface
    
    This represents both the conversation state and the final booking data
    that will be sent to the backend API.
    """
    
    # === Conversation State (AI Service specific) ===
    # Natural language inputs from customer
    customer_name: str = ""
    customer_phone: str = ""
    services_requested: str = ""  # Natural language service name
    date_requested: str = ""      # Natural language date (e.g., "Monday")
    time_requested: str = ""      # Natural language time (e.g., "1 PM")
    technician_preference: str = ""  # Customer's preferred technician
    
    # Available options (populated during conversation)
    available_technicians: List[TechnicianInfo] = field(default_factory=list)
    available_services: List[ServiceInfo] = field(default_factory=list)
    alternative_times: List[Dict[str, Any]] = field(default_factory=list)  # Alternative time slots when conflict occurs
    
    # === Backend IBooking Fields ===
    # These align exactly with the backend Booking model
    customerId: Optional[str] = None  # Will be set after customer creation
    services: List[ServiceTechnicianPair] = field(default_factory=list)  # IServiceTechnicianPair[]
    appointmentDate: Optional[str] = None  # ISO date string (parsed from date_requested)
    startTime: Optional[str] = None       # Time string (parsed from time_requested)
    endTime: Optional[str] = None         # Calculated from startTime + totalDuration
    status: BookingStatus = BookingStatus.SCHEDULED
    totalDuration: int = 0                # Sum of all service durations
    totalPrice: float = 0.0               # Sum of all service prices
    paymentStatus: str = "pending"
    paymentMethod: Optional[PaymentMethod] = None
    notes: Optional[str] = None           # General booking notes
    customerNotes: Optional[str] = None
    cancellationReason: Optional[str] = None
    reminderSent: bool = False
    confirmationSent: bool = False
    rating: Optional[BookingRating] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            # Conversation state
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "services_requested": self.services_requested,
            "date_requested": self.date_requested,
            "time_requested": self.time_requested,
            "technician_preference": self.technician_preference,
            
            # Backend IBooking fields
            "customerId": self.customerId,
            "services": [
                {
                    "serviceId": svc.serviceId,
                    "technicianId": svc.technicianId,
                    "duration": svc.duration,
                    "price": svc.price,
                    "status": svc.status,
                    "notes": svc.notes
                } for svc in self.services
            ],
            "appointmentDate": self.appointmentDate,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "status": self.status.value,
            "totalDuration": self.totalDuration,
            "totalPrice": self.totalPrice,
            "paymentStatus": self.paymentStatus,
            "paymentMethod": self.paymentMethod.value if self.paymentMethod else None,
            "notes": self.notes,
            "customerNotes": self.customerNotes,
            "cancellationReason": self.cancellationReason,
            "reminderSent": self.reminderSent,
            "confirmationSent": self.confirmationSent,
            "rating": {
                "score": self.rating.score,
                "comment": self.rating.comment,
                "ratedAt": self.rating.ratedAt.isoformat() if self.rating.ratedAt else None
            } if self.rating else None,
            "available_technicians": [
                {
                    "_id": tech._id if hasattr(tech, '_id') else tech.get('_id'),
                    "firstName": tech.firstName if hasattr(tech, 'firstName') else tech.get('firstName'),
                    "lastName": tech.lastName if hasattr(tech, 'lastName') else tech.get('lastName'),
                    "employeeId": tech.employeeId if hasattr(tech, 'employeeId') else tech.get('employeeId'),
                    "specialties": tech.specialties if hasattr(tech, 'specialties') else tech.get('specialties'),
                    "skillLevel": tech.skillLevel if hasattr(tech, 'skillLevel') else tech.get('skillLevel'),
                    "rating": tech.rating if hasattr(tech, 'rating') else tech.get('rating')
                } for tech in self.available_technicians
            ],
            "available_services": [
                {
                    "_id": svc._id if hasattr(svc, '_id') else svc.get('_id'),
                    "name": svc.name if hasattr(svc, 'name') else svc.get('name'),
                    "category": svc.category if hasattr(svc, 'category') else svc.get('category'),
                    "duration_minutes": svc.duration_minutes if hasattr(svc, 'duration_minutes') else svc.get('duration_minutes'),
                    "price": svc.price if hasattr(svc, 'price') else svc.get('price'),
                    "description": svc.description if hasattr(svc, 'description') else svc.get('description')
                } for svc in self.available_services
            ],
            "alternative_times": self.alternative_times
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BookingState':
        """Create BookingState from dictionary"""
        booking_state = cls(
            # Conversation state
            customer_name=data.get("customer_name", ""),
            customer_phone=data.get("customer_phone", ""),
            services_requested=data.get("services_requested", ""),
            date_requested=data.get("date_requested", ""),
            time_requested=data.get("time_requested", ""),
            technician_preference=data.get("technician_preference", ""),
            
            # Backend IBooking fields
            customerId=data.get("customerId"),
            appointmentDate=data.get("appointmentDate"),
            startTime=data.get("startTime"),
            endTime=data.get("endTime"),
            status=BookingStatus(data.get("status", "scheduled")),
            totalDuration=data.get("totalDuration", 0),
            totalPrice=data.get("totalPrice", 0.0),
            paymentStatus=data.get("paymentStatus", "pending"),
            paymentMethod=PaymentMethod(data.get("paymentMethod")) if data.get("paymentMethod") else None,
            notes=data.get("notes"),
            customerNotes=data.get("customerNotes"),
            cancellationReason=data.get("cancellationReason"),
            reminderSent=data.get("reminderSent", False),
            confirmationSent=data.get("confirmationSent", False)
        )
        
        # Convert services (ServiceTechnicianPair)
        for svc_data in data.get("services", []):
            service_pair = ServiceTechnicianPair(
                serviceId=svc_data["serviceId"],
                technicianId=svc_data["technicianId"],
                duration=svc_data["duration"],
                price=svc_data["price"],
                status=svc_data.get("status", "scheduled"),
                notes=svc_data.get("notes")
            )
            booking_state.services.append(service_pair)
        
        # Convert available technicians
        for tech_data in data.get("available_technicians", []):
            technician = TechnicianInfo(
                _id=tech_data["_id"],
                firstName=tech_data["firstName"],
                lastName=tech_data["lastName"],
                employeeId=tech_data["employeeId"],
                specialties=tech_data["specialties"],
                skillLevel=tech_data["skillLevel"],
                rating=tech_data["rating"]
            )
            booking_state.available_technicians.append(technician)
        
        # Convert available services
        for svc_data in data.get("available_services", []):
            service = ServiceInfo(
                _id=svc_data["_id"],
                name=svc_data["name"],
                category=svc_data["category"],
                duration_minutes=svc_data["duration_minutes"],
                price=svc_data["price"],
                description=svc_data["description"]
            )
            booking_state.available_services.append(service)
        
        # Set alternative times (already in correct format)
        booking_state.alternative_times = data.get("alternative_times", [])
        
        # Convert rating if present
        rating_data = data.get("rating")
        if rating_data:
            booking_state.rating = BookingRating(
                score=rating_data["score"],
                comment=rating_data.get("comment"),
                ratedAt=datetime.fromisoformat(rating_data["ratedAt"]) if rating_data.get("ratedAt") else None
            )
        
        return booking_state
    
    def is_ready_for_booking(self) -> bool:
        """Check if booking has all required information for backend creation"""
        return (
            bool(self.customerId) and
            bool(self.services) and
            bool(self.appointmentDate) and
            bool(self.startTime)
        )
    
    def is_conversation_complete(self) -> bool:
        """Check if conversation has enough info to proceed with booking"""
        required_fields = [
            self.customer_name,
            self.customer_phone,
            self.services_requested,
            self.date_requested,
            self.time_requested
        ]
        
        return all(field.strip() for field in required_fields)
    
    def to_backend_booking(self) -> Dict[str, Any]:
        """Convert to backend IBooking format for API calls"""
        booking_data = {
            "customerId": self.customerId,
            "services": [
                {
                    "serviceId": svc.serviceId,
                    "technicianId": svc.technicianId,
                    "duration": svc.duration,
                    "price": svc.price,
                    "status": svc.status,
                    "notes": svc.notes
                } for svc in self.services
            ],
            "appointmentDate": self.appointmentDate,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "status": self.status.value,
            "totalDuration": self.totalDuration,
            "totalPrice": self.totalPrice,
            "paymentStatus": self.paymentStatus,
            "notes": self.notes,
            "customerNotes": self.customerNotes,
            "reminderSent": self.reminderSent,
            "confirmationSent": self.confirmationSent
        }
        
        # Add optional fields
        if self.paymentMethod:
            booking_data["paymentMethod"] = self.paymentMethod.value
        if self.cancellationReason:
            booking_data["cancellationReason"] = self.cancellationReason
        if self.rating:
            booking_data["rating"] = {
                "score": self.rating.score,
                "comment": self.rating.comment,
                "ratedAt": self.rating.ratedAt.isoformat() if self.rating.ratedAt else None
            }
        
        return booking_data
    
    def get_selected_technician_info(self) -> Optional[TechnicianInfo]:
        """Get the selected technician's full information"""
        if not self.technician_id:
            return None
        
        for tech in self.available_technicians:
            if tech._id == self.technician_id:
                return tech
        
        return None
    
    def add_confirmed_service(self, service_id: str, technician_id: str, 
                            duration: int, price: float) -> None:
        """Add a confirmed service to the booking"""
        confirmed_service = ConfirmedService(
            serviceId=service_id,
            technicianId=technician_id,
            duration=duration,
            price=price
        )
        self.confirmed_services.append(confirmed_service)
        self.total_cost += price
    
    def clear_selection(self) -> None:
        """Clear current selection to start over"""
        self.technician_id = ""
        self.selected_technician = ""
        self.confirmed_services.clear()
        self.total_cost = 0.0
        self.booking_status = BookingStatus.PENDING
