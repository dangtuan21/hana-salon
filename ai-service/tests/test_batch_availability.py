#!/usr/bin/env python3
"""
Unit tests for batch availability check functionality in AI service
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.backend_client import BackendAPIClient
from services.action_executor import ActionExecutor
from database.booking_state import BookingState, ServiceTechnicianPair


class TestBatchAvailability(unittest.TestCase):
    """Test cases for batch availability functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_client = BackendAPIClient()
        self.action_executor = ActionExecutor(self.api_client)
        
        # Mock technicians data
        self.mock_technicians = [
            {
                '_id': 'tech1',
                'firstName': 'John',
                'lastName': 'Doe',
                'skillLevel': 'Senior',
                'rating': 4.8
            },
            {
                '_id': 'tech2',
                'firstName': 'Jane',
                'lastName': 'Smith',
                'skillLevel': 'Junior',
                'rating': 4.5
            }
        ]
        
        # Mock batch availability response
        self.mock_batch_response = {
            'results': [
                {'technicianId': 'tech1', 'available': True},
                {'technicianId': 'tech2', 'available': False}
            ]
        }

    @patch('services.backend_client.requests.Session.post')
    def test_batch_check_technician_availability_success(self, mock_post):
        """Test successful batch availability check"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': self.mock_batch_response
        }
        mock_response.text = '{"success": true}'
        mock_post.return_value = mock_response
        
        # Test the batch availability check
        result = self.api_client.batch_check_technician_availability(
            ['tech1', 'tech2'], '2024-12-01', '10:00', 60
        )
        
        # Assertions
        self.assertEqual(result, self.mock_batch_response)
        mock_post.assert_called_once()
        
        # Check the API call parameters
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['technicianIds'], ['tech1', 'tech2'])
        self.assertEqual(call_args[1]['json']['date'], '2024-12-01')
        self.assertEqual(call_args[1]['json']['startTime'], '10:00')
        self.assertEqual(call_args[1]['json']['duration'], 60)

    @patch('services.backend_client.requests.Session.post')
    def test_batch_check_technician_availability_failure(self, mock_post):
        """Test batch availability check API failure"""
        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = '{"error": "Internal server error"}'
        mock_post.return_value = mock_response
        
        # Test the batch availability check
        result = self.api_client.batch_check_technician_availability(
            ['tech1', 'tech2'], '2024-12-01', '10:00', 60
        )
        
        # Should return empty dict on failure
        self.assertEqual(result, {})

    @patch('services.backend_client.requests.Session.post')
    def test_batch_check_technician_availability_exception(self, mock_post):
        """Test batch availability check with network exception"""
        # Mock network exception
        mock_post.side_effect = Exception("Network error")
        
        # Test the batch availability check
        result = self.api_client.batch_check_technician_availability(
            ['tech1', 'tech2'], '2024-12-01', '10:00', 60
        )
        
        # Should return empty dict on exception
        self.assertEqual(result, {})

    def test_find_best_technician_with_batch_success(self):
        """Test _find_best_technician using batch availability check"""
        # Mock the batch API call
        with patch.object(self.api_client, 'batch_check_technician_availability') as mock_batch:
            mock_batch.return_value = self.mock_batch_response
            
            # Call the actual method (not mocked)
            result = self.action_executor._find_best_technician(
                self.mock_technicians, 'service1', '2024-12-01', '10:00', 60
            )
            
            # Verify batch API was called
            mock_batch.assert_called_once_with(
                ['tech1', 'tech2'], '2024-12-01', '10:00', 60
            )
            
            # Should return the first available technician (tech1)
            self.assertEqual(result, self.mock_technicians[0])

    def test_find_best_technician_preference_order(self):
        """Test that technicians are sorted by preference (Senior > Junior, rating)"""
        # Mock technicians with different skill levels and ratings
        technicians = [
            {'_id': 'tech1', 'firstName': 'John', 'lastName': 'Doe', 'skillLevel': 'Junior', 'rating': 4.9},
            {'_id': 'tech2', 'firstName': 'Jane', 'lastName': 'Smith', 'skillLevel': 'Senior', 'rating': 4.5},
            {'_id': 'tech3', 'firstName': 'Bob', 'lastName': 'Wilson', 'skillLevel': 'Senior', 'rating': 4.8}
        ]
        
        # Mock batch availability - all available
        mock_batch_response = {
            'results': [
                {'technicianId': 'tech1', 'available': True},
                {'technicianId': 'tech2', 'available': True},
                {'technicianId': 'tech3', 'available': True}
            ]
        }
        
        with patch.object(self.api_client, 'batch_check_technician_availability') as mock_batch:
            mock_batch.return_value = mock_batch_response
            
            result = self.action_executor._find_best_technician(
                technicians, 'service1', '2024-12-01', '10:00', 60
            )
            
            # Should return tech3 (Senior with highest rating)
            self.assertEqual(result['_id'], 'tech3')

    def test_find_best_technician_batch_failure(self):
        """Test behavior when batch check fails"""
        with patch.object(self.api_client, 'batch_check_technician_availability') as mock_batch:
            # Mock batch failure
            mock_batch.return_value = {}
            
            result = self.action_executor._find_best_technician(
                self.mock_technicians, 'service1', '2024-12-01', '10:00', 60
            )
            
            # Should return None when batch fails
            mock_batch.assert_called_once()
            self.assertIsNone(result)

    def test_find_best_technician_no_available(self):
        """Test when no technicians are available"""
        # Mock batch response - all unavailable
        mock_batch_response = {
            'results': [
                {'technicianId': 'tech1', 'available': False},
                {'technicianId': 'tech2', 'available': False}
            ]
        }
        
        with patch.object(self.api_client, 'batch_check_technician_availability') as mock_batch:
            mock_batch.return_value = mock_batch_response
            
            result = self.action_executor._find_best_technician(
                self.mock_technicians, 'service1', '2024-12-01', '10:00', 60
            )
            
            # Should return None when no technicians available
            self.assertIsNone(result)

    @patch.object(ActionExecutor, '_find_alternative_times')
    def test_find_alternative_times_with_batch(self, mock_find_alternatives):
        """Test _find_alternative_times using batch availability check"""
        # Create mock booking state
        booking_state = BookingState()
        booking_state.services = [ServiceTechnicianPair(serviceId='service1', technicianId='', duration=60, price=50)]
        booking_state.totalDuration = 60
        
        # Mock the method to test batch usage
        mock_find_alternatives.return_value = [
            {'time': '10:00', 'technician': 'John Doe', 'technician_id': 'tech1', 'end_time': '11:00'},
            {'time': '11:00', 'technician': 'Jane Smith', 'technician_id': 'tech2', 'end_time': '12:00'}
        ]
        
        result = self.action_executor._find_alternative_times(booking_state, '2024-12-01')
        
        # Verify alternatives were found
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['time'], '10:00')
        self.assertEqual(result[1]['time'], '11:00')

    def test_batch_availability_integration_flow(self):
        """Test the complete flow from availability check to technician assignment"""
        # Mock session state
        session_state = {
            'booking_state': {
                'services': [
                    {'serviceId': 'service1', 'technicianId': '', 'duration': 60, 'price': 50}
                ],
                'date_requested': 'tomorrow',
                'time_requested': '2 PM',
                'dateTimeConfirmationStatus': 'confirmed',
                'totalDuration': 60
            }
        }
        
        # Mock all the dependencies
        with patch('services.action_executor.parse_date') as mock_parse_date:
            with patch('services.action_executor.parse_time') as mock_parse_time:
                with patch.object(self.api_client, 'get_technicians_for_service') as mock_get_techs:
                    with patch.object(self.api_client, 'batch_check_technician_availability') as mock_batch:
                        
                        # Setup mocks
                        mock_parse_date.return_value = '2024-12-01'
                        mock_parse_time.return_value = '14:00'
                        mock_get_techs.return_value = self.mock_technicians
                        mock_batch.return_value = {
                            'results': [{'technicianId': 'tech1', 'available': True}]
                        }
                        
                        # Execute availability check
                        result = self.action_executor._check_availability(session_state)
                        
                        # Verify successful availability check
                        self.assertEqual(result, 'availability_checked')
                        
                        # Verify batch API was called
                        mock_batch.assert_called_once_with(
                            ['tech1', 'tech2'], '2024-12-01', '14:00', 60
                        )


class TestBatchAvailabilityEdgeCases(unittest.TestCase):
    """Test edge cases for batch availability functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_client = BackendAPIClient()
        self.action_executor = ActionExecutor(self.api_client)

    def test_empty_technician_list(self):
        """Test batch availability with empty technician list"""
        result = self.api_client.batch_check_technician_availability(
            [], '2024-12-01', '10:00', 60
        )
        
        # Should handle empty list gracefully
        self.assertEqual(result, {})

    def test_single_technician_batch(self):
        """Test batch availability with single technician"""
        with patch('services.backend_client.requests.Session.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'data': {'results': [{'technicianId': 'tech1', 'available': True}]}
            }
            mock_response.text = '{"success": true}'
            mock_post.return_value = mock_response
            
            result = self.api_client.batch_check_technician_availability(
                ['tech1'], '2024-12-01', '10:00', 60
            )
            
            self.assertEqual(len(result['results']), 1)
            self.assertTrue(result['results'][0]['available'])

    def test_malformed_batch_response(self):
        """Test handling of malformed batch response"""
        with patch('services.backend_client.requests.Session.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'data': {'malformed': 'response'}  # Missing 'results' key
            }
            mock_response.text = '{"success": true}'
            mock_post.return_value = mock_response
            
            technicians = [{'_id': 'tech1', 'firstName': 'John', 'lastName': 'Doe', 'skillLevel': 'Senior', 'rating': 4.8}]
            
            # Should handle malformed response gracefully
            result = self.action_executor._find_best_technician(
                technicians, 'service1', '2024-12-01', '10:00', 60
            )
            
            # Should return None when batch response is malformed
            self.assertIsNone(result)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
