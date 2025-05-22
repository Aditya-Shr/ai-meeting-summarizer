# AI Meeting Summarizer Architecture

## Backend Architecture

### Overview
The backend is built using FastAPI and follows a clean, modular architecture with clear separation of concerns. The application is organized into several key components:

### Directory Structure
```
backend/
├── app/
│   ├── api/            # API routes and endpoints
│   ├── core/           # Core configurations and utilities
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic schemas for data validation
│   ├── services/       # Business logic and external services
│   └── main.py         # Application entry point
├── migrations/         # Database migrations
├── tests/             # Test files
└── uploads/           # Temporary file storage
```

### Key Components

1. **API Layer** (`/api`)
   - RESTful endpoints for meetings, action items, and decisions
   - Request validation and response formatting
   - Route handlers for all API operations

2. **Core Module** (`/core`)
   - Configuration management
   - Database connection handling
   - Security and authentication
   - Process management

3. **Models** (`/models`)
   - SQLAlchemy ORM models
   - Database table definitions
   - Relationships between entities

4. **Schemas** (`/schemas`)
   - Pydantic models for data validation
   - Request/response models
   - Data transformation logic

5. **Services** (`/services`)
   - Business logic implementation
   - External service integrations
   - AI model interactions
   - Calendar integration

### Data Flow
1. **Request Processing**
   - Client request → API endpoint
   - Request validation using Pydantic schemas
   - Route handler processes request

2. **Business Logic**
   - Service layer handles core operations
   - Database operations through models
   - External service integration

3. **Response Generation**
   - Data transformation using schemas
   - Response formatting
   - Error handling

### Key Features
1. **Modular Design**
   - Easy to maintain and extend
   - Clear separation of concerns
   - Reusable components

2. **Database Integration**
   - SQLAlchemy ORM
   - Migration support
   - Connection pooling

3. **Service Integration**
   - AI model integration
   - Calendar API integration
   - File handling

4. **Error Handling**
   - Consistent error responses
   - Detailed error messages
   - Proper HTTP status codes

### Development Guidelines
1. **Code Organization**
   - Follow the established directory structure
   - Keep related code together
   - Use appropriate naming conventions

2. **Documentation**
   - Document all API endpoints
   - Include code comments
   - Maintain up-to-date schemas 