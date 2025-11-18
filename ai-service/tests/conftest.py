"""
Test configuration and fixtures for Hana Salon AI Service
"""

import pytest
import os
import mongomock
from unittest.mock import Mock, patch
from datetime import datetime
from bson import ObjectId

# Set test environment
os.environ["MONGODB_URL"] = "mongodb://test:test@localhost:27017/test_hana_salon"
os.environ["DATABASE_NAME"] = "test_hana_salon"
os.environ["OPENAI_API_KEY"] = "test-key-12345"

@pytest.fixture
def mock_mongodb():
    """Mock MongoDB client for testing"""
    with patch('database.MongoClient') as mock_client:
        # Create a mock database using mongomock
        mock_db = mongomock.MongoClient().db
        mock_client.return_value.__getitem__.return_value = mock_db
        yield mock_db

@pytest.fixture
def sample_service():
    """Sample service data for testing"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "name": "Gel Manicure",
        "category": "Premium",
        "duration_minutes": 60,
        "price": 55.0,
        "description": "Professional gel manicure with long-lasting finish",
        "required_skill_level": "Senior",
        "popularity_score": 8
    }

@pytest.fixture
def sample_technician():
    """Sample technician data for testing"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439012"),
        "name": "Emma Thompson",
        "skill_level": "Expert",
        "specialties": ["507f1f77bcf86cd799439011"],  # Gel Manicure
        "rating": 4.7,
        "years_experience": 5,
        "hourly_rate": 25.0,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "work_hours": {"start": "09:00", "end": "17:00"},
        "is_available": True,
        "bio": "Expert nail technician specializing in gel manicures"
    }

@pytest.fixture
def sample_customer():
    """Sample customer data for testing"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439013"),
        "name": "Sarah Johnson",
        "phone": "555-123-4567",
        "email": "sarah.johnson@email.com",
        "preferences": {
            "preferred_technician": "507f1f77bcf86cd799439012",
            "preferred_services": ["507f1f77bcf86cd799439011"],
            "notes": "Prefers natural colors"
        },
        "booking_history": []
    }

@pytest.fixture
def sample_booking():
    """Sample booking data for testing"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439014"),
        "customer_id": "507f1f77bcf86cd799439013",
        "service_id": "507f1f77bcf86cd799439011",
        "technician_id": "507f1f77bcf86cd799439012",
        "date": "2024-01-15",
        "time": "14:00",
        "duration_minutes": 60,
        "total_cost": 68.75,
        "status": "confirmed",
        "confirmation_id": "SPA-20240115140000",
        "notes": "Customer prefers natural colors",
        "created_at": datetime(2024, 1, 10, 10, 0, 0)
    }

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for testing"""
    return {
        "choices": [{
            "message": {
                "content": """
                {
                    "customer_name": "Sarah Johnson",
                    "customer_phone": "555-123-4567",
                    "service_type": "Gel Manicure",
                    "date": "2024-01-15",
                    "time": "14:00",
                    "validation_status": "VALID"
                }
                """
            }
        }]
    }

@pytest.fixture
def mock_langraph_state():
    """Mock Langraph state for testing"""
    return {
        "messages": [],
        "booking_request": "I want a gel manicure tomorrow at 2 PM. My name is Sarah and phone is 555-123-4567.",
        "customer_name": "Sarah Johnson",
        "customer_phone": "555-123-4567",
        "service_id": "507f1f77bcf86cd799439011",
        "service_name": "Gel Manicure",
        "technician_id": "507f1f77bcf86cd799439012",
        "technician_name": "Emma Thompson",
        "date": "2024-01-15",
        "time": "14:00",
        "duration_minutes": 60,
        "total_cost": 68.75,
        "validation_status": "VALID",
        "confirmation_id": "",
        "final_response": "",
        "available_technicians": [],
        "service_details": {}
    }

@pytest.fixture
def mock_database_manager(mock_mongodb, sample_service, sample_technician):
    """Mock DatabaseManager with sample data"""
    with patch('database.get_db_manager') as mock_get_db:
        mock_db_manager = Mock()
        
        # Setup mock methods
        mock_db_manager.get_all_services.return_value = [sample_service]
        mock_db_manager.get_service_by_name.return_value = sample_service
        mock_db_manager.get_available_technicians.return_value = [sample_technician]
        mock_db_manager.get_technicians_for_service.return_value = [sample_technician]
        mock_db_manager.create_customer.return_value = Mock(_id=ObjectId("507f1f77bcf86cd799439013"))
        mock_db_manager.create_booking.return_value = Mock(_id=ObjectId("507f1f77bcf86cd799439014"))
        
        mock_get_db.return_value = mock_db_manager
        yield mock_db_manager

@pytest.fixture
def client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    from api_server import app
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    test_env = {
        "OPENAI_API_KEY": "test-key-12345",
        "MONGODB_URL": "mongodb://test:test@localhost:27017/test_hana_salon",
        "DATABASE_NAME": "test_hana_salon",
        "DEBUG": "True",
        "LOG_LEVEL": "DEBUG"
    }
    
    # Store original values
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original values
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
