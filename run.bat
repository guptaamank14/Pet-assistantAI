@echo off
:: Activate virtual environment
call venv\Scripts\activate

:: Start the FastAPI server
uvicorn app:app --reload --host 0.0.0.0 --port 8000