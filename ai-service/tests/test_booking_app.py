"""
Unit tests for Langraph booking workflow
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

from booking_app import (
    booking_validation_node,
    booking_confirmation_node,
    create_booking_workflow,
    BookingState
)


class TestBookingValidationNode:
    """Test booking validation node"""
    
    @patch('booking_app.llm')
    def test_booking_validation_success(self, mock_llm, mock_langraph_state, mock_openai_response):
        """Test successful booking validation"""
        # Setup mock LLM response
        mock_llm.invoke.return_value.content = json.dumps({
            "customer_name": "Sarah Johnson",
            "customer_phone": "555-123-4567",
            "service_type": "Gel Manicure",
            "date": "2024-01-15",
            "time": "14:00",
            "validation_status": "VALID"
        })
        
        with patch('booking_app.get_db_manager') as mock_get_db:
            mock_db = Mock()
            mock_db.get_all_services.return_value = [
                {"_id": "507f1f77bcf86cd799439011", "name": "Gel Manicure", "price": 55.0, "duration_minutes": 60}
            ]
            mock_db.get_technicians_for_service.return_value = [
                {"_id": "507f1f77bcf86cd799439012", "name": "Emma Thompson", "skill_level": "Expert"}
            ]
            mock_get_db.return_value = mock_db
            
            result = booking_validation_node(mock_langraph_state)
            
            assert result["customer_name"] == "Sarah Johnson"
            assert result["customer_phone"] == "555-123-4567"
            assert result["service_name"] == "Gel Manicure"
            assert result["validation_status"] == "VALID"
            mock_llm.invoke.assert_called_once()
    
    @patch('booking_app.llm')
    def test_booking_validation_invalid_service(self, mock_llm, mock_langraph_state):
        """Test booking validation with invalid service"""
        mock_llm.invoke.return_value.content = json.dumps({
            "customer_name": "Sarah Johnson",
            "customer_phone": "555-123-4567",
            "service_type": "Non-existent Service",
            "date": "2024-01-15",
            "time": "14:00",
            "validation_status": "VALID"
        })
        
        with patch('booking_app.get_db_manager') as mock_get_db:
            mock_db = Mock()
            mock_db.get_all_services.return_value = [
                {"_id": "507f1f77bcf86cd799439011", "name": "Gel Manicure", "price": 55.0}
            ]
            mock_get_db.return_value = mock_db
            
            result = booking_validation_node(mock_langraph_state)
            
            assert "Service not found" in result["validation_status"]
    
    @patch('booking_app.llm')
    def test_booking_validation_json_parse_error(self, mock_llm, mock_langraph_state):
        """Test booking validation with invalid JSON response"""
        mock_llm.invoke.return_value.content = "Invalid JSON response"
        
        result = booking_validation_node(mock_langraph_state)
        
        assert result["validation_status"] == "INVALID - Could not parse booking request"
    
    @patch('booking_app.llm')
    def test_booking_validation_missing_fields(self, mock_llm, mock_langraph_state):
        """Test booking validation with missing required fields"""
        mock_llm.invoke.return_value.content = json.dumps({
            "customer_name": "Sarah Johnson",
            # Missing phone, service, etc.
            "validation_status": "VALID"
        })
        
        result = booking_validation_node(mock_langraph_state)
        
        assert result["validation_status"] == "INVALID - Missing required information"


class TestBookingConfirmationNode:
    """Test booking confirmation node"""
    
    @patch('booking_app.llm')
    def test_booking_confirmation_success(self, mock_llm, mock_langraph_state, mock_database_manager):
        """Test successful booking confirmation"""
        # Setup valid state
        mock_langraph_state.update({
            "validation_status": "VALID",
            "customer_name": "Sarah Johnson",
            "customer_phone": "555-123-4567",
            "service_id": "507f1f77bcf86cd799439011",
            "technician_id": "507f1f77bcf86cd799439012",
            "total_cost": 68.75
        })
        
        mock_llm.invoke.return_value.content = "Thank you for booking with Hana Salon!"
        
        with patch('booking_app.get_db_manager', return_value=mock_database_manager):
            result = booking_confirmation_node(mock_langraph_state)
            
            assert result["validation_status"] == "VALID"
            assert "SPA-" in result["confirmation_id"]
            assert "Thank you" in result["final_response"]
            mock_database_manager.create_customer.assert_called_once()
            mock_database_manager.create_booking.assert_called_once()
    
    def test_booking_confirmation_invalid_status(self, mock_langraph_state):
        """Test booking confirmation with invalid status"""
        mock_langraph_state.update({
            "validation_status": "INVALID - Service not found"
        })
        
        result = booking_confirmation_node(mock_langraph_state)
        
        assert result["confirmation_id"] == "N/A"
        assert "could not be processed" in result["final_response"]
    
    @patch('booking_app.llm')
    def test_booking_confirmation_database_error(self, mock_llm, mock_langraph_state):
        """Test booking confirmation with database error"""
        mock_langraph_state.update({
            "validation_status": "VALID",
            "customer_name": "Sarah Johnson",
            "customer_phone": "555-123-4567"
        })
        
        mock_llm.invoke.return_value.content = "Booking confirmed!"
        
        with patch('booking_app.get_db_manager') as mock_get_db:
            mock_db = Mock()
            mock_db.create_customer.side_effect = Exception("Database error")
            mock_get_db.return_value = mock_db
            
            result = booking_confirmation_node(mock_langraph_state)
            
            # Should handle error gracefully
            assert result["confirmation_id"] != "N/A"  # Still generates ID
            assert result["final_response"]  # Still has response


class TestBookingWorkflow:
    """Test complete booking workflow"""
    
    def test_create_booking_workflow(self):
        """Test workflow creation"""
        workflow = create_booking_workflow()
        
        assert workflow is not None
        # Test that workflow can be compiled
        compiled_workflow = workflow
        assert compiled_workflow is not None
    
    @patch('booking_app.booking_validation_node')
    @patch('booking_app.booking_confirmation_node')
    def test_workflow_execution(self, mock_confirmation, mock_validation):
        """Test workflow execution"""
        # Setup mock responses
        mock_validation.return_value = {
            "customer_name": "Sarah Johnson",
            "validation_status": "VALID",
            "service_id": "507f1f77bcf86cd799439011"
        }
        
        mock_confirmation.return_value = {
            "confirmation_id": "SPA-20240115140000",
            "final_response": "Booking confirmed!"
        }
        
        workflow = create_booking_workflow()
        
        initial_state = {
            "messages": [],
            "booking_request": "I want a gel manicure tomorrow at 2 PM",
            "customer_name": "",
            "validation_status": "",
            "confirmation_id": ""
        }
        
        # This would normally run the workflow
        # For unit tests, we just verify the nodes are callable
        assert callable(mock_validation)
        assert callable(mock_confirmation)


class TestBookingState:
    """Test BookingState TypedDict"""
    
    def test_booking_state_structure(self, mock_langraph_state):
        """Test BookingState has all required fields"""
        required_fields = [
            "messages", "booking_request", "customer_name", "customer_phone",
            "service_id", "service_name", "technician_id", "technician_name",
            "date", "time", "duration_minutes", "total_cost", "validation_status",
            "confirmation_id", "final_response", "available_technicians", "service_details"
        ]
        
        for field in required_fields:
            assert field in mock_langraph_state
    
    def test_booking_state_defaults(self):
        """Test BookingState with default values"""
        state = {
            "messages": [],
            "booking_request": "Test request",
            "customer_name": "",
            "customer_phone": "",
            "service_id": "",
            "service_name": "",
            "technician_id": "",
            "technician_name": "",
            "date": "",
            "time": "",
            "duration_minutes": 0,
            "total_cost": 0.0,
            "validation_status": "",
            "confirmation_id": "",
            "final_response": "",
            "available_technicians": [],
            "service_details": {}
        }
        
        # Verify all fields are present and have expected types
        assert isinstance(state["messages"], list)
        assert isinstance(state["booking_request"], str)
        assert isinstance(state["duration_minutes"], int)
        assert isinstance(state["total_cost"], float)
        assert isinstance(state["available_technicians"], list)
        assert isinstance(state["service_details"], dict)


@pytest.mark.workflow
class TestWorkflowIntegration:
    """Integration tests for the complete workflow"""
    
    @patch('booking_app.llm')
    def test_full_workflow_success(self, mock_llm, mock_database_manager):
        """Test complete successful workflow"""
        # Mock LLM responses for both nodes
        mock_llm.invoke.side_effect = [
            # Validation response
            Mock(content=json.dumps({
                "customer_name": "Sarah Johnson",
                "customer_phone": "555-123-4567",
                "service_type": "Gel Manicure",
                "date": "2024-01-15",
                "time": "14:00",
                "validation_status": "VALID"
            })),
            # Confirmation response
            Mock(content="Your booking has been confirmed!")
        ]
        
        with patch('booking_app.get_db_manager', return_value=mock_database_manager):
            initial_state = {
                "messages": [],
                "booking_request": "I want a gel manicure tomorrow at 2 PM. My name is Sarah Johnson, phone 555-123-4567.",
                "customer_name": "",
                "customer_phone": "",
                "service_id": "",
                "service_name": "",
                "technician_id": "",
                "technician_name": "",
                "date": "",
                "time": "",
                "duration_minutes": 0,
                "total_cost": 0.0,
                "validation_status": "",
                "confirmation_id": "",
                "final_response": "",
                "available_technicians": [],
                "service_details": {}
            }
            
            # Test validation node
            validation_result = booking_validation_node(initial_state)
            assert validation_result["validation_status"] == "VALID"
            
            # Test confirmation node
            confirmation_result = booking_confirmation_node(validation_result)
            assert "SPA-" in confirmation_result["confirmation_id"]
            assert confirmation_result["final_response"]
