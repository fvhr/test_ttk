python -m venv venv

venv/Scripts/Activate.ps1

pip install -r requirements.txt

cd app

uvicorn main:app --reload