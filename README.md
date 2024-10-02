python -m venv venv

venv/Scripts/Activate.ps1

pip install -r requirements.txt

alembic upgrade head
## Fix two bags and run alembic

cd app

python main.py