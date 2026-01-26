"""
Tests for the WorkerProfile model's Fayda ID validation
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from workers.models import WorkerProfile
from django.core.exceptions import ValidationError


User = get_user_model()


class TestWorkerProfileFaydaIDValidation(TestCase):
    """Test cases for WorkerProfile Fayda ID validation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testworker',
            password='testpass123',
            user_type='worker'
        )
    
    def test_valid_fayda_id_saves_successfully(self):
        """Test that a worker profile with a valid Fayda ID saves successfully"""
        valid_fayda_id = "2205150100000008"  # Valid ID with correct checksum

        profile = WorkerProfile(
            user=self.user,
            fayda_id=valid_fayda_id,
            full_name="Test Worker",
            age=25,
            place_of_birth="Addis Ababa",
            region_of_origin="Oromia",
            current_location="Addis Ababa",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="1234567890",
            education_level="secondary",
            religion="eth_orthodox",
            working_time="full_time",
            years_experience=2,
        )

        # This should not raise an exception
        profile.save()

        # Verify the profile was saved with the correct ID
        saved_profile = WorkerProfile.objects.get(user=self.user)
        self.assertEqual(saved_profile.fayda_id, valid_fayda_id)
    
    def test_invalid_format_fayda_id_raises_error(self):
        """Test that a worker profile with an invalid Fayda ID format raises an error"""
        invalid_fayda_id = "123456010000000"  # Invalid checksum
        
        profile = WorkerProfile(
            user=self.user,
            fayda_id=invalid_fayda_id,
            full_name="Test Worker",
            age=25,
            place_of_birth="Addis Ababa",
            region_of_origin="Oromia",
            current_location="Addis Ababa",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="1234567890",
            education_level="secondary",
            religion="eth_orthodox",
            working_time="full_time",
            years_experience=2,
        )
        
        # This should raise a ValidationError
        with self.assertRaises(ValidationError):
            profile.save()
    
    def test_invalid_length_fayda_id_raises_error(self):
        """Test that a worker profile with an invalid length Fayda ID raises an error"""
        invalid_fayda_id = "123456789012345"  # Only 15 digits
        
        profile = WorkerProfile(
            user=self.user,
            fayda_id=invalid_fayda_id,
            full_name="Test Worker",
            age=25,
            place_of_birth="Addis Ababa",
            region_of_origin="Oromia",
            current_location="Addis Ababa",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="1234567890",
            education_level="secondary",
            religion="eth_orthodox",
            working_time="full_time",
            years_experience=2,
        )
        
        # This should raise a ValidationError
        with self.assertRaises(ValidationError):
            profile.save()
    
    def test_duplicate_fayda_id_raises_error(self):
        """Test that trying to create a profile with a duplicate Fayda ID raises an error"""
        valid_fayda_id = "2205150100000008"

        # Create first profile
        profile1 = WorkerProfile(
            user=self.user,
            fayda_id=valid_fayda_id,
            full_name="Test Worker 1",
            age=25,
            place_of_birth="Addis Ababa",
            region_of_origin="Oromia",
            current_location="Addis Ababa",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="1234567890",
            education_level="secondary",
            religion="eth_orthodox",
            working_time="full_time",
            years_experience=2,
        )
        profile1.save()

        # Create second user and profile
        user2 = User.objects.create_user(
            username='testworker2',
            password='testpass123',
            user_type='worker'
        )

        profile2 = WorkerProfile(
            user=user2,
            fayda_id=valid_fayda_id,  # Same ID as profile1
            full_name="Test Worker 2",
            age=30,
            place_of_birth="Addis Ababa",
            region_of_origin="Amhara",
            current_location="Addis Ababa",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="0987654321",
            education_level="tertiary",
            religion="protestant",
            working_time="part_time",
            years_experience=5,
        )

        # This should raise a ValidationError due to duplicate ID
        with self.assertRaises(ValidationError):
            profile2.save()
    
    def test_empty_fayda_id_raises_error(self):
        """Test that an empty Fayda ID raises an error at the model level"""
        profile = WorkerProfile(
            user=self.user,
            fayda_id="",  # Empty ID
            full_name="Test Worker",
            age=25,
            place_of_birth="Addis Ababa",
            region_of_origin="Oromia",
            current_location="Addis Ababa",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="1234567890",
            education_level="secondary",
            religion="eth_orthodox",
            working_time="full_time",
            years_experience=2,
        )
        
        # This should raise a ValidationError
        with self.assertRaises(ValidationError):
            profile.save()
    
    def test_non_numeric_fayda_id_raises_error(self):
        """Test that a non-numeric Fayda ID raises an error"""
        invalid_fayda_id = "12345601000000a"  # Contains a letter
        
        profile = WorkerProfile(
            user=self.user,
            fayda_id=invalid_fayda_id,
            full_name="Test Worker",
            age=25,
            place_of_birth="Addis Ababa",
            region_of_origin="Oromia",
            current_location="Addis Ababa",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="1234567890",
            education_level="secondary",
            religion="eth_orthodox",
            working_time="full_time",
            years_experience=2,
        )
        
        # This should raise a ValidationError
        with self.assertRaises(ValidationError):
            profile.save()