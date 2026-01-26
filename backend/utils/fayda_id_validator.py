"""
Fayda ID Validation and Verification System

This module implements an Ethiopian national ID validation system with:
- Format validation
- Checksum verification
- Simulation of government ID verification
"""

import re
from typing import Dict, Optional


class FaydaIDValidator:
    """
    Validates Ethiopian national ID numbers (Fayda ID)
    Format: 16-digit number with checksum validation
    """
    
    def __init__(self):
        # Ethiopian regions and their 2-digit codes
        self.region_codes = {
            '01': 'Tigray',
            '02': 'Afar',
            '03': 'Amhara',
            '04': 'Oromia',
            '05': 'Somali',
            '06': 'Benishangul-Gumuz',
            '07': 'SNNPR',
            '08': 'Gambela',
            '09': 'Harari',
            '10': 'Addis Ababa',
            '11': 'Dire Dawa',
        }
    
    def validate_format(self, fayda_id: str) -> bool:
        """
        Validates the basic format of a Fayda ID.
        
        Args:
            fayda_id: The 16-digit ID number to validate
            
        Returns:
            True if format is valid, False otherwise
        """
        if not isinstance(fayda_id, str):
            return False
        
        # Check length and numeric format
        if len(fayda_id) != 16 or not fayda_id.isdigit():
            return False
        
        # Check if first 6 digits represent valid birth date (YYMMDD)
        birth_date_part = fayda_id[:6]
        year = birth_date_part[:2]
        month = birth_date_part[2:4]
        day = birth_date_part[4:6]
        
        # Basic validation for date components
        try:
            year_int = int(year)
            month_int = int(month)
            day_int = int(day)
            
            if not (0 <= month_int <= 12 and 1 <= day_int <= 31):
                return False
        except ValueError:
            return False
        
        # Check if next 2 digits represent valid region code
        region_code = fayda_id[6:8]
        if region_code not in self.region_codes:
            return False
        
        # Validate the checksum algorithm
        return self._validate_checksum(fayda_id)
    
    def _validate_checksum(self, fayda_id: str) -> bool:
        """
        Validates the checksum digit in the Fayda ID.

        Ethiopian ID checksum algorithm:
        - Weighted sum of first 15 digits
        - Weight pattern: alternating 1 and 3 (starting with 1)
        - Check digit is the number that, when added to the sum, makes it divisible by 10
        """
        if len(fayda_id) != 16:
            return False

        # Calculate weighted sum of first 15 digits
        total = 0
        for i in range(15):
            digit = int(fayda_id[i])
            # Apply alternating weights of 1 and 3, starting with 1
            weight = 1 if i % 2 == 0 else 3
            total += digit * weight

        # The check digit should make the total sum divisible by 10
        # So (total + check_digit) % 10 == 0
        # Which means check_digit = (10 - (total % 10)) % 10
        expected_check_digit = (10 - (total % 10)) % 10
        actual_check_digit = int(fayda_id[15])

        return expected_check_digit == actual_check_digit


class GovernmentIDVerificationService:
    """
    Simulates government ID verification service
    """

    # Class-level storage to maintain state across instances for simulation
    _valid_ids = set()
    _id_details = {}

    def __init__(self):
        # In a real implementation, this would connect to government ID verification API
        # For simulation, we'll maintain a simple database of valid IDs
        pass
        
    def verify_id(self, fayda_id: str, full_name: str = None) -> Dict[str, any]:
        """
        Simulates verification of a Fayda ID with government records.

        Args:
            fayda_id: The ID to verify
            full_name: Optional name to match against ID records

        Returns:
            Dictionary with verification result
        """
        # Validate format first
        validator = FaydaIDValidator()
        if not validator.validate_format(fayda_id):
            return {
                'is_valid': False,
                'is_verified': False,
                'error': 'Invalid ID format',
                'details': None
            }

        # Simulate checking against government database
        # In real implementation, this would call government API
        is_registered = fayda_id in GovernmentIDVerificationService._valid_ids

        if is_registered:
            # Return stored details
            details = GovernmentIDVerificationService._id_details.get(fayda_id, {})
            if full_name and details.get('full_name') != full_name:
                return {
                    'is_valid': True,
                    'is_verified': False,
                    'error': 'Name does not match ID records',
                    'details': details
                }

            return {
                'is_valid': True,
                'is_verified': True,
                'error': None,
                'details': details
            }
        else:
            # For simulation, we'll consider all valid format IDs as verified
            # In real world, this would depend on government database lookup
            details = {
                'fayda_id': fayda_id,
                'full_name': full_name,
                'region': self._extract_region_from_id(fayda_id),
                'birth_year': self._extract_birth_year_from_id(fayda_id)
            }

            # Register the ID as valid for future lookups
            GovernmentIDVerificationService._valid_ids.add(fayda_id)
            GovernmentIDVerificationService._id_details[fayda_id] = details

            return {
                'is_valid': True,
                'is_verified': True,
                'error': None,
                'details': details
            }
    
    def _extract_region_from_id(self, fayda_id: str) -> Optional[str]:
        """Extracts region name from ID's region code."""
        validator = FaydaIDValidator()
        region_code = fayda_id[6:8]
        return validator.region_codes.get(region_code)
    
    def _extract_birth_year_from_id(self, fayda_id: str) -> Optional[int]:
        """Extracts birth year from ID."""
        year_part = fayda_id[:2]
        try:
            year = int(year_part)
            # Assuming IDs are for people born in 1900s or 2000s
            # Ethiopian IDs typically use 2-digit years
            if year < 25:  # Assuming modern IDs (2000-2024)
                return 2000 + year
            else:
                return 1900 + year
        except ValueError:
            return None

    @classmethod
    def reset_storage(cls):
        """Reset the stored ID data - for testing purposes only"""
        cls._valid_ids.clear()
        cls._id_details.clear()


def validate_fayda_id_format(fayda_id: str) -> bool:
    """
    Convenience function to validate a Fayda ID format.
    
    Args:
        fayda_id: The ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    validator = FaydaIDValidator()
    return validator.validate_format(fayda_id)


def verify_fayda_id(fayda_id: str, full_name: str = None) -> Dict[str, any]:
    """
    Convenience function to verify a Fayda ID with the government service.
    
    Args:
        fayda_id: The ID to verify
        full_name: Optional name to match against ID records
        
    Returns:
        Verification result dictionary
    """
    service = GovernmentIDVerificationService()
    return service.verify_id(fayda_id, full_name)