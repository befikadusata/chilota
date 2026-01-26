"""
Service layer for handling Fayda ID verification and related operations
"""
from typing import Dict, Any, Optional
from django.core.exceptions import ValidationError
from utils.fayda_id_validator import verify_fayda_id


class IDVerificationService:
    """
    Service class for handling ID verification operations
    """
    
    @staticmethod
    def verify_worker_id(fayda_id: str, full_name: str = None) -> Dict[str, Any]:
        """
        Verifies a worker's Fayda ID through government service simulation.
        
        Args:
            fayda_id: The ID to verify
            full_name: Optional name to match against ID records
            
        Returns:
            Dictionary containing verification results
        """
        if not fayda_id:
            return {
                'is_valid': False,
                'is_verified': False,
                'error': 'Fayda ID is required',
                'details': None
            }
        
        # Perform verification using the simulation service
        result = verify_fayda_id(fayda_id, full_name)
        
        return result
        
    
    @staticmethod
    def validate_and_verify_worker_profile(fayda_id: str, full_name: str) -> Dict[str, Any]:
        """
        Validates format and verifies a worker profile's ID information.

        Args:
            fayda_id: The ID to validate and verify
            full_name: Name to match against ID records

        Returns:
            Dictionary containing validation and verification results
        """
        from utils.fayda_id_validator import validate_fayda_id_format

        # First, validate the format
        if not validate_fayda_id_format(fayda_id):
            return {
                'is_valid_format': False,
                'is_verified': False,
                'error': 'Invalid Fayda ID format or checksum',
                'details': None
            }

        # Then verify with government service
        verification_result = IDVerificationService.verify_worker_id(fayda_id, full_name)

        # Ensure consistency in response format
        return {
            'is_valid_format': verification_result['is_valid'],  # Since format passed validation, it's valid
            'is_verified': verification_result['is_verified'],
            'error': verification_result['error'],
            'details': verification_result['details']
        }