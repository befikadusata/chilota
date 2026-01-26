# Security Policy

This document outlines the security measures implemented in the Ethiopian Domestic & Skilled Worker Platform and provides guidelines for maintaining a secure environment.

## 1. Input Sanitization and SQL Injection Prevention
- All database interactions are performed using Django's Object-Relational Mapper (ORM), which inherently protects against SQL injection vulnerabilities by properly escaping user-provided data.
- Frontend forms and backend serializers implement validation to sanitize user inputs, preventing common attacks like Cross-Site Scripting (XSS).

## 2. Rate Limiting (Throttling)
- Django REST Framework's built-in throttling is used to limit the number of requests users (both anonymous and authenticated) can make to the API within a given timeframe.
  - Anonymous users are limited to `100 requests per day`.
  - Authenticated users are limited to `1000 requests per day`.
- This helps mitigate brute-force attacks and denial-of-service (DoS) attempts.

## 3. Secure File Uploads
- **File Type Validation**: All uploaded files are validated by MIME type using `python-magic` and file extension to ensure only allowed file types (e.g., images, PDFs, DOCX) are accepted.
- **File Size Limits**: Maximum file sizes are enforced (e.g., 5MB for photos, 10MB for certifications).
- **Image Dimension Validation**: Images are validated for reasonable dimensions to prevent decompression bomb attacks.
- **Filename Sanitization**: Filenames are sanitized to prevent directory traversal vulnerabilities.
- **Malware Scanning**: A placeholder is in place for malware scanning of uploaded files. In a production environment, this **must** be integrated with a robust external antivirus solution (e.g., ClamAV) to scan all uploads for malicious content.

## 4. Data Encryption for Sensitive Personal Information
- Sensitive personal information (e.g., Fayda ID, certain contact details) stored in the database should be encrypted at rest. This can be achieved using:
    - Database-level encryption features.
    - Django fields specifically designed for encryption (e.g., `django-encrypted-fields` or custom encryption logic applied at the model layer).
- Data in transit is protected using HTTPS/SSL/TLS for all communications.

## 5. Authentication and Authorization
- **JWT Authentication**: JSON Web Tokens (JWT) are used for API authentication, providing secure stateless authentication.
- **Role-Based Access Control (RBAC)**: A custom role-based permission system ensures users can only access resources and perform actions relevant to their assigned roles (Worker, Employer, Admin).
- **Strong Password Policies**: Django's built-in password validators are configured to enforce minimum length, complexity, and prevent common passwords.

## 6. Data Protection and Privacy (GDPR Compliance & RTBF)
- **User Consent**: Mechanisms for obtaining and recording user consent for data processing should be implemented (e.g., explicit checkboxes during registration/profile updates).
- **Data Minimization**: Only necessary personal data is collected and stored.
- **Right to be Forgotten (RTBF)**: Functionality to securely and permanently delete all user data upon request must be implemented. This includes data in the primary database, backups, and any integrated services.
- **Data Anonymization**: For analytics and reporting, personal data should be anonymized or pseudonymized to protect user privacy.

## 7. Audit Logging
- Sensitive operations and changes to user data are logged to provide an audit trail. This includes login attempts, profile modifications, data deletions, and administrative actions.
- Logs are protected from unauthorized access and regularly reviewed.

## 8. Secure Deployment Practices
- Production environments are configured with `DEBUG=False`.
- `SECRET_KEY` and other sensitive configurations are managed securely using environment variables.
- Static and media files are served securely.
- Regular security updates for all dependencies are performed.

## Reporting Security Issues
If you discover any security vulnerabilities, please report them immediately to [security@example.com] (replace with actual security contact).
