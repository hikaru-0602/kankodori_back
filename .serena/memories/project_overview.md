# Project Overview: 観光地検索 API (Kankodori)

## Purpose
This is a Japanese tourism API called "観光地検索" (Tourist Spot Search) that allows users to search for tourist destinations using text or images. The API provides search functionality and image suggestions for travel planning.

## Tech Stack
- **Backend Framework**: FastAPI (Python)
- **Language**: Python 3.x
- **Key Libraries**: 
  - FastAPI for web framework
  - Uvicorn as ASGI server
  - Firebase Admin SDK for authentication
  - Google Cloud Storage/Firestore for data storage
  - Various ML libraries (PyTorch, Transformers, etc.)
  - Image processing libraries (Pillow, etc.)
- **Authentication**: Firebase Authentication
- **Cloud Platform**: Google Cloud Platform (Cloud Run)
- **Containerization**: Docker

## Main Features
1. Text-based tourist spot search
2. Image-based tourist spot search
3. Image suggestions for users
4. Firebase authentication
5. API logging functionality

## Architecture
The project follows a clean architecture pattern:
- `main.py`: FastAPI application entry point
- `controllers/`: Request handlers and business logic
- `services/`: Core business services
- `infrastructures/`: External integrations (Firebase, etc.)
- `repositories/`: Data access layer