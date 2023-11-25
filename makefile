celery_worker:
	celery -A flask_api.app.celery worker -B --loglevel=info
celery_beat:
	celery -A flask_api.app.celery beat --loglevel=info
create_database:
	python flask_api/players_data/create_database.py
flask_app:
	python flask_api/app.py
run_front:
	cd front && npm run dev
basic_script:
	python mpg_main.py
