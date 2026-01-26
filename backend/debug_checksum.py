#!/usr/bin/env python
"""
Script to test the checksum algorithm step by step
"""

import sys
import os
# Add the project root to Python path
sys.path.append('/home/ubuntu/Dev2/SurveAddis/LaborCon')

# Set up Django
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laborcon.settings')
django.setup()

from utils.fayda_id_validator import FaydaIDValidator

def manual_validate(id_str):
    """Manually validate the ID step by step"""
    print(f"Validating ID: {id_str}")
    print(f"Length: {len(id_str)}")
    
    if len(id_str) != 16:
        print("FAIL: Length is not 16")
        return False
        
    # Check if all characters are digits
    if not id_str.isdigit():
        print("FAIL: Contains non-digit characters")
        return False
    
    # Check region code (positions 6-7)
    region_code = id_str[6:8]
    print(f"Region code: {region_code}")
    
    validator = FaydaIDValidator()
    if region_code not in validator.region_codes:
        print(f"FAIL: Invalid region code: {region_code}")
        return False
    
    print(f"Valid region: {validator.region_codes[region_code]}")
    
    # Validate checksum
    # Positions:  0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15
    # Digits:     1, 2, 3, 4, 5, 6, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1
    # Weights:    1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3
    print("Position analysis:")
    total = 0
    for i in range(15):  # First 15 digits for checksum calculation
        digit = int(id_str[i])
        weight = 1 if i % 2 == 0 else 3
        product = digit * weight
        total += product
        print(f"  Pos {i}: digit={digit}, weight={weight}, product={product}")
    
    print(f"Weighted sum of first 15 digits: {total}")
    expected_checksum = (10 - (total % 10)) % 10
    actual_checksum = int(id_str[15])
    print(f"Expected checksum: {expected_checksum}")
    print(f"Actual checksum (16th digit): {actual_checksum}")
    
    is_valid_checksum = expected_checksum == actual_checksum
    print(f"Checksum valid: {is_valid_checksum}")
    
    if is_valid_checksum:
        print("OVERALL: VALID")
    else:
        print("OVERALL: INVALID (checksum mismatch)")
    
    return is_valid_checksum

if __name__ == "__main__":
    # Test different IDs to find a valid one
    test_ids = [
        "1234560100000101",  # Month=34, Day=56 - invalid date
        "1234560100000109",  # Month=34, Day=56 - invalid date
        "1234560100000002",  # Month=34, Day=56 - invalid date
        "2205150100000008",  # Month=05, Day=15 - valid date, checksum should be 8
    ]

    for test_id in test_ids:
        print(f"Testing ID: {test_id}")
        manual_validate(test_id)
        print()

    # Now test using the actual validator
    validator = FaydaIDValidator()
    for test_id in test_ids:
        result = validator.validate_format(test_id)
        print(f"Validator result for {test_id}: {result}")