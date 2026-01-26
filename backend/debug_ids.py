#!/usr/bin/env python
"""
Script to validate ID calculations in the tests
"""

import sys
import os
sys.path.append('/home/ubuntu/Dev2/SurveAddis/LaborCon')

# Set up Django
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laborcon.settings')
django.setup()

from utils.fayda_id_validator import validate_fayda_id_format

# Test the specific IDs from the failing tests
test_ids = [
    '2207110400000005',  # Calculated from '220711040000000' with checksum 5
    '2207120500000002',  # From the integrity report test
]

# Calculate checksum manually for '220711040000000':
base = '220711040000000'
print(f"Base ID: {base}")
total = 0
for idx, digit in enumerate(base):
    weight = 1 if idx % 2 == 0 else 3
    product = int(digit) * weight
    total += product
    print(f"  Pos {idx}: {digit} * {weight} = {product}")

print(f"Sum of first 15 digits: {total}")
checksum = (10 - (total % 10)) % 10
print(f"Checksum: {checksum}")
full_id = base + str(checksum)
print(f"Complete ID: {full_id}")

for test_id in test_ids:
    print(f"Validating {test_id}: {validate_fayda_id_format(test_id)}")