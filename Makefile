create_venv:
	@python -m venv venv
	@venv/Scripts/activate

install_requirements:
	@pip install -r requirements/prod.txt

make_migrations:
	@cd app && alembic revision --autogenerate
	@cd app && alembic upgrade head

run_project:
	@cd app && python main.py




