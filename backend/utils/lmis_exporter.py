"""
LMIS (Labor Market Information System) Data Export and Compatibility Functions

This module provides utilities for exporting Ethiopian worker data in
formats compatible with the national Labor Market Information System.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from workers.models import WorkerProfile


class LMISDataExporter:
    """
    Exports worker data in LMIS-compatible format
    """
    
    @staticmethod
    def export_worker_data_to_lmis_format(worker_profiles: List[WorkerProfile]) -> Dict[str, Any]:
        """
        Exports worker profile data in LMIS-compatible JSON format.
        
        Args:
            worker_profiles: List of WorkerProfile objects to export
            
        Returns:
            Dictionary containing LMIS-compatible data structure
        """
        lmis_records = []
        
        for profile in worker_profiles:
            lmis_record = LMISDataExporter._convert_worker_to_lmis_format(profile)
            lmis_records.append(lmis_record)
        
        return {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_records': len(lmis_records),
                'export_source': 'Ethiopian Domestic and Skilled Worker Platform',
                'version': '1.0',
                'data_owner': 'Ethiopian Ministry of Labor and Social Affairs'
            },
            'workers': lmis_records
        }
    
    @staticmethod
    def _convert_worker_to_lmis_format(profile: WorkerProfile) -> Dict[str, Any]:
        """
        Converts a WorkerProfile to LMIS-compatible format.
        
        Args:
            profile: WorkerProfile instance
            
        Returns:
            Dictionary with LMIS-compatible structure
        """
        # Map the fields to LMIS format
        lmis_worker = {
            # Personal Information
            'personnel_id': profile.fayda_id,  # Using Fayda ID as unique identifier
            'full_name': profile.full_name,
            'age': profile.age,
            'date_of_birth': LMISDataExporter._calculate_birth_date_from_age(profile.age),
            'place_of_birth': profile.place_of_birth,
            'region_of_origin': profile.region_of_origin,
            'current_location': profile.current_location,
            
            # Demographics
            'gender': 'unknown',  # Not captured in current model, defaulting to unknown
            'religion': profile.religion,
            'education_level': profile.education_level,
            
            # Skills and Experience
            'skills': [
                {'skill_name': skill, 'proficiency_level': 'intermediate'}  # Proficiency not stored in current model
                for skill in profile.skills
            ],
            'years_of_experience': profile.years_experience,
            
            # Language Proficiency
            'languages': [
                {'language': lang.get('language', ''), 'proficiency': lang.get('proficiency', 'basic')}
                for lang in profile.languages
            ],
            
            # Employment Details  
            'preferred_working_arrangement': profile.working_time,
            'background_check_status': profile.background_check_status,
            'profile_rating': float(profile.rating),
            'registration_date': profile.created_at.isoformat(),
            'last_updated': profile.updated_at.isoformat(),
            
            # Emergency Contact
            'emergency_contact': {
                'name': profile.emergency_contact_name,
                'phone': profile.emergency_contact_phone
            },
            
            # System fields
            'profile_status': 'active' if profile.is_approved else 'pending',
            'platform_source': 'Ethiopian Worker Platform'
        }
        
        return lmis_worker
    
    @staticmethod
    def _calculate_birth_date_from_age(age: int) -> str:
        """
        Calculates approximate birth date from age.
        
        Args:
            age: Current age of the worker
            
        Returns:
            ISO formatted birth date string (YYYY-MM-DD)
        """
        current_year = datetime.now().year
        birth_year = current_year - age
        # Using Jan 1 as approximate birth date since we don't have exact DOB
        return f"{birth_year}-01-01"
    
    @staticmethod
    def export_to_csv_format(worker_profiles: List[WorkerProfile]) -> str:
        """
        Exports worker data in CSV format compatible with LMIS.
        
        Args:
            worker_profiles: List of WorkerProfile objects to export
            
        Returns:
            CSV formatted string
        """
        import csv
        import io
        
        # Create a string buffer to write CSV data to
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header row
        header = [
            'personnel_id', 'full_name', 'age', 'date_of_birth', 'place_of_birth',
            'region_of_origin', 'current_location', 'gender', 'religion', 
            'education_level', 'years_of_experience', 'preferred_working_arrangement', 
            'background_check_status', 'profile_rating', 'registration_date',
            'profile_status', 'emergency_contact_name', 'emergency_contact_phone'
        ]
        writer.writerow(header)
        
        # Write data rows
        for profile in worker_profiles:
            row = [
                profile.fayda_id,
                profile.full_name,
                profile.age,
                LMISDataExporter._calculate_birth_date_from_age(profile.age),
                profile.place_of_birth,
                profile.region_of_origin,
                profile.current_location,
                'unknown',  # gender
                profile.religion,
                profile.education_level,
                profile.years_experience,
                profile.working_time,
                profile.background_check_status,
                float(profile.rating),
                profile.created_at.isoformat(),
                'active' if profile.is_approved else 'pending',
                profile.emergency_contact_name,
                profile.emergency_contact_phone
            ]
            writer.writerow(row)
        
        # Get the CSV content
        csv_content = output.getvalue()
        output.close()
        
        return csv_content


class LMISDataValidator:
    """
    Validates data according to LMIS specifications
    """
    
    @staticmethod
    def validate_worker_data_for_lmis(profile: WorkerProfile) -> Dict[str, Any]:
        """
        Validates a worker profile against LMIS data requirements.
        
        Args:
            profile: WorkerProfile to validate
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Validate Fayda ID
        if not profile.fayda_id or len(profile.fayda_id) != 16:
            errors.append('Fayda ID must be 16 digits')
        
        # Validate required fields
        if not profile.full_name:
            errors.append('Full name is required')
        
        if profile.age < 16 or profile.age > 65:
            errors.append('Age must be between 16 and 65')
        
        if not profile.region_of_origin:
            errors.append('Region of origin is required')
        
        if not profile.current_location:
            errors.append('Current location is required')
        
        if not profile.education_level:
            errors.append('Education level is required')
        
        if not profile.religion:
            errors.append('Religion is required')
        
        if not profile.working_time:
            errors.append('Working time preference is required')
        
        if profile.years_experience < 0:
            errors.append('Years of experience cannot be negative')
        
        # Validate emergency contact
        if not profile.emergency_contact_name:
            errors.append('Emergency contact name is required')
        
        if not profile.emergency_contact_phone:
            errors.append('Emergency contact phone is required')
        
        # Check if skills list is empty
        if not profile.skills or len(profile.skills) == 0:
            warnings.append('Worker has no skills listed')
        
        # Check if languages list is empty
        if not profile.languages or len(profile.languages) == 0:
            warnings.append('Worker has no languages listed')
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validated_data': profile if len(errors) == 0 else None
        }
    
    @staticmethod
    def validate_batch_for_lmis(profiles: List[WorkerProfile]) -> Dict[str, Any]:
        """
        Validates a batch of worker profiles for LMIS export.
        
        Args:
            profiles: List of WorkerProfile objects
            
        Returns:
            Dictionary with batch validation results
        """
        results = []
        valid_profiles = []
        invalid_profiles = []
        
        for profile in profiles:
            validation_result = LMISDataValidator.validate_worker_data_for_lmis(profile)
            results.append({
                'profile_id': profile.id,
                'is_valid': validation_result['is_valid'],
                'errors': validation_result['errors'],
                'warnings': validation_result['warnings']
            })
            
            if validation_result['is_valid']:
                valid_profiles.append(profile)
            else:
                invalid_profiles.append({
                    'profile': profile,
                    'errors': validation_result['errors']
                })
        
        return {
            'total_profiles': len(profiles),
            'valid_profiles': len(valid_profiles),
            'invalid_profiles': len(invalid_profiles),
            'validation_results': results,
            'valid_data': valid_profiles,
            'invalid_data': invalid_profiles
        }


class LMISIntegrityChecker:
    """
    Performs data integrity checks for LMIS export
    """
    
    @staticmethod
    def check_integrity_of_worker_data(profiles: List[WorkerProfile]) -> Dict[str, Any]:
        """
        Checks integrity of worker profile data for LMIS export.
        
        Args:
            profiles: List of WorkerProfile objects
            
        Returns:
            Dictionary with integrity check results
        """
        total_profiles = len(profiles)
        duplicate_ids = []
        missing_critical_fields = []
        
        seen_ids = set()
        for profile in profiles:
            # Check for duplicate IDs
            if profile.fayda_id in seen_ids:
                duplicate_ids.append(profile.fayda_id)
            else:
                seen_ids.add(profile.fayda_id)
            
            # Check for missing critical fields
            missing_fields = []
            if not profile.full_name:
                missing_fields.append('full_name')
            if not profile.region_of_origin:
                missing_fields.append('region_of_origin')
            if not profile.current_location:
                missing_fields.append('current_location')
            if not profile.education_level:
                missing_fields.append('education_level')
            if not profile.religion:
                missing_fields.append('religion')
            if not profile.working_time:
                missing_fields.append('working_time')
            if not profile.emergency_contact_name:
                missing_fields.append('emergency_contact_name')
            if not profile.emergency_contact_phone:
                missing_fields.append('emergency_contact_phone')
            
            if missing_fields:
                missing_critical_fields.append({
                    'profile_id': profile.id,
                    'profile_full_name': profile.full_name,
                    'missing_fields': missing_fields
                })
        
        return {
            'total_profiles': total_profiles,
            'duplicate_ids': list(set(duplicate_ids)),  # Remove duplicates in duplicate list
            'missing_critical_fields': missing_critical_fields,
            'has_issues': len(duplicate_ids) > 0 or len(missing_critical_fields) > 0,
            'integrity_status': 'PASS' if not (duplicate_ids or missing_critical_fields) else 'FAIL'
        }
        
    @staticmethod
    def generate_integrity_report(profiles: List[WorkerProfile]) -> str:
        """
        Generates a human-readable integrity report.
        
        Args:
            profiles: List of WorkerProfile objects
            
        Returns:
            Formatted integrity report string
        """
        integrity_check = LMISIntegrityChecker.check_integrity_of_worker_data(profiles)
        
        report_lines = [
            "LMIS Data Integrity Report",
            "==========================",
            f"Total Profiles: {integrity_check['total_profiles']}",
            f"Integrity Status: {integrity_check['integrity_status']}",
            ""
        ]
        
        if integrity_check['duplicate_ids']:
            report_lines.append("Duplicate IDs Found:")
            for dup_id in integrity_check['duplicate_ids']:
                report_lines.append(f"  - {dup_id}")
            report_lines.append("")
        
        if integrity_check['missing_critical_fields']:
            report_lines.append("Profiles with Missing Critical Fields:")
            for missing in integrity_check['missing_critical_fields']:
                report_lines.append(f"  - Profile {missing['profile_id']} ({missing['profile_full_name']}): {', '.join(missing['missing_fields'])}")
            report_lines.append("")
        
        if not integrity_check['duplicate_ids'] and not integrity_check['missing_critical_fields']:
            report_lines.append("All data integrity checks passed!")
        
        return "\n".join(report_lines)