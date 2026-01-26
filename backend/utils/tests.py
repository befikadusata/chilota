"""
Tests for the Fayda ID validation and verification utilities
"""
from django.test import TestCase
from utils.fayda_id_validator import FaydaIDValidator, GovernmentIDVerificationService, validate_fayda_id_format, verify_fayda_id


class TestFaydaIDValidator(TestCase):
    """Test cases for the Fayda ID validator"""
    
    def setUp(self):
        self.validator = FaydaIDValidator()
    
    def test_valid_id_format(self):
        """Test that a valid ID format passes validation"""
        # Valid ID: 16 digits with correct checksum
        # First 6 digits: 220515 (YYMMDD format: May 15, 2022)
        # Next 2 digits: 01 (region code for Tigray)
        # Next 7 digits: 0000000 (personal identifier)
        # Last digit: 8 (checksum digit)
        # Calculating checksum for first 15 digits "220515010000000":
        # 2*1+2*3+0*1+5*3+1*1+5*3+0*1+1*3+0*1+0*3+0*1+0*3+0*1+0*3+0*1
        # = 2+6+0+15+1+15+0+3+0+0+0+0+0+0+0 = 42
        # Expected checksum: (10 - (42 % 10)) % 10 = (10 - 2) % 10 = 8
        valid_id = "2205150100000008"  # First 6: birth date, next 2: region code, next 7: personal ID, last 1: checksum
        self.assertTrue(self.validator.validate_format(valid_id))
    
    def test_invalid_length(self):
        """Test that IDs with incorrect length fail validation"""
        invalid_ids = [
            "123456789012345",  # 15 digits
            "12345678901234567",  # 17 digits
            "12345",  # 5 digits
            ""  # empty
        ]
        
        for invalid_id in invalid_ids:
            with self.subTest(invalid_id=invalid_id):
                self.assertFalse(self.validator.validate_format(invalid_id))
    
    def test_non_numeric_format(self):
        """Test that IDs with non-numeric characters fail validation"""
        invalid_ids = [
            "123456789012345a",
            "123456789012345!",
            "1234567890123 5",
            "123456789012345-",
        ]
        
        for invalid_id in invalid_ids:
            with self.subTest(invalid_id=invalid_id):
                self.assertFalse(self.validator.validate_format(invalid_id))
    
    def test_invalid_region_code(self):
        """Test that IDs with invalid region codes fail validation"""
        # Valid birth date but invalid region code (99 is not a valid region)
        invalid_id = "123456990123456"
        self.assertFalse(self.validator.validate_format(invalid_id))
    
    def test_invalid_checksum(self):
        """Test that IDs with incorrect checksum fail validation"""
        # This ID has an incorrect checksum digit
        invalid_id = "123456010000000"  # checksum should not be 0
        self.assertFalse(self.validator.validate_format(invalid_id))
    
    def test_checksum_algorithm(self):
        """Test that the checksum algorithm works correctly"""
        # Example with checksum calculation using a valid ID:
        # ID: 2205150100000008
        # First 15 digits: 220515010000000
        # Positions (0-indexed): 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14
        # Digits:                2, 2, 0, 5, 1, 5, 0, 1, 0, 0, 0, 0, 0, 0, 0
        # Weights:               1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1
        # Weighted sum: 2*1 + 2*3 + 0*1 + 5*3 + 1*1 + 5*3 + 0*1 + 1*3 + 0*1 + 0*3 + 0*1 + 0*3 + 0*1 + 0*3 + 0*1
        # = 2 + 6 + 0 + 15 + 1 + 15 + 0 + 3 + 0 + 0 + 0 + 0 + 0 + 0 + 0 = 42
        # Expected checksum: (10 - (42 % 10)) % 10 = (10 - 2) % 10 = 8
        # Actual 16th digit: 8
        # Since 8 == 8, the ID is valid
        valid_checksum_id = "2205150100000008"
        self.assertTrue(self.validator.validate_format(valid_checksum_id))
    
    def test_convenience_function(self):
        """Test the convenience function for validation"""
        valid_id = "2205150100000008"
        invalid_id = "2205150100000009"  # Invalid checksum (should end in 8, not 9)

        self.assertTrue(validate_fayda_id_format(valid_id))
        self.assertFalse(validate_fayda_id_format(invalid_id))


class TestGovernmentIDVerificationService(TestCase):
    """Test cases for the government ID verification service"""

    def setUp(self):
        # Reset the class-level storage before each test
        GovernmentIDVerificationService.reset_storage()
        self.service = GovernmentIDVerificationService()
    
    def test_valid_id_verification(self):
        """Test that a valid ID gets verified successfully"""
        valid_id = "2205150100000008"
        result = self.service.verify_id(valid_id)

        self.assertEqual(result['is_valid'], True)
        self.assertEqual(result['is_verified'], True)
        self.assertIsNone(result['error'])
        self.assertIsNotNone(result['details'])
        self.assertEqual(result['details']['fayda_id'], valid_id)
    
    def test_invalid_format_verification(self):
        """Test that an ID with invalid format fails verification"""
        invalid_id = "123456010000000"  # Invalid checksum
        
        result = self.service.verify_id(invalid_id)
        
        self.assertEqual(result['is_valid'], False)
        self.assertEqual(result['is_verified'], False)
        self.assertEqual(result['error'], 'Invalid ID format')
        self.assertIsNone(result['details'])
    
    def test_name_matching(self):
        """Test that name verification works correctly"""
        valid_id = "2205150100000008"
        valid_name = "Test Name"

        # First call registers the ID with the name
        result1 = self.service.verify_id(valid_id, valid_name)
        self.assertEqual(result1['is_valid'], True)
        self.assertEqual(result1['is_verified'], True)

        # Second call with matching name should succeed
        result2 = self.service.verify_id(valid_id, valid_name)
        self.assertEqual(result2['is_valid'], True)
        self.assertEqual(result2['is_verified'], True)

        # Third call with non-matching name should fail
        result3 = self.service.verify_id(valid_id, "Different Name")
        self.assertEqual(result3['is_valid'], True)
        self.assertEqual(result3['is_verified'], False)
        self.assertEqual(result3['error'], 'Name does not match ID records')
    
    def test_convenience_function(self):
        """Test the convenience function for verification"""
        valid_id = "2205150100000008"
        result = verify_fayda_id(valid_id)

        self.assertEqual(result['is_valid'], True)
        self.assertEqual(result['is_verified'], True)
        self.assertIsNone(result['error'])