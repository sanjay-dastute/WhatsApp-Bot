# WhatsApp Bot for Family & Samaj Data Collection

A comprehensive WhatsApp bot system for collecting and managing family and Samaj-wise information, featuring an admin dashboard and secure data management.

## Features

- WhatsApp-based data collection with step-by-step guidance
- Interactive data collection with validation
- Review and confirmation steps
- Secure admin dashboard with JWT authentication
- CSV export/import functionality
- PostgreSQL database for reliable data storage
- Docker containerization for easy deployment
- CI/CD pipeline with GitHub Actions
- Comprehensive input validation for all fields

## Additional Data Fields

Beyond the core columns, we've added 20 additional fields to capture comprehensive family information:

1. Education - Educational qualifications
2. Occupation - Current profession
3. Marital Status - Current marital status
4. Address - Current residential address
5. Email - Contact email address
6. Birth Date - Date of birth
7. Anniversary Date - Marriage anniversary date
8. Native Place - Place of origin
9. Current City - Current city of residence
10. Languages Known - Languages spoken/written
11. Skills - Professional/personal skills
12. Hobbies - Personal interests
13. Emergency Contact - Emergency contact information
14. Relationship Status - Family relationship status
15. Family Role - Role in the family
16. Medical Conditions - Important health information
17. Dietary Preferences - Food preferences/restrictions
18. Social Media Handles - Social media profiles
19. Profession Category - Industry/sector of work
20. Volunteer Interests - Areas of community service interest

## Setup Instructions

1. Clone the repository
2. Create a .env file with required credentials
3. Run with Docker:
   ```bash
   docker-compose up --build
   ```

## Development Setup

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Run the application:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## API Documentation

Access the API documentation at `/docs` endpoint after starting the server.

## Environment Variables

Required environment variables:
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- DATABASE_URL

## Project Structure

```
├── app/
│   ├── controllers/      # Business logic
│   ├── models/          # Database models
│   ├── services/        # Business services
│   ├── routes/          # API routes
│   └── utils/           # Utility functions
├── tests/               # Test cases
├── docker-compose.yml   # Docker configuration
├── Dockerfile          # Docker build instructions
├── README.md           # Documentation
└── .env               # Environment variables
```
