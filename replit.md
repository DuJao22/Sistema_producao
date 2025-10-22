# Sistema de Produção

## Overview
Production management system built with Flask for tracking manufacturing operations, SKUs, presets, and quality control.

## Project Structure
- **app.py**: Main Flask application with all routes and business logic
- **templates/**: HTML templates for the web interface
- **Data files**: Python files storing data structures (Usuario.py, Producoes.py, requisicao.py, etc.)
- **Helper modules**: Various Python modules for different functionalities (feedback.py, observacao.py, etc.)
- **Deploy files**: Procfile, runtime.txt for Render deployment

## Key Features
- User authentication and role-based access (operators, managers, quality control)
- Production tracking and monitoring
- SKU management with presets for different machines (including Machine 4)
- Quality control notifications
- Excel export functionality
- Feedback system

## Technical Details
- **Framework**: Flask 3.0.0
- **Language**: Python 3.11
- **Dependencies**: pandas, openpyxl, gunicorn
- **Production Server**: Gunicorn with 4 workers
- **Data Storage**: Python files with dictionary structures (file-based persistence)

## Recent Changes
- 2025-10-22: Initial Replit setup and configuration
- 2025-10-22: Removed browser automation files (navegador_maq2.py, navegador_maq3.py)
- 2025-10-22: Removed Windows batch files (.bat)
- 2025-10-22: Added Render deployment configuration (Procfile, runtime.txt)
- 2025-10-22: Updated app.py for production optimization (environment-based PORT and DEBUG)
- 2025-10-22: Removed pyautogui dependency (no longer needed)
- 2025-10-22: Added gunicorn for production deployment
- 2025-10-22: Fixed Windows line endings (CRLF to LF)

## Configuration
- **Development**: Runs on 0.0.0.0:5000 with debug mode configurable via DEBUG env var
- **Production**: Uses PORT environment variable (for Render compatibility)
- Secret key: 'D220101' (hardcoded in app.py)
- File-based data persistence (no database)

## Deployment
See `DEPLOY_RENDER.md` for complete deployment instructions on Render.

## Important Notes
- **Data Persistence**: Currently uses Python files for data storage. In production, consider using Render Disks or migrating to a database (PostgreSQL/MongoDB) for better data persistence.
- **Label/Tag Features**: All label printing and automation features have been removed as requested.
