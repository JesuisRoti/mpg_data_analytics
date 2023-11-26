celery_worker:
	celery -A flask_api.app.celery worker -B --loglevel=info
celery_beat:
	celery -A flask_api.app.celery beat --loglevel=info
create_database:
	python flask_api/players_data/create_database.py
flask_app:
	python flask_api/app.py
run_front_dev:
	cd front && npm run dev
run_front_prod:
	cd front && npm run build && npm run start
basic_script:
	python mpg_main.py
