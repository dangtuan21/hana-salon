#!/usr/bin/env python3
"""
Integration tests for batch availability check functionality
Tests the complete flow from AI service to backend API
"""

import sys
import os
import unittest
import requests
import time
from unittest.mock import patch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.backend_client import BackendAPIClient
from services.action_executor import ActionExecutor


class TestBatchAvailabilityIntegration(unittest.TestCase):
    """Integration tests for batch availability functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - check if backend is running"""
        cls.backend_url = "http://localhost:3060"
        cls.ai_service_url = "http://localhost:8060"
        
        try:
            # Check if backend is running
            response = requests.get(f"{cls.backend_url}/api/health", timeout=5)
            if response.status_code != 200:
                raise unittest.SkipTest("Backend API is not running")
        except requests.exceptions.RequestException:
            raise unittest.SkipTest("Backend API is not accessible")
        
        try:
            # Check if AI service is running
            response = requests.get(f"{cls.ai_service_url}/health", timeout=5)
            if response.status_code != 200:
                raise unittest.SkipTest("AI service is not running")
        except requests.exceptions.RequestException:
            raise unittest.SkipTest("AI service is not accessible")

    def setUp(self):
        """Set up test fixtures"""
        self.api_client = BackendAPIClient(self.backend_url)
        self.action_executor = ActionExecutor(self.api_client)
        
        # Get existing technicians for testing
        self.technicians = self.api_client.get_available_technicians()
        if len(self.technicians) < 2:
            self.skipTest("Need at least 2 technicians for batch testing")

    def test_batch_availability_api_endpoint(self):
        """Test the batch availability API endpoint directly"""
        technician_ids = [tech['_id'] for tech in self.technicians[:2]]
        
        result = self.api_client.batch_check_technician_availability(
            technician_ids, '2024-12-01', '10:00', 60
        )
        
        # Verify response structure
        self.assertIn('results', result)
        self.assertEqual(len(result['results']), 2)
        
        for tech_result in result['results']:
            self.assertIn('technicianId', tech_result)
            self.assertIn('available', tech_result)
            self.assertIn(tech_result['technicianId'], technician_ids)
            self.assertIsInstance(tech_result['available'], bool)

    def test_batch_vs_individual_consistency(self):
        """Test that batch and individual availability checks return consistent results"""
        technician_ids = [tech['_id'] for tech in self.technicians[:2]]
        test_date = '2024-12-01'
        test_time = '14:00'
        test_duration = 60
        
        # Get batch results
        batch_result = self.api_client.batch_check_technician_availability(
            technician_ids, test_date, test_time, test_duration
        )
        
        # Get individual results
        individual_results = {}
        for tech_id in technician_ids:
            individual_result = self.api_client.check_technician_availability(
                tech_id, test_date, test_time, test_duration
            )
            individual_results[tech_id] = individual_result.get('available', False)
        
        # Compare results
        self.assertEqual(len(batch_result['results']), len(technician_ids))
        
        for batch_tech in batch_result['results']:
            tech_id = batch_tech['technicianId']
            batch_available = batch_tech['available']
            individual_available = individual_results[tech_id]
            
            self.assertEqual(
                batch_available, individual_available,
                f"Batch and individual results differ for technician {tech_id}"
            )

    def test_find_best_technician_integration(self):
        """Test _find_best_technician with real API calls"""
        # Get technicians for a service
        services = self.api_client.get_all_services()
        if not services:
            self.skipTest("No services available for testing")
        
        service_id = services[0]['_id']
        technicians = self.api_client.get_technicians_for_service(service_id)
        
        if len(technicians) < 2:
            self.skipTest("Need at least 2 technicians for this service")
        
        # Test finding best technician
        result = self.action_executor._find_best_technician(
            technicians, service_id, '2024-12-01', '15:00', 60
        )
        
        # Should return a technician (assuming no conflicts)
        if result:  # May be None if all technicians are busy
            self.assertIn('_id', result)
            self.assertIn('firstName', result)
            self.assertIn('lastName', result)
            self.assertIn('skillLevel', result)

    def test_performance_comparison(self):
        """Test performance improvement of batch vs individual calls"""
        technician_ids = [tech['_id'] for tech in self.technicians]
        test_date = '2024-12-01'
        test_time = '16:00'
        test_duration = 60
        
        # Time individual calls
        start_time = time.time()
        for tech_id in technician_ids:
            self.api_client.check_technician_availability(
                tech_id, test_date, test_time, test_duration
            )
        individual_time = time.time() - start_time
        
        # Time batch call
        start_time = time.time()
        self.api_client.batch_check_technician_availability(
            technician_ids, test_date, test_time, test_duration
        )
        batch_time = time.time() - start_time
        
        print(f"\nPerformance comparison for {len(technician_ids)} technicians:")
        print(f"Individual calls: {individual_time:.3f}s")
        print(f"Batch call: {batch_time:.3f}s")
        print(f"Improvement: {individual_time/batch_time:.1f}x faster")
        
        # Batch should be faster (or at least not significantly slower)
        # Allow some tolerance for network variability
        self.assertLessEqual(batch_time, individual_time * 1.5, 
                           "Batch call should not be significantly slower than individual calls")

    def test_full_booking_flow_with_batch(self):
        """Test complete booking flow using batch availability"""
        # Create a mock session state for booking
        session_state = {
            'booking_state': {
                'services': [],
                'date_requested': 'December 1st',
                'time_requested': '2 PM',
                'dateTimeConfirmationStatus': 'CONFIRMED',
                'totalDuration': 0,
                'totalPrice': 0.0
            }
        }
        
        # Get a service and add it to booking
        services = self.api_client.get_all_services()
        if not services:
            self.skipTest("No services available for testing")
        
        service = services[0]
        session_state['booking_state']['services'] = [{
            'serviceId': service['_id'],
            'technicianId': '',
            'duration': 60,
            'price': service['price'],
            'status': 'scheduled'
        }]
        session_state['booking_state']['totalDuration'] = 60
        session_state['booking_state']['totalPrice'] = service['price']
        
        # Mock the date/time parsing
        with patch('services.action_executor.parse_date') as mock_parse_date:
            with patch('services.action_executor.parse_time') as mock_parse_time:
                mock_parse_date.return_value = '2024-12-01'
                mock_parse_time.return_value = '14:00'
                
                # Execute availability check
                result = self.action_executor._check_availability(session_state)
                
                # Should complete successfully (either available or with alternatives)
                self.assertIsInstance(result, str)
                self.assertTrue(
                    'availability_checked' in result or 
                    'Conflict detected' in result or 
                    'No availability' in result
                )

    def test_error_handling_integration(self):
        """Test error handling in integration scenarios"""
        # Test with invalid technician IDs
        result = self.api_client.batch_check_technician_availability(
            ['invalid_id_1', 'invalid_id_2'], '2024-12-01', '10:00', 60
        )
        
        # Should handle gracefully (may return empty results or error)
        self.assertIsInstance(result, dict)
        
        # Test with malformed date
        result = self.api_client.batch_check_technician_availability(
            [self.technicians[0]['_id']], 'invalid-date', '10:00', 60
        )
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)

    def test_concurrent_batch_requests(self):
        """Test handling of concurrent batch requests"""
        import threading
        import queue
        
        technician_ids = [tech['_id'] for tech in self.technicians[:2]]
        results_queue = queue.Queue()
        
        def make_batch_request():
            try:
                result = self.api_client.batch_check_technician_availability(
                    technician_ids, '2024-12-01', '11:00', 60
                )
                results_queue.put(('success', result))
            except Exception as e:
                results_queue.put(('error', str(e)))
        
        # Start multiple concurrent requests
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_batch_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Check results
        success_count = 0
        while not results_queue.empty():
            status, result = results_queue.get()
            if status == 'success':
                success_count += 1
                self.assertIn('results', result)
        
        # At least some requests should succeed
        self.assertGreater(success_count, 0, "At least one concurrent request should succeed")


class TestBatchAvailabilityFallback(unittest.TestCase):
    """Test fallback mechanisms when batch API is unavailable"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_client = BackendAPIClient("http://localhost:3060")
        self.action_executor = ActionExecutor(self.api_client)

    def test_fallback_to_individual_when_batch_fails(self):
        """Test fallback to individual calls when batch endpoint fails"""
        technicians = [
            {
                '_id': 'tech1',
                'firstName': 'John',
                'lastName': 'Doe',
                'skillLevel': 'Senior',
                'rating': 4.8
            }
        ]
        
        # Mock batch failure and individual success
        with patch.object(self.api_client, 'batch_check_technician_availability') as mock_batch:
            with patch.object(self.api_client, 'check_technician_availability') as mock_individual:
                mock_batch.return_value = {}  # Simulate batch failure
                mock_individual.return_value = {'available': True}
                
                result = self.action_executor._find_best_technician(
                    technicians, 'service1', '2024-12-01', '10:00', 60
                )
                
                # Should fallback to individual and succeed
                self.assertEqual(result, technicians[0])
                mock_batch.assert_called_once()
                mock_individual.assert_called_once()


if __name__ == '__main__':
    # Run the integration tests
    print("Running batch availability integration tests...")
    print("Note: These tests require both backend (port 3060) and AI service (port 8060) to be running")
    unittest.main(verbosity=2)
