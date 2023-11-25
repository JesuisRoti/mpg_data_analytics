celery_worker:
	celery -A flask_api.app.celery worker -B --loglevel=info
celery_beat:
	celery -A flask_api.app.celery beat --loglevel=info
create_database:
	python players_data/create_database.py
