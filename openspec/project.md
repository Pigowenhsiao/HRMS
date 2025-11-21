# Project Context

## Purpose
HRMS (Human Resource Management System) is a Python-based employee management system with a desktop UI built using PySide6. The system uses CSV files as a backend to store employee data, with support for file locking and atomic write operations to prevent data corruption. The system provides CRUD operations for employee data, Excel export functionality, and an optional FastAPI-based API layer. This project is a rewrite of a previous VB.NET + Access system to Python with CSV storage.

Currently, the system has an employee management module (TE_BASIC) with query, load, upsert (create/update), delete, and Excel export functions. It also includes lookup/reference tables such as departments, areas, job titles, and vacation types. The system follows a layered architecture with UI, Service, Repository, and Storage/Adapter layers.

## Tech Stack
- Python 3.10+
- PySide6 (for desktop UI)
- Pandas (for CSV data manipulation)
- Openpyxl (for Excel export)
- Pydantic (for data validation and settings management)
- Python-dotenv (for environment variables)
- PyYAML (for configuration files)
- Filelock (for file locking during CSV operations)
- FastAPI (optional API layer)
- Uvicorn (ASGI server for FastAPI)
- SQLAlchemy (in some parts of the project)

## Project Conventions

### Code Style
- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Type hints are encouraged using Python's typing module
- Class names should use PascalCase
- Function and variable names should use snake_case
- Module names should be short, lowercase, and can include underscores

### Architecture Patterns
- Layered architecture (UI ↔ Service ↔ Repository ↔ Storage/Adapter)
- Repository pattern for data access abstraction
- Unit of Work pattern for managing transactions (CSV version implemented)
- Data Transfer Objects (DTOs) and dataclasses for data models
- Dependency injection through constructor parameters
- Abstract base classes for adapters to allow swappable backends (CSV ↔ potential future DB backends)

### Testing Strategy
- Use pytest for testing
- Unit tests for individual functions and methods
- Integration tests for repository and service layers
- End-to-end tests for UI components where feasible
- Test sanity check exists at tests/test_sanity.py

### Git Workflow
- Feature branches for new functionality
- Descriptive commit messages focusing on the "why" rather than the "what"
- Pull requests for code reviews before merging to main branch
- Branch naming convention: feature/your-feature-name, bugfix/issue-description

## Domain Context
- Employee data is stored in CSV files in the /data directory
- Main employee table is BASIC.csv with fields like EMP_ID, C_Name, Title, etc.
- Lookups and reference data are stored in separate CSV files (L_Section.csv, Area.csv, etc.)
- EMP_ID serves as the primary identifier for employees
- Boolean fields are stored as string values "true"/"false" in CSV
- Dates are stored as string values in consistent format (YYYY-MM-DD or YYYY/MM/DD)
- The system handles upsert operations (update if exists, create if not)
- File locking is implemented to prevent data corruption during concurrent access

## Important Constraints
- CSV files are used instead of traditional databases, limiting concurrent write operations
- Date fields are stored as strings, requiring conversion for date operations
- Boolean fields stored as strings require parsing
- File locking reduces but doesn't eliminate all risks of data corruption in high-concurrency scenarios
- Desktop UI is built with PySide6, making it a client-side application
- Data validation primarily occurs at the service layer
- Export functionality generates Excel files to the exports/ directory

## External Dependencies
- CSV files in the /data directory serve as the primary data store
- Environment variables via .env file for configuration
- YAML configuration via config/settings.yaml
- Optional FastAPI API server for web access to data
- Pandas for data processing and manipulation
- Excel export functionality via openpyxl
- File locking via filelock for safe concurrent access
- SQLAlchemy used in some parts of the project for database connectivity (potentially legacy)
