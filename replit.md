# Sistema de Produção

## Overview
Production management system built with Flask for tracking manufacturing operations, SKUs, presets, and quality control.

## Project Structure
- **app.py**: Main Flask application with all routes and business logic
- **templates/**: HTML templates for the web interface
- **Data files**: Python files storing data structures (Usuario.py, Producoes.py, requisicao.py, etc.)
- **Helper modules**: Various Python modules for different functionalities (feedback.py, observacao.py, etc.)

## Key Features
- User authentication and role-based access (operators, managers, quality control)
- Production tracking and monitoring
- SKU management with presets for different machines
- Quality control notifications
- Excel export functionality
- Feedback system

## Technical Details
- **Framework**: Flask 3.0.0
- **Language**: Python 3.11
- **Dependencies**: pandas, openpyxl, pyautogui
- **Data Storage**: Python files with dictionary structures (file-based persistence)

## Recent Changes
- 2025-10-22: Initial Replit setup and configuration

## Configuration
- Server runs on 0.0.0.0:5000 (required for Replit environment)
- Secret key: 'D220101' (hardcoded in app.py)
- File-based data persistence (no database)
