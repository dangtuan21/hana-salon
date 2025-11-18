"""
Unit tests for database operations
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId
from datetime import datetime

from database import DatabaseManager, Service, Technician, Customer, Booking


class TestDatabaseManager:
    """Test DatabaseManager class"""
    
    def test_init_database_manager(self, mock_mongodb):
        """Test DatabaseManager initialization"""
        with patch('database.MongoClient') as mock_client:
            mock_client.return_value.__getitem__.return_value = mock_mongodb
            
            db_manager = DatabaseManager()
            
            assert db_manager.db_name == "test_hana_salon"
            mock_client.assert_called_once()
    
    def test_get_all_services(self, mock_database_manager, sample_service):
        """Test getting all services"""
        services = mock_database_manager.get_all_services()
        
        assert len(services) == 1
        assert services[0]["name"] == "Gel Manicure"
        mock_database_manager.get_all_services.assert_called_once()
    
    def test_get_service_by_name(self, mock_database_manager, sample_service):
        """Test getting service by name"""
        service = mock_database_manager.get_service_by_name("Gel Manicure")
        
        assert service["name"] == "Gel Manicure"
        assert service["price"] == 55.0
        mock_database_manager.get_service_by_name.assert_called_once_with("Gel Manicure")
    
    def test_get_service_by_name_not_found(self, mock_database_manager):
        """Test getting non-existent service"""
        mock_database_manager.get_service_by_name.return_value = None
        
        service = mock_database_manager.get_service_by_name("Non-existent Service")
        
        assert service is None
    
    def test_create_service(self, mock_mongodb):
        """Test creating a new service"""
        with patch('database.MongoClient') as mock_client:
            mock_client.return_value.__getitem__.return_value = mock_mongodb
            
            db_manager = DatabaseManager()
            
            # Mock the insert operation
            mock_mongodb.services.insert_one.return_value.inserted_id = ObjectId()
            
            service = db_manager.create_service(
                name="Test Service",
                category="Basic",
                duration_minutes=30,
                price=25.0,
                description="Test service description",
                required_skill_level="Junior",
                popularity_score=5
            )
            
            assert service is not None
            mock_mongodb.services.insert_one.assert_called_once()
    
    def test_get_available_technicians(self, mock_database_manager, sample_technician):
        """Test getting available technicians"""
        technicians = mock_database_manager.get_available_technicians()
        
        assert len(technicians) == 1
        assert technicians[0]["name"] == "Emma Thompson"
        assert technicians[0]["is_available"] is True
    
    def test_get_technicians_for_service(self, mock_database_manager, sample_technician):
        """Test getting technicians for specific service"""
        service_id = "507f1f77bcf86cd799439011"
        technicians = mock_database_manager.get_technicians_for_service(service_id)
        
        assert len(technicians) == 1
        assert technicians[0]["name"] == "Emma Thompson"
        mock_database_manager.get_technicians_for_service.assert_called_once_with(service_id)
    
    def test_create_customer(self, mock_database_manager):
        """Test creating a new customer"""
        customer_data = {
            "name": "Test Customer",
            "phone": "555-999-8888",
            "email": "test@example.com"
        }
        
        customer = mock_database_manager.create_customer(**customer_data)
        
        assert customer is not None
        mock_database_manager.create_customer.assert_called_once_with(**customer_data)
    
    def test_create_booking(self, mock_database_manager):
        """Test creating a new booking"""
        booking_data = {
            "customer_id": "507f1f77bcf86cd799439013",
            "service_id": "507f1f77bcf86cd799439011",
            "technician_id": "507f1f77bcf86cd799439012",
            "date": "2024-01-15",
            "time": "14:00",
            "duration_minutes": 60,
            "total_cost": 68.75,
            "confirmation_id": "SPA-20240115140000"
        }
        
        booking = mock_database_manager.create_booking(**booking_data)
        
        assert booking is not None
        mock_database_manager.create_booking.assert_called_once_with(**booking_data)


class TestServiceModel:
    """Test Service data model"""
    
    def test_service_creation(self, sample_service):
        """Test Service model creation"""
        service = Service(**sample_service)
        
        assert service.name == "Gel Manicure"
        assert service.category == "Premium"
        assert service.price == 55.0
        assert service.duration_minutes == 60
    
    def test_service_validation(self):
        """Test Service model validation"""
        # Test invalid price
        with pytest.raises(ValueError):
            Service(
                name="Test Service",
                category="Basic",
                duration_minutes=30,
                price=-10.0,  # Invalid negative price
                description="Test",
                required_skill_level="Junior",
                popularity_score=5
            )


class TestTechnicianModel:
    """Test Technician data model"""
    
    def test_technician_creation(self, sample_technician):
        """Test Technician model creation"""
        technician = Technician(**sample_technician)
        
        assert technician.name == "Emma Thompson"
        assert technician.skill_level == "Expert"
        assert technician.rating == 4.7
        assert technician.is_available is True
    
    def test_technician_specialties(self, sample_technician):
        """Test technician specialties handling"""
        technician = Technician(**sample_technician)
        
        assert len(technician.specialties) == 1
        assert "507f1f77bcf86cd799439011" in technician.specialties


class TestCustomerModel:
    """Test Customer data model"""
    
    def test_customer_creation(self, sample_customer):
        """Test Customer model creation"""
        customer = Customer(**sample_customer)
        
        assert customer.name == "Sarah Johnson"
        assert customer.phone == "555-123-4567"
        assert customer.email == "sarah.johnson@email.com"
    
    def test_customer_preferences(self, sample_customer):
        """Test customer preferences handling"""
        customer = Customer(**sample_customer)
        
        assert customer.preferences["preferred_technician"] == "507f1f77bcf86cd799439012"
        assert "507f1f77bcf86cd799439011" in customer.preferences["preferred_services"]


class TestBookingModel:
    """Test Booking data model"""
    
    def test_booking_creation(self, sample_booking):
        """Test Booking model creation"""
        booking = Booking(**sample_booking)
        
        assert booking.customer_id == "507f1f77bcf86cd799439013"
        assert booking.service_id == "507f1f77bcf86cd799439011"
        assert booking.technician_id == "507f1f77bcf86cd799439012"
        assert booking.total_cost == 68.75
        assert booking.status == "confirmed"
    
    def test_booking_confirmation_id(self, sample_booking):
        """Test booking confirmation ID"""
        booking = Booking(**sample_booking)
        
        assert booking.confirmation_id == "SPA-20240115140000"
        assert booking.confirmation_id.startswith("SPA-")


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    def test_full_booking_workflow(self, mock_database_manager):
        """Test complete booking workflow with database"""
        # Create customer
        customer = mock_database_manager.create_customer(
            name="Integration Test Customer",
            phone="555-111-2222",
            email="integration@test.com"
        )
        
        # Get service
        service = mock_database_manager.get_service_by_name("Gel Manicure")
        
        # Get technician
        technicians = mock_database_manager.get_technicians_for_service(service["_id"])
        technician = technicians[0]
        
        # Create booking
        booking = mock_database_manager.create_booking(
            customer_id=str(customer._id),
            service_id=str(service["_id"]),
            technician_id=str(technician["_id"]),
            date="2024-01-20",
            time="15:00",
            duration_minutes=service["duration_minutes"],
            total_cost=service["price"] * 1.25,  # With premium
            confirmation_id="SPA-20240120150000"
        )
        
        assert customer is not None
        assert service is not None
        assert technician is not None
        assert booking is not None
