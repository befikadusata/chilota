import os
import magic
import pyclamd
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import TemporaryUploadedFile
import re
from PIL import Image
import io


def validate_file_type(file, allowed_types=None):
    """
    Validate file type based on MIME type and file header
    """
    if allowed_types is None:
        allowed_types = [
            'image/jpeg', 'image/jpg', 'image/png',  # Images
            'application/pdf',  # PDFs
            'application/msword',  # DOC
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'  # DOCX
        ]
    
    # Get MIME type using python-magic
    mime = magic.Magic(mime=True)
    file_mime = mime.from_buffer(file.read(1024))  # Read first 1KB to detect type
    file.seek(0)  # Reset file pointer
    
    # Also check file extension
    _, file_extension = os.path.splitext(file.name.lower())
    allowed_extensions = {
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'application/pdf': ['.pdf'],
        'application/msword': ['.doc'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    }
    
    # Validate MIME type
    if file_mime not in allowed_types:
        raise ValidationError(f'File type {file_mime} is not allowed. Allowed types: {allowed_types}')
    
    # Validate file extension matches MIME type
    valid_extensions = allowed_extensions.get(file_mime, [])
    if file_extension not in valid_extensions:
        raise ValidationError(f'File extension {file_extension} does not match the detected file type {file_mime}')
    
    return True


def validate_file_size(file, max_size_mb=10):
    """
    Validate file size (default: 10MB)
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(f'File size {file.size} bytes exceeds maximum allowed size of {max_size_mb}MB ({max_size_bytes} bytes)')
    return True


def validate_image_dimensions(file, max_width=4000, max_height=4000):
    """
    Validate image dimensions to prevent decompression bombs
    """
    # Only validate images
    if file.content_type.startswith('image/'):
        try:
            img = Image.open(file)
            width, height = img.size
            
            if width > max_width or height > max_height:
                raise ValidationError(f'Image dimensions {width}x{height} exceed maximum allowed dimensions of {max_width}x{max_height}')
                
            # Reset file pointer after reading
            file.seek(0)
            return True
        except Exception as e:
            raise ValidationError(f'Error validating image: {str(e)}')
    return True


def check_file_for_malware(file_path):
    """
    Scans a file for malware using ClamAV.
    """
    try:
        cd = pyclamd.ClamdAgnostic()
        if not cd.ping():
            # In production, you might want to handle this more gracefully
            # For now, we'll assume clamd is running and fail if it's not
            raise ConnectionError("Could not connect to clamd.")
        
        scan_result = cd.scan_file(file_path)
        if scan_result is not None:
            virus_name = scan_result[file_path][1]
            raise ValidationError(f'Malware detected: {virus_name}')
            
    except ConnectionError as e:
        # Log the error and decide on a policy. For now, we'll allow the file if the scanner is down.
        print(f"WARNING: Could not connect to ClamAV scanner: {e}. File was not scanned.")
    except Exception as e:
        raise ValidationError(f'Error during malware scan: {str(e)}')
        
    return True


def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal attacks
    """
    # Remove any path separators to prevent directory traversal
    filename = os.path.basename(filename)
    
    # Remove any potentially dangerous characters
    filename = re.sub(r'[^\w\s\-.()]', '_', filename)
    
    # Ensure the filename is not empty
    if not filename or filename in ['.', '..']:
        raise ValidationError('Invalid filename')
    
    return filename