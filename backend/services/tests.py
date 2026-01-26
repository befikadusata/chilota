"""
Tests for the ID Verification Service
"""
from django.test import TestCase
from services.id_verification_service import IDVerificationService


class TestIDVerificationService(TestCase):
    """Test cases for the ID Verification Service"""
    
    def test_verify_worker_id_with_valid_id(self):
        """Test verifying a worker ID with a valid format"""
        valid_id = "2205150100000008"
        result = IDVerificationService.verify_worker_id(valid_id)

        self.assertEqual(result['is_valid'], True)
        self.assertEqual(result['is_verified'], True)
        self.assertIsNone(result['error'])
        self.assertIsNotNone(result['details'])
        self.assertEqual(result['details']['fayda_id'], valid_id)
    
    def test_verify_worker_id_with_invalid_format(self):
        """Test verifying a worker ID with an invalid format"""
        invalid_id = "123456010000000"  # Invalid checksum
        result = IDVerificationService.verify_worker_id(invalid_id)
        
        self.assertEqual(result['is_valid'], False)
        self.assertEqual(result['is_verified'], False)
        self.assertEqual(result['error'], 'Invalid ID format')
        self.assertIsNone(result['details'])
    
    def test_verify_worker_id_with_invalid_id(self):
        """Test verifying a worker ID with completely invalid input"""
        invalid_id = "not_an_id"
        result = IDVerificationService.verify_worker_id(invalid_id)
        
        self.assertEqual(result['is_valid'], False)
        self.assertEqual(result['is_verified'], False)
        self.assertEqual(result['error'], 'Invalid ID format')
        self.assertIsNone(result['details'])
    
    def test_verify_worker_id_with_none(self):
        """Test verifying a worker ID with None input"""
        result = IDVerificationService.verify_worker_id(None)
        
        self.assertEqual(result['is_valid'], False)
        self.assertEqual(result['is_verified'], False)
        self.assertEqual(result['error'], 'Fayda ID is required')
        self.assertIsNone(result['details'])
    
    def test_verify_worker_id_with_empty_string(self):
        """Test verifying a worker ID with empty string"""
        result = IDVerificationService.verify_worker_id("")
        
        self.assertEqual(result['is_valid'], False)
        self.assertEqual(result['is_verified'], False)
        self.assertEqual(result['error'], 'Fayda ID is required')
        self.assertIsNone(result['details'])
    
    def test_validate_and_verify_worker_profile_with_valid_data(self):
        """Test validating and verifying a worker profile with valid data"""
        valid_id = "2205150100000008"
        full_name = "John Doe"
        result = IDVerificationService.validate_and_verify_worker_profile(valid_id, full_name)

        self.assertEqual(result['is_valid_format'], True)
        self.assertEqual(result['is_verified'], True)
        self.assertIsNone(result['error'])
        self.assertIsNotNone(result['details'])
        self.assertEqual(result['details']['fayda_id'], valid_id)
        self.assertEqual(result['details']['full_name'], full_name)
    
    def test_validate_and_verify_worker_profile_with_invalid_id(self):
        """Test validating and verifying a worker profile with invalid ID"""
        invalid_id = "123456010000000"  # Invalid checksum
        full_name = "John Doe"
        result = IDVerificationService.validate_and_verify_worker_profile(invalid_id, full_name)
        
        self.assertEqual(result['is_valid_format'], False)
        self.assertEqual(result['is_verified'], False)
        self.assertEqual(result['error'], 'Invalid Fayda ID format or checksum')
        self.assertIsNone(result['details'])
    
    def test_validate_and_verify_worker_profile_with_mismatched_name(self):
        """Test validating and verifying when name doesn't match records"""
        valid_id = "2205150100000008"
        full_name = "John Doe"

        # First call registers the ID with a name
        result1 = IDVerificationService.validate_and_verify_worker_profile(valid_id, full_name)
        self.assertEqual(result1['is_valid_format'], True)
        self.assertEqual(result1['is_verified'], True)

        # Second call with different name should fail verification
        result2 = IDVerificationService.validate_and_verify_worker_profile(valid_id, "Jane Doe")
        self.assertEqual(result2['is_valid_format'], True)  # Format is valid
        self.assertEqual(result2['is_verified'], False)  # But name doesn't match
        self.assertEqual(result2['error'], 'Name does not match ID records')