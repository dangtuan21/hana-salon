"""
Unit tests for FastAPI endpoints
"""

import pytest
from unittest.mock import Mock, patch
import json
from fastapi.testclient import TestClient

from api_server import app


class TestHealthEndpoints:
    """Test health and root endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "Hana Salon Booking" in data["message"]
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "endpoints" in data
    
    @patch('api_server.create_booking_workflow')
    def test_health_endpoint_success(self, mock_workflow, client):
        """Test health endpoint when service is healthy"""
        mock_workflow.return_value = Mock()
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "hana-ai-booking-service"
        assert data["langraph_status"] == "healthy"
    
    @patch('api_server.create_booking_workflow')
    def test_health_endpoint_failure(self, mock_workflow, client):
        """Test health endpoint when service is unhealthy"""
        mock_workflow.side_effect = Exception("Workflow error")
        
        response = client.get("/health")
        
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["langraph_status"] == "error"


class TestBookingEndpoints:
    """Test booking-related endpoints"""
    
    @patch('api_server.process_booking')
    def test_process_booking_success(self, mock_process, client):
        """Test successful booking processing"""
        mock_process.return_value = {
            "customer_name": "Sarah Johnson",
            "customer_phone": "555-123-4567",
            "service_name": "Gel Manicure",
            "confirmation_id": "SPA-20240115140000",
            "validation_status": "VALID",
            "final_response": "Booking confirmed!"
        }
        
        booking_request = {
            "booking_request": "I want a gel manicure tomorrow at 2 PM. My name is Sarah Johnson, phone 555-123-4567."
        }
        
        response = client.post("/process-booking", json=booking_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["customer_name"] == "Sarah Johnson"
        assert data["service_name"] == "Gel Manicure"
        assert "SPA-" in data["confirmation_id"]
        mock_process.assert_called_once()
    
    @patch('api_server.process_booking')
    def test_process_booking_failure(self, mock_process, client):
        """Test booking processing failure"""
        mock_process.side_effect = Exception("Processing error")
        
        booking_request = {
            "booking_request": "Invalid booking request"
        }
        
        response = client.post("/process-booking", json=booking_request)
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to process booking" in data["detail"]
    
    def test_process_booking_invalid_request(self, client):
        """Test booking processing with invalid request format"""
        invalid_request = {
            "invalid_field": "Invalid data"
        }
        
        response = client.post("/process-booking", json=invalid_request)
        
        assert response.status_code == 422  # Validation error
    
    @patch('api_server.booking_validation_node')
    def test_validate_booking_success(self, mock_validation, client):
        """Test successful booking validation"""
        mock_validation.return_value = {
            "customer_name": "Sarah Johnson",
            "customer_phone": "555-123-4567",
            "service_name": "Gel Manicure",
            "validation_status": "VALID",
            "available_technicians": [],
            "service_details": {}
        }
        
        booking_request = {
            "booking_request": "I want a gel manicure tomorrow at 2 PM"
        }
        
        response = client.post("/validate-booking", json=booking_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["customer_name"] == "Sarah Johnson"
        assert data["validation_status"] == "VALID"
    
    @patch('api_server.booking_validation_node')
    def test_validate_booking_invalid(self, mock_validation, client):
        """Test booking validation with invalid booking"""
        mock_validation.return_value = {
            "customer_name": "",
            "customer_phone": "",
            "service_name": "",
            "validation_status": "INVALID - Missing required information",
            "available_technicians": [],
            "service_details": {}
        }
        
        booking_request = {
            "booking_request": "Invalid booking"
        }
        
        response = client.post("/validate-booking", json=booking_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "INVALID" in data["validation_status"]


class TestBookingManagementEndpoints:
    """Test booking management endpoints"""
    
    @patch('api_server.get_db_manager')
    def test_get_booking_success(self, mock_get_db, client, sample_booking):
        """Test getting booking by confirmation ID"""
        mock_db = Mock()
        mock_db.get_booking_by_confirmation_id.return_value = Mock(**sample_booking)
        mock_db.get_service_by_id.return_value = {"name": "Gel Manicure", "description": "Professional gel manicure"}
        mock_db.get_technician_by_id.return_value = {"name": "Emma Thompson", "skill_level": "Expert"}
        mock_db.get_customer_by_id.return_value = {"name": "Sarah Johnson", "phone": "555-123-4567"}
        mock_get_db.return_value = mock_db
        
        response = client.get("/booking/SPA-20240115140000")
        
        assert response.status_code == 200
        data = response.json()
        assert data["booking"]["confirmation_id"] == "SPA-20240115140000"
        assert data["customer"]["name"] == "Sarah Johnson"
        assert data["service"]["name"] == "Gel Manicure"
        assert data["technician"]["name"] == "Emma Thompson"
    
    @patch('api_server.get_db_manager')
    def test_get_booking_not_found(self, mock_get_db, client):
        """Test getting non-existent booking"""
        mock_db = Mock()
        mock_db.get_booking_by_confirmation_id.return_value = None
        mock_get_db.return_value = mock_db
        
        response = client.get("/booking/INVALID-ID")
        
        assert response.status_code == 404
        data = response.json()
        assert "Booking not found" in data["detail"]
    
    @patch('api_server.get_db_manager')
    def test_update_booking_status_success(self, mock_get_db, client, sample_booking):
        """Test updating booking status"""
        mock_db = Mock()
        mock_db.get_booking_by_confirmation_id.return_value = Mock(**sample_booking)
        mock_db.update_booking_status.return_value = True
        mock_get_db.return_value = mock_db
        
        response = client.put("/booking/SPA-20240115140000/status?status=completed")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["new_status"] == "completed"
        mock_db.update_booking_status.assert_called_once()
    
    @patch('api_server.get_db_manager')
    def test_update_booking_status_invalid_status(self, mock_get_db, client):
        """Test updating booking with invalid status"""
        response = client.put("/booking/SPA-20240115140000/status?status=invalid_status")
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid status" in data["detail"]
    
    @patch('api_server.get_db_manager')
    def test_update_booking_status_not_found(self, mock_get_db, client):
        """Test updating non-existent booking status"""
        mock_db = Mock()
        mock_db.get_booking_by_confirmation_id.return_value = None
        mock_get_db.return_value = mock_db
        
        response = client.put("/booking/INVALID-ID/status?status=completed")
        
        assert response.status_code == 404
        data = response.json()
        assert "Booking not found" in data["detail"]


class TestRequestValidation:
    """Test request validation and error handling"""
    
    def test_booking_request_validation(self, client):
        """Test booking request validation"""
        # Missing booking_request field
        response = client.post("/process-booking", json={})
        assert response.status_code == 422
        
        # Empty booking_request
        response = client.post("/process-booking", json={"booking_request": ""})
        assert response.status_code == 422
        
        # Invalid JSON
        response = client.post("/process-booking", data="invalid json")
        assert response.status_code == 422
    
    def test_content_type_validation(self, client):
        """Test content type validation"""
        # Send form data instead of JSON
        response = client.post("/process-booking", data={"booking_request": "test"})
        assert response.status_code == 422
    
    def test_method_not_allowed(self, client):
        """Test method not allowed"""
        response = client.delete("/process-booking")
        assert response.status_code == 405


@pytest.mark.api
class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    @patch('api_server.process_booking')
    @patch('api_server.get_db_manager')
    def test_full_booking_flow(self, mock_get_db, mock_process, client):
        """Test complete booking flow through API"""
        # Mock process_booking to return complete booking data
        mock_process.return_value = {
            "customer_name": "Integration Test User",
            "customer_phone": "555-999-8888",
            "service_id": "507f1f77bcf86cd799439011",
            "service_name": "Gel Manicure",
            "technician_id": "507f1f77bcf86cd799439012",
            "technician_name": "Emma Thompson",
            "date": "2024-01-20",
            "time": "15:00",
            "duration_minutes": 60,
            "total_cost": 68.75,
            "validation_status": "VALID",
            "confirmation_id": "SPA-20240120150000",
            "final_response": "Your booking has been confirmed!",
            "available_technicians": [],
            "service_details": {}
        }
        
        # Mock database for booking retrieval
        mock_db = Mock()
        mock_booking = Mock()
        mock_booking.confirmation_id = "SPA-20240120150000"
        mock_booking.date = "2024-01-20"
        mock_booking.time = "15:00"
        mock_booking.total_cost = 68.75
        mock_booking.status = "confirmed"
        mock_db.get_booking_by_confirmation_id.return_value = mock_booking
        mock_get_db.return_value = mock_db
        
        # Step 1: Process booking
        booking_request = {
            "booking_request": "I want a gel manicure on January 20th at 3 PM. My name is Integration Test User, phone 555-999-8888."
        }
        
        response = client.post("/process-booking", json=booking_request)
        assert response.status_code == 200
        
        booking_data = response.json()
        confirmation_id = booking_data["confirmation_id"]
        
        # Step 2: Retrieve booking
        response = client.get(f"/booking/{confirmation_id}")
        assert response.status_code == 200
        
        retrieved_booking = response.json()
        assert retrieved_booking["booking"]["confirmation_id"] == confirmation_id
        
        # Step 3: Update booking status
        response = client.put(f"/booking/{confirmation_id}/status?status=completed")
        assert response.status_code == 200
        
        status_update = response.json()
        assert status_update["success"] is True
        assert status_update["new_status"] == "completed"
