@echo off
call %~dp0..\.venv\Scripts\activate.bat
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

